# -*- coding: utf-8 -*-

{
    'name': 'SW - Import Qty to Inventory',
    'version': '2.0',
    'category': 'Warehouse',
    'summary':"Create inventory adjustments from excel sheet",
    'description': """
    """,
    'author': 'Smart Way Business Solutions',
    'website': 'https://www.smartway.co',
    'depends': ['base', 'stock', 'product'],
    'data': [
            'views/stock.xml',
            'wizard/import_qty_wizard_view.xml',
            
    ],
}
