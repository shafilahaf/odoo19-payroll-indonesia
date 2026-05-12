from odoo import fields, models


class HrVersion(models.Model):
    """Extension of hr.version (Contract Template / Salary Package) for Indonesian PPh21.

    In Odoo 19 Enterprise, hr.version (provided by hr_contract_salary) is the
    Contract Template / Salary Package model.  The classic community hr.contract model
    is NOT available in this distribution.  All contract-level PPh21 configuration is
    therefore stored on hr.version.

    Note on currency_field: hr.version already exposes a currency_id field related to
    the company currency via hr_contract_salary.  If your distribution uses a different
    field name, update currency_field on the Monetary fields below accordingly.
    """

    _inherit = "hr.version"

    l10n_id_pph21_method = fields.Selection(
        selection=[
            ("ter", "TER Placeholder"),
            ("progressive", "Progressive Annual Reconciliation Placeholder"),
        ],
        string="PPh21 Method",
        default="ter",
        required=True,
        help="Salary package PPh21 method used by the payslip placeholder helper.",
    )
    l10n_id_pph21_effective_date = fields.Date(
        string="PPh21 Effective Date",
        default=fields.Date.context_today,
        help="Effective date used when matching placeholder TER/progressive tables.",
    )
    l10n_id_pph21_additional_taxable_amount = fields.Monetary(
        string="Additional Taxable Input",
        currency_field="currency_id",
        help="Extra monthly taxable amount placeholder added on top of the package wage.",
    )
    l10n_id_pph21_override_active = fields.Boolean(
        string="Manual PPh21 Override",
        help="Enable this to force the placeholder payslip amount from the salary package.",
    )
    l10n_id_pph21_override_amount = fields.Monetary(
        string="Override Amount",
        currency_field="currency_id",
        help="Manual placeholder amount used when the override flag is enabled.",
    )
    l10n_id_pph21_annual_reconciliation = fields.Boolean(
        string="Annual Reconciliation Mode",
        default=True,
        help="Keeps the progressive method explicitly marked as an annual reconciliation placeholder.",
    )
    l10n_id_pph21_note = fields.Text(
        string="PPh21 Notes",
        help="Salary-package-specific notes for future statutory PPh21 logic.",
    )
