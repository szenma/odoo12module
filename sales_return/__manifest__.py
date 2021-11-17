# -*- coding: utf-8 -*-
{
    'name': "SW - Sales Return - Credit Note",
    'summary': """
    This module automate the credit note invoice foe the returns.
        """,
    'description': """
    This module adds a new checkbox on the picking type operation to flag the returns operation type and to automatically create a credit note per return.
    """,
    'author': "Smart Way Business Solutions",
    'website': "https://www.smartway.co",
    'category': 'Sales',
    'version': '12.0.1.0',
    'depends': ['base','stock','sale'],
    'data': [
        'views/view.xml'
    ],
}