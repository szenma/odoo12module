# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging
import ast
_logger = logging.getLogger('SoL-Qty')


class ResConfigSettings(models.TransientModel):
    
    _inherit = 'res.config.settings'
    
    #sol_qty_other_company_ids =  fields.One2many('sale.qty.other.company',related="company_id.sol_qty_other_company_ids")
    sol_qty_other_company_ids = fields.Many2many("sale.qty.other.company",string='Company SoL Qty. Settings')
    sol_qty = fields.Selection([('qty_on_hand', 'Quantity on Hand'),
                                ('qty_forecasted', 'Forecasted Quantity'), ('qty_available', 'Available Quantity')], default='qty_on_hand', 
                               string="SOL Available Qty", related="company_id.sol_qty",
                               help="""Quantity on Hand: Is the quantity of the selected product currently in the warehouse.\n
                                        Forecasted Quantity: Is the forecasted quantity or "quantity to be" of the selected product.\n
                                        Available Quantity: Is the quantity on hand minus the reserved quantity of the selected product.""")
           
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
#         rec_ids = self.env['ir.config_parameter'].sudo().get_param('sol_qty_available.sol_qty_other_company_ids')
        rec_ids = self.env['sale.qty.other.company'].sudo().search([]).ids
        _logger.info(rec_ids)
#         if not rec_ids:
        res.update(sol_qty_other_company_ids=[(6, 0, rec_ids)])
#         else:
#             res.update(sol_qty_other_company_ids=[(6, 0, ast.literal_eval(rec_ids))])
        return res
    
#     @api.multi
#     def set_values(self):
#         super(ResConfigSettings, self).set_values()
#         set_param = self.env['ir.config_parameter'].sudo().set_param
#         set_param('sol_qty_available.sol_qty_other_company_ids', self.sol_qty_other_company_ids.ids)