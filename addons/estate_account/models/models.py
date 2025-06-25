# -*- coding: utf-8 -*-

from odoo import models, fields, api,  Command
import logging

_logger = logging.getLogger(__name__)

class InheritedPropertyModel(models.Model):
    _inherit = 'estate.property'

    def action_mark_sold(self):
        """Extend the action_mark_sold method to add invoice creation."""
        logging.info("Marking property as sold and creating invoice.")
        values = {
            'partner_id': self.buyer.id,
            'move_type': 'out_invoice',
            'journal_id': self.env['account.journal'].search([('type', '=', 'sale')], limit=1).id,
            'invoice_line_ids': [
            (0, 0, {
                'name': '6% Commission',
                'quantity': 1,
                'price_unit': self.selling_price * 0.06,
            }),
            (0, 0, {
                'name': 'Administrative Fees',
                'quantity': 1,
                'price_unit': 100.00,
            }),
        ]
        }
        self.env['account.move'].create(values)
        return super().action_mark_sold()
