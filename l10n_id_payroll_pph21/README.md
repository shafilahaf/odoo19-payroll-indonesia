# l10n_id_payroll_pph21

`l10n_id_payroll_pph21` is an **Odoo 19 Enterprise** payroll extension focused only on Indonesian **PPh21**.

## Odoo 19 Enterprise — hr.version architecture

In **Odoo 19 Enterprise** the classic community `hr_contract` module and its `hr.contract`
model are **not** part of the Enterprise distribution.  Contract Templates and Salary
Packages are provided by the `hr_contract_salary` Enterprise module as the **`hr.version`**
model.

This addon extends `hr.version` (not `hr.contract`) for all contract/salary-package-level
PPh21 configuration.

## Scope

This addon extends the built-in Enterprise payroll flow instead of creating a standalone payroll engine. The first scaffold focuses on:

- employee-level PPh21 identity and default method fields
- `hr.version` (Contract Template / Salary Package) PPh21 method, taxable input placeholders, and manual override fields
- payslip helper fields/methods to surface placeholder PPh21 output
- placeholder configuration models for:
  - `TER Placeholder`
  - `Progressive Annual Reconciliation Placeholder`

## Dependencies (Odoo 19 Enterprise)

- `hr` — base HR module
- `hr_contract_salary` — Enterprise salary-package module; provides `hr.version` (Contract
  Templates / Salary Packages) and its primary form view
- `hr_contract_salary_payroll` — Enterprise bridge between salary packages and the payroll
  engine; transitively provides `hr.payslip` and related payroll infrastructure

> **Why not `hr_payroll` directly?**  In Odoo 19 Enterprise `hr_payroll` (community) depends
> on `hr_contract` which is not distributed.  Depending on `hr_contract_salary_payroll`
> instead pulls in the payroll engine without triggering the missing `hr_contract` error.

## What is implemented right now

### Employee fields

- NPWP presence flag
- NPWP number
- PPh21 tax/PTKP-related status
- dependent count
- default PPh21 method
- payroll notes

### Contract Template / Salary Package fields (`hr.version`)

- selected PPh21 method (`ter` or `progressive`)
- effective date for placeholder table matching
- additional taxable monthly input placeholder
- manual placeholder override flag/amount
- annual reconciliation flag for the progressive method
- salary-package notes

### Payslip integration

The addon extends `hr.payslip` with placeholder helpers and visible fields:

- monthly taxable basis
- placeholder rate
- placeholder PPh21 amount
- text breakdown explaining the calculation source
- salary rule hook methods:
  - `payslip._l10n_id_get_pph21_salary_rule_vals()`
  - `payslip._l10n_id_get_pph21_salary_rule_amount()`

**Primary data source:** employee-level PPh21 settings (always available).

**Extension hooks for `hr.version` integration:**
- `payslip._l10n_id_get_pph21_salary_version()` — override to return the `hr.version`
  record linked to the payslip once the relation path is confirmed in your environment.
- `payslip._l10n_id_get_pph21_wage_base()` — override to supply the taxable wage amount
  from the salary package once the above relation is in place.

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
5. Open a Contract Template (Salary Package) under **Employees > Salary Packages** and fill the **Indonesian PPh21** tab:
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

- `monthly taxable basis × placeholder rate`

### `progressive`

The payslip helper annualizes the monthly taxable basis, applies the progressive placeholder brackets, and then converts the annual placeholder result back to a monthly amount for display.

## View reference troubleshooting

### Contract Template / Salary Package (`hr.version`)

The addon inherits `hr_contract_salary.hr_version_view_form`.  If your distribution
uses a different XML ID for the `hr.version` form view, edit
`views/hr_version_views.xml` and update the `inherit_id` ref.  Common alternatives:

- `hr_contract_salary.hr_version_view_form_salary`
- `hr_contract_salary.view_hr_version_form`

### Payslip (`hr.payslip`)

The addon inherits `hr_payroll.view_hr_payslip_form`.  This XML ID is accessible when
`hr_payroll` is installed as a transitive dependency of `hr_contract_salary_payroll`.
If your distribution ships the payslip form view under a different module, edit
`views/hr_payslip_views.xml` and update the `inherit_id` ref.  Common alternatives:

- `hr_contract_salary_payroll.view_hr_payslip_form`
- `payroll.view_hr_payslip_form`

## Known limitations

- This is **not** a legally final/statutory Indonesian PPh21 implementation yet.
- The shipped TER and progressive tables are **sample placeholders only**.
- The addon does **not** create a final official salary rule or legal reporting output yet.
- The payslip taxable wage base returns **0.0** until `_l10n_id_get_pph21_wage_base()` is overridden with the correct `hr.version → hr.payslip` relation for your environment.
- PTKP reductions, tax gross-up/net variants, NPWP penalties, benefits-in-kind treatment, and other statutory edge cases still need to be implemented.
- Full validation requires running inside an Odoo 19 Enterprise environment with `hr_contract_salary_payroll` installed.

## Recommended next steps

1. Confirm the `hr.payslip → hr.version` relation path in your environment (check `hr_contract_salary_payroll` source or Odoo debug info).
2. Override `_l10n_id_get_pph21_salary_version()` and `_l10n_id_get_pph21_wage_base()` to wire up the salary package wage to the payslip computation.
3. Replace placeholder TER and progressive records with validated tax-year-specific tables.
4. Add a proper salary rule record once the exact Enterprise payroll structure assumptions are confirmed.
5. Implement statutory taxable base composition, PTKP handling, and annual reconciliation logic.
6. Add Odoo test coverage in an environment where Enterprise payroll modules are available.

