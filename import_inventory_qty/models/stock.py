# -*- coding: utf-8 -*-
from odoo import models, fields,api

class StockInventory(models.Model):
    _inherit = 'stock.inventory'
  
    note = fields.Text("Note")
    
    

class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'
  
    cost = fields.Float("Cost")
    
    def _get_move_values(self, qty, location_id, location_dest_id, out):
        res = super(StockInventoryLine, self)._get_move_values( qty, location_id, location_dest_id, out)
        if self.cost > 0.0:
            res['price_unit'] = self.cost
        return res
  
