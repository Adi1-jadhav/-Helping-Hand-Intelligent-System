import mysql.connector
from Config import db_config
from db.database import execute_query, get_db_connection
from models.pickup_recommender import should_recommend_pickup  # ✅ used in logic

# 🔍 All Donations + Donor Info
def get_all_donations():
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT d.id, d.title, d.description, d.location, d.quantity,
               d.predicted_category, d.image_filename, d.created_at,
               d.pickup_required, d.pickup_time, d.pickup_status,
               d.claimed_by, d.claimed_at,
               u.name AS user_name
        FROM donations d
        LEFT JOIN users u ON d.user_id = u.id
        ORDER BY d.created_at DESC
    """)
    donations = cur.fetchall()
    cur.close()
    conn.close()

    for d in donations:
        d['pickup_status'] = d.get('pickup_status') or 'Pending'
        d['pickup_recommended'] = should_recommend_pickup(
            d['quantity'], d['predicted_category'], d['description']
        )
    print(f"📦 Donations fetched: {len(donations)}")
    return donations

# 📊 Category Stats for Filters
def get_category_stats():
    query = """
        SELECT predicted_category, COUNT(*) as count
        FROM donations
        GROUP BY predicted_category
    """
    result = execute_query(query)
    return {
        row['predicted_category'] or "Uncategorized": row['count']
        for row in result
    }

# 💾 Save Donation
# def save_donation(user_id, title, description, location, quantity,
#                   predicted_category, image_filename,
#                   pickup_required=False, pickup_time=None, pickup_status=None):
#     try:
#         conn = mysql.connector.connect(**db_config)
#         cur = conn.cursor()
#         cur.execute("""
#             INSERT INTO donations (
#                 user_id, title, description, location, quantity,
#                 predicted_category, image_filename,
#                 pickup_required, pickup_time, pickup_status
#             ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """, (
#             user_id, title, description, location, quantity,
#             predicted_category, image_filename,
#             pickup_required, pickup_time, pickup_status
#         ))
#         conn.commit()
#         print("✅ Donation saved.")
#     except Exception as e:
#         print("❌ Donation insert failed:", e)
#     finally:
#         cur.close()
#         conn.close()
def save_donation(user_id, title, description, location, quantity,
                  predicted_category, image_filename,
                  pickup_required=False, pickup_time=None, pickup_status=None):
    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()

        # Ensure safe defaults
        if pickup_status is None:
            pickup_status = 'pending'
        if predicted_category is None:
            predicted_category = ''
        if image_filename is None:
            image_filename = ''

        cur.execute("""
            INSERT INTO donations (
                user_id, title, description, location, quantity,
                predicted_category, image_filename,
                pickup_required, pickup_time, pickup_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id, title, description, location, quantity,
            predicted_category, image_filename,
            pickup_required, pickup_time, pickup_status
        ))

        conn.commit()
        print("✅ Donation saved.")
    except Exception as e:
        print("❌ Donation insert failed:", e)

    finally:
     if cur:
        cur.close()
     if conn:
        conn.close()


# 🛠 Update Pickup Status
def update_pickup_status(donation_id, status):
    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()
        cur.execute("""
            UPDATE donations SET pickup_status = %s WHERE id = %s
        """, (status, donation_id))
        conn.commit()
        print(f"✅ Pickup status updated to '{status}' for donation ID: {donation_id}")
    except Exception as e:
        print("❌ Pickup status update failed:", e)
    finally:
        cur.close()
        conn.close()

# 📥 Unclaimed Donations
def get_unclaimed_donations():
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT d.*, u.name AS user_name
        FROM donations d
        LEFT JOIN users u ON d.user_id = u.id
        WHERE claimed_by IS NULL
        ORDER BY d.created_at DESC
    """)
    records = cur.fetchall()
    cur.close()
    conn.close()

    for d in records:
        d['pickup_status'] = d.get('pickup_status') or 'Pending'
        d['pickup_recommended'] = should_recommend_pickup(
            d['quantity'], d['predicted_category'], d['description']
        )
    return records

# ✅ Claimed Donations by NGO
def get_claimed_donations(ngo_id):
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT d.*, dc.claimed_at, dc.pickup_time, dc.pickup_notes,
               n.org_name AS claimed_by_name,
               u.name AS user_name
        FROM donation_claims dc
        JOIN donations d ON dc.donation_id = d.id
        LEFT JOIN ngos n ON dc.ngo_id = n.id
        LEFT JOIN users u ON d.user_id = u.id
        WHERE dc.ngo_id = %s
        ORDER BY dc.claimed_at DESC
    """, (ngo_id,))
    claimed = cur.fetchall()
    cur.close()
    conn.close()

    for d in claimed:
        d['pickup_status'] = d.get('pickup_status') or 'Pending'
        d['pickup_recommended'] = should_recommend_pickup(
            d['quantity'], d['predicted_category'], d['description']
        )
    return claimed

# 📍 Mark Donation as Claimed
def mark_donation_claimed(donation_id, ngo_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()
        cur.execute("""
            UPDATE donations
            SET claimed_by = %s, claimed_at = NOW()
            WHERE id = %s
        """, (ngo_id, donation_id))
        conn.commit()
        print(f"📥 Donation {donation_id} marked as claimed by NGO {ngo_id}")
    except Exception as e:
        print("❌ Claim marking failed:", e)
    finally:
        cur.close()
        conn.close()

# 📧 Get Donor Info by Donation — used for notifications
def get_donor_by_donation_id(donation_id):
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT u.id, u.name, u.email
        FROM donations d
        LEFT JOIN users u ON d.user_id = u.id
        WHERE d.id = %s
    """, (donation_id,))
    donor = cur.fetchone()
    cur.close()
    conn.close()
    return donor

# 🔍 Single Donation by ID
def get_donation_by_id(donation_id):
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM donations WHERE id = %s", (donation_id,))
    donation = cur.fetchone()
    cur.close()
    conn.close()
    return donation
