# -*- coding: utf-8 -*-
{
    'name': "SW - Consignment Sales Managemnet",
    'summary': """
    This module makes easy of management for the consignment sales.
        """,
    'description': """
    This module adds a new field at the contact page "Warehouse" so the SO to be delivered from this warehouse to manage the consignment quantity.
    """,
    'author': "Smart Way Business Solutions",
    'website': "https://www.smartway.co",
    'category': 'Sales',
    'version': '12.0.1.0',
    'depends': ['base','sale','stock'],
    'data': [
        'views/views.xml'
    ],
}
