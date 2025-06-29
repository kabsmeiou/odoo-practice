# -*- coding: utf-8 -*-
{
    'name': "estate",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Real Estate/Brokerage',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        # 'views/views.xml',
        # 'views/templates.xml',
        'views/estate_property_menus.xml',
        'views/estate_property_views.xml',
        'views/res_user_views.xml',
        'report/estate_property_offer_table.xml',
        'report/user_estate_properties_report.xml',
        'report/estate_property_report_template.xml',
        'report/estate_property_report.xml',
    ],
    # only loaded in demonstration mode
    "demo": [
        "data/estate_demo.xml"
    ],
    'application': True,
}

