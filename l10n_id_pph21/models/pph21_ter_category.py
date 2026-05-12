from odoo import models, fields


class Pph21TerCategory(models.Model):
    """TER Category (A, B, C) based on PTKP status"""
    _name = 'pph21.ter.category'
    _description = 'TER Category'
    _order = 'code'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True,
                       help='Category code: A, B, or C')
    description = fields.Text(string='Description')
    ptkp_ids = fields.One2many('pph21.ptkp', 'ter_category_id', string='PTKP Status')
    rate_ids = fields.One2many('pph21.ter.rate', 'category_id', string='TER Rates')
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    _sql_constraints = [
        ('code_company_unique', 'unique(code, company_id)',
         'TER Category code must be unique per company!'),
    ]
