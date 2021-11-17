# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    cheque_date = fields.Date('Cheque Date',readonly=True, states={'draft': [('readonly', False)]} )
    
    
    def get_journal_entries(self):
        return self.move_line_ids.mapped("move_id")
    
    
    def _get_report_values(self,move):
        return self.env["report.journal_entry_report.report_journal_entries"]._get_report_values(move.ids)
    
    
    
    def get_columns(self,move):
        return self.env["report.journal_entry_report.report_journal_entries"].get_columns(move)
    
    
    def get_total(self,move):
        vals = self._get_report_values(move)
        return vals["Totals"]
    
        
        
        
        

