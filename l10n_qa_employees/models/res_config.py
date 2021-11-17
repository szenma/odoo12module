# -*- coding: utf-8 -*-

from odoo import models, fields, api



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    
    employee_ids = fields.Many2many("hr.employee", string='Documents Responsible(s)', related='company_id.employee_ids', readonly=False)
    
class ResCompany(models.Model):
    _inherit = 'res.company'
    
    employee_ids = fields.Many2many("hr.employee", string='Documents Responsible(s)')