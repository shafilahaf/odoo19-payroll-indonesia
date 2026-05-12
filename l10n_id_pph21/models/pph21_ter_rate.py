from odoo import models, fields, api


class Pph21TerRate(models.Model):
    """TER Rate lines - monthly effective rates per income bracket"""
    _name = 'pph21.ter.rate'
    _description = 'TER Rate'
    _order = 'category_id, range_from'

    category_id = fields.Many2one('pph21.ter.category', string='TER Category',
                                  required=True, ondelete='cascade')
    range_from = fields.Float(string='Gross Income From (Rp)', required=True,
                              help='Lower bound of monthly gross income')
    range_to = fields.Float(string='Gross Income To (Rp)', required=True,
                            help='Upper bound of monthly gross income (0 = unlimited)')
    rate = fields.Float(string='TER Rate (%)', required=True, digits=(5, 2),
                        help='Effective tax rate percentage')
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    @api.model
    def get_ter_rate(self, category_code, gross_amount, company=None):
        """Get the TER rate percentage for a given category and gross income amount.
        
        Args:
            category_code: TER category code (A, B, or C)
            gross_amount: Monthly gross income amount
            company: Company record (optional, defaults to current company)
            
        Returns:
            float: TER rate percentage
        """
        if not company:
            company = self.env.company
        
        # Accept records either belonging to current company or with no company
        # (loaded from XML data without company_id set)
        domain = [
            ('category_id.code', '=', category_code),
            ('range_from', '<=', gross_amount),
            '|', ('company_id', '=', company.id), ('company_id', '=', False),
        ]
        
        # Filter by upper bound too: either range_to = 0 (unlimited)
        # or gross_amount <= range_to
        rates = self.search(domain, order='range_from desc')
        
        for rate_line in rates:
            if rate_line.range_to == 0 or gross_amount <= rate_line.range_to:
                return rate_line.rate
        
        return 0.0