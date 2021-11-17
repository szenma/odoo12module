# -*- encoding: utf-8 -*-
{
    'name' : 'SW - SOL Available Quantity',
    'author' : 'Smart Way Business Solutions',
    'website' : 'https://www.smartway.co',
    'license':  "Other proprietary",
    'category' : 'Sales',
    'version' : '12.0.1.3',
    'summary':"Allows you to see the on hand, forecasted and available quantities for your product across your companies.",
     'description': """ Adds a new table on the settings/congfigurations page for sales that allows you to select what type of quantity you would like to show on the SOL and for which companies. 
     The SOL field is computed, and configured to re-compute if status is not done(sales order)
    """,

    'depends' : ['base', 'sale', 'stock','sale_stock', 'sale_management'],
    'data': [
             
             "view/sale_order.xml",
             "view/res_config_settings_views.xml",
             "security/ir.model.access.csv"
             ],
    #'images':  ["static/description/image.png"],
    'price'    :  25,
    'currency' :  'EUR',
    'installable': True,
    'auto_install': False,
    'application':False,
    
}