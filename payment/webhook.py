import asyncpg

import settings


async def webhook_db_transaction(
    bill_id: int, transaction_id: int, deposit: int
):
    connection = await asyncpg.connect(settings.connection)

    async with connection.transaction():
        await connection.execute(
            "INSERT INTO transaction(id, deposit, bill_id, created_at) VALUES ( $1, $2, $3, NOW())",
            transaction_id,
            deposit,
            bill_id,
        )
        await connection.execute(
            "UPDATE bill SET balance = balance + $1 WHERE id = $2",
            deposit,
            bill_id,
        )
    await connection.close()
