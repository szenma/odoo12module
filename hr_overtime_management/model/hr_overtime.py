# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
CT = fields.Datetime.context_timestamp
from odoo.exceptions import UserError
import datetime
from datetime import timedelta, date
from pytz import timezone, all_timezones, UTC
import time


def period_datetime(a, b):
    dt_list = []
    nod = (b - a).days
    if a.date() == b.date():
        return [[a, b]]
    dt_list.append([a, a.replace(hour=23, minute=59, second=59, microsecond=999999)])
    for i in range(1 , nod):
        dt_list.append([a.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=i),
                    a.replace(hour=23, minute=59, second=59, microsecond=999999)+ datetime.timedelta(days=i)])
    dt_list.append([b.replace(hour=0, minute=0, second=0, microsecond=0), b])
    return dt_list


class resource_calendar(models.Model):
    _inherit = "resource.calendar"

    overtime_off_days = fields.Float('Holiday Overtime Rate')
    overtime_work_days = fields.Float('Normal Overtime Rate')


class hr_overtime(models.Model):
    _name = "hr.overtime"
    _rec_name = "employee_id"
    _order = "id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    date = fields.Date('Date', required=True, readonly=True, default=fields.Date.today(), states={'draft': [('readonly', False)]}, track_visibility='onchange')
    start_datetime = fields.Datetime('Start Date', required=True, readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    end_datetime = fields.Datetime('End Date', required=True, readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    start_datetime_text = fields.Char('Employee Start Date',   compute='_compute_text_field', store=True)
    end_datetime_text = fields.Char('Employee End Date', compute='_compute_text_field', store=True)
    duration = fields.Float('Duration by hour', compute='calculate_overtime', readonly=True, store=True)
    overtime = fields.Float('Overtime by hour', compute='calculate_overtime', readonly=True, store=True)
    analytic_account_id = fields.Many2one('account.analytic.account',string="Cost Center/Project", readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('first_approve', 'First Approval'),
                              ('second_approve', 'Second Approval'),
                              ('done', 'Done'),
                              ('cancel', 'Canceled')], string='Status', default='draft', track_visibility='onchange')
    cost = fields.Float('Total Cost', compute='calculate_overtime', readonly=True, store=True)
    analytic_line_id = fields.Many2one('account.analytic.line', readonly=True,copy=False, track_visibility='onchange')
    payslip_id = fields.Many2one('hr.payslip', 'Payslip', readonly=True)
    show_analytic_fields = fields.Boolean(compute='_compute_show_analytic_fields')
    is_employee = fields.Boolean(compute='_compute_is_employee')
    do_first_approval = fields.Boolean(compute='button_privilege')
    do_second_approval = fields.Boolean(compute='button_privilege')
    do_done = fields.Boolean(compute='button_privilege')
    note = fields.Text('Notes')
    
    @api.depends('end_datetime','start_datetime','employee_id')
    def _compute_text_field(self):
        record_lang = self.env['res.lang'].search([("code", "=", self._context['lang'])], limit=1)
        format_date, format_time = record_lang.date_format,record_lang.time_format
        strftime_pattern = (u"%s %s" % (format_date,format_time))
        for rec in self:
            if rec.end_datetime and rec.employee_id:
                to_dt = fields.Datetime.from_string(rec.end_datetime).replace(tzinfo=UTC)
                to_dt = to_dt.astimezone(timezone(rec.employee_id.tz))
                rec.end_datetime_text = to_dt.strftime(strftime_pattern)
                
            else:
                rec.end_datetime_text = False
            if rec.start_datetime and rec.employee_id:
                from_dt = fields.Datetime.from_string(rec.start_datetime).replace(tzinfo=UTC)
                from_dt = from_dt.astimezone(timezone(rec.employee_id.tz))
                rec.start_datetime_text =  from_dt.strftime(strftime_pattern)
            else:
                rec.start_datetime_text = False
        
    @api.multi
    @api.depends('state')
    def button_privilege(self):
        employee_id = self.env['hr.employee'].search([('user_id','=',self._uid)],limit = 1)
        if employee_id:
            for rec in self:
                if employee_id.id == rec.employee_id.parent_id.id:
                    rec.do_first_approval = True
                if employee_id.id == rec.employee_id.department_id.manager_id.id:
                    rec.do_second_approval = True
        ad_mng = self.env.user.has_group('account.group_account_manager') or  self.env.user.has_group('hr_payroll.group_hr_payroll_manager')or  self.env.user.has_group('hr.group_hr_manager')

        if ad_mng:
            self.update({'do_done': True })
            
            
    @api.multi
    @api.depends('state')
    def _compute_is_employee(self):
        is_officer = self.env.user.has_group('hr.group_hr_user')
        self.update({'is_employee': not is_officer })
    
    
    @api.model
    def default_get(self, fields_list):
        res = super(hr_overtime, self).default_get(fields_list)
        employee_id = self.env['hr.employee'].search([('user_id','=',self._uid)],limit = 1)
        res['employee_id'] = employee_id and employee_id.id or False
        return res
        
    @api.multi
    @api.depends('state')
    def _compute_show_analytic_fields(self):
        show_analytic_fields = self.env.user.company_id.overtime_analytic == 'with_entries'
        for rec in self:
            rec.show_analytic_fields = show_analytic_fields
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        res = super(hr_overtime, self).create(vals)
        add_follower = self.env['mail.wizard.invite'].create({'res_model':self._name, 'res_id':res.id,
                                           'partner_ids':[(4, id) for id in self.env.user.company_id.users_to_notify_ot_ids.mapped('partner_id.id') + res.employee_id.mapped('parent_id.user_id.partner_id.id') + res.employee_id.mapped('department_id.manager_id.user_id.partner_id.id')]})
        add_follower.add_followers()
        return res
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError('You cannon delete confirmed record')
        return super(hr_overtime, self).unlink()
    

    @api.onchange('end_datetime', 'start_datetime','employee_id')
    @api.constrains('employee_id', 'end_datetime', 'start_datetime')
    def constrains_employee_id(self):
        payslip_obj = self.env['hr.payslip']
        if not (self.employee_id and self.start_datetime and self.end_datetime):
            return
        contract_ids = payslip_obj.get_contract(self.employee_id , self.start_datetime, self.end_datetime)
        if not contract_ids:
            raise UserError("Please make sure the employee has a running contract.")
   
    @api.constrains('end_datetime', 'start_datetime')
    def date_constrains(self):
        for rec in self:
            if rec.start_datetime and rec.end_datetime and rec.start_datetime > rec.end_datetime:
                raise UserError(_('The start date must be before the end date.'))
    
    @api.one
    @api.depends('employee_id', 'start_datetime', 'end_datetime')
    def calculate_overtime(self):
        if not(self.start_datetime or self.end_datetime):
            self.cost = self.overtime = self.duration = 0.0
        payslip_obj = self.env['hr.payslip']
        contract_id = False   
        if self.start_datetime and self.end_datetime and self.employee_id:
            contract_ids = payslip_obj.get_contract(self.employee_id , self.start_datetime, self.end_datetime)
            if contract_ids:
                contract_id = self.env['hr.contract'].browse(contract_ids[0])
            from_dt = fields.Datetime.from_string(self.start_datetime).replace(tzinfo=UTC)
            to_dt = fields.Datetime.from_string(self.end_datetime).replace(tzinfo=UTC)
            from_dt = from_dt.astimezone(timezone(self.employee_id.tz))
            to_dt = to_dt.astimezone(timezone(self.employee_id.tz))
            # # just for overtime
            work_overtiem = 0.0
            off_overtiem = 0.0
            cost_by_hour = 0.0
            if contract_id:
                cost_by_hour = contract_id.wage / 30.4 / 8
                work_overtiem = contract_id.resource_calendar_id.overtime_work_days
                off_overtiem = contract_id.resource_calendar_id.overtime_off_days
            # #
            
            over_time = 0.0
            total_hours = 0.0 
            for r in self._calculate_durations(from_dt, to_dt, contract_id):
                total_hours += r[0]
                if r[1]:
                    over_time += r[0] * off_overtiem
                else:
                    over_time += r[0] * work_overtiem
            self.duration = total_hours
            self.overtime = over_time
            self.cost = over_time * cost_by_hour
    
    @api.model
    def _calculate_durations(self, from_dt , to_dt, contract_id):
        calendar = {}
        overtime_list = []
        for line in contract_id.resource_calendar_id.attendance_ids:
            dayofweek = int(line.dayofweek)
            if dayofweek not in calendar:
               calendar[dayofweek] = {'start':line.hour_from, 'end':line.hour_to}
            else:
                if line.hour_from < calendar[dayofweek]['start']:
                    calendar[dayofweek]['start'] = line.hour_from
                if line.hour_to > calendar[dayofweek]['end']:
                    calendar[dayofweek]['end'] = line.hour_to
        
        for from_dt , to_dt in period_datetime(from_dt, to_dt):
            float_time_from = from_dt.hour + from_dt.minute / 60
            float_time_to = to_dt.hour + to_dt.minute / 60
            dow = from_dt.weekday()
            if not self.is_off_day(from_dt  , contract_id, calendar):
                if float_time_from > calendar[dow]['end'] or  float_time_to < calendar[dow]['start']:
                    duration = (to_dt - from_dt).total_seconds() / 60 / 60
                    overtime_list.append([duration, False])
                else:
                    if float_time_from < calendar[dow]['start']:
                        from_dt1 = from_dt.replace(minute=int((calendar[dow]['start'] - int(calendar[dow]['start'])) * 100 * 0.6), hour=int(calendar[dow]['start']))
                        duration = (from_dt1 - from_dt).total_seconds() / 60 / 60
                        overtime_list.append([duration, False])
                    if float_time_to > calendar[dow]['end']:
                        to_dt1 = to_dt.replace(minute=int((calendar[dow]['end'] - int(calendar[dow]['end'])) * 100 * 0.6), hour=int(calendar[dow]['end']))
                        duration = (to_dt - to_dt1).total_seconds() / 60 / 60
                        overtime_list.append([duration, False])
                    
            else:
                duration = (to_dt - from_dt).total_seconds() / 60 / 60
                overtime_list.append([duration, True])
        return overtime_list
    
    @api.model
    def is_off_day(self, date_time  , contract, calendar):
        if 'hr.public_holiday' in self.env:
            public_holiday = self.env['hr.leave'].search([('date', '>=', str(date_time)[:10] + ' 00:00:00'),
                                                                   ('date_to', '<=', str(date_time)[:10] + ' 23:59:59'),
                                                                   ('holiday_status_id.is_public_holiday', '=', True),
                                                                   ('state', '=', 'validate'),
                                                                   ('employee_id', '=', contract.employee_id.id)])
            if public_holiday:
                return True
        if date_time.weekday() not in calendar:
            return True
        return False
        
    @api.multi
    def done_overtime(self):
        analytic_line_pool = self.env['account.analytic.line']
        timenow = time.strftime('%Y-%m-%d')
        tag = self.env.ref('hr_overtime_management.overtime_tag')
        general_account_id = False
        vals_1 = {'state':'done'}
        if self.show_analytic_fields:
            vals = {
                    'name': _('Overtime for ') + str(self.employee_id.name),
                    'account_id': self.analytic_account_id and self.analytic_account_id.id or False,
                    'tag_ids' : [(6, 0, [tag.id])],
                    'date': timenow,
                    'unit_amount': self.overtime,
                    'general_account_id': self.env.user.company_id.overtime_account_id.id,
                    'amount': self.cost * -1,
                    }
            res = analytic_line_pool.create(vals)
            vals_1['analytic_line_id'] = res.id
        self.write(vals_1)    
        return True
        
    @api.multi
    def confirm(self):
        self.write({'state':'confirmed'})  
        
    @api.multi
    def first_approve(self):
        self.write({'state':'first_approve'})    
        
    @api.multi
    def second_approve(self):
        self.write({'state':'second_approve'})

    @api.multi
    def draft(self): 
        self.write({'state':'draft'})
        
    @api.multi
    def cancel(self):
        self.analytic_line_id.unlink()
        self.write({'state':'cancel'})
    
    
     
class hr_payslip_inhe(models.Model): 
    _inherit = 'hr.payslip'
    
    extra_hours = fields.Float("Extra Hours", compute="_compute_extra_hours")
    
    @api.depends("employee_id","date_from","date_to")
    def _compute_extra_hours(self):
        ot_obj = self.env['hr.overtime']
        for rec in self:
            if self.env.user.company_id.overtime_type == 'request':
                overtime_ids = self.env['hr.overtime'].search([('state', '=', 'done'),
                                                                ('employee_id', '=', rec.employee_id.id),
                                                                ('date', '>=', fields.Date.to_string(rec.date_from)),
                                                                ('date', '<=', fields.Date.to_string(rec.date_to)),
                                                                '|',('payslip_id', '=', False),('payslip_id', '=', rec.id)])
                if overtime_ids:
                    rec.extra_hours = sum(overtime_ids.mapped("duration"))
            elif self.env.user.company_id.overtime_type == 'attendance':
                total_overtime = 0.0
                att_ids = self.env['hr.attendance'].search([('employee_id', '=', rec.employee_id.id),
                                                  ('check_in', '>=', fields.Date.to_string(rec.date_from)),
                                                  ('check_in', '<', fields.Date.to_string(rec.date_to) + ' 24:00:00'),
                                                  ('check_out', '!=', False)])
                overtime_list = []
                for att_id in att_ids:
                    check_in = fields.Datetime.from_string(att_id.check_in).replace(tzinfo=UTC)
                    check_in = check_in.astimezone(timezone(att_id.employee_id.tz))
                    check_out = fields.Datetime.from_string(att_id.check_out).replace(tzinfo=UTC)
                    check_out = check_out.astimezone(timezone(att_id.employee_id.tz))
                    overtime  = ot_obj._calculate_durations( check_in, check_out,contract)
                    if overtime:
                        overtime_list.extend(overtime)
                if overtime_list:
                    work_overtiem = contract.resource_calendar_id.overtime_work_days
                    off_overtiem = contract.resource_calendar_id.overtime_off_days
                    total_overtime = 0.0
                    for i in overtime_list:
                        total_overtime += i[0] * (off_overtiem if i[1] else work_overtiem)
                rec.extra_hours = total_overtime
                    
    @api.multi
    def refund_sheet(self):
        for payslip in self:
            overtime_ids = self.env['hr.overtime'].search([('state', '=', 'done'),
                                                                ('employee_id', '=', self.employee_id.id),
                                                                ('date', '>=', self.date_from),
                                                                ('date', '<=', self.date_to)])
            overtime_ids.write({'payslip_id':False})
        return super(hr_payslip_inhe, self).refund_sheet()
    
    @api.multi
    def action_payslip_done(self):
        res = super(hr_payslip_inhe, self).action_payslip_done()
        for payslip in self.filtered(lambda x: not x.credit_note):
            overtime_ids = self.env['hr.overtime'].search([('state', '=', 'done'),
                                                                ('employee_id', '=', payslip.employee_id.id),
                                                                ('date', '>=', payslip.date_from),
                                                                ('date', '<=', payslip.date_to)])
            
            overtime_ids.write({'payslip_id':payslip.id})
        
        return res
    
    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        res = super(hr_payslip_inhe, self).get_inputs(contracts, date_from, date_to)
        ot_obj = self.env['hr.overtime']
        if self.employee_id and date_from and date_to and contracts:
            contract =  contracts[0]
            
            if self.env.user.company_id.overtime_type == 'request':
                overtime_ids = self.env['hr.overtime'].search([('state', '=', 'done'),
                                                                ('employee_id', '=', self.employee_id.id),
                                                                ('date', '>=', fields.Date.to_string(date_from)),
                                                                ('date', '<=', fields.Date.to_string(date_to)),
                                                                ('payslip_id', '=', False)])
                if overtime_ids:
                    total_overtimes = 0.0
                    total_overtimes_holiday = 0.0
                    for rec in overtime_ids:
                        total_overtimes += rec.cost
                             
                    if total_overtimes:
                        vals = {'name': 'Overtime', 'code': 'OTN', 'amount': total_overtimes, 'contract_id': contract.id}
                        res += [vals]
            elif self.env.user.company_id.overtime_type == 'attendance':
                att_ids = self.env['hr.attendance'].search([('employee_id', '=', contract.employee_id.id),
                                                  ('check_in', '>=', fields.Date.to_string(date_from)),
                                                  ('check_in', '<', fields.Date.to_string(date_to) + ' 24:00:00'),
                                                  ('check_out', '!=', False)])
                overtime_list = []
                for att_id in att_ids:
                    check_in = fields.Datetime.from_string(att_id.check_in).replace(tzinfo=UTC)
                    check_in = check_in.astimezone(timezone(att_id.employee_id.tz))
                    check_out = fields.Datetime.from_string(att_id.check_out).replace(tzinfo=UTC)
                    check_out = check_out.astimezone(timezone(att_id.employee_id.tz))
                    overtime  = ot_obj._calculate_durations( check_in, check_out,contract)
                    if overtime:
                        overtime_list.extend(overtime)
                if overtime_list:
                    cost_by_hour = contract.wage / 30.4 / 8
                    work_overtiem = contract.resource_calendar_id.overtime_work_days
                    off_overtiem = contract.resource_calendar_id.overtime_off_days
                    toata_hours = 0.0
                    for i in overtime_list:
                        toata_hours += i[0] * (off_overtiem if i[1] else work_overtiem)
                    vals = {'name': 'Overtime %0.2f Hour(s)'%toata_hours, 'code': 'OTN', 'amount': toata_hours * cost_by_hour, 'contract_id': contract.id}
                    res += [vals]
                
        return res
