# l10n_id_payroll_pph21

`l10n_id_payroll_pph21` is an **Odoo 19 Enterprise** payroll extension focused only on Indonesian **PPh21**.

## Scope

This addon extends the built-in Enterprise payroll flow instead of creating a standalone payroll engine. The first scaffold focuses on:

- employee-level PPh21 identity and default method fields
- contract-level PPh21 method, taxable input placeholders, and manual override fields
- payslip helper fields/methods to surface placeholder PPh21 output
- placeholder configuration models for:
  - `TER Placeholder`
  - `Progressive Annual Reconciliation Placeholder`

## Dependencies (Odoo 19 Enterprise)

- `hr` — base HR module
- `hr_payroll` — Enterprise payroll engine (provides `hr.payslip`, `hr.salary.rule`, etc.)
- `hr_contract_salary` — Enterprise salary-package/contract extension (provides the
  `hr.contract` model and its primary form view in Odoo 19 Enterprise)

> **Compatibility note**: In Odoo 19 Enterprise the standalone `hr_contract` community
> module is not distributed separately. The `hr.contract` model and its base form view
> (`hr_contract_salary.hr_contract_view_form_salary`) are supplied by the
> `hr_contract_salary` Enterprise module. All references to `hr_contract.hr_contract_view_form`
> have been updated accordingly. If your distribution uses a different view ID for the
> contract form, update the `inherit_id` references in
> `views/hr_contract_views.xml` to match.

## What is implemented right now

### Employee fields

- NPWP presence flag
- NPWP number
- PPh21 tax/PTKP-related status
- dependent count
- default PPh21 method
- payroll notes

### Contract fields

- selected PPh21 method (`ter` or `progressive`)
- effective date for placeholder table matching
- additional taxable monthly input placeholder
- manual placeholder override flag/amount
- annual reconciliation flag for the progressive method
- contract notes

### Payslip integration

The addon extends `hr.payslip` with placeholder helpers and visible fields:

- monthly taxable basis
- placeholder rate
- placeholder PPh21 amount
- text breakdown explaining the calculation source
- salary rule hook methods:
  - `payslip._l10n_id_get_pph21_salary_rule_vals()`
  - `payslip._l10n_id_get_pph21_salary_rule_amount()`

These helpers are designed so a future salary rule can reuse the placeholder output without duplicating logic.

## Setup flow

1. Put the addon on the Odoo addons path.
2. Update the app list.
3. Install **Indonesia PPh21 Payroll Extension**.
4. Open an employee and fill the **Indonesian PPh21** tab:
   - Has NPWP
   - NPWP Number
   - PPh21 Tax Status
   - Dependent Count
   - Default PPh21 Method
5. Open the employee contract and fill the **Indonesian PPh21** tab:
   - PPh21 Method
   - PPh21 Effective Date
   - Additional Taxable Input (optional)
   - Manual override flag/amount if you need a temporary amount override
6. Review placeholder configuration under **Employees > Indonesian PPh21**:
   - TER Tables
   - Progressive Brackets
7. Generate or open a payslip and inspect the **Indonesian PPh21** tab to see:
   - method used
   - taxable basis
   - placeholder rate
   - placeholder amount
   - breakdown and salary-rule hook reference

## Placeholder method behavior

### `ter`

The payslip helper searches the `l10n_id.pph21.ter.bracket` placeholder table for a matching monthly taxable basis, then computes:

- `monthly taxable basis x placeholder rate`

### `progressive`

The payslip helper annualizes the monthly taxable basis, applies the progressive placeholder brackets, and then converts the annual placeholder result back to a monthly amount for display.

## Known limitations

- This is **not** a legally final/statutory Indonesian PPh21 implementation yet.
- The shipped TER and progressive tables are **sample placeholders only**.
- The addon does **not** create a final official salary rule or legal reporting output yet.
- PTKP reductions, tax gross-up/net variants, NPWP penalties, benefits-in-kind treatment, and other statutory edge cases still need to be implemented.
- Full validation requires running inside an Odoo 19 Enterprise environment with `hr_payroll` available.

## Recommended next steps

1. Replace placeholder TER and progressive records with validated tax-year-specific tables.
2. Add a proper salary rule record once the exact Enterprise payroll structure assumptions are confirmed.
3. Implement statutory taxable base composition, PTKP handling, and annual reconciliation logic.
4. Add Odoo test coverage in an environment where Enterprise payroll modules are available.
