from odoo import fields, models, api
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"
    
    currency_id = fields.Many2one(
        string="Moeda",
        comodel_name="res.currency",
    )
    
    @api.onchange("currency_id")
    def onchange_currency_id(self):
        if self.currency_id.id != self.env.company.currency_id.id:
            foreign_exchange = self.env["account.foreign.exchange.rate"].search([
                ("currency_from_id", "=", self.currency_id.id), 
                ("currency_to_id", "=", self.env.company.currency_id.id),
                ("date", "<=", self.date),
            ], order="date desc", limit=1)
            
            if not foreign_exchange:
                raise UserError("Não foi encontrada uma taxa de câmbio para a data informada.")
            
            self.transaction_value = self.transaction_value * foreign_exchange.exchange_rate
