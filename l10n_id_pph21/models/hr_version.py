from odoo import models, fields, api


class HrVersion(models.Model):
    """Extend hr.version (contract in Odoo 19) to allow per-contract PPh 21
    configuration that overrides employee-level defaults.

    Precedence:
    - If `pph21_use_contract_config` is True, use contract fields.
    - Otherwise, fall back to employee-level fields.
    """
    _inherit = 'hr.version'

    pph21_use_contract_config = fields.Boolean(
        string='Override PPh 21 from Contract',
        default=False,
        help='If checked, PPh 21 calculation will use values from this contract '
             'instead of the employee record. Use this when a specific contract '
             'has different tax treatment than the employee default.')

    pph21_ptkp_id = fields.Many2one(
        'pph21.ptkp', string='PTKP Status (Contract)',
        help='Non-taxable income status for this contract. Overrides employee setting.')

    pph21_ter_category_id = fields.Many2one(
        'pph21.ter.category', string='TER Category (Contract)',
        compute='_compute_ter_category', store=True, readonly=True,
        help='TER category derived from PTKP status on this contract.')

    pph21_calculation_method = fields.Selection([
        ('ter', 'TER (Tarif Efektif Rata-rata)'),
        ('progressive', 'Progressive (Tarif Progresif)'),
    ], string='PPh 21 Method (Contract)', default='ter',
       help='TER: Regular months use TER, December/resign uses progressive.\n'
            'Progressive: Always uses progressive (annualized).')

    pph21_employment_type = fields.Selection([
        ('permanent', 'Karyawan Tetap (Permanent)'),
        ('contract', 'Karyawan Kontrak (Contract)'),
        ('outsource', 'Karyawan Outsource'),
        ('non_permanent', 'Karyawan Tidak Tetap (Non-Permanent)'),
    ], string='Employment Type (Tax, Contract)', default='permanent',
       help='Employment type for PPh 21 purposes on this contract.')

    pph21_has_npwp = fields.Boolean(
        string='Has NPWP (Contract)', default=True,
        help='If unchecked, tax amount will be increased by 20%.')

    pph21_npwp = fields.Char(
        string='NPWP (Contract)',
        help='NPWP number for this contract (optional, informational).')

    @api.depends('pph21_ptkp_id', 'pph21_ptkp_id.ter_category_id')
    def _compute_ter_category(self):
        for version in self:
            if version.pph21_ptkp_id and version.pph21_ptkp_id.ter_category_id:
                version.pph21_ter_category_id = version.pph21_ptkp_id.ter_category_id
            else:
                version.pph21_ter_category_id = False

    # ------------------------------------------------------------------
    # Helpers used by hr.payslip to read PPh 21 configuration
    # ------------------------------------------------------------------
    def _get_pph21_config(self):
        """Return a dict of PPh 21 configuration for this contract.

        If the contract has `pph21_use_contract_config` enabled, use its own
        fields; otherwise fall back to the employee's configuration.
        """
        self.ensure_one()
        employee = self.employee_id

        if self.pph21_use_contract_config:
            return {
                'ptkp_id': self.pph21_ptkp_id,
                'ter_category_id': self.pph21_ter_category_id,
                'calculation_method': self.pph21_calculation_method,
                'employment_type': self.pph21_employment_type,
                'has_npwp': self.pph21_has_npwp,
                'npwp': self.pph21_npwp,
                'source': 'contract',
            }

        return {
            'ptkp_id': employee.pph21_ptkp_id,
            'ter_category_id': employee.pph21_ter_category_id,
            'calculation_method': employee.pph21_calculation_method,
            'employment_type': employee.pph21_employment_type,
            'has_npwp': employee.pph21_has_npwp,
            'npwp': employee.pph21_npwp,
            'source': 'employee',
        }
