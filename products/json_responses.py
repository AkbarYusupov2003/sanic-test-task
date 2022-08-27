# Products List
class ProductsListResponse200:
    worked = True


# Product Payment
class ProductPaymentResponse200:
    message = "The product was successfully purchased"


class ProductPaymentResponse400:
    error = "The bill id entered incorrectly"


class ProductPaymentResponse404:
    error = "The product was not found"


class ProductPaymentResponse422:
    error = "The product purchase failed, insufficient funds on the bill"
