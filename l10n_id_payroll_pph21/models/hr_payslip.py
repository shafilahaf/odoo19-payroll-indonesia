from odoo import _, api, fields, models


class HrPayslip(models.Model):
    """Extension of hr.payslip for Indonesian PPh21 placeholder integration.

    In Odoo 19 Enterprise, the classic hr.contract model is replaced by hr.version
    (salary packages, provided by hr_contract_salary).  The exact relation between
    hr.payslip and hr.version depends on your Enterprise payroll engine version.

    This extension therefore uses employee-level PPh21 settings as the primary data
    source and provides clearly named extension hooks (_l10n_id_get_pph21_salary_version
    and _l10n_id_get_pph21_wage_base) that you can override once you have confirmed
    the hr.payslip → hr.version relation path in your environment.
    """

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

    # ------------------------------------------------------------------
    # Extension points
    # ------------------------------------------------------------------

    def _l10n_id_get_pph21_salary_version(self):
        """Return the hr.version (salary package) linked to this payslip.

        Extension point: override this method to return the correct hr.version
        record once the hr.payslip → hr.version relation path is confirmed in
        your Odoo 19 Enterprise environment.

        Possible paths to investigate:
          - self.contract_id          if payslip.contract_id → hr.version
          - self.employee_id.version_id   if employee carries a direct version link
          - Other: check hr_contract_salary_payroll source for the actual field name

        Returns an empty hr.version recordset when the relation is unknown.
        """
        self.ensure_one()
        return self.env["hr.version"].browse()

    def _l10n_id_get_pph21_wage_base(self):
        """Return the monthly wage amount to use as PPh21 taxable basis.

        Extension point: override this method to supply the correct taxable wage
        for your Odoo 19 Enterprise payroll setup.

        In a standard hr_contract_salary_payroll setup the wage may be accessible
        via the hr.version (salary package) record returned by
        _l10n_id_get_pph21_salary_version().  Once that relation is confirmed,
        adapt this method to read the wage from there.

        Currently returns 0.0 as a safe default; the placeholder PPh21 amounts
        will be 0 until this is overridden.
        """
        self.ensure_one()
        return 0.0

    # ------------------------------------------------------------------
    # Core helpers
    # ------------------------------------------------------------------

    def _l10n_id_get_pph21_base_amount(self):
        """Return total monthly taxable basis: wage base + additional taxable input.

        The additional taxable input is read from the linked hr.version salary
        package when _l10n_id_get_pph21_salary_version() returns a record.
        """
        self.ensure_one()
        wage = self._l10n_id_get_pph21_wage_base()
        additional = 0.0
        salary_version = self._l10n_id_get_pph21_salary_version()
        if salary_version:
            additional = salary_version.l10n_id_pph21_additional_taxable_amount or 0.0
        return wage + additional

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
        employee = self.employee_id
        company = self.company_id
        salary_version = self._l10n_id_get_pph21_salary_version()

        # PPh21 method: prefer salary package override, fall back to employee default.
        method = (
            (salary_version and salary_version.l10n_id_pph21_method)
            or employee.l10n_id_pph21_method
            or "ter"
        )
        # Effective date: prefer salary package, fall back to payslip end date.
        effective_date = (
            (salary_version and salary_version.l10n_id_pph21_effective_date)
            or self.date_to
            or fields.Date.context_today(self)
        )

        monthly_taxable_amount = self._l10n_id_get_pph21_base_amount()
        placeholder_rate = 0.0
        amount = 0.0
        source = _("No placeholder table matched.")

        # Manual override on salary package takes highest priority.
        if salary_version and salary_version.l10n_id_pph21_override_active:
            amount = salary_version.l10n_id_pph21_override_amount or 0.0
            source = _("Manual salary package override")
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
        "date_to",
    )
    def _compute_l10n_id_pph21_placeholder(self):
        for payslip in self:
            if not payslip.employee_id:
                payslip.l10n_id_pph21_method = False
                payslip.l10n_id_pph21_monthly_taxable_income = 0.0
                payslip.l10n_id_pph21_placeholder_rate = 0.0
                payslip.l10n_id_pph21_amount = 0.0
                payslip.l10n_id_pph21_rule_code = "PPH21"
                payslip.l10n_id_pph21_breakdown = _("No employee linked to this payslip.")
                continue
            values = payslip._l10n_id_get_pph21_placeholder_values()
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

