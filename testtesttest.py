import psycopg2

try:
    connection = psycopg2.connect(
        host = "127.0.0.1",
        user = "postgres",
        password = "imnotweakbyanymeans",
        database = "reviews"
    )
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT version();"
        )
        print(f'Version: {cursor.fetchone()}')
except Exception as ex:
    print(ex)
finally:
    if connection:
        connection.close()
