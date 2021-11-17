# -*- coding: utf-8 -*-
import base64
from odoo import http
from odoo.http import request,content_disposition

class Controller(http.Controller):


    @http.route('/web/binary/download_xls_document_outstanding_report', type='http', auth="user")
    def download_document(self,model ,id, **kwargs):
        outstanding_report = request.env[model].browse(int(id))
        file = base64.b64decode(outstanding_report.file)
        file_name = outstanding_report.file_name
        
        return request.make_response(file,
                                      [('Content-Type', 'text/plain'),
                                         ('Content-Disposition' ,content_disposition(file_name ))])