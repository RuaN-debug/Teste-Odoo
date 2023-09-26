from odoo import models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        
        invoice_integration = self.env["account.invoice.integration"].create({
            "invoice_id": res.id,
            "status": "pending",
        })
        
        invoice_integration.send_invoice_to_api()

        return res
    