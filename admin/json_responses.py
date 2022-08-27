# Products
class ProductsRetrieveResponse200:
    message = "Products were successfully retrieved"


class ProductCreateResponse201:
    message = "The product was successfully created"


class ProductUpdateResponse200:
    message = "The product was successfully updated"


class ProductDeleteResponse200:
    message = "The product was successfully deleted"


# Users
class UsersGetResponse200:
    users = "data list"


class UserPatchResponse200:
    message = "The user is 'activated / deactivated' successfully"
