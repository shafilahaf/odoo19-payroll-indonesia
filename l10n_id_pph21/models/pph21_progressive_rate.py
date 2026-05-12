from odoo import models, fields, api


class Pph21ProgressiveRate(models.Model):
    """Progressive Tax Rate (Tarif Progresif Pasal 17 UU HPP)"""
    _name = 'pph21.progressive.rate'
    _description = 'Progressive Tax Rate (Pasal 17)'
    _order = 'sequence, range_from'

    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Name', required=True)
    range_from = fields.Float(string='PKP From (Rp)', required=True,
                              help='Lower bound of annual taxable income (PKP)')
    range_to = fields.Float(string='PKP To (Rp)', required=True,
                            help='Upper bound of annual taxable income (0 = unlimited)')
    rate = fields.Float(string='Rate (%)', required=True, digits=(5, 2))
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    @api.model
    def calculate_progressive_tax(self, annual_pkp, company=None):
        """Calculate annual PPh 21 using progressive rates.
        
        Args:
            annual_pkp: Annual taxable income (PKP) amount
            company: Company record (optional)
            
        Returns:
            float: Total annual tax amount
        """
        if not company:
            company = self.env.company
        
        if annual_pkp <= 0:
            return 0.0
        
        rates = self.search([
            ('company_id', '=', company.id),
        ], order='sequence, range_from')
        
        total_tax = 0.0
        remaining = annual_pkp
        
        for rate_line in rates:
            if remaining <= 0:
                break
            
            if rate_line.range_to > 0:
                bracket_size = rate_line.range_to - rate_line.range_from
            else:
                bracket_size = remaining  # unlimited bracket
            
            taxable_in_bracket = min(remaining, bracket_size)
            total_tax += taxable_in_bracket * (rate_line.rate / 100)
            remaining -= taxable_in_bracket
        
        return total_tax
