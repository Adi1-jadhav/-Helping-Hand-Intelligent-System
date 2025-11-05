import mysql.connector
from Config import db_config  # your DB credentials


def execute_query(query, params=None):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)  # ✅ this is the key!

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        result = cursor.fetchall()
        connection.close()
        return result
    except mysql.connector.Error as err:
        print(f"❌ Query Error: {err}")
        return []
