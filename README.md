# 🧠 DonateWise – AI-Powered NGO Donation Tracker

**DonateWise** is a full-stack donation management system that connects donors with verified NGOs. 
It uses AI to auto-categorize donations, recommends pickups, and ensures transparency in charitable logistics.

---

## 🚀 Features

- 🔐 **NGO Verification Workflow** – Admin approval system for secure donation claims
- 📦 **Donation Categorization** – ML model predicts donation type (e.g., food, clothes)
- 🚚 **Pickup Recommendation** – Smart logic suggests pickups based on quantity and urgency
- 🧾 **Claim Management** – NGOs can claim donations with scheduled pickup times
- 📊 **Admin Dashboard** – View, approve, and manage all donations
- 📱 **Mobile-Friendly UI** – Responsive design for donors and NGOs

---

## 🧰 Tech Stack

| Layer        | Tools Used                          |
|--------------|-------------------------------------|
| Backend      | Flask, MySQL, REST APIs             |
| Frontend     | HTML, CSS, Bootstrap                |
| ML Model     | Naive Bayes  |
| Deployment   | Render (Flask app), Railway (MySQL) |
| Database     | MySQL (cloud-hosted via Railway)    |
---

## 👥 User Roles

- **Donor**: Submits donations with optional pickup requests
- **NGO**: Views and claims donations after admin approval
- **Admin**: Verifies NGOs, manages donations, and monitors system activity


-## 🧠 AI Integration

- **Donation Category Predictor**: Uses a **Naive Bayes classifier** trained on donation titles and descriptions to automatically tag donations into categories like food, clothes, books, etc.
- **Pickup Recommender**: Applies rule-based logic to suggest pickups based on quantity, urgency, and donation type.

---

## 🛠️ Setup Instructions

1. **Clone the repo**
   ```bash
   git clone https://github.com/<your-username>/donatewise-ngotracker.git
   cd donatewise-ngotracker

2. Install Dependencies   
pip install -r requirements.txt

3.Configure environment
Add your MySQL credentials in .env or directly in db/database.py

4. flask run




