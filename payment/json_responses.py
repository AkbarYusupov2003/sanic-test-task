class ReceiveBillsInfoResponse200:
    bills = "data list"


# payment/webhook
class WebhookResponse200:
    message = "The payment was completed successfully"


class WebhookResponse201:
    message = "The payment was completed successfully, the bill was created"


class WebhookResponse404:
    error = "The user was not found"


class WebhookResponse406:
    error = "The signature is incorrect"


class WebhookResponse428:
    error = "The amount must be a positive number"
