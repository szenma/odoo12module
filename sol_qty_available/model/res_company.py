# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError

class QtyOtheCompany(models.Model):
    _name = 'sale.qty.other.company'
    _description = "Company SOL Quantity Settings"
    
    _rec_name = 'short_code'
    #company_inv_id = fields.Many2one('res.company',string="Company", default=lambda self: self.env.user and self.env.user.company_id.id)
    company_id = fields.Many2one('res.company',string="Company",required=True)
    short_code = fields.Char('Short Code', size=4,required=True)
    show = fields.Boolean('Show in SOL',default=True,help="If enabled, uses this company's quantity in purchase order")
    warehouse_ids = fields.Many2many("stock.warehouse", string="Warehouse")
    sol_qty = fields.Selection([('qty_on_hand', 'Quantity on Hand'),
                                ('qty_forecasted', 'Forecasted Quantity'), 
                                ('qty_available', 'Available Quantity')], 
                                string="POL Available Qty", default='qty_on_hand', 
                                help="""Quantity on Hand: Is the quantity of the selected product currently in the warehouse.\n
                                        Forecasted Quantity: Is the forecasted quantity or "quantity to be" of the selected product.\n
                                        Available Quantity: Is the quantity on hand minus the reserved quantity of the selected product.""")
    
    @api.constrains('company_id')
    def company_check(self):
        record_ids = self.search([('company_id','=',self.company_id.id)])
        if len(record_ids)>1:
            raise UserError("You can't choose the same company twice in SOL quantity" )
        


class ResCompany(models.Model):
    _inherit = 'res.company'

    sol_qty = fields.Selection([('qty_on_hand', 'Quantity on Hand'),
                                ('qty_forecasted', 'Forecasted Quantity'), ('qty_available', 'Available Quantity')], default='qty_on_hand', 
                               string="POL Available Qty", compute='_get_sol_qty', store=True,
                               help="""Quantity on Hand: Is the quantity of the selected product currently in the warehouse.\n
                                        Forecasted Quantity: Is the forecasted quantity or "quantity to be" of the selected product.\n
                                        Available Quantity: Is the quantity on hand minus the reserved quantity of the selected product.""")
    
    sol_qty_other_company_ids =  fields.One2many('sale.qty.other.company','company_id')
    
    
    @api.depends('sol_qty_other_company_ids.sol_qty')
    def _get_sol_qty(self):
        for rec in self:
            sol_qty='qty_on_hand'
            if rec.sol_qty_other_company_ids:
                sol_qty = rec.sol_qty_other_company_ids.sol_qty
            rec.sol_qty = sol_qty
    
    