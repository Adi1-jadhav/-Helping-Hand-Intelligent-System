import mysql.connector

# 🔌 Establish connection
def get_db_connection():
    return mysql.connector.connect(
        host='nozomi.proxy.rlwy.net',
        user='root',
        password='password',
        database='donation',  # ✅ use your actual DB name
        port=18801,
        connection_timeout=10,
        use_pure=True

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
