from Crypto.Hash import SHA1
from sanic import Blueprint, Request, response
from sanic_openapi.openapi3 import openapi
from sanic_validation import validate_json

import settings
from payment.json_responses import (ReceiveBillsInfoResponse200,
                                    WebhookResponse200, WebhookResponse201,
                                    WebhookResponse404, WebhookResponse406,
                                    WebhookResponse428)
from payment.json_validators import WebhookRequestBody, webhook_schema
from payment.utils import create_bill, create_transaction, get_bill
from payment.webhook import webhook_db_transaction
from users.auth import login_required
from users.json_responses import UnauthorizedResponse401
from users.models import User
from users.utils import get_user_by_id

payment_blueprint = Blueprint("payment", url_prefix="api/")


@openapi.summary("Bills info")
@openapi.description("Get detailed information about your bills")
@openapi.tag("Payment")
@openapi.parameter(
    "Authorization",
    str,
    location="header",
    required=True,
    description="Bearer Token",
)
@openapi.response(
    200,
    {"application/json": ReceiveBillsInfoResponse200},
    "Successful Response",
)
@openapi.response(
    401, {"application/json": UnauthorizedResponse401}, "Unauthorized Error"
)
@payment_blueprint.route(
    "/receive-bills-info", name="receive-bills-info", methods=("GET",)
)
@login_required(insert_user=True)
async def receive_bills_info(request: Request, user: User):
    query = """
               SELECT bill.id, bill.balance,
                   array_agg(transaction.id) AS transaction_id,
                   array_agg(transaction.deposit) AS deposit,
                   array_agg(transaction.created_at) AS created_at
               FROM bill
               LEFT JOIN transaction
                   ON transaction.bill_id = bill.id
               WHERE bill.user_id = :user_id
               GROUP by bill.id
               ORDER BY bill.id;
            """
    database = request.app.config["database"]
    bills = await database.fetch_all(query=query, values={"user_id": user.id})

    data = []

    for bill in bills:
        transactions = []

        if bill.transaction_id[0]:
            for i in range(len(bill.transaction_id)):
                transactions.append(
                    {
                        "id": bill.transaction_id[i],
                        "deposit": bill.deposit[i],
                        "created_at": bill.created_at[i].isoformat(),
                    }
                )

        data.append(
            {
                "id": bill.id,
                "balance": bill.balance,
                "transactions": transactions,
            }
        )

    result = {"bills": data}

    return response.json(result, status=200)


@openapi.summary("Payment webhook")
@openapi.description(
    "Webhook making a deposit to the bill for internal services"
)
@openapi.tag("Payment")
@openapi.parameter(
    "Authorization",
    str,
    location="header",
    required=True,
    description="Bearer Token",
)
@openapi.body(
    {"application/json": WebhookRequestBody},
    description="",
    required=True,
)
@openapi.response(
    200, {"application/json": WebhookResponse200}, "Successful Response"
)
@openapi.response(
    201, {"application/json": WebhookResponse201}, "Successful Response"
)
@openapi.response(
    401, {"application/json": UnauthorizedResponse401}, "Unauthorized Error"
)
@openapi.response(
    404, {"application/json": WebhookResponse404}, "Not Found Response"
)
@openapi.response(
    406, {"application/json": WebhookResponse406}, "Not Acceptable Response"
)
@openapi.response(
    428,
    {"application/json": WebhookResponse428},
    "Precondition Required Response",
)
@payment_blueprint.route("/payment/webhook", name="webhook", methods=("POST",))
@login_required()
@validate_json(webhook_schema)
async def webhook(request: Request):
    database = request.app.config["database"]
    signature = request.json.get("signature")
    transaction_id = request.json.get("transaction_id")
    user_id = request.json.get("user_id")
    bill_id = request.json.get("bill_id")
    amount = request.json.get("amount")
    correct_signature = SHA1.new(
        f"{settings.private_key}:{transaction_id}:{user_id}:{bill_id}:{amount}".encode()
    ).hexdigest()
    print(correct_signature)
    if signature == correct_signature:
        if await get_user_by_id(database, user_id):
            if amount > 0:
                if await get_bill(database, bill_id, user_id):
                    await webhook_db_transaction(
                        bill_id, transaction_id, amount
                    )
                    return response.json(
                        {"message": "The payment was completed successfully"},
                        status=200,
                    )
                else:
                    await create_bill(database, bill_id, amount, user_id)
                    await create_transaction(
                        database, bill_id, transaction_id, amount
                    )
                    return response.json(
                        {
                            "message": "The payment was completed successfully, the bill was created"
                        },
                        status=201,
                    )
            else:
                return response.json(
                    {"error": "The amount must be a positive number"},
                    status=428,
                )
        else:
            return response.json(
                {"error": "The user was not found"}, status=404
            )
    else:
        return response.json(
            {"error": "The signature is incorrect"}, status=406
        )
