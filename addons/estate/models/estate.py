# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
import logging

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)
# docker compose exec odoo18 odoo -u library_app,estate -d postgres --test-enable --test-tags library_app,estate --no-http --http-port 8070 --stop-after-init

# docker compose exec odoo18 odoo -u library_app,estate_account,estate -d odoo --test-enable --test-tags library_app,estate_account,estate --no-http --http-port 8070 --stop-after-init
class Estate(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _order = 'id desc'  # Order by ID descending by default

    # sql constraints
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'Expected price must be greater than 0.'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'Selling price must be greater than or equal to 0.'),
    ]
    
    name = fields.Char(required=True)
    expected_price = fields.Float(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(default=lambda *a: fields.Date.today() + relativedelta(months=3), copy=False)
    selling_price = fields.Float(readonly=True, copy=False, default=0.0, compute='_compute_selling_price', store=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[
            ('north', 'North'), 
            ('south', 'South'), 
            ('east', 'East'), 
            ('west', 'West')
        ], 
        string="Garden Orientation",
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ('new', 'New'), 
            ('offer_received', 'Offer Received'), 
            ('offer_accepted', 'Offer Accepted'), 
            ('sold', 'Sold'), 
            ('cancelled', 'Cancelled')
        ], 
        default='new',
        string="State",
        required=True,
        copy=False,
        compute='_compute_state',
        store=True,
        help="State of the property: New, Offer Received, Offer Accepted, Sold, or Cancelled."
    )

    # records of estate.property can only have one salesman, buyer, and property type
    salesman = fields.Many2one(
        'res.users', 
        string="Salesman", 
        default=lambda self: self.env.user,  # default to the current user
        required=True
    )
    buyer = fields.Many2one('res.partner', string="Buyer", copy=False, readonly=True, help="The partner who bought the property. This field is set when the property is sold.")
    property_type_id = fields.Many2one(
        'estate.property.type', 
        string="Property Type",
        default=lambda self: self.env['estate.property.type'].search([], limit=1),  # default to the first type from the database
        required=True
    )
    property_tag_ids = fields.Many2many(
        'estate.property.tag', 
        string="Property Tags", 
        relation='estate_property_tag_rel',
        column1='property_id',
        column2='tag_id',
    )
    property_offer_ids = fields.One2many(
        'estate.property.offer',
        'property_id',
        string="Property Offers",
        copy=True,
        help="Offers made on this property",
    )
    total_area = fields.Float(
        compute='_compute_total_area',
        string="Total Area (sqm)",
        help="Total area of the property including garden and living area",
        store=True
    )
    best_offer = fields.Float(
        string="Best Offer",
        help="Best available offer for the property, excluding refused offers",
        store=True
    )
    has_accepted_an_offer = fields.Boolean(
        string="An offer has been accepted",
        compute='_has_accepted_an_offer',
        store=True,
        default=False,
        help="Indicates if a decision has been made on the offer(Accepted)",
    )


    @api.depends('property_offer_ids.status')
    def _compute_selling_price(self):
        """When the offer is accepted, the selling price is set to the offer price and buyer is set to the partner of the offer."""
        logging.info("Computing....dasikjdas..")
        for record in self:
            accepted_offer = record.property_offer_ids.filtered(lambda o: o.status == 'accepted')
            if accepted_offer:
                # If there are multiple accepted offers, take the first one (shouldn't happen in a good workflow)
                logging.info(f"Accepted offer found for property {record.name}: {accepted_offer[0].price}")
                record.selling_price = accepted_offer[0].price
                record.buyer = accepted_offer[0].partner_id


    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            # check if living_area or garden_area is None, if so, set them to 0
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)


    # if there are offers, change state to 'offer_received'
    @api.depends('has_accepted_an_offer', 'property_offer_ids')
    def _compute_state(self):
        """Offer accepted when has_accepted_an_offer, update the state to 'offer_received' if there are offers."""
        logging.info(f"Computing state for {self.name}...")
        for record in self:
            if record.has_accepted_an_offer:
                record.state = 'offer_accepted'
            elif record.property_offer_ids:
                record.state = 'offer_received'
            else:
                record.state = 'new'
    

    @api.onchange('property_offer_ids')
    def _compute_best_offer(self):
        for record in self:
            if not record.property_offer_ids:
                record.best_offer = 0.0
            else:
                # exclude refused offers and calculate the maximum price from accepted/inprogress offers
                non_refused_offers = record.property_offer_ids.filtered(lambda o: o.status != 'refused')
                # Get the maximum price from the non-refused offers
                record.best_offer = max(non_refused_offers.mapped('price'), default=0.0)
            
            # # sort the offers by price in desc order and by create_date from oldest to newest
            # offers = record.property_offer_ids.sorted(key=lambda o: (-o.price, o.create_date))
            # record.best_offer = offers[0].price if offers else 0.0
    

    @api.depends('property_offer_ids.status')
    def _has_accepted_an_offer(self):
        """Compute if a decision has been made on the offer."""
        logging.info(f"Computing has_accepted_an_offer for {self.name}...")
        for record in self:
            # Check if any offer has been accepted or refused
            record.has_accepted_an_offer = any(
                offer.status in ['accepted'] for offer in record.property_offer_ids
            )


    @api.constrains('selling_price', 'expected_price')
    def _check_offer_price(self):
        """Ensure the accepted price is at least 90% of the expected price of the property."""
        logging.info("Checking selling price against expected price for properties...")
        for record in self:
            if record.selling_price <= 0:
                continue  # Skip if selling price is not set or is zero
            min_price = 0.9 * record.expected_price
            if float_compare(record.selling_price, min_price, precision_digits=2) < 0: # -1 if selling_price < min_price, < 0 for safer approach
                raise UserError(
                    f"Selling price {record.selling_price} must be at least 90% of the expected price {record.expected_price}."
                )


    @api.constrains('garden')
    def _check_garden_fields(self):
        """Ensure that if garden is True, garden_area must be greater than 0 and orientation is set to something."""
        for record in self:
            if record.garden and (record.garden_area <= 0):
                raise UserError("If there is a garden, garden area must be greater than 0.")
            if record.garden and not record.garden_orientation:
                raise UserError("If there is a garden, garden orientation must be set to a valid value (north, south, east, west).")


    @api.onchange('garden')
    def _onchange_garden(self):
        """On change of garden field and orientation, set garden_area to 0 if garden is False."""
        if not self.garden:
            self.garden_area = 0
            self.garden_orientation = False
            return

        self.garden_area = 10
        self.garden_orientation = 'north'

    
    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_cancelled(self):
        """Prevent deletion of properties that are not in 'new' or 'cancelled' state."""
        for record in self:
            if record.state not in ['new', 'cancelled']:
                raise UserError(f"Cannot delete property {record.name} as it is not in 'new' or 'cancelled' state.")
    

    def action_mark_sold(self):
        """Action to mark the property as sold."""
        for property in self:
            if property.state == 'sold':
                raise UserError(f"Property {property.name} is already marked sold.")
            if property.state != 'offer_accepted':
                raise UserError(f"Property {property.name} must have an accepted offer to be sold.")
            property.state = 'sold'
            # expect one accepted offer
            property.selling_price = property.best_offer
            property.buyer = property.property_offer_ids.filtered(lambda o: o.status == 'accepted').partner_id

    
    def action_mark_cancelled(self):
        """Action to mark the property as cancelled."""
        for property in self:
            if property.state in ['sold', 'cancelled']:
                raise UserError(f"Property {property.name} cannot be cancelled as it is already sold or cancelled.")
            property.state = 'cancelled'
            property.selling_price = 0.0
            property.buyer = False


class PropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _order = 'sequence, name' 

    # each type must be unique
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Property type name must be unique.'),
    ]

    name = fields.Char(required=True, string="Property Type")
    property_ids = fields.One2many(
        'estate.property', 
        'property_type_id', 
        string="Properties", 
        help="Properties associated with this tag"
    )
    offer_ids = fields.One2many(
        'estate.property.offer', 
        'property_type_id', 
        string="Offers", 
        help="Offers associated with this property type"
    )
    offer_count = fields.Integer(
        compute='_compute_offer_count', 
        string="Offer Count", 
        help="Number of offers associated with this property type",
        store=True
    )
    sequence = fields.Integer(
        'Sequence',
        default=10, 
        help="Used to order the property types in the UI"
    )
    description = fields.Text(string="Description", help="Description of the property type")


    @api.depends('offer_ids')
    def _compute_offer_count(self):
        """Compute the number of offers associated with this property type."""
        for record in self:
            logging.info(f"Computing offer count for property type {record.name}...")
            record.offer_count = len(record.offer_ids)


class PropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'
    _order = 'name' 

    # each tag must be unique
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Tag name must be unique.'),
    ]

    name = fields.Char(required=True, string="Tag Name")
    color = fields.Integer(string="Color Index")  # Color index for the tag

    


