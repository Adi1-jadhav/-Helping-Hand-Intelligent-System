# 📁 email_utils.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Replace with your actual config or import from Config.py
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'adityajadhav3117@gmail.com'
EMAIL_PASS = 'xmfx rgfi dslk njpg'  # Use app-specific password or env variable

def send_donor_notification(to_email, donor_name, donation_title, pickup_time, ngo_name):
    subject = "🎁 Your donation has been claimed!"
    body = f"""
Hi {donor_name},

Great news! Your donation (“{donation_title}”) has been claimed by {ngo_name}.
Pickup is scheduled for: {pickup_time}

Thank you for making an impact!
– DonateWise Team
"""

    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent to donor {donor_name} at {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
