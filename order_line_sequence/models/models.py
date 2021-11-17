# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    number = fields.Integer(compute='_compute_get_number',string="#", store=True)

    @api.depends('sequence', 'order_id')
    def _compute_get_number(self):
        for order in self.mapped('order_id'):
            number = 1
            for line in order.order_line.filtered(lambda x:x.display_type != "line_section" ):
                line.number = number
                number += 1
    
    
    
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    number = fields.Integer(compute='_compute_number',string="#", store=True)
    
    @api.depends('sequence', 'order_id')
    def _compute_number(self):
        for order in self.mapped('order_id'):
            number = 1
            for line in order.order_line:
                line.number = number
                number += 1
    
class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    number = fields.Integer(compute='_compute_number',string="#", store=True)
    
    @api.depends('sequence', 'invoice_id')
    def _compute_number(self):
        for invoice in self.mapped('invoice_id'):
            number = 1
            for line in invoice.invoice_line_ids.filtered(lambda x:x.display_type != "line_section" ):
                line.number = number
                number += 1
                
    
class StockMove(models.Model):
    _inherit = 'stock.move'
    
    number = fields.Integer(compute='_compute_number',string="#", store=True)
    
    
    @api.depends('sequence', 'picking_id')
    def _compute_number(self):
        for order in self.mapped('picking_id'):
            number = 1
            for line in order.move_lines:
                line.number = number
                number += 1

                
class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    number = fields.Integer(compute='_compute_number',string="#", store=True)
    
    @api.depends('picking_id')
    def _compute_number(self):
        for order in self.mapped('picking_id'):
            number = 1
            for line in order.move_line_ids:
                line.number = number
                number += 1
    
    
    
    