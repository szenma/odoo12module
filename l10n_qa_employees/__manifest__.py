# -*- coding: utf-8 -*-
{
    'name': "SW - Qatar Employee",

    'summary': """
     This module customizes In-Place the Employees App by adding new fields and functionality to meet the Qatari market needs.
    """,
    'description': """
   This module customizes In-Place the Employees App by adding new fields and functionality to meet the Qatari market needs.
    """,
    'author': "Smart Way Business Solutions",
    'website': "https://www.smartway.co",
    'category': 'SKY',
    'version': '12.0.1.0',
    'depends': ['base','hr'],
    'data': [
        "views/hr_employee_views.xml",
        "data/schedule.xml",
        "views/res_config.xml"
    ],
}
