from databases import Database


async def get_bill(database: Database, bill_id: int, user_id: int):
    print("USER ID", user_id)
    query = "SELECT * FROM bill WHERE id = :bill_id AND user_id = :user_id"
    return await database.fetch_one(
        query=query, values={"bill_id": bill_id, "user_id": user_id}
    )


async def update_bill_balance(
    database: Database, bill_id: int, new_balance: int
):
    query = "UPDATE bill SET balance = :new_balance WHERE id = :bill_id"
    return await database.execute(
        query=query, values={"bill_id": bill_id, "new_balance": new_balance}
    )


# /payment/webhook
async def create_transaction(
    database: Database, bill_id: int, transaction_id: int, deposit: int
):
    query = "INSERT INTO transaction(id, deposit, bill_id, created_at) VALUES (:transaction_id, :deposit, :bill_id, NOW())"
    return await database.execute(
        query=query,
        values={
            "bill_id": bill_id,
            "transaction_id": transaction_id,
            "deposit": deposit,
        },
    )


async def create_bill(
    database: Database, bill_id: int, balance: int, user_id: int
):
    query = "INSERT INTO bill(id, balance, user_id) VALUES(:bill_id, :balance,:user_id)"
    return await database.execute(
        query=query,
        values={
            "bill_id": bill_id,
            "balance": balance,
            "user_id": user_id,
        },
    )
