from databases import Database

from products.models import product


async def get_all_products(database: Database):
    query = product.select()
    return await database.fetch_all(query=query)


async def get_product_by_id(database: Database, product_id: int):
    query = "SELECT price FROM product WHERE id = :product_id"
    return await database.fetch_one(
        query=query, values={"product_id": product_id}
    )


async def create_product(
    database: Database, title: str, description: str, price: int
):
    return await database.execute(
        query=product.insert(),
        values={
            "title": title,
            "description": description,
            "price": price,
        },
    )


async def update_product(
    database: Database,
    product_id: int,
    title: str,
    description: str,
    price: int,
):
    return await database.execute(
        query=product.update().where(product.c.id == product_id),
        values={
            "title": title,
            "description": description,
            "price": price,
        },
    )


async def delete_product(database: Database, product_id: int):
    return await database.execute(
        query=product.delete().where(product.c.id == product_id)
    )
