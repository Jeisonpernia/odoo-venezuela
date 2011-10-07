# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    This module was developen by Vauxoo Team:
#    Coded by: javier@vauxoo.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name" : "Fiscal requirements Venezuelan laws",
    "version" : "0.5",
    "author" : "Vauxoo",
    "website" : "http://vauxoo.com",
    "category": 'Generic Modules/Accounting',
    "description": """Venezuelan Tax Laws Requirements:
    - Invoice Control Number.
    - Tax-except concept, necesary rule by Venezuelan Laws.
    - Required address invoice.
    - Unique billing address (invoice), necesary rule by Venezuelan Laws.
    - VAT verification for Venezuela rules.
    - Damaged "Legal free forms" declaration.
    - Tax Units configuration.
    ---------------------------------------------------------------------------
    For damaged invoices (Free form formats), you must go to the company and, under the configuration section,
    create the corresponding journal and account.
    TODO : Include this on wizard configuration.

    If you install this module with invoice data on the database, the concept_id will be 
    Empty for all those invoices, so, when you try to modify them you have to add a value on
    that field

    This module should also install a menu item under the accounting configuration menu.
    """,
    'init_xml': [
        'data/l10n_ut_data.xml',
    ],
    "depends" : ["base_vat", "account", "account_accountant"],
    'update_xml': [
        'security/ir.model.access.csv',
        'view/account_invoice_view.xml',
        'view/res_company_view.xml',
        'view/l10n_ut_view.xml',
        'view/partner_view.xml',
        'view/seniat_url_view.xml',
        'wizard/wizard_invoice_nro_ctrl_view.xml',
        'wizard/wizard_nro_ctrl_view.xml',
    ],
    'demo_xml': [
        'demo/demo_partners.xml',
    ],
    'test': [],
    'installable': True,
    'active': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
