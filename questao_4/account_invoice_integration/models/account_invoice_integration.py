from odoo import fields, models, api

import requests


class AccountInvoiceIntegration(models.Model):
    _name = "account.invoice.integration"
    _description = "Integração de Faturas"

    invoice_id = fields.Many2one(
        string="Fatura",
        comodel_name="account.move",
    )

    external_system_id = fields.Char(
        string="ID externo", help="ID da fatura no sistema externo."
    )

    status = fields.Selection(
        string="Status da integração",
        selection=[
            ("pending", "Pendente"),
            ("success", "Sucesso"),
            ("error", "Erro"),
        ],
    )

    response_message = fields.Text(
        string="Mensagem de resposta",
    )

    def get_json_invoice(self):
        invoice = self.env["account.move"].browse(self.id)
        if invoice:
            invoice_data = {
                "invoice_number": invoice.name,
                "invoice_amount": invoice.amount_total,
            }

        return invoice_data

    def send_invoice_to_api(self):
        """Envia a fatura para uma api externa."""
        for record in self:
            login_user = self.env.user.company_id.invoice_api_login or "teste"
            login_password = self.env.user.company_id.invoice_api_password or "teste123"
            url = (
                self.env.user.company_id.invoice_api_url
                or "https://webhook.site/d3951522-e0f3-4575-8ac2-90d6c594418f"
            )

            try:
                res = requests.post(
                    url,
                    auth=(login_user, login_password),
                    json=record.get_json_invoice(),
                    timeout=60,
                )

                record.external_system_id = res.id
                record.status = res.status
                record.response_message = res.text

            except Exception as e:
                record.status = "error"
                record.response_message = str(e)
