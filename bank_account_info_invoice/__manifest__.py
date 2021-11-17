# -*- coding: utf-8 -*-
{
    'name': "SW - Bank Account Info Invoice",
    'summary': """
        This module adds the bank account details to the invoice.""",
    'description': """
        This module adds a new field at the bank page 'SWIFT Code'
         and adds the bank details to the invoice by selecting the bank on the invoice.""",
    'author': "Smart Way Business Solutions",
    'website': "https://www.smartway-jo.com",
    'category': 'Accounting',
    'version': '12.0.1.0',
    'depends': ['base','account'],
    'data': [
        'views/bank_view.xml',
        'template/account_invoice_template.xml'
    ],
}