from odoo import models, fields, api


class Pph21Ptkp(models.Model):
    """PTKP (Penghasilan Tidak Kena Pajak) - Non-Taxable Income Threshold"""
    _name = 'pph21.ptkp'
    _description = 'PTKP (Penghasilan Tidak Kena Pajak)'
    _order = 'code'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    annual_amount = fields.Float(string='Annual Amount (Rp)', required=True,
                                 help='Annual non-taxable income amount')
    monthly_amount = fields.Float(string='Monthly Amount (Rp)', compute='_compute_monthly_amount',
                                  store=True)
    marital_status = fields.Selection([
        ('tk', 'TK - Tidak Kawin (Single)'),
        ('k', 'K - Kawin (Married)'),
    ], string='Marital Status', required=True)
    dependents = fields.Integer(string='Number of Dependents', default=0,
                                help='Number of dependents (max 3)')
    ter_category_id = fields.Many2one('pph21.ter.category', string='TER Category',
                                      help='TER category for this PTKP status')
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    _sql_constraints = [
        ('code_company_unique', 'unique(code, company_id)',
         'PTKP code must be unique per company!'),
    ]

    @api.depends('annual_amount')
    def _compute_monthly_amount(self):
        for record in self:
            record.monthly_amount = record.annual_amount / 12
