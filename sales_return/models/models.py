# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tests.common import Form

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'
    
    to_invoice = fields.Boolean('To Invoice')
    
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    to_invoice = fields.Boolean('To Invoice',related="picking_type_id.to_invoice")
    
    
    def generate_invoice(self):
        invoice_obj = self.env['account.invoice'].with_context({'default_type': 'out_refund', 'type': 'out_refund', 'journal_type': 'sale'})
        for rec in self.filtered(lambda x:x.to_invoice == True and not( x.sale_id or (hasattr(x,'purchase_id') and x.purchase_id))):
            lines = rec.move_ids_without_package
            if lines:
                with Form(invoice_obj, view='account.invoice_form') as account_invoice:
                    account_invoice.partner_id = rec.partner_id
                    account_invoice.user_id = self.env.user
                    account_invoice.type = 'out_refund'
                    account_invoice.user_id = rec.partner_id.user_id if rec.partner_id.user_id else  self.env.user
                    account_invoice.team_id = rec.partner_id.team_id if rec.partner_id.team_id else invoice_obj._get_default_team()
                    for line in lines:
                         with account_invoice.invoice_line_ids.new() as invoice_line:
                             pricelist_id = rec.partner_id.property_product_pricelist
                             price = pricelist_id.get_product_price(line.product_id, 1, rec.partner_id) 
                             invoice_line.product_id = line.product_id
                             invoice_line.quantity = line.quantity_done
                             invoice_line.price_unit = price
                    invoice =  account_invoice.save()
                    invoice.action_invoice_open()
    
    def action_done(self):
        res = super(StockPicking, self).action_done()
        self.generate_invoice()
        return res
                     
                     
            