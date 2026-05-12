from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    l10n_id_nik = fields.Char(string="Indonesian NIK")
    l10n_id_npwp = fields.Char(string="NPWP Number")
    l10n_id_npwp_name = fields.Char(string="Registered NPWP Name")
    l10n_id_ptkp_status = fields.Selection(
        selection=[
            ("TK0", "TK/0"),
            ("TK1", "TK/1"),
            ("TK2", "TK/2"),
            ("TK3", "TK/3"),
            ("K0", "K/0"),
            ("K1", "K/1"),
            ("K2", "K/2"),
            ("K3", "K/3"),
        ],
        string="PTKP Status",
        default="TK0",
        help="Tax family status used as a starting point for PTKP configuration.",
    )
    l10n_id_tax_method = fields.Selection(
        selection=[
            ("gross", "Gross"),
            ("gross_up", "Gross Up"),
            ("net", "Net"),
        ],
        string="Income Tax Method",
        default="gross",
        help="Commercial tax treatment placeholder for future payroll computation logic.",
    )
    l10n_id_bpjs_kesehatan = fields.Boolean(string="BPJS Kesehatan Participant", default=True)
    l10n_id_bpjs_kesehatan_no = fields.Char(string="BPJS Kesehatan Number")
    l10n_id_bpjs_ketenagakerjaan = fields.Boolean(
        string="BPJS Ketenagakerjaan Participant", default=True
    )
    l10n_id_bpjs_ketenagakerjaan_no = fields.Char(string="BPJS Ketenagakerjaan Number")
    l10n_id_bpjs_join_date = fields.Date(string="BPJS Enrollment Date")
    l10n_id_payroll_note = fields.Text(
        string="Payroll Localization Notes",
        help="Developer / payroll admin notes for cases that need manual handling.",
    )
