# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import Form


class BundleWizard(models.TransientModel):
    _name = 'bundle.wizard'
    _description = 'Bundle Wizard'

    product_id = fields.Many2one('product.product', 'Product', required=True, domain=[('is_bundle', '=', True),('bundle_ids', '!=', False)])
    bundle_id = fields.Many2one('bundle.history', 'Bundle Reference', domain=[('bundle_type', '=', 'assembly'), ('remaining_qty', '>', 0)])
    location_id = fields.Many2one('stock.location', 'Location', required=True, domain=[('usage', '=', 'internal')])
    quantity = fields.Integer('Quantity', required=True, default=1)
    options = fields.Selection([('assembly', 'Assembly'), ('disassembly', 'Disassembly')], string='Action', required=True, default='assembly')

    @api.constrains('quantity', 'bundle_id')
    def _constrains_bundle_id_quantity(self):
        for rec in self:
            if self.quantity <= 0 :
                raise ValidationError('The quantity should be more than zero.')
            if rec.bundle_id and rec.quantity > self.bundle_id.remaining_qty:
                raise ValidationError('The remaining quantity is less then the quantity that you want to disassembly, The remaining quantuty is %s.' % self.bundle_id.remaining_qty)

    @api.onchange('bundle_id', 'options')
    def onchange_bundle_id(self):
        self.product_id = False
        self.quantity = 0
        if self.bundle_id:
            self.product_id = self.bundle_id.bundle_inventory_id.product_id.id

    def action_confirm(self):
        return getattr(self, "action_confirm_" + self.options)()

    def action_confirm_assembly(self):
        bundle_location_id = self.env.user.company_id.bundle_location_id.id
        if not bundle_location_id:
            raise UserError("Please select 'Bundle Location' in configuration")
        sequance_name = self.env['ir.sequence'].next_by_code('bundle.history')
        qty_map = {}
        quant_obj = self.env['stock.quant']
        for line in self.product_id.bundle_ids:
            need_qty = self.quantity * line.quantity
            qty_map[line.product_id] = need_qty
            available_qty = quant_obj._get_available_quantity(line.product_id, self.location_id)
            if available_qty < need_qty:
                val = {'need_qty':need_qty,
                     'product_id':line.product_id.display_name,
                     'location_id':self.location_id.display_name,
                     'available_qty':available_qty,
                     'uom':line.product_id.uom_id.display_name
                     }
                msg = ("You plan to consume {need_qty} {uom} of {product_id}"
                 " but you only have {available_qty} {uom} available in {location_id}").format(**val)
                raise UserError(msg)

        inventory_id = Form(self.env['stock.inventory'], 'stock.view_inventory_form')
        inventory_id.name = sequance_name + ' (Component)'
        inventory_id.filter = 'partial'
        inventory_id.location_id = self.location_id
        inventory_id = inventory_id.save()
        inventory_id.action_start()

        with Form(inventory_id, 'stock.view_inventory_form') as inventory_id:
            for k, v in qty_map.items():
                with inventory_id.line_ids.new() as line:
                    line.product_id = k
                    line.product_qty -= v

        inventory_id = inventory_id.save()
        inventory_id.with_context(bundle_location_id=bundle_location_id).action_validate()

        cost = sum(inventory_id.mapped('move_ids').filtered(lambda move: move.state == 'done').mapped(lambda x: abs(x.value))) / self.quantity
        inventory_in_id = Form(self.env['stock.inventory'], 'stock.view_inventory_form')
        inventory_in_id.name = sequance_name + ' (Bundle)'
        inventory_in_id.filter = 'product'
        inventory_in_id.location_id = self.location_id
        inventory_in_id.product_id = self.product_id
        inventory_in_id = inventory_in_id.save()
        inventory_in_id.action_start()
        with Form(inventory_in_id, 'stock.view_inventory_form') as inventory_in_id:
            with inventory_in_id.line_ids.edit(0) as line:
                line.product_qty += self.quantity

        inventory_in_id = inventory_in_id.save()
        inventory_in_id.with_context(bundle_location_id=bundle_location_id,bundule_cost=cost).action_validate()

        history_id = self.env['bundle.history'].create({'name':sequance_name,
                                           'bundle_inventory_id':inventory_in_id.id,
                                           'comp_inventory_id':inventory_id.id,
                                           'bundle_type':'assembly',
                                           'remaining_qty':self.quantity,
                                           'quantity':self.quantity})
        
        action = self.env.ref('physical_bundles.bundle_history_action').read()[0]
        
        view_id =  self.env.ref('physical_bundles.bundle_history_form_view').id
        action.update({'view_type': 'form',
           'view_mode': 'form',
           'views': [(view_id, "form")],
           'res_id': history_id.id,
           'view_id': view_id})
        return action

    def action_confirm_disassembly(self):
        bundle_location_id = self.env.user.company_id.bundle_location_id.id
        if not bundle_location_id:
            raise UserError("Please select 'Bundle Location' in configuration")
        sequance_name = self.env['ir.sequence'].next_by_code('bundle.history')
        quant_obj = self.env['stock.quant']
        available_qty = quant_obj._get_available_quantity(self.product_id, self.location_id)
        if available_qty < self.quantity:
            val = {'need_qty':self.quantity,
                 'product_id':self.product_id.display_name,
                 'location_id':self.location_id.display_name,
                 'available_qty':available_qty,
                 'uom':self.product_id.uom_id.display_name
                 }
            msg = ("You plan to consume {need_qty} {uom} of {product_id}"
             " but you only have {available_qty} {uom} available in {location_id}").format(**val)
            raise UserError(msg)

        inventory_in_id = Form(self.env['stock.inventory'], 'stock.view_inventory_form')
        inventory_in_id.name = sequance_name + ' (Bundle)'
        inventory_in_id.filter = 'product'
        inventory_in_id.location_id = self.location_id
        inventory_in_id.product_id = self.product_id
        inventory_in_id = inventory_in_id.save()
        inventory_in_id.action_start()
        with Form(inventory_in_id, 'stock.view_inventory_form') as inventory_in_id:
            with inventory_in_id.line_ids.edit(0) as line:
                line.product_qty -= self.quantity

        inventory_in_id = inventory_in_id.save()
        inventory_in_id.with_context(bundle_location_id=bundle_location_id).action_validate()

        qty_map = {}
        for line in self.bundle_id.comp_inventory_id.move_ids:
            qty_map[line.product_id] = self.quantity * (line.product_qty / self.bundle_id.quantity)

        inventory_id = Form(self.env['stock.inventory'], 'stock.view_inventory_form')
        inventory_id.name = sequance_name + ' (Component)'
        inventory_id.filter = 'partial'
        inventory_id.location_id = self.location_id
        inventory_id = inventory_id.save()
        inventory_id.action_start()

        with Form(inventory_id, 'stock.view_inventory_form') as inventory_id:
            for k, v in qty_map.items():
                with inventory_id.line_ids.new() as line:
                    line.product_id = k
                    line.product_qty += v

        inventory_id = inventory_id.save()

        cost_map = {}
        for move in self.bundle_id.comp_inventory_id.move_ids:
            cost_map[move.product_id.id] = abs(move.price_unit)

        inventory_id.with_context(bundle_location_id=bundle_location_id,cost_map=cost_map).action_validate()

        self.bundle_id.remaining_qty -= self.quantity

        history_id = self.env['bundle.history'].create({'name':sequance_name,
                                           'bundle_inventory_id':inventory_in_id.id,
                                           'comp_inventory_id':inventory_id.id,
                                           'bundle_type':'disassembly',
                                           'remaining_qty':0,
                                           'quantity':0})
        
        
        action = self.env.ref('physical_bundles.bundle_history_action').read()[0]
        
        view_id =  self.env.ref('physical_bundles.bundle_history_form_view').id
        action.update({'view_type': 'form',
           'view_mode': 'form',
           'views': [(view_id, "form")],
           'res_id': history_id.id,
           'view_id': view_id})
        return action
