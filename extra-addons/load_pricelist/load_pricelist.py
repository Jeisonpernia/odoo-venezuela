# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    This Modules was developed by Netquatro, C.A. (<http://openerp.netquatro.com>)
#    Silver partner of Tiny.
#    author Nhomar Hernandez (nhomar.hernandez@netquatro.com) &
#           Javier Duran (<javier.duran@netquatro.com>)
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from osv import fields
import time
import pooler
#import urllib
import base64
import tools
from tools.translate import _
#import wizard
from tools.misc import currency
import csv

#class product_template(osv.osv):
#    '''
#    Relation with product
#    '''
#    _description = 'Inheriting Products templates'
#    _inherit = 'product.template'
#    #Do not touch _name it must be same as _inherit
#    _name = 'product.template'
#    _columns = {
#        'list_line_ids': fields.one2many('load.pricelist.lines', 'product_id', 'Partners'),
#    }
#product_template()


class load_pricelist(osv.osv):
    '''
Price agreements from suppliers
    '''
    _name = 'load.pricelist'
    _description = 'load_pricelist'
    _columns = {
        'name':fields.char('Name', size=64, required=False, readonly=False),
        'partner_id':fields.many2one('res.partner', 'Partner Supplier', required=False),
        'file_csv':fields.binary('CSV List', filters=None, help='Load in this order supplier,price,quantity,product_code'),
        'date': fields.date('Valid Since'),
        'price_ids':fields.one2many('load.pricelist.lines', 'pricelist_id', 'Price2Load', required=False),
        'state':fields.selection([
        ('draft','Draft'),
        ('loaded','Loaded'),
        ('review','Review'),
        ('toprocess','To Process'),
        ('done','Done'),
        ],'State', select=True, readonly=False),
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'state': lambda *a: 'draft',
    }



    def product_price_list_import(self, cr, uid, id, file, filename, context={}):
        file2 = base64.decodestring(file)
        file2 = file2.split('\n')
        reader = csv.DictReader(file2, delimiter=',', quotechar='"')
        print 'archivo: ',list(reader)
        return []

    def _get_csv(self, cr, uid, ids, context={}):
#        result=self.read(cr,uid,ids,['file_csv'])[-1]['file_csv']
        vals = {}
        obj_pricelst = self.browse(cr, uid, ids)[0]
        if obj_pricelst.file_csv:
            file2 = base64.decodestring(obj_pricelst.file_csv)
            file2 = file2.split('\n')
            reader = csv.DictReader(file2, delimiter=',', quotechar='"')
#            print "Datos de entrada",list(reader)            
#            lst = []

            load_pl = self.price_line_get_item(cr, uid, list(reader), context)
            vals['price_ids'] = load_pl
            print 'lista verificada: ',load_pl
            self.write(cr, uid, [obj_pricelst.id], vals, context=context)


#                lineDict = {}               
#                for fields in row.keys():
#                    check = getattr(self, '_check_' + fields, self._check_default)
#                    lineDict[fields] = (row[fields], check(cr, uid, ids, row[fields], context))

#                self.move_line_get_item(cr, uid, row, context)
#                lst.append(lineDict)
#            print 'lista',lst


                    
        else:
            reader = {}
            print "Datos de entrada",list(reader)
        return list(reader)


    def price_line_get_item(self, cr, uid, lines, context=None):
        pricelines_obj = self.pool.get('load.pricelist.lines')
        vals = {}
        for line in lines:
            for field in line.keys():
                if not pricelines_obj._columns.has_key(field):
                    raise osv.except_osv(_('Field Error!'), _('You have no Fields : %s ') % (field,) )

        return map(lambda x: (0,0,x), lines)



    def _check_default_code(self, cr, uid, ids, code, context):
        warnings = ''
        flag = False
        cr.execute("SELECT p.id FROM product_product p WHERE p.default_code = '%s'" % (code,))
        res = cr.fetchall()
        if not res:
            warnings = 'codigo no existe, producto nuevo'
        if len(res) > 1:
            warnings = 'codigo duplicado'
        if len(res)==1:
            return (res[0][0], True)
        return (warnings, flag)


    def _check_default(self, cr, uid, ids, code, context):
        flag = True
        warnings = 'valor de chequeo por defecto'
        return (warnings, flag)



            
load_pricelist()

class load_pricelist_lines(osv.osv):
    '''
Pricelist from supplier
This is recorded and imported before put on right place for control of changes
    '''
    _name = 'load.pricelist.lines'
    _description = 'Pricelist from supplier'
    _columns = {
        'name':fields.char("Element's Identifier", size=64, required=False, readonly=False),
        'product_id': fields.many2one('product.product', 'Product', ondelete='set null'),
        'product_name':fields.char('Product name', size=64, required=False, readonly=False),
        'product_sup_name':fields.char('Product Sup Name', size=64, required=False, readonly=False),
        'min_qt':fields.float('Min Quantity'),
        'cost':fields.float('Cost by Unit'),
        'price':fields.float('Sugested Price'),
        'pricelist_id':fields.many2one('load.pricelist', 'Load ID', required=False),
        'imported':fields.boolean('Imported', required=False),
    }
load_pricelist_lines()

class res_partner_list(osv.osv):
    '''
    Adding relation with Partners
    '''
    _name = 'res.partner'
    _description = 'Partners'
    _inherit = 'res.partner'
    _columns = {
    'loadpl_ids':fields.one2many('load.pricelistl', 'partner_id', 'Partner', required=False),   
    }
res_partner_list()
