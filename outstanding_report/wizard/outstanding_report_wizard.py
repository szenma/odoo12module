# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import tempfile
import base64
import xlsxwriter
import babel.dates
import io
from xlsxwriter.utility import xl_rowcol_to_cell
import json

class OutstandingReport(models.TransientModel):
    _name = "outstanding.report"
    _description = "Outstanding Report"
    
    partner_id = fields.Many2one("res.partner", string="Customer", required=True)
    from_date = fields.Date("From Date",required=True)
    to_date = fields.Date("To Date",required=True)
    file = fields.Binary("File")
    file_name = fields.Char("File Name")
    show_paid_invoices = fields.Boolean("Show Paid Invoices")  
        
    def _get_data(self):
        invoices_data = {}
        
        state_domain = [('state','in',('open','paid'))] if self.show_paid_invoices else [('state','=','open')]
        domain = ['&','&','&','|',("partner_id",'=',self.partner_id.id),
                  ("partner_id",'child_of',self.partner_id.id)
                  ,'&',("date_invoice",">=",self.from_date),("date_invoice","<=",self.to_date),
                  ('type','=','out_invoice')] + state_domain
        
        
        
        invoices = self.env["account.invoice"].search(domain)
        per_month_balances = {}
        total_invoice_amount = 0
        total_invoice_balance = 0
        total_rebate = 0
        total_balance = 0
        total_return = 0
        total_paymnets = 0
        total = {}
        for invoice in invoices:
            payment_vals = invoice._get_payments_vals()
            payments = sum(p["amount"]  for p in payment_vals if p["account_payment_id"] != invoice.rebate_payment_id.id)
            sale_order = invoice.invoice_line_ids[0].sale_line_ids[0].order_id if invoice.invoice_line_ids and  invoice.invoice_line_ids[0].sale_line_ids else False
            total_refund = sum(invoice.refund_invoice_ids.mapped("amount_total")) if invoice.refund_invoice_ids else 0
            rebate_amount = invoice.rebate_payment_id.amount if invoice.rebate_payment_id else 0 
            invoice_date = invoice.date_invoice if invoice.date_invoice else False 
            today_date = fields.Date.today()
            ivoice_balance = invoice.residual
            month_name = babel.dates.get_month_names(locale=self.env.context.get('lang') or 'en_US')[invoice_date.month] if invoice_date else ""
            if per_month_balances.get(month_name,False):
               per_month_balances[month_name] = per_month_balances[month_name] + ivoice_balance
            else :
               per_month_balances[month_name] = ivoice_balance
           
            
            total_invoice_amount += invoice.amount_total
            total_invoice_balance += ivoice_balance
            total_rebate += rebate_amount
            total_return += total_refund
            total_paymnets += payments
            invoices_data[invoice.id] = {"month_name":month_name}
            invoices_data[invoice.id]["invoice_date"] = str(invoice_date)
            invoices_data[invoice.id]["invoice_number"] = invoice.number
            invoices_data[invoice.id]["cllien_ref"] = invoice.name if invoice.name else ""
            invoices_data[invoice.id]["shipping_address"] = sale_order.partner_shipping_id.name   if sale_order and sale_order.partner_shipping_id else ""
            invoices_data[invoice.id]["sky_ref"] = sale_order.name   if sale_order else ""
            invoices_data[invoice.id]["days"] = (today_date - invoice_date).days if invoice_date else ""
            invoices_data[invoice.id]["bill_amount"] = invoice.amount_total
            invoices_data[invoice.id]["payment"] = payments
            invoices_data[invoice.id]["returns"] = total_refund
            invoices_data[invoice.id]["rebate"] = rebate_amount
            invoices_data[invoice.id]["balance"] = ivoice_balance
            invoices_data[invoice.id]["due_date"] = str(invoice.date_due)
        
        total["total_invoice_amount"] = total_invoice_amount
        total["total_payment"] = total_paymnets
        total["total_invoice_balance"] = total_invoice_balance
        total["total_rebate"] = total_rebate
        total["total_refund"] = total_return
        
        return {
             "total":total,
             "partner":self.partner_id.display_name,
             "date_to":self.to_date,
             "date_from":self.from_date,
            "invoices_data":invoices_data,
            "per_month_balances":per_month_balances
            
            }
        
    def generate_excel_report(self):
        
        data = self._get_data()
        invoices_data = data.get("invoices_data")
        per_month_balances = data.get("per_month_balances")
        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx")
        workbook = xlsxwriter.Workbook(temp_file.name)
        money_format = workbook.add_format({'num_format': '#,###,###.##'}) 
        

        header_style = workbook.add_format({'bold': True,'font_name':'Calibri Light','align': 'center','bg_color':'#d3d3d3'})
        label_style = workbook.add_format({'bold': True,'font_name':'Calibri Light','bg_color':'#d3d3d3'})
        worksheet = workbook.add_worksheet('Sheet 1')
        worksheet.merge_range(0,3,0,8,self.env.user.company_id.name,header_style)
        worksheet.merge_range(1, 3, 1, 8, "Outstanding Receivable Report",header_style)
        worksheet.merge_range(2,3,2,8,self.partner_id.display_name,header_style)
        worksheet.write(1,9,"From")
        worksheet.write(2,9,"To")
        worksheet.write(1,10,str(self.from_date))
        worksheet.write(2,10,str(self.to_date))
        
        worksheet.write(4,0,"Month",label_style)
        worksheet.write(4,1,"INV Date",label_style)
        worksheet.write(4,2,"INV #",label_style)
        worksheet.write(4,3,"Client Ref",label_style)
        worksheet.write(4,4,"Shipping Address",label_style)
        worksheet.write(4,5,"Sky Ref.",label_style)
        worksheet.write(4,6,"Days",label_style)
        worksheet.write(4,7,"Bill Amt",label_style)
        worksheet.write(4,8,"Payment",label_style)
        worksheet.write(4,9,"Returns",label_style)
        worksheet.write(4,10,"Rebate",label_style)
        worksheet.write(4,11,"Balance",label_style)
        worksheet.write(4,12,"Due Date",label_style)
        row = 5
        for invoice , invoice_info  in invoices_data.items():
            worksheet.write(row,0,invoice_info.get("month_name",""))
            worksheet.write(row,1,invoice_info.get("invoice_date",""))
            worksheet.write(row,2,invoice_info.get("invoice_number",""))
            worksheet.write(row,3,invoice_info.get("cllien_ref",""))
            worksheet.write(row,4,invoice_info.get("shipping_address",""))
            worksheet.write(row,5,invoice_info.get("sky_ref",""))
            worksheet.write(row,6,invoice_info.get("days",""))
            worksheet.write(row,7,invoice_info.get("bill_amount",0),money_format)
            worksheet.write(row,8,invoice_info.get("payment",0),money_format)
            worksheet.write(row,9,invoice_info.get("returns",0),money_format)
            worksheet.write(row,10,invoice_info.get("rebate",0),money_format)
            worksheet.write(row,11,invoice_info.get("balance",0),money_format)
            worksheet.write(row,12,invoice_info.get("due_date",""))            
            row+=1
        worksheet.write(row,7,data["total"]["total_invoice_amount"],money_format)
        worksheet.write(row,8,data["total"]["total_refund"],money_format)
        worksheet.write(row,9,data["total"]["total_rebate"],money_format)
        worksheet.write(row,10,data["total"]["total_invoice_balance"],money_format)
        
        row+=4
        
        worksheet.write(row,0,"Total Amount",label_style)
        worksheet.write(row+1,0,"LESS RETURNS",label_style)
        worksheet.write(row+2,0,"LESS REBATES" ,label_style)
        worksheet.write(row+3,0,"OUTSTANDING BALANCE" ,label_style)
        
        
        worksheet.write(row,2,data["total"]["total_invoice_amount"],money_format)
        worksheet.write(row+1,2,data["total"]["total_payment"],money_format)
        worksheet.write(row+2,2,data["total"]["total_refund"],money_format)
        worksheet.write(row+3,2,data["total"]["total_rebate"],money_format)
        worksheet.write(row+4,2,data["total"]["total_invoice_balance"],money_format)
        row+=8
        
        for month , month_balance in per_month_balances.items():
            worksheet.merge_range(row,0,row,1,"Outstanding from %s"%(month),label_style)
            worksheet.write(row,2,month_balance,money_format)
            row+=1
            
        
        workbook.close()
        data = open(temp_file.name, 'rb').read()
        self.file =  base64.b64encode(data)
        self.file_name = "Outstanding_report.xlsx"
        action =  {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_xls_document_outstanding_report/?model=outstanding.report&id=%s' % (self.id),
            'target': 'self',
        }
        return action
        
    
    
    def generate_pdf_report(self):
        data = self._get_data()
        return self.env.ref("outstanding_report.outstanding_report").report_action([], data=data)
    
    
   