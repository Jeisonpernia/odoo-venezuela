# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Netquatro C.A. (http://openerp.netquatro.com/) All Rights Reserved.
#                    Javier Duran <javier.duran@netquatro.com>
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

'''
Fiscal Report For Venezuela
'''

import time
from report import report_sxw
from osv import osv
import pooler

class pur_sal_book(report_sxw.rml_parse):
    '''
    Book generates purchase and sale
    '''

    def __init__(self, cr, uid, name, context):
        '''
        Reference to the current instance
        '''
        super(pur_sal_book, self).__init__(cr, uid, name, context)    
        self.localcontext.update({
            'time': time,
            'get_data':self._get_data,
            'get_partner_addr': self._get_partner_addr,
            'get_p_country': self._get_p_country,
            'get_alicuota': self._get_alicuota,
            'get_rif': self._get_rif,
            'get_month':self._get_month,
            'get_dates':self._get_dates,
            'get_totals':self._get_totals,
            'get_doc':self._get_doc,
            'get_ret':self._get_ret,
            'get_prev_ret': self._get_prev_ret,
            'get_totals_ret': self._get_totals_ret,
            'get_data_adjustment': self._get_data_adjustment,
            'validation': self._validation,
            'validation_wh': self._validation_wh,
            'get_data_wh': self._get_data_wh,
            'get_amount_withheld': self._get_amount_withheld,
        })

    def _validation(self,form):
        d1=form['date_start']
        d2=form['date_end']
        type_doc = 'sale'
        if form['type']=='purchase':
            type_doc = 'purchase'
        period_obj=self.pool.get('account.period')
        adjust_obj = self.pool.get('adjustment.book')
        period_ids = period_obj.search(self.cr,self.uid,[('date_start','<=',d1),('date_stop','>=',d2)])
        if len(period_ids)<=0:
            return False
        fr_ids = adjust_obj.search(self.cr,self.uid,[('period_id','in',period_ids),('type','=',type_doc)])
        if not fr_ids:
            return False
        return True

    def _get_data_adjustment(self,form):
        d1=form['date_start']
        d2=form['date_end']
        type_doc = 'sale'
        
        if form['type']=='purchase':
            type_doc = 'purchase'
        
        adjust_obj = self.pool.get('adjustment.book')
        adjust_line_obj = self.pool.get('adjustment.book.line')
        period_obj=self.pool.get('account.period')
        data=[]
        data_line=[]
        period_ids = period_obj.search(self.cr,self.uid,[('date_start','<=',d1),('date_stop','>=',d2)])
        fr_ids = adjust_obj.search(self.cr,self.uid,[('period_id', 'in',period_ids),('type','=',type_doc)])
        
        adj_ids = adjust_line_obj.search(self.cr,self.uid,[('adjustment_id','=',fr_ids[0])])
        #Data to review first and add more records to be printed before ordering and send to rml.
        data = adjust_obj.browse(self.cr,self.uid, fr_ids)
        data_line = adjust_line_obj.browse(self.cr,self.uid, adj_ids)
        return (data,data_line)

    def _get_data(self,form):
        d1=form['date_start']
        d2=form['date_end']
        if form['type']=='purchase':
            book_type='fiscal.reports.purchase'
            orden='ai_date_invoice'
        else:
            book_type='fiscal.reports.sale'
            orden='ai_nro_ctrl'
        data=[]
        fr_obj = self.pool.get(book_type)
        fr_ids = fr_obj.search(self.cr,self.uid,[('ai_date_invoice', '<=', d2), ('ai_date_invoice', '>=', d1)], order=orden)
        #Data to review first and add more records to be printed before ordering and send to rml.
        data = fr_obj.browse(self.cr,self.uid, fr_ids)
        return data

    def _validation_wh(self,form):
        if form['type']=='sale':
            return True
        return False

    def _get_data_wh(self,form):
        d1=form['date_start']
        d2=form['date_end']

        data=[]
        fr_obj = self.pool.get('fiscal.reports.whs')
        fr_ids = fr_obj.search(self.cr,self.uid,[('ar_date_ret', '<=', d2), ('ar_date_ret', '>=', d1),('ai_date_inv','<=',d1)], order='ar_date_ret')
        #Data to review first and add more records to be printed before ordering and send to rml.
        data = fr_obj.browse(self.cr,self.uid, fr_ids)
        return data

    def _get_prev_ret(self,form):
        '''
            Point 3: method to locate withholding outsite period but that need 
            be declared on this one. 
        '''
        d1=form['date_start']
        d2=form['date_end']
        if form['type']=='purchase':
            book_type='fiscal.reports.whp'
            _type='fiscal.reports.purchase'
        else:
            book_type='fiscal.reports.whs'
            _type='fiscal.reports.sale'
        data=[]
        ret_obj = self.pool.get(book_type)
        fr_obj = self.pool.get(_type)
        ret_ids = fr_obj.search(self.cr,self.uid,[('ar_date_ret', '<=', d2), ('ar_date_ret', '>=', d1)])
        fr_ids = fr_obj.search(self.cr,self.uid,[('ar_date_ret', '<=', d2), ('ar_date_ret', '>=', d1)])
        #Data to review first and add more records to be printed before ordering and send to rml.
        
        data = fr_obj.browse(self.cr,self.uid, fr_ids)
        return data


    def _get_ret(self,form,ret_id=None):
        '''
            Ensure that Withholding date is inside period specified on form.
        '''
        d1=form['date_start']
        d2=form['date_end']
        if form['type']=='purchase':
            if ret_id:
                ret_obj = self.pool.get('account.retention')
                rets = ret_obj.browse(self.cr,self.uid,[ret_id])
                return rets[0].number
        if ret_id:
            ret_obj = self.pool.get('account.retention')
            rets = ret_obj.browse(self.cr,self.uid,[ret_id])
            if rets:
                if time.strptime(rets[0].date, '%Y-%m-%d') >= time.strptime(d1, '%Y-%m-%d') \
                and time.strptime(rets[0].date, '%Y-%m-%d') <=  time.strptime(d2, '%Y-%m-%d'):
                    return rets[0].number
                else:
                    return False
            else:
                return False
        else:
            return False

    def _get_totals_ret(self,form):
        d1=form['date_start']
        d2=form['date_end']
        if form['type']=='purchase':
            book_type='fiscal.reports.purchase'
        else:
            book_type='fiscal.reports.sale'
        data=[]
        fr_obj = self.pool.get(book_type)
        fr_ids = fr_obj.search(self.cr,self.uid,[('ai_date_invoice', '<=', d2), ('ai_date_invoice', '>=', d1)], order='ai_nro_ctrl')
        #Data to review first and add more records to be printed before ordering and send to rml.
        data = fr_obj.browse(self.cr,self.uid, fr_ids)
        total=0.00
        for d in data:
            if self._get_ret(form,d.ar_id.id):
                total+=d.ar_id.total_tax_ret
        return total

    def _get_amount_withheld(self,wh_line_id):
        wh_obj = self.pool.get('account.retention.line')
        data = wh_obj.browse(self.cr,self.uid, [wh_line_id])[0]
        return data.amount_tax_ret

    def _get_partner_addr(self, idp=None):
        '''
        Obtains the address of partner
        '''
        if not idp:
            return []

        addr_obj = self.pool.get('res.partner.address')
        addr_inv = 'NO HAY DIRECCION FISCAL DEFINIDA'
        addr_ids = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp), ('type','=','invoice')])
        if addr_ids:                
            addr = addr_obj.browse(self.cr,self.uid, addr_ids[0])
            addr_inv = (addr.street or '')+' '+(addr.street2 or '')+' '+(addr.zip or '')+ ' '+(addr.city or '')+ ' '+ (addr.country_id and addr.country_id.name or '')+ ', TELF.:'+(addr.phone or '')
        return addr_inv
    
    def _get_p_country(self, idp=None):
        '''
        Obtains the address of partner
        '''
        if not idp:
            return []

        addr_obj = self.pool.get('res.partner.address')
        a_id = 1000
        a_ids = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp), ('type','=','invoice')])
        if a_ids:                
            a = addr_obj.browse(self.cr,self.uid, a_ids[0])
            a_id = a.country_id.id
        return a_id 


    def _get_alicuota(self, tnom=None):
        '''
        Get Aliquot
        '''
        if not tnom:
            return []

        tax_obj = self.pool.get('account.tax')
        tax_ids = tax_obj.search(self.cr,self.uid,[('name','=',tnom)])[0]
        tax = tax_obj.browse(self.cr,self.uid, tax_ids)

        return tax.amount*100

    def _get_doc(self, inv_id=None):
        '''
        Get String Document Type
        '''
        inv_obj = self.pool.get('account.invoice')
        inv_ids = inv_obj.search(self.cr,self.uid,[('id', '=', inv_id)])
        inv = inv_obj.browse(self.cr,self.uid, inv_ids)[0]        
        doc_type = ''
        if (inv.type=="in_invoice" or inv.type=="out_invoice") and inv.parent_id:
            doc_type = "ND"
        elif inv.type=='in_refund' or inv.type=='out_refund':
            doc_type = "NC"
        elif inv.type=="in_invoice" or inv.type=="out_invoice":
            doc_type = "F"
        return doc_type


    def _get_rif(self, vat=''):
        '''
        Get R.I.F.
        '''
        if not vat:
            return []
        return vat[2:].replace(' ', '')


    def _get_month(self, form):
        '''
        return year and month
        '''
        months=["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
        res = ['',0]
        res[0] = months[time.strptime(form['date_start'],"%Y-%m-%d")[1]-1]
        res[1] = time.strptime(form['date_start'],"%Y-%m-%d")[0]
        return res
    
    def _get_dates(self, form):
        res=[]
        res.append(form['date_start'])
        res.append(form['date_end'])
        return res

    def _get_totals(self,form):
        '''
        Get Totals
        Total:
            [0],[1],[2] Absolute totals
            [3],[4] Invoice without right to fiscal declaration.
            [5],[6] National Invoices
            [7],[8] International Invoices
        '''    
        d1=form['date_start']
        d2=form['date_end']
        if form['type']=='purchase':
            book_type='fiscal.reports.purchase'
        else:
            book_type='fiscal.reports.sale'
        fr_obj = self.pool.get(book_type)
        user_obj = self.pool.get('res.users')
        user_ids = user_obj.search(self.cr,self.uid,[('id', '=', self.uid)])
        fr_ids = fr_obj.search(self.cr,self.uid,[('ai_date_invoice', '<=', d2), ('ai_date_invoice', '>=', d1)])
        user=user_obj.browse(self.cr,self.uid, [self.uid])
        total=[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        for d in fr_obj.browse(self.cr,self.uid, fr_ids):
            #Sum for Invoice in period
            total[1]+=d.ai_amount_untaxed
            total[2]+=d.ai_amount_tax
            if d.ai_id.sin_cred:
                #Sum for Invoice without right to fiscal declaration.
                total[3]+=d.ai_amount_untaxed
                total[4]+=d.ai_amount_tax
            if self._get_p_country(user[0].company_id.partner_id.id)==self._get_p_country(d.ai_id.partner_id.id):
                #National Invoices
                total[5]+=d.ai_amount_untaxed
                total[6]+=d.ai_amount_tax
            else:
                #International Invoices
                total[7]+=d.ai_amount_untaxed
                total[8]+=d.ai_amount_tax
        return total
      
report_sxw.report_sxw(
    'report.fiscal.reports.purchase.purchase_seniat',
    'fiscal.reports.purchase',
    'addons/l10n_ve_fiscal_reports/report/book_seniat.rml',
    parser=pur_sal_book,
    header=False
)      