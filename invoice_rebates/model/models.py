# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tests.common import Form
from odoo.exceptions import UserError

class RebatePercentage(models.Model):
    _name = 'rebate.percentage'
    _description = 'Rebate Percentage'
    
    partenr_id = fields.Many2one('res.partner','Customer',ondelete='cascade')
    category_id = fields.Many2one('product.category','Category',ondelete='cascade',required=True)
    rebate_percentage = fields.Float('Percentage',required=True)
    
    
    _sql_constraints = [('partenr_id_category_id_unique', 'unique(partenr_id,category_id)', "The Category already exist.")]
    
    @api.constrains('rebate_percentage')
    def _constrains_rebate_percentage(self):
        for rec in self.filtered(lambda x:x.rebate_percentage > 100 or x.rebate_percentage < 0 ):
            raise UserError("The percentage must be between 0 and 100.")
                       

class ResPar(models.Model):
    _inherit = "res.partner"
    
    is_rebate_customer = fields.Boolean('Is Rebate Customer')
    follow_parent_company_rebate = fields.Boolean('Follow Parent Company Rebate',default=True)
    rebate_percentage_ids = fields.One2many('rebate.percentage','partenr_id',string='Rebate Percentage')
    auto_reconcile = fields.Boolean('Auto Reconcile')
    
    @api.onchange('customer','is_rebate_customer')
    def onchange_rebate(self):
        for rec in self:
            if not rec.customer or not rec.is_rebate_customer:
                rec.is_rebate_customer = False
                rec.rebate_percentage = 0.0
                rec.auto_reconcile = False

class AJ(models.Model):
    _inherit = "account.journal"
    
    rebate_journal = fields.Boolean('Rebate Journal')
    
    
class AI(models.Model):
    _inherit = 'account.invoice'
    
    rebate_payment_id = fields.Many2one('account.payment','Payment', copy=False)

        
    @api.multi
    def action_invoice_open(self):
        res = super(AI, self).action_invoice_open()
        self.with_context(invoice_date=self.date_invoice).rebates_create_payments()
        return res
    
    
    @api.multi
    def action_cancel(self):
        res =super(AI, self).action_cancel()
        payment_ids = self.mapped('rebate_payment_id')
        payment_ids.cancel() if payment_ids else ':p'
        return res
        
        
    @api.multi
    def rebates_create_payments(self):
        journal_id = self.env['account.journal'].search([('rebate_journal','=',True)],limit=1)
        payment_obj = self.env['account.payment'].with_context({'default_partner_type': 'customer'})
        if journal_id:
            invoice_ids = self.filtered(lambda x:x.amount_total > 0 and x.type in ['out_invoice','out_refund'] and (x.partner_id.is_rebate_customer and x.partner_id.rebate_percentage_ids or x.partner_id.follow_parent_company_rebate and x.partner_id.parent_id.is_rebate_customer and x.partner_id.parent_id.rebate_percentage_ids ))
            for inv in invoice_ids:
                payment_type =  inv.type == 'out_invoice' and 'inbound' or  'outbound'
                categ_map = {}
                rebate_percentage_ids = inv.partner_id.is_rebate_customer and inv.partner_id.rebate_percentage_ids or inv.partner_id.parent_id.rebate_percentage_ids
                for rp_line in rebate_percentage_ids:
                    categ_map[rp_line.category_id.id] = rp_line.rebate_percentage
                amount = 0.0
                for ail in inv.invoice_line_ids.filtered(lambda x:x.price_total>0):
                    id = False
                    categ_id = ail.product_id.categ_id
                    while True:
                        if categ_map.get(categ_id.id):
                            id = categ_id.id
                            break
                        categ_id = categ_id.parent_id
                        if not categ_id:break
                    if id:
                        amount += ail.price_total * (categ_map.get(id) / 100)
                amount = inv.currency_id.round(amount)
                if not inv.currency_id.is_zero(amount):
                    if  inv.rebate_payment_id:
                        if inv.rebate_payment_id.state not in ['cancelled']:
                            inv.rebate_payment_id.cancel()
                        inv.rebate_payment_id.action_draft()
                        
                    with Form(inv.rebate_payment_id or payment_obj,'account.view_account_payment_form') as payment_id:
                        payment_id.payment_type = payment_type
                        payment_id.currency_id = inv.currency_id
                        payment_id.partner_id = inv.partner_id
                        payment_id.journal_id = journal_id
                        payment_id.communication = inv.number
                        payment_id.partner_type = 'customer'
                        payment_id.amount = amount
                    payment_id = payment_id.save()
                    payment_id.invoice_ids = False
                    inv.rebate_payment_id = payment_id.id
                    inv.rebate_payment_id.post()
                    auto_reconcile = inv.partner_id.is_rebate_customer and inv.partner_id.auto_reconcile or not inv.partner_id.is_rebate_customer and inv.partner_id.parent_id.auto_reconcile
                    if auto_reconcile:
                        line = inv.rebate_payment_id.move_line_ids.filtered(lambda x:x.account_id.id ==inv.account_id.id)
                        if line:
                            inv.assign_outstanding_credit(line[0].id)
                    
                
                
   
