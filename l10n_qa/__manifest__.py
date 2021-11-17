# -*- coding: utf-8 -*-
{
    'name': 'SW - Qatar Accounting',
    'version': '12.0.1.0',
    'category': 'Localization',
    'description': """
This is the base module to manage the accounting chart for Qatar in Odoo.
==============================================================================
    """,
    'website': 'https://www.smartway.co',
    'author': 'Smart Way Business Solutions',
    'depends': ['account','l10n_multilang',],
    'data': [
        'data/account.group.csv',
        'data/account_chart_template_data.xml',
        'data/account.account.template.csv',
        'data/account_coa_data.xml',
        'data/account_data.xml',
        'data/account_tax_template_data.xml',
        'data/fiscal_templates_data.xml',
        'data/res.lang.csv',
        'data/account_chart_template.xml',
        'data/res_currency.xml',
        'data/decimal.precision.csv'
    ],
    
    'post_init_hook': '_update_translations',
}
