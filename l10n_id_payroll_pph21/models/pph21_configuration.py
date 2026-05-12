from odoo import api, fields, models
from odoo.exceptions import ValidationError


class L10nIdPPh21TerBracket(models.Model):
    _name = "l10n_id.pph21.ter.bracket"
    _description = "Indonesian PPh21 TER Placeholder Bracket"
    _order = "sequence, income_from, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one("res.company", string="Company")
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    effective_date_from = fields.Date(string="Effective From", default=fields.Date.context_today)
    effective_date_to = fields.Date(string="Effective To")
    income_from = fields.Monetary(string="Monthly Income From", required=True)
    income_to = fields.Monetary(string="Monthly Income To")
    placeholder_rate = fields.Float(
        string="Placeholder Rate (%)",
        digits=(16, 4),
        required=True,
        help="Illustrative percentage only. Replace with a validated TER table later.",
    )
    note = fields.Text(
        string="Developer Note",
        help="Document statutory source references or future replacement notes here.",
    )

    @api.constrains("income_from", "income_to", "effective_date_from", "effective_date_to")
    def _check_placeholder_ranges(self):
        for record in self:
            if record.income_to and record.income_to < record.income_from:
                raise ValidationError("Monthly Income To must be greater than or equal to Monthly Income From.")
            if (
                record.effective_date_to
                and record.effective_date_from
                and record.effective_date_to < record.effective_date_from
            ):
                raise ValidationError("Effective To date must not be earlier than Effective From date.")

    def _l10n_id_matches_income(self, amount):
        self.ensure_one()
        return amount >= self.income_from and (not self.income_to or amount <= self.income_to)

    @api.model
    def _l10n_id_get_placeholder_brackets(self, company=None, on_date=None):
        domain = [("active", "=", True)]
        if company:
            domain.extend(["|", ("company_id", "=", False), ("company_id", "=", company.id)])
        if on_date:
            domain.extend(
                [
                    ("effective_date_from", "<=", on_date),
                    "|",
                    ("effective_date_to", "=", False),
                    ("effective_date_to", ">=", on_date),
                ]
            )
        return self.search(domain, order="sequence, income_from, id")

    @api.model
    def _l10n_id_find_placeholder_bracket(self, income_amount, company=None, on_date=None):
        for bracket in self._l10n_id_get_placeholder_brackets(company=company, on_date=on_date):
            if bracket._l10n_id_matches_income(income_amount):
                return bracket
        return self.browse()


class L10nIdPPh21ProgressiveBracket(models.Model):
    _name = "l10n_id.pph21.progressive.bracket"
    _description = "Indonesian PPh21 Progressive Placeholder Bracket"
    _order = "sequence, annual_income_from, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one("res.company", string="Company")
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    effective_date_from = fields.Date(string="Effective From", default=fields.Date.context_today)
    effective_date_to = fields.Date(string="Effective To")
    annual_income_from = fields.Monetary(string="Annual Income From", required=True)
    annual_income_to = fields.Monetary(string="Annual Income To")
    placeholder_rate = fields.Float(
        string="Placeholder Rate (%)",
        digits=(16, 4),
        required=True,
        help="Illustrative percentage only. Replace with a validated annual reconciliation table later.",
    )
    note = fields.Text(
        string="Developer Note",
        help="Document statutory source references or future replacement notes here.",
    )

    @api.constrains(
        "annual_income_from",
        "annual_income_to",
        "effective_date_from",
        "effective_date_to",
    )
    def _check_placeholder_ranges(self):
        for record in self:
            if record.annual_income_to and record.annual_income_to < record.annual_income_from:
                raise ValidationError("Annual Income To must be greater than or equal to Annual Income From.")
            if (
                record.effective_date_to
                and record.effective_date_from
                and record.effective_date_to < record.effective_date_from
            ):
                raise ValidationError("Effective To date must not be earlier than Effective From date.")

    @api.model
    def _l10n_id_get_placeholder_brackets(self, company=None, on_date=None):
        domain = [("active", "=", True)]
        if company:
            domain.extend(["|", ("company_id", "=", False), ("company_id", "=", company.id)])
        if on_date:
            domain.extend(
                [
                    ("effective_date_from", "<=", on_date),
                    "|",
                    ("effective_date_to", "=", False),
                    ("effective_date_to", ">=", on_date),
                ]
            )
        return self.search(domain, order="sequence, annual_income_from, id")
