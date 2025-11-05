import os
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from markupsafe import Markup
from routes.email_utils import send_donor_notification  # Add this near your imports


from db.database import get_db_connection
from models.ngo_models import register_ngo, get_ngo_profile
from ai_model.predictor import predict_category
from models.pickup_recommender import should_recommend_pickup
from models.donation_model import (
    get_category_stats,
    save_donation,
    get_all_donations,
    update_pickup_status,
    get_unclaimed_donations,
    get_claimed_donations,
    mark_donation_claimed,
    get_donor_by_donation_id  # 🆕 Added to fetch donor info
)

main = Blueprint('main', __name__)
UPLOAD_FOLDER = os.path.join('static', 'uploads')

@main.route('/')
def index():
    return redirect(url_for('main.home'))

@main.route('/home')
def home():
    if session.get('role') != 'donor':
        flash("Please log in as donor to access home.")
        return redirect(url_for('auth.login'))
    return render_template('landing.html')

@main.route('/dashboard')
def dashboard():
    if session.get('role') != 'admin':
        flash("Admin access only.")
        return redirect(url_for('auth.admin_login'))

    stats = get_category_stats()
    donations = get_all_donations()
    for d in donations:
        d['pickup_recommended'] = False
        if d.get('pickup_required'):
            d['pickup_recommended'] = should_recommend_pickup(
                d['quantity'], d['predicted_category'], d['description']
            )
    return render_template('dashboard.html', donations=donations, stats=stats)

@main.route('/donate', methods=['GET', 'POST'])
def donate():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        quantity = request.form['quantity']
        pickup_required = 'pickup_required' in request.form
        pickup_time = request.form.get('pickup_time') or None

        image_file = request.files.get('image')
        image_filename = None
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(save_path)
            image_filename = filename

        category = predict_category(title, description)
        pickup_recommended = should_recommend_pickup(quantity, category, description)

        session['donation_data'] = {
            'title': title,
            'description': description,
            'location': location,
            'quantity': quantity,
            'predicted_category': category,
            'image_filename': image_filename,
            'pickup_required': pickup_required,
            'pickup_time': pickup_time,
            'pickup_status': 'Pending',
            'pickup_recommended': pickup_recommended
        }

        return redirect(url_for('main.result'))

    return render_template('donate.html')

@main.route('/result', methods=['GET', 'POST'])
def result():
    data = session.get('donation_data')
    if request.method == 'POST' and data and session.get('user_id'):
        save_donation(
            user_id=session['user_id'],
            title=data['title'],
            description=data['description'],
            location=data['location'],
            quantity=data['quantity'],
            predicted_category=data['predicted_category'],
            image_filename=data.get('image_filename'),
            pickup_required=data.get('pickup_required'),
            pickup_time=data.get('pickup_time'),
            pickup_status=data.get('pickup_status')
        )
        flash("Donation confirmed successfully!")
        return redirect(url_for('main.dashboard'))
    return render_template('result.html', prediction=data.get('predicted_category'))

@main.route('/confirm', methods=['POST'])
def confirm():
    user_id = session.get('user_id')
    data = session.get('donation_data')

    if data and user_id:
        save_donation(
            user_id=user_id,
            title=data['title'],
            description=data['description'],
            location=data['location'],
            quantity=data['quantity'],
            predicted_category=data['predicted_category'],
            image_filename=data.get('image_filename'),
            pickup_required=data.get('pickup_required'),
            pickup_time=data.get('pickup_time'),
            pickup_status=data.get('pickup_status')
        )
        flash("Donation confirmed successfully!")
        return redirect(url_for('main.dashboard'))
    else:
        flash("Missing donation data or user session.")
        return redirect(url_for('main.donate'))

@main.route('/verify_pickup', methods=['POST'])
def verify_pickup():
    donation_id = request.form.get('donation_id')
    action = request.form.get('action')

    if donation_id and action:
        if action == "approve":
            update_pickup_status(donation_id, "Approved")
            flash(f"✅ Pickup approved for donation ID {donation_id}")
        elif action == "decline":
            update_pickup_status(donation_id, "Declined")
            flash(f"❌ Pickup declined for donation ID {donation_id}")
    else:
        flash("❌ Invalid request for pickup verification.")
    return redirect(url_for('main.dashboard'))

@main.route('/feedback', methods=['GET', 'POST'])
def feedback():
    return render_template('feedback.html')

@main.route('/history')
def history():
    return "<h3>Donation history will be added next 🚧</h3>"

# 🔔 Notify donor after NGO claims their donation
def notify_donor(donation_id, pickup_time, ngo_name):
    donor = get_donor_by_donation_id(donation_id)
    if donor and donor.get('email'):
        print(f"📬 Email to {donor['email']}: 'Your donation was claimed by {ngo_name}. Pickup is scheduled for {pickup_time}.'")
        # You can replace this with an actual send_email() function

# 🔷 NGO ROUTES

