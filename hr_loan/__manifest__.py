# -*- coding: utf-8 -*-
{
    'name': 'SW - Employee Loans Management',
    'version': '12.0.1.1',
    'license':  "Other proprietary",
    'category': 'Human Resources',
    'website' : 'https://www.smartway.co',
    'author' : 'Smart Way Business Solutions',
    'summary': """One significant module to manage all your employees loans""",
    'depends': ['web','hr','hr_payroll','hr_contract','hr_payroll_account','account','hr_payroll_enhancement'],
    'data': ['wizard/reciept_voucher_view.xml',
             'views/loan.xml',
             'security/ir.model.access.csv',
             'security/loan_rule.xml',
             'views/loan_sequence.xml',
             'views/res_config_settings_views.xml',
             'data/cron_job_move_res_partner.xml'],
    'images':  ["static/description/image.png"],
    'price' : 150,
    'currency' :  'EUR',
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
