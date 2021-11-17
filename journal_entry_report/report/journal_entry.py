# -*- coding: utf-8 -*-
import time
from odoo import api, fields, models,_
from odoo.tools.misc import formatLang

class ReportJournalEntry(models.AbstractModel):
    _name = 'report.journal_entry_report.report_journal_entries'
    _description = 'Journal Entry Report'
    
    
    def get_columns(self,move):
        columns = {_('Amount Currency'):['amount_currency',False],_('Partner'):['partner_id',False],
                   _('Analytic Account'):['analytic_account_id',False],_('Currency'):['currency_id',False]}
        # check if there is Currency (currency_id) for move_line
        self.env.cr.execute('SELECT m.currency_id FROM account_move_line m WHERE m.move_id = %s' % move.id)
        for line in self.env.cr.dictfetchall():
            if line['currency_id']:
                columns[_('Currency')][1] = True
                break
        # check if there is Analytic Account (analytic_account_id) for move_line
        self.env.cr.execute('SELECT m.analytic_account_id FROM account_move_line m WHERE m.move_id = %s' % move.id)
        for line in self.env.cr.dictfetchall():
            if line['analytic_account_id']:
                columns[_('Analytic Account')][1] = True
                break
        # check if there is Partner(partner_id) for move_line
        self.env.cr.execute('SELECT m.partner_id FROM account_move_line m WHERE m.move_id = %s' % move.id)
        for line in self.env.cr.dictfetchall():
            if line['partner_id']:
                columns[_('Partner')][1] = True
                break
        # check if there is Amount Currency (amount_currency) for move_line
        self.env.cr.execute('SELECT m.amount_currency FROM account_move_line m WHERE m.move_id = %s' % move.id)
        for line in self.env.cr.dictfetchall():
            if line['amount_currency']:
                columns[_('Amount Currency')][1] = True
                break
        
        return columns
    
    def formatDigits(self, amount, digits):
        return formatLang(self.env, amount, digits=digits)
    
    
    @api.model
    def _get_report_values(self, docids, data=None):
        totals = {}
        for move_id in docids:
            move = self.env['account.move'].browse(move_id)
            totals[move_id] = {'debit': 0.0, 'credit': 0.0, 'total': 0.0}
            for line in move.line_ids:
                totals[move_id]['debit'] += line['debit']
                totals[move_id]['credit'] += line['credit']
                totals[move_id]['total'] += line['debit'] - line['credit']
                
                    
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': self.env['account.move'].browse(docids),
            'time': time,
            'Totals': totals,
            'formatLang': self.formatDigits,
            'getColumns': self.get_columns,
        }
        
