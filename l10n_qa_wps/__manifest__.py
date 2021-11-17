# -*- encoding: utf-8 -*-
{
    "name" : "SIF - WPS Report",
    "version" : "12.0.1.2",
    'author' : 'Smart Way Business Solutions',
    'website' : 'https://www.smartway.co',
    "category" : "Human Resources",
    'summary': """Generate and Export valid WPS reports.""",
    "description": """
        This module adds new functionality to the payroll app enables the user to generate and export valid WPS reports.
                        """,
    "depends" : ["base","hr","hr_payroll","base_payroll_qa"],
    "data" : [
        "views/views.xml",
        "wizard/wps_wizard_view.xml"
                ],
}
