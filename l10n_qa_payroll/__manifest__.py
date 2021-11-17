# -*- coding: utf-8 -*-
{
    'name': "SW - Qatar Payroll Localization",

    'summary': """
     This module customizes In-Place the Employees App by adding new fields and functionality to meet the Qatari market needs.
    """,
    'description': """
   This module customizes In-Place the Employees App by adding new fields and functionality to meet the Qatari market needs.
    """,
    'author': "Smart Way Business Solutions",
    'website': "https://www.smartway.co",
    'category': 'Human Resources',
    'version': '12.0.1.0',
    'depends': ['base','hr','hr_contract','base_payroll_qa'],
    'data': [
        "views/contract_view.xml",
        "data/salary_rules.xml"
        
    ],
}
