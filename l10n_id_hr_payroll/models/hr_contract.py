from odoo import fields, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    l10n_id_pay_schedule = fields.Selection(
        selection=[
            ("monthly", "Monthly"),
            ("daily", "Daily"),
            ("other", "Other"),
        ],
        string="Indonesia Payroll Schedule",
        default="monthly",
    )
    l10n_id_allowance_transport = fields.Monetary(string="Transport Allowance")
    l10n_id_allowance_meal = fields.Monetary(string="Meal Allowance")
    l10n_id_allowance_communication = fields.Monetary(string="Communication Allowance")
    l10n_id_allowance_other_taxable = fields.Monetary(string="Other Taxable Allowance")
    l10n_id_allowance_other_nontaxable = fields.Monetary(string="Other Non-taxable Allowance")
    l10n_id_deduction_cooperative = fields.Monetary(string="Cooperative Deduction")
    l10n_id_deduction_other = fields.Monetary(string="Other Deduction")
    l10n_id_bpjs_base_override = fields.Monetary(
        string="Custom BPJS Base",
        help="Optional manual base used when BPJS should not follow the regular wage basis.",
    )
    l10n_id_pph21_override = fields.Monetary(
        string="Manual PPh21 Override",
        help="Temporary field for manual adjustments while statutory calculation is still scaffolded.",
    )
    l10n_id_thr_method = fields.Selection(
        selection=[
            ("prorated", "Prorated"),
            ("full_month_salary", "Full Monthly Salary"),
            ("manual", "Manual"),
        ],
        string="THR Method",
        default="prorated",
    )
    l10n_id_thr_amount = fields.Monetary(
        string="Manual THR Amount",
        help="Used only when THR is maintained manually outside the future calculation engine.",
    )
    l10n_id_payroll_note = fields.Text(string="Payroll Localization Notes")
