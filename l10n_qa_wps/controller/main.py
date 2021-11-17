# -*- coding: utf-8 -*-
import base64
from odoo import http
from odoo.http import request,content_disposition
import json

from odoo.addons.web.controllers.main import ReportController

class ReportControllerExt(ReportController):
    
    @http.route(['/report/download'], type='http', auth="user")
    def report_download(self, data, token):
        requestcontent = json.loads(data)
        url = requestcontent[0]
        if 'wps.report' in url:
            id = int(url.split('/')[3].split('-')[1])
            wizard_id = request.env['wps.report'].browse(id)
            file = base64.b64decode(wizard_id.file)
#             wizard_id.eport_data = False
            file_name = wizard_id.file_name
            return request.make_response(file,
                                          [('Content-Type', 'text/plain'),
                                             ('Content-Disposition' ,content_disposition(file_name))])
        return super(ReportControllerExt, self).report_download(data, token)

