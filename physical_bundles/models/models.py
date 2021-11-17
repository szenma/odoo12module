# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BundleHistory(models.Model):
    _name = 'bundle.history'
    _description = 'Bundle History'

    name = fields.Char('Number', required=True, readonly=True)
    bundle_inventory_id = fields.Many2one('stock.inventory', 'Bundle Adjustment', required=True, readonly=True)
    comp_inventory_id = fields.Many2one('stock.inventory', 'Components Adjustment', required=True, readonly=True)
    bundle_type = fields.Selection([('assembly', 'Assembly'), ('disassembly', 'Disassembly')], string='Action', required=True, readonly=True)
    remaining_qty = fields.Integer('Remaining Bundle Quantity', required=True, readonly=True)
    quantity = fields.Integer('Quantity', required=True, readonly=True)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bundle_location_id = fields.Many2one('stock.location','Bundle Location',related="company_id.bundle_location_id",readonly=False)


class ResCompany(models.Model):
    _inherit = 'res.company'

    bundle_location_id = fields.Many2one('stock.location','Bundle Location')


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_price_unit(self):
        bundule_cost = self._context.get('bundule_cost')
        if bundule_cost is not None:
            return bundule_cost
        cost_map = self._context.get('cost_map')
        if cost_map is not None:
            return cost_map.get(self.product_id.id, 0.0)
        return super(StockMove, self)._get_price_unit()


class ProductBundleLine(models.Model):
    _name = 'product.bundle.line'
    _description = 'Product Bundle Line'

    product_id = fields.Many2one('product.product', 'Product', ondelete='restrict', required=True)
    quantity = fields.Integer('Quantity', required=True)
    note = fields.Text('Notes')
    product_inv_id = fields.Many2one('product.product', 'Product', ondelete='cascade')
    product_tmpl_id = fields.Many2one('product.template', 'Product', ondelete='cascade')


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_bundle = fields.Boolean('Is Bundle', related='product_variant_ids.is_bundle', readonly=False)
    bundle_ids = fields.One2many('product.bundle.line', 'product_tmpl_id', string='Bundle')


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_bundle = fields.Boolean('Is Bundle')
    bundle_ids = fields.One2many('product.bundle.line', 'product_inv_id', string='Bundle')

class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"
    
    def _get_move_values(self, qty, location_id, location_dest_id, out):
        bundle_location_id = self.env.context.get('bundle_location_id')
        if bundle_location_id:
            diff = self.theoretical_qty - self.product_qty
            if diff < 0:  # found more than expected
                location_id = bundle_location_id
            else:
                location_dest_id = bundle_location_id
        return super(InventoryLine, self)._get_move_values( qty, location_id, location_dest_id, out)

