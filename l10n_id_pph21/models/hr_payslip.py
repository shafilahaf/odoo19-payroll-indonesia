from odoo import models, fields, api
from datetime import date


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    pph21_method_used = fields.Selection([
        ('ter', 'TER (Monthly Effective Rate)'),
        ('progressive', 'Progressive (Annual Settlement)'),
    ], string='PPh 21 Method Used', readonly=True, copy=False,
       help='Method used for this payslip PPh 21 calculation')
    pph21_is_final_period = fields.Boolean(
        string='Final Tax Period',
        compute='_compute_pph21_is_final_period', store=True,
        help='True if this is December or resignation month (uses progressive calculation)')
    pph21_gross_annual = fields.Float(string='Gross Annual (Calculated)', readonly=True, copy=False)
    pph21_tax_amount = fields.Float(string='PPh 21 Amount', readonly=True, copy=False)
    pph21_ter_rate_applied = fields.Float(string='TER Rate Applied (%)', readonly=True, copy=False)
    pph21_config_source = fields.Selection([
        ('employee', 'Employee'),
        ('contract', 'Contract'),
    ], string='PPh 21 Config Source', readonly=True, copy=False,
       help='Where the PPh 21 configuration was read from for this payslip.')

    @api.depends('date_from', 'date_to', 'employee_id', 'employee_id.pph21_resign_date')
    def _compute_pph21_is_final_period(self):
        for payslip in self:
            is_final = False
            if payslip.date_from:
                # December is always final period
                if payslip.date_from.month == 12:
                    is_final = True
                # Resignation month is final period
                elif (payslip.employee_id and payslip.employee_id.pph21_resign_date
                      and payslip.date_from <= payslip.employee_id.pph21_resign_date <= (payslip.date_to or payslip.date_from)):
                    is_final = True
            payslip.pph21_is_final_period = is_final

    # ------------------------------------------------------------------
    # PPh 21 configuration resolution (contract overrides employee)
    # ------------------------------------------------------------------
    def _get_pph21_config(self):
        """Resolve the PPh 21 configuration for this payslip.

        Priority:
        1. If the contract (hr.version) on this payslip has
           `pph21_use_contract_config` enabled -> use contract values.
        2. Otherwise fall back to employee-level fields.

        Returns a dict with keys:
            ptkp_id, ter_category_id, calculation_method,
            employment_type, has_npwp, npwp, source
        """
        self.ensure_one()
        if self.version_id:
            return self.version_id._get_pph21_config()

        # Last-resort fallback if no contract (unlikely)
        employee = self.employee_id
        return {
            'ptkp_id': employee.pph21_ptkp_id,
            'ter_category_id': employee.pph21_ter_category_id,
            'calculation_method': employee.pph21_calculation_method,
            'employment_type': employee.pph21_employment_type,
            'has_npwp': employee.pph21_has_npwp,
            'npwp': employee.pph21_npwp,
            'source': 'employee',
        }

    def _get_pph21_monthly_gross(self):
        """Get the monthly gross income for PPh 21 calculation.

        Priority:
        1. If GROSS category line exists in computed lines -> use it
        2. Sum BASIC + ALW lines if they exist
        3. Fall back to contract.wage (when called during compute, lines
           may not be persisted yet)
        """
        self.ensure_one()
        gross_line_total = 0.0
        basic_alw_total = 0.0
        has_gross = False
        has_basic_alw = False
        for line in self.line_ids:
            code = line.category_id.code if line.category_id else ''
            if code == 'GROSS':
                gross_line_total += line.total
                has_gross = True
            elif code in ('BASIC', 'ALW'):
                basic_alw_total += line.total
                has_basic_alw = True

        if has_gross:
            return gross_line_total
        if has_basic_alw:
            return basic_alw_total
        # Fallback to contract wage when lines not yet computed
        if self.version_id:
            return self.version_id.wage
        return 0.0

    def _get_pph21_previous_payslips(self):
        """Find previous payslips in the same tax year.
        Accepts any state except draft/cancel (covers Odoo versions with
        different state names: verify, done, validated, paid, etc.)
        """
        self.ensure_one()
        employee = self.employee_id
        year = self.date_from.year

        return self.search([
            ('employee_id', '=', employee.id),
            ('date_from', '>=', date(year, 1, 1)),
            ('date_from', '<', self.date_from),
            ('state', 'not in', ['draft', 'cancel']),
            ('id', '!=', self.id),
        ])

    def _get_pph21_annual_gross(self, current_month_gross=0):
        """Calculate annualized gross income across the current tax year."""
        self.ensure_one()
        prev_payslips = self._get_pph21_previous_payslips()

        annual_gross = current_month_gross
        for slip in prev_payslips:
            annual_gross += slip._get_pph21_monthly_gross()

        return annual_gross

    def _get_pph21_total_ter_paid(self):
        """Get total PPh 21 already paid in previous months of same year."""
        self.ensure_one()
        prev_payslips = self._get_pph21_previous_payslips()
        return sum(slip.pph21_tax_amount for slip in prev_payslips)

    def _get_working_months_in_year(self):
        """Get number of working months in the year for this employee."""
        self.ensure_one()
        employee = self.employee_id
        year = self.date_from.year

        start_month = 1
        if employee.pph21_join_date and employee.pph21_join_date.year == year:
            start_month = employee.pph21_join_date.month

        end_month = self.date_from.month
        if employee.pph21_resign_date and employee.pph21_resign_date.year == year:
            end_month = min(end_month, employee.pph21_resign_date.month)

        return max(1, end_month - start_month + 1)

    # ------------------------------------------------------------------
    # Core PPh 21 calculation methods
    # ------------------------------------------------------------------
    def calculate_pph21_ter(self, gross_monthly, config=None):
        """Calculate PPh 21 using TER method (Jan-Nov regular months).

        Formula: PPh 21 = Gross Monthly x TER Rate

        Returns:
            tuple: (tax_amount, ter_rate_applied)
        """
        self.ensure_one()
        if config is None:
            config = self._get_pph21_config()

        ter_category = config['ter_category_id']
        if not ter_category:
            return 0.0, 0.0

        ter_rate = self.env['pph21.ter.rate'].get_ter_rate(
            ter_category.code, gross_monthly, company=self.company_id)

        tax_amount = gross_monthly * (ter_rate / 100)

        if config['has_npwp'] is False:
            tax_amount *= 1.2

        return tax_amount, ter_rate

    def calculate_pph21_progressive_outsource(self, gross_monthly, config=None):
        """Calculate PPh 21 for outsource: annualized progressive divided by 12."""
        self.ensure_one()
        if config is None:
            config = self._get_pph21_config()

        annual_gross = gross_monthly * 12
        biaya_jabatan = min(annual_gross * 0.05, 6000000)
        net_annual = annual_gross - biaya_jabatan

        ptkp = config['ptkp_id']
        ptkp_annual = ptkp.annual_amount if ptkp else 0.0

        pkp = max(0, net_annual - ptkp_annual)
        annual_tax = self.env['pph21.progressive.rate'].calculate_progressive_tax(
            pkp, company=self.company_id)

        monthly_tax = annual_tax / 12

        if config['has_npwp'] is False:
            monthly_tax *= 1.2

        return monthly_tax

    def _calculate_progressive_with_annual(self, gross_monthly, config=None):
        """Helper returning (tax, annual_gross) for progressive settlement calc."""
        self.ensure_one()
        if config is None:
            config = self._get_pph21_config()

        annual_gross = self._get_pph21_annual_gross(gross_monthly)
        working_months = self._get_working_months_in_year()

        max_biaya_jabatan = min(6000000, working_months * 500000)
        biaya_jabatan = min(annual_gross * 0.05, max_biaya_jabatan)

        max_iuran_pensiun = working_months * 200000
        iuran_pensiun = min(annual_gross * 0.01, max_iuran_pensiun)

        net_annual = annual_gross - biaya_jabatan - iuran_pensiun

        ptkp = config['ptkp_id']
        ptkp_annual = ptkp.annual_amount if ptkp else 0.0

        pkp = max(0, net_annual - ptkp_annual)
        annual_tax = self.env['pph21.progressive.rate'].calculate_progressive_tax(
            pkp, company=self.company_id)

        if config['has_npwp'] is False:
            annual_tax *= 1.2

        total_paid = self._get_pph21_total_ter_paid()
        tax_this_month = max(0, annual_tax - total_paid)

        return tax_this_month, annual_gross

    def compute_pph21(self):
        """Main entry point to compute PPh 21. Call from salary rule Python code.

        Returns:
            float: PPh 21 tax amount (positive value, should be deducted).
        """
        self.ensure_one()
        config = self._get_pph21_config()
        gross_monthly = self._get_pph21_monthly_gross()

        values = {
            'pph21_tax_amount': 0.0,
            'pph21_method_used': False,
            'pph21_ter_rate_applied': 0.0,
            'pph21_gross_annual': 0.0,
            'pph21_config_source': config.get('source'),
        }

        if gross_monthly <= 0:
            self._write_pph21_values(values)
            return 0.0

        tax_amount = 0.0
        method_used = 'ter'
        ter_rate_applied = 0.0
        gross_annual = 0.0

        if config['employment_type'] == 'outsource':
            tax_amount = self.calculate_pph21_progressive_outsource(gross_monthly, config)
            method_used = 'progressive'
            gross_annual = gross_monthly * 12
        elif config['calculation_method'] == 'progressive' or self.pph21_is_final_period:
            tax_amount, gross_annual = self._calculate_progressive_with_annual(gross_monthly, config)
            method_used = 'progressive'
        else:
            tax_amount, ter_rate_applied = self.calculate_pph21_ter(gross_monthly, config)
            method_used = 'ter'

        values.update({
            'pph21_tax_amount': tax_amount,
            'pph21_method_used': method_used,
            'pph21_ter_rate_applied': ter_rate_applied,
            'pph21_gross_annual': gross_annual,
        })
        self._write_pph21_values(values)
        return tax_amount

    def _write_pph21_values(self, values):
        """Persist PPh 21 calculation results to the payslip."""
        self.ensure_one()
        try:
            self.sudo().write(values)
        except Exception:
            # Silently fail to avoid breaking payslip computation
            pass
