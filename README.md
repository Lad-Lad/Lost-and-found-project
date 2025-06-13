 Campus Lost & Found Board — 
 Purpose:
A digital platform for University of Something students and staff to report, find, and manage lost or found items on campus.

 Client:
Campus Life Office (University of Something)
They handle student wellbeing/events and want a centralized way to deal with lost items.

 Problem:
No official lost & found system.

Students rely on sticky notes and scattered social media posts.

Leads to confusion and low item recovery rates.

Goals & Features:
 Users can post Lost or Found items.

 Include description, optional image, and location.

Confirmation email sent after posting.

 Browse, filter by Lost/Found, and view post details.

 Logged-in users can comment, edit, or delete their own posts.

 Only registered users can post or comment.

👀 Guests can browse posts only.

⚙️ Setup Instructions:
🐍 1. Create & Activate Virtual Environment
bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate
📦 2. Install Dependencies
bash
Copy
Edit
pip install flask flask-wtf flask-sqlalchemy flask-migrate flask-login email-validator pyjwt flask-mail
📄 3. Optional: Create .flaskenv
bash
Copy
Edit
echo "FLASK_APP=app.py" > .flaskenv
🧱 4. Initialize & Migrate Database
bash
Copy
Edit
flask db init
flask db migrate -m "Initial migration"
flask db migrate -m "Transform to Lost & Found, add item fields"
flask db upgrade
6. flask run
