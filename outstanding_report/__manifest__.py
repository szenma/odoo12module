# -*- coding: utf-8 -*-
{
    'name': "Sw - OutStanding Report",
    'summary': """
    Customers Outstanding Balance Report
     """,
    'description': """
    This module adds a new report "Outstanding Balance" under Accounting -> Reporting -> Partner Reports.
     This report will allow the user to select the period of reporting and the customer. the report can be generated in PDF or Excel format.
    """,
    'author': "Smart Way Business Solutions",
    'website': "https://www.smartway.co",
    'category': 'Accounting',
    'version': '12.0.1.1',
    'depends': ['base','account'],
    'data': [
        'data/report_paperformat_data.xml',
        'template/outstanding_layout.xml',
        'template/outstanding_report_template.xml',
        'views/views.xml',
        'template/outstanding_report_template.xml',
        
    ],
}