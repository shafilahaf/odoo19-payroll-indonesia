{
    "name": "Indonesia Payroll Foundation",
    "summary": "Initial Odoo 19 Community foundation for Indonesian payroll localization",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Payroll",
    "author": "shafilahaf",
    "website": "https://github.com/shafilahaf/odoo19-payroll-indonesia",
    "license": "LGPL-3",
    "depends": ["hr", "hr_contract_salary"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_employee_views.xml",
        "views/hr_contract_views.xml",
        "views/payroll_localization_views.xml",
        "data/payroll_structure_data.xml",
    ],
    "installable": True,
    "application": False,
}
