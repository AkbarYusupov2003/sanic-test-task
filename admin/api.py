from sanic import Blueprint, Request, response
from sanic_openapi.openapi3 import openapi
from sanic_validation import validate_json

from admin.json_responses import (ProductCreateResponse201,
                                  ProductDeleteResponse200,
                                  ProductsRetrieveResponse200,
                                  ProductUpdateResponse200,
                                  UserPatchResponse200, UsersGetResponse200)
from admin.json_validators import (ProductCreateRequestBody,
                                   ProductDeleteRequestBody,
                                   ProductUpdateRequestBody,
                                   UserPatchRequestBody, product_create_schema,
                                   product_delete_schema,
                                   product_update_schema, user_patch_schema)
from products.utils import (create_product, delete_product, get_all_products,
                            update_product)
from users.auth import admin_rights_required
from users.json_responses import NoAccessResponse403, UnauthorizedResponse401
from users.utils import change_user_activity

admin_blueprint = Blueprint("admin", url_prefix="api/admin/")


class ProductsCRUD:
    @staticmethod
    @openapi.summary("Retrieve products")
    @openapi.description("Retrieve products by request")
    @openapi.tag("Admin")
    @openapi.parameter(
        "Authorization",
        str,
        location="header",
        required=True,
        description="Bearer Token",
    )
    @openapi.response(
        201,
        {"application/json": ProductsRetrieveResponse200},
        "Successful Response",
    )
    @openapi.response(
        401,
        {"application/json": UnauthorizedResponse401},
        "Unauthorized Error",
    )
    @openapi.response(
        403,
        {"application/json": NoAccessResponse403},
        "Unauthorized Error",
    )
    @admin_blueprint.route(
        "/products", name="products-retrieve", methods=("GET",)
    )
    @admin_rights_required()
    async def get(request: Request):
        products = await get_all_products(request.app.config["database"])
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

    @staticmethod
    @openapi.summary("Create a product")
    @openapi.description("Post the product's data and create it")
    @openapi.tag("Admin")
    @openapi.parameter(
        "Authorization",
        str,
        location="header",
        required=True,
        description="Bearer Token",
    )
    @openapi.body(
        {"application/json": ProductCreateRequestBody},
        description="",
        required=True,
    )
    @openapi.response(
        201,
        {"application/json": ProductCreateResponse201},
        "Successful Response",
    )
    @openapi.response(
        401,
        {"application/json": UnauthorizedResponse401},
        "Unauthorized Error",
    )
    @openapi.response(
        403,
        {"application/json": NoAccessResponse403},
        "Unauthorized Error",
    )
    @admin_blueprint.route(
        "/products", name="products-create", methods=("POST",)
    )
    @validate_json(product_create_schema)
    @admin_rights_required()
    async def post(request):
        title = request.json.get("title")
        description = request.json.get("description")
        price = request.json.get("price")
        await create_product(
            request.app.config["database"], title, description, price
        )
        return response.json(
            {"message": "The product was successfully created"}, status=201
        )

    @staticmethod
    @openapi.summary("Update a product")
    @openapi.description(
        "Send the new data for the product and it will be updated"
    )
    @openapi.tag("Admin")
    @openapi.parameter(
        "Authorization",
        str,
        location="header",
        required=True,
        description="Bearer Token",
    )
    @openapi.body(
        {"application/json": ProductUpdateRequestBody},
        description="",
        required=True,
    )
    @openapi.response(
        200,
        {"application/json": ProductUpdateResponse200},
        "Successful Response",
    )
    @openapi.response(
        401,
        {"application/json": UnauthorizedResponse401},
        "Unauthorized Error",
    )
    @openapi.response(
        403,
        {"application/json": NoAccessResponse403},
        "Unauthorized Error",
    )
    @admin_blueprint.route(
        "/products", name="products-update", methods=("PUT",)
    )
    @validate_json(product_update_schema)
    @admin_rights_required()
    async def put(request):
        id_ = request.json.get("id")
        title = request.json.get("title")
        description = request.json.get("description")
        price = request.json.get("price")
        await update_product(
            request.app.config["database"], id_, title, description, price
        )
        return response.json(
            {"message": "The product was successfully updated"}, status=200
        )

    @staticmethod
    @openapi.summary("Delete a product")
    @openapi.description("Send the product's id to delete it")
    @openapi.tag("Admin")
    @openapi.parameter(
        "Authorization",
        str,
        location="header",
        required=True,
        description="Bearer Token",
    )
    @openapi.body(
        {"application/json": ProductDeleteRequestBody},
        description="",
        required=True,
    )
    @openapi.response(
        200,
        {"application/json": ProductDeleteResponse200},
        "Successful Response",
    )
    @openapi.response(
        401,
        {"application/json": UnauthorizedResponse401},
        "Unauthorized Error",
    )
    @openapi.response(
        403,
        {"application/json": NoAccessResponse403},
        "Unauthorized Error",
    )
    @admin_blueprint.route(
        "/products", name="products-delete", methods=("DELETE",)
    )
    @validate_json(product_delete_schema)
    @admin_rights_required()
    async def delete(request):
        id_ = request.json.get("id")
        await delete_product(
            request.app.config["database"],
            id_,
        )
        return response.json(
            {"message": "The product was successfully deleted"}, status=200
        )


