# -*- coding: utf-8 -*-
{
    'name': 'SW - Physical Bundles',
    'version': '12.0.1.0',
    'category': 'Accounting',
    'summary': """This module allows to manage the assembly and disassembly of bundles products""",
    'description':"""This module allows to manage the assembly and disassembly of bundles products""",
    'author' : 'Smart Way Business Solutions',
    'website' : 'https://www.smartway.co',
    'depends': ['base','product','stock_account','purchase_stock'],
    'data': [
             'views/views.xml',
             'security/ir.model.access.csv',
             'wizard/bundle_wizard_view.xml',
             'data/data.xml'
             ],
}
