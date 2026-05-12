from odoo import _, api, fields, models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    l10n_id_pph21_method = fields.Selection(
        selection=[
            ("ter", "TER Placeholder"),
            ("progressive", "Progressive Annual Reconciliation Placeholder"),
        ],
        string="PPh21 Method",
        compute="_compute_l10n_id_pph21_placeholder",
    )
    l10n_id_pph21_tax_status = fields.Selection(
        related="employee_id.l10n_id_pph21_tax_status",
        string="PPh21 Tax Status",
        readonly=True,
    )
    l10n_id_pph21_monthly_taxable_income = fields.Monetary(
        string="Monthly Taxable Basis",
        compute="_compute_l10n_id_pph21_placeholder",
    )
    l10n_id_pph21_placeholder_rate = fields.Float(
        string="Placeholder Rate (%)",
        digits=(16, 4),
        compute="_compute_l10n_id_pph21_placeholder",
    )
    l10n_id_pph21_amount = fields.Monetary(
        string="PPh21 Placeholder Amount",
        compute="_compute_l10n_id_pph21_placeholder",
    )
    l10n_id_pph21_rule_code = fields.Char(
        string="Salary Rule Hook Code",
        compute="_compute_l10n_id_pph21_placeholder",
    )
    l10n_id_pph21_breakdown = fields.Text(
        string="PPh21 Placeholder Breakdown",
        compute="_compute_l10n_id_pph21_placeholder",
    )

    def _l10n_id_get_pph21_base_amount(self):
        self.ensure_one()
        contract = self.contract_id
        return (contract.wage or 0.0) + (contract.l10n_id_pph21_additional_taxable_amount or 0.0)

    def _l10n_id_compute_progressive_placeholder_tax(self, annual_taxable_amount, brackets):
        self.ensure_one()
        annual_tax = 0.0
        for bracket in brackets:
            upper_bound = bracket.annual_income_to or annual_taxable_amount
            taxable_slice = max(min(annual_taxable_amount, upper_bound) - bracket.annual_income_from, 0.0)
            if taxable_slice:
                annual_tax += taxable_slice * bracket.placeholder_rate / 100.0
        return annual_tax

    def _l10n_id_get_pph21_placeholder_values(self):
        self.ensure_one()
        contract = self.contract_id
        employee = self.employee_id
        company = self.company_id
        effective_date = contract.l10n_id_pph21_effective_date or self.date_to or fields.Date.context_today(self)
        method = contract.l10n_id_pph21_method or employee.l10n_id_pph21_method or "ter"
        monthly_taxable_amount = self._l10n_id_get_pph21_base_amount()
        placeholder_rate = 0.0
        amount = 0.0
        source = _("No placeholder table matched.")

        if contract.l10n_id_pph21_override_active:
            amount = contract.l10n_id_pph21_override_amount or 0.0
            source = _("Manual contract override")
        elif method == "ter":
            bracket = self.env["l10n_id.pph21.ter.bracket"]._l10n_id_find_placeholder_bracket(
                monthly_taxable_amount,
                company=company,
                on_date=effective_date,
            )
            if bracket:
                placeholder_rate = bracket.placeholder_rate
                amount = monthly_taxable_amount * placeholder_rate / 100.0
                source = bracket.name
        else:
            brackets = self.env["l10n_id.pph21.progressive.bracket"]._l10n_id_get_placeholder_brackets(
                company=company,
                on_date=effective_date,
            )
            annual_taxable_amount = monthly_taxable_amount * 12.0
            annual_tax = self._l10n_id_compute_progressive_placeholder_tax(annual_taxable_amount, brackets)
            amount = annual_tax / 12.0 if annual_taxable_amount else 0.0
            placeholder_rate = (annual_tax / annual_taxable_amount * 100.0) if annual_taxable_amount else 0.0
            if brackets:
                source = _("Progressive placeholder brackets")

        breakdown = _(
            "Placeholder only.\n"
            "Method: %(method)s\n"
            "Monthly taxable basis: %(monthly_taxable).2f\n"
            "Placeholder rate: %(rate).4f%%\n"
            "Estimated payslip deduction: %(amount).2f\n"
            "Source: %(source)s\n"
            "Salary rule hook: payslip._l10n_id_get_pph21_salary_rule_vals()"
        ) % {
            "method": dict(self._fields["l10n_id_pph21_method"].selection).get(method, method),
            "monthly_taxable": monthly_taxable_amount,
            "rate": placeholder_rate,
            "amount": amount,
            "source": source,
        }

        return {
            "method": method,
            "monthly_taxable_amount": monthly_taxable_amount,
            "placeholder_rate": placeholder_rate,
            "amount": amount,
            "source": source,
            "breakdown": breakdown,
            "rule_code": "PPH21",
        }

    @api.depends(
        "employee_id",
        "employee_id.l10n_id_pph21_method",
        "employee_id.l10n_id_pph21_tax_status",
        "contract_id",
        "contract_id.wage",
        "contract_id.l10n_id_pph21_method",
        "contract_id.l10n_id_pph21_effective_date",
        "contract_id.l10n_id_pph21_additional_taxable_amount",
        "contract_id.l10n_id_pph21_override_active",
        "contract_id.l10n_id_pph21_override_amount",
        "date_to",
    )
    def _compute_l10n_id_pph21_placeholder(self):
        for payslip in self:
            values = payslip._l10n_id_get_pph21_placeholder_values() if payslip.contract_id else {
                "method": False,
                "monthly_taxable_amount": 0.0,
                "placeholder_rate": 0.0,
                "amount": 0.0,
                "source": _("No active contract linked to this payslip."),
                "breakdown": _("No active contract linked to this payslip."),
                "rule_code": "PPH21",
            }
            payslip.l10n_id_pph21_method = values["method"]
            payslip.l10n_id_pph21_monthly_taxable_income = values["monthly_taxable_amount"]
            payslip.l10n_id_pph21_placeholder_rate = values["placeholder_rate"]
            payslip.l10n_id_pph21_amount = values["amount"]
            payslip.l10n_id_pph21_rule_code = values["rule_code"]
            payslip.l10n_id_pph21_breakdown = values["breakdown"]

    def _l10n_id_get_pph21_salary_rule_vals(self):
        self.ensure_one()
        values = self._l10n_id_get_pph21_placeholder_values()
        return {
            "code": values["rule_code"],
            "name": _("PPh21 Placeholder"),
            "amount": values["amount"],
            "quantity": 1.0,
            "rate": 100.0,
            "note": values["breakdown"],
        }

    def _l10n_id_get_pph21_salary_rule_amount(self):
        self.ensure_one()
        return self._l10n_id_get_pph21_placeholder_values()["amount"]
