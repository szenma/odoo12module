# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Bank(models.Model):
    _inherit = "res.bank"
    
    swift_code = fields.Text("SWIFT Code")