@main.route('/ngo/dashboard')
def ngo_dashboard():
    if not session.get('ngo_id'):
        return redirect(url_for('auth.login'))

    ngo = get_ngo_profile(session['ngo_id'])
    if not ngo:
        flash("NGO profile could not be loaded.")
        return redirect(url_for('main.ngo_profile'))

    stats = get_category_stats()
    unclaimed = get_unclaimed_donations()
    claimed = get_claimed_donations(session['ngo_id'])

    for d in unclaimed + claimed:
        d['pickup_status'] = d.get('pickup_status') or 'Pending'
        d['pickup_recommended'] = should_recommend_pickup(
            d['quantity'], d['predicted_category'], d['description']
        )

    return render_template('ngo_dashboard.html', stats=stats, unclaimed=unclaimed, claimed=claimed, ngo=ngo)


@main.route('/ngo/claim', methods=['POST'])
def claim_donation():
    if not session.get('ngo_id'):
        return redirect(url_for('auth.ngo_login'))

    ngo = get_ngo_profile(session['ngo_id'])
    if ngo['status'] != 'Approved':
        flash("🚫 Only verified NGOs can claim donations. Please wait for admin approval.")
        return redirect(url_for('main.ngo_dashboard'))

    donation_id = request.form.get('donation_id')
    pickup_time = request.form.get('pickup_time')
    pickup_notes = request.form.get('pickup_notes')

    if not donation_id or not pickup_time:
        flash("⚠️ Pickup time is required to claim.")
        return redirect(url_for('main.ngo_dashboard'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO donation_claims (donation_id, ngo_id, pickup_time, pickup_notes, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (donation_id, session['ngo_id'], pickup_time, pickup_notes, 'Scheduled'))

    cur.execute("""
        UPDATE donations SET claimed_by = %s WHERE id = %s
    """, (session['ngo_id'], donation_id))

    conn.commit()
    cur.close()
    conn.close()

    ngo_name = ngo.get('org_name') or 'your NGO'
    notify_donor(donation_id, pickup_time, ngo_name)

    flash(Markup(
        f"✅ Claimed for pickup at <strong>{pickup_time}</strong>. " +
        f"<a href='{url_for('main.ngo_claimed')}' class='btn btn-sm btn-success ms-2'>View Claimed Donations</a>"
    ))
    return redirect(url_for('main.ngo_dashboard'))


@main.route('/ngo/claimed')
def ngo_claimed():
    if not session.get('ngo_id'):
        return redirect(url_for('auth.login'))
    claimed = get_claimed_donations(session['ngo_id'])
    return render_template('ngo_claimed.html', claimed=claimed)

@main.route('/ngo/profile')
def ngo_profile():
    if not session.get('ngo_id'):
        flash("🚫 Session expired. Please log in again.")
        return redirect(url_for('auth.login'))

    ngo_id = session['ngo_id']

    # ✅ Always fetch latest profile directly from DB
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM ngos WHERE id = %s", (ngo_id,))
    ngo = cur.fetchone()
    cur.close()
    conn.close()

    if not ngo:
        flash("⚠️ NGO profile not found.")
        return redirect(url_for('auth.login'))

    print(f"🧪 NGO Profile Loaded: {ngo['org_name']} - Status: {repr(ngo['status'])}")
    return render_template('ngo_profile.html', ngo=ngo)



from werkzeug.security import generate_password_hash

@main.route('/ngo/register', methods=['GET', 'POST'])
def register_ngo_route():
    if request.method == 'POST':
        org_name = request.form.get('org_name')
        contact_email = request.form.get('contact_email')
        location = request.form.get('location')
        mission = request.form.get('mission')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        # 🔒 Validate all required fields
        if not all([org_name, contact_email, location, mission, password, confirm]):
            flash("⚠️ Please fill out all fields.")
            return redirect(url_for('main.register_ngo_route'))

        if password != confirm:
            flash("❌ Passwords do not match.")
            return redirect(url_for('main.register_ngo_route'))

        hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO ngos (org_name, contact_email, location, mission, password_hash, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (org_name, contact_email, location, mission, hashed_password, 'Pending'))
            conn.commit()
            flash("✅ NGO registration successful! Awaiting admin approval.")
            return redirect(url_for('main.ngo_profile'))

        except Exception as e:
            print("❌ NGO registration failed:", e)
            flash("An error occurred during registration. Please try again.")

        finally:
            cur.close()
            conn.close()

    return render_template('ngo_register.html')




def notify_donor(donation_id, pickup_time, ngo_name):
    donor = get_donor_by_donation_id(donation_id)
    if donor and donor.get('email'):
        donation_title = f"Donation #{donation_id}"  # Replace with real title if needed
        send_donor_notification(
            to_email=donor['email'],
            donor_name=donor['name'],
            donation_title=donation_title,
            pickup_time=pickup_time,
            ngo_name=ngo_name
        )


