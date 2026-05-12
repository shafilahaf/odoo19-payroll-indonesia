{
    'name': 'Indonesia PPh 21 - TER & Progressive',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'PPh 21 Calculation with TER (Tarif Efektif Rata-rata) and Progressive Tax Rates for Indonesia',
    'description': """
Indonesia PPh 21 Tax Calculation Module
========================================

This module provides:
- Master data for TER (Tarif Efektif Rata-rata) rates based on PP 58/2023 & PMK 168/2023
- Progressive tax rate tables (Pasal 17 UU HPP)
- PTKP (Penghasilan Tidak Kena Pajak) configuration
- Automatic PPh 21 calculation on payslips:
  * TER method for January - November (regular months)
  * Progressive method for December or resignation month (final tax settlement)
- Support for different employee types (permanent, contract, outsource)
- Biaya Jabatan (position cost) deduction

References:
- PP 58 Tahun 2023
- PMK 168 Tahun 2023
- UU HPP (Harmonisasi Peraturan Perpajakan)
    """,
    'author': 'Shafil Ahaf',
    'website': 'https://github.com/shafilahaf/odoo19-payroll-indonesia',
    'license': 'LGPL-3',
    'depends': [
        'hr_payroll',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/pph21_ter_category_data.xml',
        'data/pph21_ter_rate_data.xml',
        'data/pph21_progressive_rate_data.xml',
        'data/pph21_ptkp_data.xml',
        'views/pph21_ptkp_views.xml',
        'views/pph21_ter_category_views.xml',
        'views/pph21_ter_rate_views.xml',
        'views/pph21_progressive_rate_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_payslip_views.xml',
        'views/pph21_menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
