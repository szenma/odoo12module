# -*- coding: utf-8 -*-
{
    'name': "SW - Payment Report Enhancement",
    'summary': """
    This module adds new fields in the Payment report.
        """,
    'description': """
    This enhancement prints new fields in the "Payment Report" located in  'account.payment' model.
    """,
    'author': "Smart Way Business Solutions",
    'website': "https://www.smartway.co",
    'category': 'Accounting',
    'version': '12.0.1.3',
    'depends': ['base','account','web'],
    'data': [
        'views/views.xml',
        'views/payment_template.xml',
        'views/assets.xml'
    ],
}