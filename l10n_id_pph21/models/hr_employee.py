from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    pph21_ptkp_id = fields.Many2one('pph21.ptkp', string='PTKP Status',
                                    help='Non-taxable income status (e.g., TK/0, K/1, etc.)')
    pph21_ter_category_id = fields.Many2one('pph21.ter.category', string='TER Category',
                                            compute='_compute_ter_category', store=True,
                                            help='TER category based on PTKP status')
    pph21_calculation_method = fields.Selection([
        ('ter', 'TER (Tarif Efektif Rata-rata)'),
        ('progressive', 'Progressive (Tarif Progresif)'),
    ], string='PPh 21 Method', default='ter',
       help='TER: For permanent/contract employees (Jan-Nov uses TER, Dec uses progressive).\n'
            'Progressive: For outsource or special cases (always uses progressive rates).')
    pph21_npwp = fields.Char(string='NPWP', help='Nomor Pokok Wajib Pajak')
    pph21_has_npwp = fields.Boolean(string='Has NPWP', default=True,
                                    help='If employee does not have NPWP, tax is 20% higher')
    pph21_employment_type = fields.Selection([
        ('permanent', 'Karyawan Tetap (Permanent)'),
        ('contract', 'Karyawan Kontrak (Contract)'),
        ('outsource', 'Karyawan Outsource'),
        ('non_permanent', 'Karyawan Tidak Tetap (Non-Permanent)'),
    ], string='Employment Type (Tax)', default='permanent',
       help='Employment type for PPh 21 calculation purposes')
    pph21_join_date = fields.Date(string='Tax Join Date',
                                  help='Date when employee started for tax year calculation. '
                                       'Used to prorate annual calculation.')
    pph21_resign_date = fields.Date(string='Tax Resign Date',
                                    help='Resignation date for final tax settlement calculation')

    @api.depends('pph21_ptkp_id', 'pph21_ptkp_id.ter_category_id')
    def _compute_ter_category(self):
        for employee in self:
            if employee.pph21_ptkp_id and employee.pph21_ptkp_id.ter_category_id:
                employee.pph21_ter_category_id = employee.pph21_ptkp_id.ter_category_id
            else:
                employee.pph21_ter_category_id = False
