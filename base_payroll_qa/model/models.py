# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime,timedelta,time
import calendar
    

class HrContract(models.Model):
    _inherit = 'hr.contract'
    
     
    @api.multi
    def write(self, vals):
        res = super(HrContract, self).write(vals)
        if vals.get('resource_calendar_id',False):
            for contract in self:
                contract.employee_id.resource_calendar_id = vals['resource_calendar_id']
        return res
    
    
    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(HrContract, self).create(vals)
        for contract in self.filtered(lambda x:x.employee_id):
            contract.employee_id.resource_calendar_id = contract.resource_calendar_id
        return res


class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = 'hr.payslip'
    
    refund_id = fields.Many2one('hr.payslip', 'Refunded Slip', readonly=True)
    actuall_days = fields.Float('Number Of Days', help="Scheduled working days in period", compute="_compute_employee_days")
    paid_days = fields.Float("Number of Paid Days", compute="_compute_employee_days")
    unpaid_days = fields.Float("Number of UnPaid Days", compute="_compute_employee_days")
    show_refund_button = fields.Boolean("Show Refund Button", compute="_compute_show_refund_button")
    slip_days = fields.Float("Month Days", compute="_compute_employee_days")
    
    def _compute_show_refund_button(self):
        for rec in self:
            refund = self.search([("refund_id","=",rec.id)],limit=1)
            rec.show_refund_button = not  (refund or rec.credit_note)
    
    @api.multi
    def refund_sheet(self):
        return super(HrPayslip, self.with_context(from_refund=True)).refund_sheet()
   
    
    @api.multi
    @api.returns('self', lambda value:value.id)
    def copy(self, default=None):
        res =  super(HrPayslip, self).copy(default)
        if 'from_refund' in self._context:
            for rec1,rec2 in zip(res,self):
                rec1.number = rec1.number or  self.env['ir.sequence'].next_by_code('salary.slip')
                
                rec1.refund_id = rec2.id
        return res
    
    
    @api.depends("employee_id",'date_to','date_from')
    def _compute_employee_days(self):
        for rec in self.filtered(lambda x:x.employee_id and x.date_from and x.date_to):
            paid = 0
            data = self.actuall_days_hours_to_work(rec.employee_id, rec.date_from, rec.date_to)
            rec.actuall_days = data['days']
            max_day = calendar.monthrange(rec.date_from.year,rec.date_from.month)[1]
            for line in rec.worked_days_line_ids:
                if line.code != "WORK100":
                    leave_type = self.env["hr.leave.type"]
                    if hasattr(leave_type, 'code'):
                        domain = ['|',('code','=',line.code),('name','=',line.code)]
                    else :
                        domain = [('name','=',line.code)]
                    leave_rec = self.env['hr.leave.type'].search(domain,limit=1)
                    if not(leave_rec.unpaid):
                        paid+=line.number_of_days
            rec.paid_days = paid+sum(line.number_of_days for line in rec.worked_days_line_ids if line.code == "WORK100")
            leaves = self.env["hr.leave"].search([('holiday_status_id.unpaid','=',True),
                                         ('employee_id','=',rec.employee_id.id),
                                         '|','|',('request_date_from','>=',rec.date_from),
                                         ('request_date_from','<=',rec.date_to),
                                         '|',('request_date_to','>=',rec.date_from),
                                         ('request_date_to','<=',rec.date_to),
                                         ])
            days = 0
            for leave in leaves:
                if leave.request_date_from < rec.date_from and leave.request_date_to > rec.date_from and leave.request_date_to < rec.date_to:
                    days+=(leave.request_date_to + timedelta(days=1) - rec.date_from).days
                elif  leave.request_date_from >= rec.date_from and leave.request_date_from <= rec.date_to and leave.request_date_to < rec.date_to:  
                    days+=(leave.request_date_to + timedelta(days=1) - leave.request_date_from).days
                elif  leave.request_date_from >= rec.date_from and leave.request_date_from <= rec.date_to and  leave.request_date_to >= rec.date_to:  
                    days+=(rec.date_to + timedelta(days=1)- leave.request_date_from).days    
                elif  leave.request_date_from <= rec.date_from and leave.request_date_to >= rec.date_to:  
                    days+=(rec.date_to + timedelta(days=1) - rec.date_from).days    
            rec.unpaid_days = days
            rec.slip_days = (rec.date_to + timedelta(days=1) - rec.date_from).days  
            
    def actuall_days_hours_to_work(self, employee_id ,_from, _to):
        '''
            This function will get the number of days,hours that employees should works in period.
            Depends on working schedule in contract page.
        '''
        day_of_week = {'Monday':'0' ,'Tuesday':'1' ,'Wednesday':'2' ,'Thursday':'3' ,'Friday':'4' ,'Saturday':'5' ,'Sunday':'6' }
        hours_of_days = {}
        number_of_hours = number_of_days = 0.0
        res = {'hours': 0.0, 'days': 0.0}
        date_from = _from
        date_to = _to
        if employee_id:
            contract = employee_id.contract_id
            if contract.resource_calendar_id:
                break_duration = 0.0
                if hasattr(contract.resource_calendar_id, 'break_duration'):
                    break_duration = contract.resource_calendar_id.break_duration
                for day in contract.resource_calendar_id.attendance_ids:
                    if hours_of_days.get(str(day.dayofweek), False): 
                        hours_of_days[str(day.dayofweek)] +=  day.hour_to - day.hour_from - break_duration
                    else:
                        hours_of_days[str(day.dayofweek)] =  day.hour_to - day.hour_from - break_duration
                while date_from <= date_to: 
                    date_day = day_of_week[date_from.strftime('%A')]
                    if date_day in hours_of_days.keys():
                        number_of_days += 1
                        number_of_hours += hours_of_days[date_day]
                    date_from = date_from+timedelta(days=1)
        res['hours'] = number_of_hours
        res['days'] = number_of_days
        return res
    
    @api.model
    def create(self, vals):
        res = super(HrPayslip, self).create(vals)
        res.onchange_employee()
        return res
    
