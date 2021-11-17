# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    
    
    passport_expiry_date = fields.Date("Passport Expiry Date")
    passport_last_notification_date = fields.Date("Passport Last Notification Date")
    qid = fields.Char("QID")
    driving_license_number = fields.Char("Driving License Number")
    qid_expiry_date = fields.Date("QID Expiry Date")
    qid_last_notification_date = fields.Date("QID Last Notification Date")
    driving_license_issuing_date = fields.Date("Driving License Issuing Date")
    driving_license_expiry_date = fields.Date("Driving License Expiry Date")
    driving_license_last_notification_date = fields.Date("Driving License Last Notification Date")
    health_care_card_no = fields.Char("Health Care Card No.")
    health_care_card_expiry_date = fields.Date("Health Care Card Expiry date")
    health_care_card_last_notification_date = fields.Date("Health Care Card Last Notification Date")
    
    @api.constrains('qid')
    def _constrains_qid(self):    
        for rec in self.filtered(lambda x:x.qid != False):
            same_qid = self.search([('qid','=',rec.qid),('id','!=',rec.id),('company_id','=',self.env.user.company_id.id)])
            if same_qid : 
                raise UserError("QID must be unique per employee.")
            if len(rec.qid)!=11:
                raise UserError("QID must contain 11 character.")
            
            
    def send_documnets_expiry_email(self):
        lagally_to_renotify = fields.Date.today()  + timedelta(days=14)
        soon_expiry_date = fields.Date.today()  + timedelta(days=30) 
        qid_expire_soon = self.search(['&',("qid_expiry_date","<=",soon_expiry_date),'|',("qid_last_notification_date",">",lagally_to_renotify),("qid_last_notification_date","=",False)])
        driving_license_expire_soon = self.search(['&',("driving_license_expiry_date","<=",soon_expiry_date),'|',("driving_license_last_notification_date",">",lagally_to_renotify),("driving_license_last_notification_date","=",False)])
        health_care_card_expire_soon = self.search(['&',("health_care_card_expiry_date","<=",soon_expiry_date),'|',("health_care_card_last_notification_date",">",lagally_to_renotify),("health_care_card_last_notification_date","=",False)])
        passport_expire_soon = self.search(['&',("passport_expiry_date","<=",soon_expiry_date),'|',("passport_last_notification_date",">",lagally_to_renotify),("passport_last_notification_date","=",False)])
        
        if qid_expire_soon or driving_license_expire_soon or health_care_card_expire_soon or passport_expire_soon:
            body = """<!DOCTYPE html><html><head><style>table, th, td {
                            border: 1px solid black;
                            border-collapse: collapse;
                        }
                        td{
                        width:200px;
                        
                        }
                        </style></head><body>
                        <img src="/l10n_qa_employees/static/src/img/logo.jpeg"
                        
                        
                        """
            body +='<div style="direction:ltr"></br><h2  style="font-size:17px;text-align:center;">Documents will expire soon</h2> '
            if passport_expire_soon:
                body += """
                <p>Passports will expire soon</p>
                <table class="tb1 table table-sm o_main_table">
                                    <tr>
                                        <th >Employee Name</th>
                                        <th >Passport Number</th>
                                        <th >Passport Expiry Date</th>
                                </tr>""" 
                                
                for passport_employee in  passport_expire_soon:
                    body+="""<tr>  <td>{}</td>
                                <td>{}</td>
                                <td >{}</td>
                                </tr>
                             """.format(passport_employee.name , passport_employee.passport_id,passport_employee.passport_expiry_date)
                    passport_employee.passport_last_notification_date = fields.Date.today()
                body+="""</table> <br/> <br/> <br/>"""
            
            
            if qid_expire_soon:
                body += """
                 <p>QID will expire soon</p>
                <table class="tb1 table table-sm o_main_table">
                                    <tr>
                                        <th >Employee Name</th>
                                        <th >QID Number</th>
                                        <th >QID Expiry Date</th>
                                </tr>""" 
                for qid_employee in  qid_expire_soon:
                    body+="""<tr>  <td>{}</td>
                                <td>{}</td>
                                <td >{}</td>
                                </tr>
                             """.format(qid_employee.name  , qid_employee.qid if qid_employee.qid else "",qid_employee.qid_expiry_date)
                    qid_employee.qid_last_notification_date = fields.Date.today()
                    
                body+="""</table> <br/> <br/> <br/>"""
            
            if driving_license_expire_soon:
                body += """
                <p>Driving License will expire soon</p>
                <table class="tb1">
                                    <tr>
                                        <th >Employee Name</th>
                                        <th >Driving License Number</th>
                                        <th >Driving License Expiry Date</th>
                                </tr>""" 
                                
                for driving_license_employee in  driving_license_expire_soon:
                    body+="""<tr>  <td>{}</td>
                                <td>{}</td>
                                <td >{}</td>
                                </tr>
                             """.format(driving_license_employee.name , driving_license_employee.driving_license_number if driving_license_employee.driving_license_number else "", \
                                        driving_license_employee.driving_license_expiry_date )
                    driving_license_employee.driving_license_last_notification_date = fields.Date.today()
                body+="""</table> <br/> <br/> <br/>"""
            
            if health_care_card_expire_soon:
                body += """<table class="tb1">
                                    <tr>
                                        <th >Employee Name</th>
                                        <th >Health Care Card Number</th>
                                        <th >Health Care Card Expiry Date</th>
                                </tr>""" 
                                
                for health_care_card in  health_care_card_expire_soon:
                    body+="""<tr>  <td>{}</td>
                                <td>{}</td>
                                <td >{}</td>
                                </tr>
                             """.format(health_care_card.name , health_care_card.health_care_card_no,health_care_card.health_care_card_expiry_date)
                    health_care_card.health_care_card_last_notification_date = fields.Date.today()
                body+="""</table> <br/> <br/> <br/>"""
            
            recipients = self.env.user.company_id.employee_ids
            email_values = {
                  'subject': "Employees' Document Will expire soon",
                    'body_html': body ,
                    'layout':'mail.mail_notification_light',
                    'parent_id': False,
                    'attachment_ids': [],
                    'auto_delete': False,
                    'email_from':self.env.user.company_id.email,
                }
            for r in recipients:
                email_values["email_to"] = r.work_email
                self.env['mail.mail'].create(email_values).send()
            
        