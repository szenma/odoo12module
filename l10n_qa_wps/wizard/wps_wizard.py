# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
import time ,base64 ,os, io ,csv
from datetime import datetime
import tempfile
import calendar

class WPSReportWizard(models.TransientModel):
    _name = "wps.report"
    _description = "WPS Report"
    
    SALARIES_total = 0.0
    file = fields.Binary("File")
    file_name = fields.Char("File name")
    from_date = fields.Date('From date', required=True)
    to_date = fields.Date('To date', required=True)
    employee_ids = fields.Many2many('hr.employee', 'salary_detail_employee_rel', 'employee_id', 'report_id',required=True)
    partner_bank_id = fields.Many2one("res.partner.bank", string="Bank", required=True)
    state = fields.Selection([('draft','Draft'),
                              ('done','Done'),
                              ('all','Draft and Done'),]
                              ,'Payslip State', required=True)
    
    def get_report_data(self):
        state_domain = [('state','in',['draft','done'])] if self.state == "all" else [('state','=',self.state)]
        total_salaries = 0
        payslip_obj = self.env['hr.payslip']
        payslip_line_obj = self.env['hr.payslip.line']
        res=[]
        apply_refund = hasattr(payslip_obj,"refund_id")
        employees = []
        month_days = calendar.monthrange(self.from_date.year,self.from_date.month)[1]
        payslips = payslip_obj.search([("employee_id",'in',self.employee_ids.ids),
                                        ("date_from",">=",self.from_date),
                                        ("credit_note",'=',False),
                                         ("date_to","<=",self.to_date)
                                         ]+state_domain , order="id desc" )
        
        refunded_slips = []
        if apply_refund:
            refunded_slips = payslip_obj.search([("employee_id",'in',self.employee_ids.ids),
                            ("date_from",">=",self.from_date),
                            ("credit_note",'=',True),
                            ("date_to","<=",self.to_date),
                            ('refund_id','!=',False)
                             ]+state_domain).mapped("refund_id.id")
        
        
        i = 1
        for slip in payslips.filtered(lambda x:x.id not in refunded_slips):          
            net = 0
            allowances = 0
            deductions = 0
            basic = slip.employee_id.contract_id.basic if 'basic' in slip.employee_id.contract_id._fields else slip.employee_id.contract_id.wage       
            for pLine in slip.line_ids:
                if pLine.category_id.code == 'NET':
                    net += pLine.total
                elif pLine.category_id.code == 'ALW' or pLine.category_id.code == 'EXTRA':
                    allowances += pLine.total
                elif pLine.category_id.code == 'DED':
                    deductions += abs(pLine.total)
            employee = slip.employee_id
            payment_method = "Settlement" if slip.input_line_ids.filtered(lambda x:x.code == "EOSB") else "Normal Payment"
            if employee not in employees:
                employees.append(employee)
                value = [i,employee.qid if "qid" in employee._fields else employee.identification_id or "" ,employee.visa_no or "",employee.name,employee.bank_account_id.bank_id.bank_bsc or "",
                        employee.bank_account_id and employee.bank_account_id.acc_number or "",str(slip.employee_id.contract_id and slip.employee_id.contract_id.schedule_pay and  slip.employee_id.contract_id.schedule_pay)[0] or ""
                         ,0 if slip.unpaid_days == slip.actuall_days else int(month_days-slip.unpaid_days),net,basic,int(slip.overtime if "overtime" in slip._fields else slip.extra_hours),allowances
                         ,deductions,payment_method,slip.name]
                self.SALARIES_total += net
                res.append(value)
                i+=1
        return res 
    
    def export_file(self):
        rows = [] 
        temp_file = tempfile.NamedTemporaryFile(suffix=".csv")
        company = self.env.user.company_id
        data = self.get_report_data()
        seq = 1
        rows.append(["Employer EID","File Creation Date","File Creation Time","Payer EID","Payer QID",
                     "Payer Bank Short Name","Payer IBAN","Salary Year and Month","Total Salaries","Total records"])
        
        rows.append([company.employer_id or "",str(fields.Date.today()).replace("-",""),str(datetime.now().time()).replace(":","")[0:4],
                     company.payer_eid or "", company.payer_qid if not company.payer_eid else "" 
                    ,self.partner_bank_id.bank_id.bank_bsc or "",self.partner_bank_id.acc_number,str(self.from_date)[0:7].replace("-",""),
                    self.SALARIES_total,len(data)])
        
        rows.append(['Record Sequence','Employee QID','Employee Visa ID','Employee Name','Employee Bank Short Name','Employee Account','Salary Frequency','Number of Working Days'
                    ,'Net Salary','Basic Salary','Extra hours','Extra Income','Deductions','Payment Type','Notes / Comments'])
        for payslip in  data:
           rows.append(payslip)
        
        
        with open(temp_file.name, mode='w') as file:
            writer = csv.writer(file, dialect=None)
            writer.writerows(rows)
        file = open(temp_file.name,"rb")

        self.file =  base64.encodestring(file.read())
        self.file_name = "SIF_%s_%s_%s_%s.csv"%(company.employer_id,self.partner_bank_id.bank_id.bank_bsc,str(fields.Date.today()).replace("-",""),str(datetime.now().time()).replace(":","")[0:4])
        
        return {
            'type': 'ir.actions.report',
            'report_name': self._name + '-%d' % self.id,
            'report_type': 'qweb-pdf',
             
        }
