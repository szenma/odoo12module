# -*- coding: utf-8 -*-

from . import models

from odoo import api, SUPERUSER_ID

def load_translations(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('l10n_qa.l10nsa_chart_template').process_coa_translations()
    
def _update_translations(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    mods = env['ir.module.module'].search([('state', '=', 'installed')])
    mods.with_context(overwrite=True)._update_translations('ar_SY')