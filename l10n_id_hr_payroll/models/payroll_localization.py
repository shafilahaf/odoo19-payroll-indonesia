from odoo import fields, models


class L10nIdPayrollSettings(models.Model):
    _name = "l10n_id.payroll.settings"
    _description = "Indonesian Payroll Settings"
    _rec_name = "company_id"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(related="company_id.currency_id", store=True, readonly=True)
    effective_date = fields.Date(string="Effective Date", default=fields.Date.context_today)
    pph21_method = fields.Selection(
        selection=[
            ("ter", "TER Placeholder"),
            ("progressive", "Progressive Annual Reconciliation Placeholder"),
        ],
        string="PPh21 Method",
        default="ter",
        required=True,
    )
    pph21_note = fields.Text(
        string="PPh21 Developer Note",
        help="Use this field to document assumptions until the statutory formula is finalized.",
    )
    bpjs_kesehatan_employee_rate = fields.Float(string="BPJS Kesehatan Employee Rate (%)", digits=(16, 4))
    bpjs_kesehatan_employer_rate = fields.Float(string="BPJS Kesehatan Employer Rate (%)", digits=(16, 4))
    bpjs_kesehatan_cap = fields.Monetary(string="BPJS Kesehatan Monthly Cap")
    bpjs_jht_employee_rate = fields.Float(string="JHT Employee Rate (%)", digits=(16, 4))
    bpjs_jht_employer_rate = fields.Float(string="JHT Employer Rate (%)", digits=(16, 4))
    bpjs_jp_employee_rate = fields.Float(string="JP Employee Rate (%)", digits=(16, 4))
    bpjs_jp_employer_rate = fields.Float(string="JP Employer Rate (%)", digits=(16, 4))
    bpjs_jp_cap = fields.Monetary(string="JP Wage Cap")
    bpjs_jkk_employer_rate = fields.Float(string="JKK Employer Rate (%)", digits=(16, 4))
    bpjs_jkm_employer_rate = fields.Float(string="JKM Employer Rate (%)", digits=(16, 4))
    bpjs_note = fields.Text(
        string="BPJS Developer Note",
        help="Statutory rates and caps change over time. Validate before using in production.",
    )
    thr_policy = fields.Selection(
        selection=[
            ("prorated_service_months", "Prorated by Service Months"),
            ("full_month_salary", "Full Monthly Salary"),
            ("manual", "Manual"),
        ],
        string="Default THR Policy",
        default="prorated_service_months",
        required=True,
    )
    thr_note = fields.Text(
        string="THR Developer Note",
        help="Document any company-specific THR eligibility or proration policy here.",
    )

    _sql_constraints = [
        ("company_unique", "unique(company_id)", "Payroll settings must be unique per company."),
    ]


class L10nIdPayrollStructure(models.Model):
    _name = "l10n_id.payroll.structure"
    _description = "Indonesian Payroll Structure"
    _order = "sequence, id"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one("res.company", string="Company")
    note = fields.Text(
        string="Developer Note",
        help="Explain localization assumptions or future work for this structure.",
    )
    rule_ids = fields.One2many("l10n_id.payroll.rule", "structure_id", string="Rules")

    _sql_constraints = [
        (
            "structure_code_company_unique",
            "unique(code, company_id)",
            "Payroll structure code must be unique per company.",
        ),
    ]


class L10nIdPayrollRule(models.Model):
    _name = "l10n_id.payroll.rule"
    _description = "Indonesian Payroll Rule"
    _order = "sequence, id"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    structure_id = fields.Many2one(
        "l10n_id.payroll.structure",
        string="Payroll Structure",
        required=True,
        ondelete="cascade",
    )
    company_id = fields.Many2one(related="structure_id.company_id", store=True, readonly=True)
    category = fields.Selection(
        selection=[
            ("basic", "Basic Salary"),
            ("allowance", "Allowance"),
            ("deduction", "Deduction"),
            ("bpjs", "BPJS"),
            ("pph21", "PPh21"),
            ("thr", "THR"),
            ("other", "Other"),
        ],
        string="Category",
        default="other",
        required=True,
    )
    rule_type = fields.Selection(
        selection=[
            ("earning", "Earning"),
            ("deduction", "Deduction"),
            ("employer_contribution", "Employer Contribution"),
            ("information", "Information"),
        ],
        string="Rule Type",
        default="earning",
        required=True,
    )
    amount_type = fields.Selection(
        selection=[
            ("fixed", "Fixed Amount"),
            ("python", "Python Expression Placeholder"),
            ("note", "Documentation Only"),
        ],
        string="Amount Type",
        default="note",
        required=True,
    )
    amount_fixed = fields.Float(string="Fixed Amount")
    python_expression = fields.Text(
        string="Python Expression Placeholder",
        help=(
            "This module stores formulas as developer scaffolding only. "
            "No payroll engine evaluates them yet."
        ),
    )
    appears_on_payslip = fields.Boolean(string="Show on Payslip", default=True)
    note = fields.Text(string="Developer Note")

    _sql_constraints = [
        (
            "rule_code_structure_unique",
            "unique(code, structure_id)",
            "Payroll rule code must be unique within its structure.",
        ),
    ]
