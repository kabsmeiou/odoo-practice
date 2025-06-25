# -*- coding: utf-8 -*-

from odoo import models, fields, api

# docker compose exec odoo18 odoo -u library_app,estate -d postgres --test-enable --test-tags library_app,estate --no-http --http-port 8070 --stop-after-init

class ResPartner(models.Model):
    _inherit = 'res.partner'

    library_staff_ids = fields.One2many("library.staff", "partner_id", string="Library Staff")
    is_library_staff = fields.Boolean("Library Staff?", compute='_compute_is_library_staff', store=True)

    published_book_ids = fields.One2many(
        'library.book', 
        'publisher_id', 
        string="Published Books",
    )

    @api.depends('library_staff_ids')
    def _compute_is_library_staff(self):
        for record in self:
            record.is_library_staff = bool(record.library_staff_ids)


class library_app(models.Model):
    _name = 'library.book'
    _description = 'Book'

    name = fields.Char("Title", required=True)
    isbn = fields.Char("ISBN")
    active = fields.Boolean("Active?", default=True)
    date_published = fields.Date()
    image = fields.Binary("Cover")
    publisher_id = fields.Many2one("res.partner", string="Publisher", domain=[('is_library_staff', '=', True)])
    author_ids = fields.Many2many("res.partner", string="Authors")

    def _check_isbn(self):
        if self.isbn:
            if len(self.isbn) == 10 or len(self.isbn) == 13:
                return True
        return False


    def button_check_isbn(self):
        # This is called when the button is clicked
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'ISBN Check',
                'message': f'The ISBN is: {self.isbn}' if self.isbn else 'No ISBN',
                'type': f'{"success" if self._check_isbn() else "info"}',
                'sticky': False,
            }
        }


class LibraryStaff(models.Model):
    _name = 'library.staff'
    _description = 'Staff'

    # Link to res.partner. This is the main connection.
    partner_id = fields.Many2one("res.partner", string="Partner", required=True, ondelete='restrict')
    name = fields.Char(related='partner_id.name', string="Staff Name", store=True, readonly=True)
    job = fields.Char("Job", compute='_get_job_position', store=True)

    # Set sql constraint for a unique(One2one) connection
    _sql_constraints = [
        ('unique_partner_id', 'UNIQUE(partner_id)', 'A partner can only be linked to one staff role.'),
    ]

    @api.depends('partner_id.function')
    def _get_job_position(self):
        for record in self:
            if record.partner_id.function:
                record.job = record.partner_id.function
            else:
                record.job = 'Staff'

