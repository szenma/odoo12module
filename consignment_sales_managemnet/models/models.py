# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    warehouse_id = fields.Many2one('stock.warehouse',string='Warehouse')
    
    
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    

    @api.onchange('partner_id')
    def set_so_warehouse(self):
        for rec in self:
            if rec.partner_id and rec.partner_id.warehouse_id:
                rec.warehouse_id = rec.partner_id.warehouse_id
            else:
                rec.warehouse_id = rec._default_warehouse_id()