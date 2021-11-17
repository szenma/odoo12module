# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    
    _inherit = "sale.order.line"

    sol_display = fields.Text(string='QTY Available',readonly=True ,copy=False,help="Displays the qty of the product according to the option selected in settings")
     
    
    @api.model
    @api.returns('self',
        upgrade=lambda self, value, args, offset=0, limit=None, order=None, count=False: value if count else self.browse(value),
        downgrade=lambda self, value, args, offset=0, limit=None, order=None, count=False: value if count else value.ids)
    def search(self, args, offset=0, limit=None, order=None, count=False):
        res = super(SaleOrderLine, self).search(args, offset, limit, order, count)
        if not count:
            sol_ids = res.filtered(lambda x :x.state in ['draft','sent'])
            if sol_ids:
                sol_ids.get_product_quantity()
        return res
    
     
     
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        if 'sol_display' not in vals:
            res.get_product_quantity()
        return res
    
    
    @api.multi
    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        if 'sol_display' not in vals and 'product_id' in vals:
            self.get_product_quantity()
        return res
    
    @api.onchange('product_id')
    def get_product_quantity(self):
        for record in self:
            record.sol_display = record._get_product_quantity(record.product_id.id) if record.product_id else ''
            
                
                
    def _get_product_quantity(self,id):
        text = ''
        move = self.env["stock.move"]
        product_id = self.env['product.product'].browse(id)
        uom_dp = str(self.env['decimal.precision'].precision_get('Product Unit of Measure'))
        quant = self.env['stock.quant'].sudo()
        for rec in self.env.user.company_id.sol_qty_other_company_ids.filtered(lambda x: x.show):
            if self.env.user.company_id.sol_qty == 'qty_on_hand' : 
                if rec.warehouse_ids:
                    for wh in rec.warehouse_ids:
                        qty = "{:.{}f}".format( sum(quant._gather(product_id,wh.view_location_id).mapped('quantity')), uom_dp ) 
                        text += rec.short_code +' - '+ wh.code + ' ('+str(qty)+')' + '\n'
                else :
                    qty_onhand = product_id.with_context(force_company = rec.company_id.id).sudo().qty_available
                    qty = "{:.{}f}".format( qty_onhand, uom_dp )
                    text += rec.short_code +  ' ('+str(qty)+')' + '\n'
            
            elif self.env.user.company_id.sol_qty == 'qty_forecasted':
                if rec.warehouse_ids:
                     for wh in rec.warehouse_ids:
                        location_domain = product_id.with_context(warehouse=wh.id)._get_domain_locations()
                        onhand_qty = sum(quant._gather(product_id,wh.view_location_id).mapped('quantity'))
                        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = product_id._get_domain_locations()
                        onhand_qty = sum(quant._gather(product_id,wh.view_location_id).mapped('quantity'))
                        not_yet_in_qty = sum(move.search([('product_id','=',product_id.id),('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))]+domain_move_in_loc).mapped('product_uom_qty'))
                        not_yet_out_qty = sum(move.search([('product_id','=',product_id.id),('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))]+domain_move_out_loc).mapped('product_uom_qty'))
                        qty = "{:.{}f}".format( onhand_qty+not_yet_in_qty-not_yet_out_qty, uom_dp ) 
                        text += rec.short_code +' - '+ wh.code + ' ('+str(qty)+')' + '\n'
                else:
                    qty_forecasted = product_id.with_context(force_company = rec.company_id.id).sudo().virtual_available
                    qty = "{:.{}f}".format( qty_forecasted, uom_dp )
                    text += rec.short_code + ' ('+str(qty)+')' + '\n'
                
            elif self.env.user.company_id.sol_qty == 'qty_available' :
               
                if rec.warehouse_ids:
                    for wh in rec.warehouse_ids:
                        qty = "{:.{}f}".format( quant._get_available_quantity(product_id,wh.view_location_id), uom_dp )
                        text += rec.short_code +' - '+ wh.code + ' ('+str(qty)+')' + '\n'
                else :
                    stock_quant = self.env['stock.quant'].sudo().search([('company_id', '=',rec.company_id.id),('product_id', '=', product_id.id)])
                    reserved_qty = 0.0
                    actual_qty = 0.0
                    for quant in stock_quant:
                        reserved_qty += quant.with_context(force_company = rec.company_id.id).sudo().reserved_quantity
                        actual_qty += quant.with_context(force_company = rec.company_id.id).sudo().quantity
                    available_qty = actual_qty - reserved_qty
                    qty = "{:.{}f}".format( available_qty, uom_dp )
                    text += rec.short_code + ' ('+str(qty)+')' + '\n'
        return text and text[:-1] or ''
