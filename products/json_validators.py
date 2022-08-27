bill_id_validation = {
    "type": "integer",
    "required": True,
}

product_id_validation = {
    "type": "integer",
    "required": True,
}

product_payment_schema = {
    "product_id": product_id_validation,
    "bill_id": bill_id_validation,
}


class ProductPaymentRequestBody:
    product_id = 1
    bill_id = 123456
