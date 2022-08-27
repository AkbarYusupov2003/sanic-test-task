from sanic import Blueprint, Request, json, response
from sanic_openapi.openapi3 import openapi
from sanic_validation import validate_json

from payment.utils import get_bill, update_bill_balance
from products.json_responses import (ProductPaymentResponse200,
                                     ProductPaymentResponse400,
                                     ProductPaymentResponse404,
                                     ProductPaymentResponse422,
                                     ProductsListResponse200)
from products.json_validators import (ProductPaymentRequestBody,
                                      product_payment_schema)
from products.utils import get_all_products, get_product_by_id
from users.auth import login_required
from users.json_responses import UnauthorizedResponse401
from users.models import User

products_blueprint = Blueprint("products", url_prefix="api/")


@openapi.summary("Products list")
@openapi.description(
    "List of products, in order to purchase a product, you will need its id"
)
@openapi.tag("Products")
@openapi.response(
    200, {"application/json": ProductsListResponse200}, "Successful Response"
)
@openapi.response(
    401, {"application/json": UnauthorizedResponse401}, "Unauthorized Error"
)
@products_blueprint.route(
    "/products-list", name="products-list", methods=("GET",)
)
async def products_list(request: Request) -> json:
    database = request.app.config["database"]
    products = await get_all_products(database)
    data = []
    for product in products:
        data.append(
            {
                "id": product.id,
                "title": product.title,
                "description": product.description,
                "price": product.price,
            }
        )
    result = {"products": data}
    return response.json(result, status=200)


@openapi.summary("Single product")
@openapi.description("Pay for the product and get it")
@openapi.tag("Products")
@openapi.parameter(
    "Authorization",
    str,
    location="header",
    required=True,
    description="Bearer Token",
)
@openapi.body(
    {"application/json": ProductPaymentRequestBody},
    description="Send the ID of the bill that you own to pay for the product",
    required=True,
)
@openapi.response(
    200, {"application/json": ProductPaymentResponse200}, "Successful Response"
)
@openapi.response(
    400, {"application/json": ProductPaymentResponse400}, "Bad Request Error"
)
@openapi.response(
    401, {"application/json": UnauthorizedResponse401}, "Unauthorized Error"
)
@openapi.response(
    404, {"application/json": ProductPaymentResponse404}, "Not Found"
)
@openapi.response(
    422,
    {"application/json": ProductPaymentResponse422},
    "Unprocessable Entity Error",
)
@products_blueprint.route(
    "/product-payment",
    name="product-payment",
    methods=("POST",),
)
@login_required(insert_user=True)
@validate_json(product_payment_schema)
async def product_payment(request: Request, user: User) -> json:
    product_id = request.json.get("product_id")
    bill_id = request.json.get("bill_id")
    database = request.app.config["database"]
    product = await get_product_by_id(database, product_id)
    bill = await get_bill(database, bill_id, user.id)
    if not bill:
        return response.json(
            {"error": "The bill id entered incorrectly"}, status=400
        )
    if not product:
        return response.json(
            {"error": "The product was not found"}, status=404
        )

    if bill.balance - product.price >= 0:

        new_balance = bill.balance - product.price
        await update_bill_balance(database, bill_id, new_balance)
        return response.json(
            {"message": "The product was successfully purchased"},
            status=200,
        )

    else:

        return response.json(
            {
                "error": "The product purchase failed, insufficient funds on the bill"
            },
            status=422,
        )
