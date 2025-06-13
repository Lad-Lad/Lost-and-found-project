Client:
Campus counseling Office at University of something
Client Background:
The Campus Life Office manages student wellbeing and events on campus. They’ve received complaints about lost items and want a centralized, digital solution to reduce lost item confusion.
Client Problem:
Students and staff frequently lose or find items on campus, but there’s no official online bulletin board to report or view them. The only methods now are sticky notes on walls or scattered social media posts.
Client Goals:
Allow users to post details and photos of lost or found items.


Differentiate posts clearly between "Lost" and "Found".


Include optional fields like location.


Enable users to manage (edit/delete) their own posts.


Send confirmation emails when posts are submitted.


Support image uploads for better item identification.


Allow only registered users to post or comment.

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
and also pip install flask_moment
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
The Campus Lost & Found Board allows registered users at the University of Something to report and search for lost or found items. Users can create posts by selecting "Lost" or "Found," adding a description, uploading an optional image, and specifying the location. Each submission triggers a confirmation email. Logged-in users can comment on posts, as well as edit or delete their own. All users can browse and filter posts by type, while guests must sign up or log in to contribute. The platform streamlines item recovery and replaces outdated methods like sticky notes and random social media posts.