class Offer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'
    _order = 'price desc, create_date asc'  # Order by price descending and then by creation date ascending


    # SQL constraints
    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'Offer price must be greater than 0.'),
    ]


    price = fields.Float(string="Offer Price")
    status = fields.Selection(
        selection=[
            ('accepted', 'Accepted'), 
            ('refused', 'Refused'), 
            ('in_progress', 'In Progress')
        ], 
        default='in_progress', 
        string="Status",
        copy=False,
        required=True
    )
    property_id = fields.Many2one('estate.property', string="Property", required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string="Partner", required=True, default=lambda self: self.env.user.partner_id)
    property_type_id = fields.Many2one(
        'estate.property.type', 
        related='property_id.property_type_id',
        string="Property Type",
        store=True,
        readonly=True,
        help="Type of the property associated with this offer"
    )
    validity = fields.Integer(
        string="Validity (days)", 
        default=7, 
        help="Number of days the offer is valid",
        readonly=False,
    )
    date_deadline = fields.Date(
        string="Deadline Date", 
        compute='_compute_date_deadline', 
        store=True, 
        help="Deadline date for the offer based on validity",
        inverse='_compute_validity_inverse'
    )


    @api.depends('validity')
    def _compute_date_deadline(self):
        for record in self:
            # If create_date is not set, use today's date
            # it means that the offer is being created now if self.create_date is None(null)
            create_date = record.create_date.date() if record.create_date else fields.Date.today()
            if record.validity:
                record.date_deadline = create_date + relativedelta(days=record.validity)
            else:
                record.date_deadline = False


    @api.onchange('date_deadline')
    def _compute_validity_inverse(self):
        for record in self:
            # Refer to _compute_date_deadline for the comment info
            create_date = record.create_date.date() if record.create_date else fields.Date.today()
            if record.date_deadline:
                record.validity = (record.date_deadline - create_date).days


    @api.model_create_multi
    def create(self, vals_list):
        """Prevent offer creation if less than the best offer price"""
        for vals in vals_list:
            if 'property_id' in vals:
                property_id = vals['property_id']
                property_record = self.env['estate.property'].browse(property_id)
                if property_record:
                    # Check if the offer price is less than the best offer price
                    self._compare_with_best_offer(vals, property_record)
                    
        return super().create(vals_list)
    

    def action_accept_offer(self):
        """Action to accept the offer."""
        for offer in self:
            if offer.status != 'in_progress':
                raise UserError("Offer can only be accepted/refused if it is in progress.")
            if offer.property_id.state == 'sold':
                raise UserError("Property is already sold. Cannot accept the offer.")
            if offer.property_id.has_accepted_an_offer:
                raise UserError("An offer has already been accepted for this property. Cannot accept another offer.")
            if offer.property_id.state == 'cancelled':
                raise UserError("Property is cancelled. Cannot accept the offer.")
            offer.status = 'accepted'


    def action_decline_offer(self):
        """Action to decline the offer."""
        for offer in self:
            if offer.status != 'in_progress':
                raise UserError("Offer can only be declined if it is in progress.")
            offer.status = 'refused'


    def _compare_with_best_offer(self, vals, property_record):
        """Compare the offer price with the best offer price of the property."""
        # Get the best offer price for the property
        best_offer_price = property_record.best_offer
        if 'price' in vals and vals['price'] < best_offer_price:
            raise UserError(
                f"Offer price {vals['price']} must be greater than or equal to the best offer price {best_offer_price}."
            )