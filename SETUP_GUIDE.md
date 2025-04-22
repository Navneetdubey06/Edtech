# Learning Portal Setup Guide

This document provides instructions for setting up the Learning Portal application locally or on a server.


## Installation Steps

### 1. Clone the Repository or download as zip


### 2. Set Up Virtual Environment 
python -m venv venv
source venv/bin/activate  

### 3. Install Dependencies
pip install -r requirements.txt
if it doesnt work use this in terminal after entering venv
'''
pip install Flask==2.2.5
Flask-Login==0.6.2
Flask-SocketIO==5.3.2
SQLAlchemy==1.4.46
Werkzeug==2.2.3
Jinja2==3.1.2
itsdangerous==2.1.2
click==8.1.3
python-dotenv==0.21.0
eventlet==0.33.3
requests==2.28.2
gunicorn==20.1.0
email-validator==2.0.0
flask==2.3.3
flask-login==0.6.2
flask-sqlalchemy==3.1.1
flask-wtf==1.2.1
gunicorn==23.0.0
psycopg2-binary==2.9.9
sqlalchemy==2.0.21
stripe==12.0.1
werkzeug==2.3.7
wtforms==3.0.1
'''
### 4. Set Up Environment Variables
change .env file values

For production, make sure to set a strong random value for `SESSION_SECRET`.

### 5. Set Up the Database

# Create a PostgreSQL database
createdb learning_portal  #you can use any db name on your pg admin 4(firstly install postgresql)
When first running the application, the database tables will be created automatically.

### 6. Run the Application
run in bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app


For development, you can also use:
run in bash
flask run --host=0.0.0.0 --port=5000


## Initial Setup

### 1. Create an Admin Account
1. Navigate to `/register` and create a regular user account
2. Use the following SQL command to promote the user to admin status:
   ```sql
   UPDATE users SET role = 1 WHERE email = 'your_email@example.com';
   ```

### 2. Set Up Stripe Integration
1. Log in to your Stripe Dashboard (https://dashboard.stripe.com/)
2. Create products and price IDs for your courses
3. Add the price IDs to your courses in the admin dashboard

### 3. Create Courses and Content
1. Log in as an admin
2. Navigate to the admin dashboard
3. Create courses, chapters, lessons, and quizzes

## Directory Structure

```
/
├── app.py              # Main Flask application setup
├── main.py             # Application entry point
├── models.py           # Database models
├── forms.py            # WTForms definitions
├── routes/             # Route handlers
│   ├── __init__.py
│   ├── admin.py        # Admin routes
│   ├── auth.py         # Authentication routes
│   ├── courses.py      # Course viewing routes
│   ├── payments.py     # Payment processing
│   └── quiz.py         # Quiz functionality
├── templates/          # Jinja2 HTML templates
│   ├── admin/          # Admin interface templates
│   ├── auth/           # Login/registration templates
│   ├── student/        # Student-facing templates
│   └── base.html       # Base template
└── static/             # Static assets
    ├── css/
    └── js/
```

## Testing Payments

To test the payment system:
1. Use Stripe's test cards (e.g., 4242 4242 4242 4242)
2. Set the expiration date to a future date
3. Use any 3-digit CVC code
4. For more test cards with different behaviors, see https://stripe.com/docs/testing

