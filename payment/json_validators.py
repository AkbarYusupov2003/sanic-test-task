signature_validation = {
    "type": "string",
    "required": True,
}

transaction_id_validation = {
    "type": "integer",
    "required": True,
}

user_id_validation = {
    "type": "integer",
    "required": True,
}

bill_id_validation = {
    "type": "integer",
    "required": True,
}

amount_validation = {
    "type": "integer",
    "required": True,
}

webhook_schema = {
    "signature": signature_validation,
    "transaction_id": transaction_id_validation,
    "user_id": user_id_validation,
    "bill_id": bill_id_validation,
    "amount": amount_validation,
}


class WebhookRequestBody:
    signature = "encrypted_string"
    transaction_id = 1234567
    user_id = 123
    bill_id = 123456
    amount = 100
