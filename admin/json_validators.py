# Products
id_ = {
    "type": "integer",
    "required": True,
}

title = {
    "type": "string",
    "maxlength": 64,
    "required": True,
}

description = {
    "type": "string",
    "required": True,
}

price = {
    "type": "integer",
    "required": True,
}

product_create_schema = {
    "title": title,
    "description": description,
    "price": price,
}

product_update_schema = {
    "id": id_,
    "title": title,
    "description": description,
    "price": price,
}

product_delete_schema = {"id": id_}


class ProductCreateRequestBody:
    title = "String"
    description = "Text"
    price = 150


class ProductUpdateRequestBody:
    id = 5
    title = "String"
    description = "Text"
    price = 150


class ProductDeleteRequestBody:
    id = 5


# Users
is_active = {
    "type": "boolean",
    "required": True,
}

user_patch_schema = {
    "id": id_,
    "is_active": is_active,
}


class UserPatchRequestBody:
    id = 5
    is_active = False
