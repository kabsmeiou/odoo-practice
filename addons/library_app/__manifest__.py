# -*- coding: utf-8 -*-
{
    'name': "Library Management",

    'summary': "Library application to perform various library operations and management",

    'description': """
        This module provides a library application that allows users to perform various operations related to library management.
        It includes features for managing books, and authors, as well as lending.
        The application aims to streamline library operations and enhance user experience by providing an intuitive interface for managing library resources.
    """,

    'license': 'LGPL-3',
    'author': "AWB",
    'website': "https://achievewithoutborders.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Services/Library',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'report/estate_property_offer_table.xml',
        'report/library_book_report_template.xml',
        'report/library_book_report.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/search_view.xml',
        'views/book_view.xml',
        'views/library_menu.xml',
        'views/library_staff_view.xml',
        'views/book_list_template.xml',
    ],
    
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
} # type: ignore

