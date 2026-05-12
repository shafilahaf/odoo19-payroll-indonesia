from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    l10n_id_has_npwp = fields.Boolean(
        string="Has NPWP",
        help="Enable this when the employee already has an NPWP registered for PPh21 handling.",
    )
    l10n_id_npwp = fields.Char(string="NPWP Number")
    l10n_id_pph21_tax_status = fields.Selection(
        selection=[
            ("TK0", "TK/0"),
            ("TK1", "TK/1"),
            ("TK2", "TK/2"),
            ("TK3", "TK/3"),
            ("K0", "K/0"),
            ("K1", "K/1"),
            ("K2", "K/2"),
            ("K3", "K/3"),
        ],
        string="PPh21 Tax Status",
        default="TK0",
        required=True,
        help="Placeholder PTKP-related status for future statutory PPh21 logic.",
    )
    l10n_id_pph21_dependent_count = fields.Integer(
        string="Dependent Count",
        default=0,
        help="Simple family/dependent counter kept for future PPh21 refinement.",
    )
    l10n_id_pph21_method = fields.Selection(
        selection=[
            ("ter", "TER Placeholder"),
            ("progressive", "Progressive Annual Reconciliation Placeholder"),
        ],
        string="Default PPh21 Method",
        default="ter",
        required=True,
        help="Default placeholder method copied into contract/payslip flows when no contract override is set.",
    )
    l10n_id_pph21_note = fields.Text(
        string="PPh21 Notes",
        help="Payroll admin notes for PPh21 assumptions or manual exceptions.",
    )
