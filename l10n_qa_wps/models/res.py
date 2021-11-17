# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class Company(models.Model):
    _inherit = "res.company"
    
    employer_id = fields.Char('Employer ID')
    payer_eid = fields.Char('Payer EID')
    payer_qid = fields.Char('Payer QID')

class Bank(models.Model):
    _inherit = "res.bank"
    
    bank_bsc = fields.Char(string='Bank Short Code')
    
class PartnerBank(models.Model):
    _inherit = "res.partner.bank"
    
    wps_activated = fields.Boolean("WPS activated")
        
    @api.multi
    def name_get(self):
        names = super(PartnerBank, self).name_get()
        result_dict = {}
        result = []
        for name in names:
            result_dict[name[0]] = name[1]
        for rec in self:
            name = rec.bank_id.name if rec.bank_id else "" + "-" if rec.bank_id and rec.acc_number else "" + rec.acc_number if rec.acc_number else ""
            result.append((rec.id,rec.bank_id.name + "-" + name))
            
        return result
    
class Contract(models.Model):
    _inherit = 'hr.contract'
    
    schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('bi-weekly', 'Bi-weekly'),
    ], string='Scheduled Pay', index=True, default='monthly',
    help="Defines the frequency of the wage payment.")
    
class Payslip(models.Model):
    _inherit = "hr.payslip"
     
    extra_hours = fields.Float("Extra Hours")
     
