import psycopg2
from manager import Manager

import settings
from users.utils import generate_hash

manager = Manager()


@manager.command
def create_admin(username, password):

    sql = "INSERT INTO users(username, hashed_password, is_active, is_admin) VALUES(%s, %s, %s, %s)"
    data = (username, generate_hash(password), True, True)
    connection = None
    try:
        connection = psycopg2.connect(settings.connection)

        cursor = connection.cursor()

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        username_taken = cursor.fetchone()

        if username_taken:
            return "Username already taken"

        cursor.execute(sql, data)

        connection.commit()

        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    else:
        print(
            "The user was successfully created, login and get token to access admin functionality"
        )
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    manager.main()