class UsersManagement:
    @staticmethod
    @openapi.summary("Get detailed users data")
    @openapi.description(
        "Get id, username, is_active, is_admin, bills data about users"
    )
    @openapi.tag("Admin")
    @openapi.parameter(
        "Authorization",
        str,
        location="header",
        required=True,
        description="Bearer Token",
    )
    @openapi.response(
        200,
        {"application/json": UsersGetResponse200},
        "Successful Response",
    )
    @openapi.response(
        401,
        {"application/json": UnauthorizedResponse401},
        "Unauthorized Error",
    )
    @openapi.response(
        403,
        {"application/json": NoAccessResponse403},
        "Unauthorized Error",
    )
    @admin_blueprint.route(
        "/users", name="user-bills-retrieve", methods=("GET",)
    )
    @admin_rights_required()
    async def get(request):

        database = request.app.config["database"]
        query = """
                   SELECT users.id, users.username, users.is_active,
                          users.is_admin, array_agg(bill.id) AS bills_id,
                          array_agg(bill.balance) AS bills_balance
                   FROM users
                   LEFT JOIN bill
                       ON bill.user_id = users.id
                   GROUP by users.id
                   ORDER BY users.id;
                """

        users = await database.fetch_all(
            query=query,
        )
        data = []

        for user in users:
            bills = []

            if user.bills_id[0]:
                for i in range(len(user.bills_id)):
                    bills.append(
                        {
                            "id": user.bills_id[i],
                            "balance": user.bills_balance[i],
                        }
                    )

            data.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "is_active": user.is_active,
                    "is_admin": user.is_admin,
                    "bills": bills,
                }
            )

        result = {"users": data}
        return response.json(result, status=200)

    @staticmethod
    @openapi.summary("Activate / Deactivate the user")
    @openapi.description("Send an integer id and boolean is_active variables")
    @openapi.tag("Admin")
    @openapi.parameter(
        "Authorization",
        str,
        location="header",
        required=True,
        description="Bearer Token",
    )
    @openapi.body(
        {"application/json": UserPatchRequestBody},
        description="",
        required=True,
    )
    @openapi.response(
        200,
        {"application/json": UserPatchResponse200},
        "Successful Response",
    )
    @openapi.response(
        401,
        {"application/json": UnauthorizedResponse401},
        "Unauthorized Error",
    )
    @openapi.response(
        403,
        {"application/json": NoAccessResponse403},
        "Unauthorized Error",
    )
    @admin_blueprint.route(
        "/users", name="user-change-activity", methods=("PATCH",)
    )
    @validate_json(user_patch_schema)
    @admin_rights_required()
    async def patch(request):
        user_id = request.json.get("id")
        is_active = request.json.get("is_active")
        await change_user_activity(
            request.app.config["database"], user_id, is_active
        )
        s = "activated" if is_active else "deactivated"
        return response.json({"message": f"The user is {s}"}, status=200)
