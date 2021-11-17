# -*- encoding: utf-8 -*-
{
    "name" : "SW - Journal Entry Reports",
    "version" : "12.0.1.0",
    'author' : 'Smart Way Business Solutions',
    'website' : 'https://www.smartway.co',
    "category" : "Accounting",
    "description": """
    - Journal Entry Report.
    - Adds Chatter to journal entries.
                        """,
    "depends" : ["base",'account'],
    "data" : [
                    "extra_account_reports.xml",
                    'views/journal_entries.xml',
                    'views/account_move.xml'
            ],
    "installable": True
}