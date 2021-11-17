# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class Contract(models.Model):
    _inherit = "hr.contract"
    
    
    housing_allowance = fields.Monetary("Housing Allowance")
    transportation_allowance = fields.Monetary("Transportation Allowance")
    communication_allowance = fields.Monetary("Communication Allowance")
    food_allowance = fields.Monetary("Food Allowance")
    social_allowance = fields.Monetary("Social Allowance")
    other_allowance = fields.Monetary("Other Allowance")


