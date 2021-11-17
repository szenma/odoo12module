# -*- coding: utf-8 -*-
{
    'name': "SW - Invoice Rebates",

    'summary': """This module manages the rebates for sales & credit notes
        """,

    'description': """
    
* This module adds the following fields at contact form view:
    - Is Rebate Customer
    - Rebate Percentage
    - Auto Reconcile
    
* This Module adds a new field at the Journal form view "Rebate Journal"

* The logic behind this module is quite simple:

    - Basically, once an invoice is validated and the customer is rebate customer a new journal entry will be generated debiting the rebates expense account [The account should be set as default in the rebate journal] and crediting account receivable with the value of the rebate (subtotal invoice amount*rebate percentage).
    
    - If the customer is marked as rebate auto reconcile then the system will reconcile [Add] the rebate transaction to the invoice itself and the invoice will show the amount, rebate amount, and the balance (Due Amount).
    
    - While creating a credit note invoice the same workflow will be executed BUT altering debit to credit, and vice versa of the rebate journal entry    
            
                 """,

    'author': "Smart Way Business Solutions",
    'website': "https://www.smartway.co/",

    'category': 'Accounting',
    'version': '12.0.1.0',

    'depends': ['base','account','sales_team'],

    'data': ['view/views.xml',
             'security/ir.model.access.csv'
              ],
}
