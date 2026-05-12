{
    "name": "Indonesia PPh21 Payroll Extension",
    "summary": "Odoo 19 Enterprise payroll extension scaffold for Indonesian PPh21",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Payroll",
    "author": "shafilahaf",
    "website": "https://github.com/shafilahaf/odoo19-payroll-indonesia",
    "license": "LGPL-3",
    # hr_contract (community) is not distributed in Odoo 19 Enterprise.
    # hr_contract_salary provides hr.version (Contract Templates / Salary Packages).
    # hr_contract_salary_payroll bridges salary packages with the Enterprise payroll engine.
    # Do NOT add hr_payroll directly: it depends on hr_contract which is unavailable.
    "depends": [
        "hr",
        "hr_contract_salary",
        "hr_contract_salary_payroll",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/pph21_placeholder_data.xml",
        "views/hr_employee_views.xml",
        "views/hr_version_views.xml",
        "views/hr_payslip_views.xml",
        "views/pph21_configuration_views.xml",
    ],
    "installable": True,
    "application": False,
}
