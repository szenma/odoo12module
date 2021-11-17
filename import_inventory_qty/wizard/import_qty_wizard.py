# -*- coding: utf-8 -*-
import base64
from odoo import models,api,fields,_
from odoo.exceptions import UserError
import tempfile
from xlrd import open_workbook
import csv



FILE_TYPE_DICT = {
    'csv': 'text/csv',
    'xls':'application/vnd.ms-excel',
    'xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
}


class ImportQtyWizard(models.TransientModel):
    _name = "import.qty.wizard"
    _description = "Import Qty Wizard Inventory"
    

    name = fields.Char('Name', required=True)
    location_id = fields.Many2one('stock.location','Location', required=True)
    data = fields.Binary('File', required=True )
    data_fname = fields.Char('Data Name')
    is_header = fields.Boolean(string='The first line is header?',default=True)
    

    def import_qty(self):
        file_type = FILE_TYPE_DICT.get(self.data_fname.split('.')[-1].lower(),False)
        if not file_type:
            raise UserError("Oops, the format of your file is not compatible. Kindly try importing formats of XLS, XLSX or CSV only")
        import_wizard = self.env['base_import.import'].create({
            'res_model': 'import.qty.wizard',
            'file': base64.b64decode(self.data),
            'file_name': self.data_fname,
             'file_type': file_type})
        
        lines = import_wizard._read_file({'quoting':'"',
                                        'separator':','})
            
        prod_obj = self.env['product.product']
        inventory_obj = self.env['stock.inventory']
        lot_obj = self.env['stock.production.lot']
        inventory_line = []
        
            
        note = ""
        error_msg = ''
        barcode_list = []
        
        inv_id = inventory_obj.create({'name': self.name, 'filter': 'partial', 'location_id': self.location_id.id})
        x=1
        if self.is_header:
            x=2
            next(lines)
        for line in lines:
            barcode = line[0].replace(' ','')
            if not barcode:
                raise UserError("The barcode must be not empty in line %d"%x)
            qty = float(line[1] or 0.0)
            if barcode in barcode_list:
                error_msg += barcode + '\n'
            else:
                barcode_list.append(barcode)
            prod_id= prod_obj.search([('barcode','=',barcode)],limit=1)
                
            if prod_id:
                val = {'location_id':self.location_id.id,
                                                'product_id':prod_id.id,
                                                'product_qty':qty,
                                                'product_uom':prod_id.uom_id.id,
                                                }
                if len(line) >2 :
                    val['cost'] = float(line[2] or 0.0)
                    if len(line) >3 :
                        lot_id =  lot_obj.search([('name','=',line[3]),('product_id','=',prod_id.id)])
                        if lot_id:
                            val['prod_lot_id'] = lot_id.id
                inventory_line.append((0,0,val))
                          
            else:
                note += (barcode + '     ,    '+str(qty) + '\n')
            x+=1
    #if error_msg:
        #raise UserError(_('The Following Barcode/s are Duplicated : \n \n'+ error_msg))
        if note:
            n_note = "The Following Barcode/s not exist : \n \n(Barcode      ,     Qty) \n" + note
            inv_id.write({"note" : n_note})
        inv_id.write({'line_ids':inventory_line})
        inv_id.action_start()
        
        action = self.env.ref('stock.action_inventory_form').read()[0]
        action['res_id'] = inv_id.id
        return action

