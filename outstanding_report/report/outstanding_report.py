#-*- coding:utf-8 -*-

from odoo import api, fields, models, _
import time

class OutStandingReport(models.AbstractModel):
    _name = 'report.outstanding_report.invoice_outstanding_report'
    _description = "Invoice Outstanding Report"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        return {
             'doc_ids': docids,
            'doc_model': 'account.invoice',
            'docs': {},
            'time': time,
            'data': data,
        }
