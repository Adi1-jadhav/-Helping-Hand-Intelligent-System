from db.database import get_db_connection
from datetime import datetime

def register_ngo(org_name, contact_email, location, mission, password_hash, verified=False):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ngos (org_name, contact_email, location, mission, password_hash, verified, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (org_name, contact_email, location, mission, password_hash, verified, datetime.now()))
    conn.commit()
    cur.close()
    conn.close()


def get_ngo_profile(ngo_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)  # Use dictionary cursor
    cur.execute("SELECT * FROM ngos WHERE id = %s", (ngo_id,))
    ngo = cur.fetchone()
    cur.close()
    conn.close()
    return ngo


def get_claimed_donations(ngo_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT d.* FROM donations d
        WHERE d.claimed_by = %s
        ORDER BY d.claimed_at DESC
    """, (ngo_id,))
    claimed = cur.fetchall()
    cur.close()
    conn.close()
    return claimed

def get_all_ngos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ngos ORDER BY created_at DESC")
    ngos = cur.fetchall()
    cur.close()
    conn.close()
    return ngos

def get_ngo_by_email(email):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM ngos WHERE contact_email = %s", (email,))
    ngo = cur.fetchone()
    cur.close()
    conn.close()
    return ngo

