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

    def _get_pph21_monthly_gross(self):
        """Get the monthly gross income for PPh 21 calculation.
        Override this method to customize which salary components are included.
        """
        self.ensure_one()
        gross = 0.0
        for line in self.line_ids:
            if line.category_id.code in ('BASIC', 'ALW', 'GROSS'):
                gross += line.total
        return gross

    def _get_pph21_annual_gross(self, current_month_gross=0):
        """Calculate annualized gross income.
        For final period calculation, we need all months in the year.
        """
        self.ensure_one()
        employee = self.employee_id
        year = self.date_from.year

        # Get all payslips for the same employee in the same year, excluding current
        prev_payslips = self.search([
            ('employee_id', '=', employee.id),
            ('date_from', '>=', date(year, 1, 1)),
            ('date_from', '<', self.date_from),
            ('state', 'in', ['done', 'paid']),
            ('id', '!=', self.id),
        ])

        annual_gross = current_month_gross
        for slip in prev_payslips:
            annual_gross += slip._get_pph21_monthly_gross()

        return annual_gross

    def _get_pph21_total_ter_paid(self):
        """Get total PPh 21 already paid via TER in previous months of same year."""
        self.ensure_one()
        employee = self.employee_id
        year = self.date_from.year

        prev_payslips = self.search([
            ('employee_id', '=', employee.id),
            ('date_from', '>=', date(year, 1, 1)),
            ('date_from', '<', self.date_from),
            ('state', 'in', ['done', 'paid']),
            ('id', '!=', self.id),
        ])

        total_paid = sum(slip.pph21_tax_amount for slip in prev_payslips)
        return total_paid

    def _get_working_months_in_year(self):
        """Get number of working months in the year for this employee."""
        self.ensure_one()
        employee = self.employee_id
        year = self.date_from.year
        
        # Determine start month
        start_month = 1
        if employee.pph21_join_date and employee.pph21_join_date.year == year:
            start_month = employee.pph21_join_date.month
        
        # Determine end month
        end_month = self.date_from.month
        if employee.pph21_resign_date and employee.pph21_resign_date.year == year:
            end_month = min(end_month, employee.pph21_resign_date.month)
        
        return max(1, end_month - start_month + 1)

    def calculate_pph21_ter(self, gross_monthly):
        """Calculate PPh 21 using TER method (Jan-Nov for permanent employees).
        
        Formula: PPh 21 = Gross Monthly x TER Rate
        
        Args:
            gross_monthly: Monthly gross income
            
        Returns:
            tuple: (tax_amount, ter_rate_applied)
        """
        self.ensure_one()
        employee = self.employee_id

        if not employee.pph21_ter_category_id:
            return 0.0, 0.0

        category_code = employee.pph21_ter_category_id.code
        ter_rate = self.env['pph21.ter.rate'].get_ter_rate(
            category_code, gross_monthly, company=self.company_id)

        tax_amount = gross_monthly * (ter_rate / 100)

        # If employee doesn't have NPWP, increase by 20%
        if employee.pph21_has_npwp is False:
            tax_amount *= 1.2

        return tax_amount, ter_rate

    def calculate_pph21_progressive(self, gross_monthly):
        """Calculate PPh 21 using progressive method (Dec/resign or outsource).
        
        Steps:
        1. Calculate annual gross income
        2. Deduct biaya jabatan (5% of gross, max 6M/year)
        3. Deduct iuran pensiun (if applicable)
        4. Deduct PTKP
        5. Calculate PKP
        6. Apply progressive rates
        7. Subtract PPh 21 already paid (TER) in previous months
        
        Args:
            gross_monthly: Current month's gross income
            
        Returns:
            float: Tax amount for this month
        """
        self.ensure_one()
        employee = self.employee_id

        # Step 1: Calculate annual gross
        annual_gross = self._get_pph21_annual_gross(gross_monthly)

        # Step 2: Biaya Jabatan (5% of gross, max Rp 500,000/month or Rp 6,000,000/year)
        working_months = self._get_working_months_in_year()
        max_biaya_jabatan = min(6000000, working_months * 500000)
        biaya_jabatan = min(annual_gross * 0.05, max_biaya_jabatan)

        # Step 3: Iuran pensiun (standard deduction, can be customized)
        # Standard: max Rp 200,000/month
        max_iuran_pensiun = working_months * 200000
        iuran_pensiun = min(annual_gross * 0.01, max_iuran_pensiun)  # 1% or max

        # Step 4: Net annual income
        net_annual = annual_gross - biaya_jabatan - iuran_pensiun

        # Step 5: PTKP deduction
        ptkp_annual = 0.0
        if employee.pph21_ptkp_id:
            ptkp_annual = employee.pph21_ptkp_id.annual_amount

        # Step 6: PKP (Penghasilan Kena Pajak)
        pkp = max(0, net_annual - ptkp_annual)

        # Step 7: Apply progressive tax rates
        annual_tax = self.env['pph21.progressive.rate'].calculate_progressive_tax(
            pkp, company=self.company_id)

        # If employee doesn't have NPWP, increase by 20%
        if employee.pph21_has_npwp is False:
            annual_tax *= 1.2

        # Step 8: Subtract PPh 21 already paid in previous months
        total_paid = self._get_pph21_total_ter_paid()
        tax_this_month = max(0, annual_tax - total_paid)

        # Store calculated values
        self.pph21_gross_annual = annual_gross

        return tax_this_month

    def calculate_pph21_progressive_outsource(self, gross_monthly):
        """Calculate PPh 21 for outsource employees using progressive rates monthly.
        
        For outsource, the tax is calculated per month using progressive rates
        applied to monthly PKP (annualized then divided back).
        
        Args:
            gross_monthly: Monthly gross income
            
        Returns:
            float: Tax amount for this month
        """
        self.ensure_one()
        employee = self.employee_id

        # Annualize monthly income
        annual_gross = gross_monthly * 12

        # Biaya Jabatan: 5% of gross, max 6M/year
        biaya_jabatan = min(annual_gross * 0.05, 6000000)

        # Net annual
        net_annual = annual_gross - biaya_jabatan

        # PTKP
        ptkp_annual = 0.0
        if employee.pph21_ptkp_id:
            ptkp_annual = employee.pph21_ptkp_id.annual_amount

        # PKP
        pkp = max(0, net_annual - ptkp_annual)

        # Progressive tax on annual
        annual_tax = self.env['pph21.progressive.rate'].calculate_progressive_tax(
            pkp, company=self.company_id)

        # Monthly tax = annual / 12
        monthly_tax = annual_tax / 12

        # If employee doesn't have NPWP, increase by 20%
        if employee.pph21_has_npwp is False:
            monthly_tax *= 1.2

        return monthly_tax

    def compute_pph21(self):
        """Main method to compute PPh 21 for the payslip.
        Call this from salary rule Python code.
        
        Returns:
            float: PPh 21 tax amount (positive value, should be deducted)
        """
        self.ensure_one()
        employee = self.employee_id
        gross_monthly = self._get_pph21_monthly_gross()

        if gross_monthly <= 0:
            self.pph21_tax_amount = 0
            self.pph21_method_used = False
            return 0.0

        tax_amount = 0.0
        method_used = 'ter'

        if employee.pph21_employment_type == 'outsource':
            # Outsource always uses progressive
            tax_amount = self.calculate_pph21_progressive_outsource(gross_monthly)
            method_used = 'progressive'
        elif employee.pph21_calculation_method == 'progressive':
            # Employee configured to always use progressive
            tax_amount = self.calculate_pph21_progressive(gross_monthly)
            method_used = 'progressive'
        elif self.pph21_is_final_period:
            # December or resignation month - use progressive for settlement
            tax_amount = self.calculate_pph21_progressive(gross_monthly)
            method_used = 'progressive'
        else:
            # Regular month (Jan-Nov) - use TER
            tax_amount, ter_rate = self.calculate_pph21_ter(gross_monthly)
            self.pph21_ter_rate_applied = ter_rate
            method_used = 'ter'

        self.pph21_tax_amount = tax_amount
        self.pph21_method_used = method_used
        return tax_amount
