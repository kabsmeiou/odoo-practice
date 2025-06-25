import logging

from odoo import models, fields


_logger = logging.getLogger(__name__)

class InheritedUserModel(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many(
        comodel_name='estate.property',
        inverse_name='salesman',
        domain=['|', '|', ('state', '=', 'new'), ('state', '=', 'offer_received'), ('state', '=', 'sold')],
        string='Properties',
    )