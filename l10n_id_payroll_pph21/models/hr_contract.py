from odoo import fields, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    l10n_id_pph21_method = fields.Selection(
        selection=[
            ("ter", "TER Placeholder"),
            ("progressive", "Progressive Annual Reconciliation Placeholder"),
        ],
        string="PPh21 Method",
        default="ter",
        required=True,
        help="Contract-level placeholder method used by the payslip helper.",
    )
    l10n_id_pph21_effective_date = fields.Date(
        string="PPh21 Effective Date",
        default=fields.Date.context_today,
        help="Effective date used when matching placeholder TER/progressive tables.",
    )
    l10n_id_pph21_additional_taxable_amount = fields.Monetary(
        string="Additional Taxable Input",
        help="Extra monthly taxable amount placeholder added on top of the contract wage.",
    )
    l10n_id_pph21_override_active = fields.Boolean(
        string="Manual PPh21 Override",
        help="Enable this to force the placeholder payslip amount from the contract.",
    )
    l10n_id_pph21_override_amount = fields.Monetary(
        string="Override Amount",
        help="Manual placeholder amount used when the override flag is enabled.",
    )
    l10n_id_pph21_annual_reconciliation = fields.Boolean(
        string="Annual Reconciliation Mode",
        default=True,
        help="Keeps the progressive method explicitly marked as an annual reconciliation placeholder.",
    )
    l10n_id_pph21_note = fields.Text(
        string="PPh21 Notes",
        help="Contract-specific implementation notes for future statutory logic.",
    )
