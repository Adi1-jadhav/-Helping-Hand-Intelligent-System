import mysql.connector

# 🔌 Establish connection
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',  # Replace with your actual DB password
        database='donation'
    )

# 🧠 Execute query (SELECT / INSERT / UPDATE / DELETE)
def execute_query(query, params=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(query, params or ())

        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.rowcount
    except Exception as e:
        print(f"❌ Query Error: {e}")
        result = None
    finally:
        cursor.close()
        conn.close()

    return result
