from odoo import fields, models


class AccountForeignExchangeRate(models.Model):
    _name = "account.foreign.exchange.rate"
    _description = "Taxas de Câmbio entre Moedas"
    
    date = fields.Date(
        string="Data da taxa de câmbio",
    )
    
    currency_from_id = fields.Many2one(
        string="Moeda de origem",
        comodel_name="res.currency",
    )
    
    currency_to_id = fields.Many2one(
        string="Moeda de destino",
        comodel_name="res.currency",
    )
    
    exchange_rate = fields.Float(
        string="Taxa de câmbio",
    )
