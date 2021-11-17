# -*- coding: utf-8 -*-
{
    'name': "SW - Order Line Sequence",
    'summary': """
        This module adds a new column [sequence number] at SO, DO, INV, 
    and PO """,
    'description': """
         This module adds a new column [sequence number] at SO, DO, INV, 
    and PO
    """,
    'author': "Smart Way Business Solutions",
    'website': "https://www.smartway.co",
    'category': 'Extra Tools',
    'version': '12.0.1.2',
    'depends': ['base','sale','purchase','stock','account'],
    'data': [
        'views/seq_column.xml',
        'template/sale_order_template.xml',
        'template/purchase_rder_template.xml',
        'template/invoice_template.xml',
        'template/picking_operation.xml'
    ],
}