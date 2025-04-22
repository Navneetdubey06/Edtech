
A comprehensive online learning platform built with Flask, featuring course management, student progress tracking, quizzes, and integrated payment processing.

## Key Features

1) For Students
User Authentication: Secure registration and login system
Course Catalog: Browse available courses with detailed descriptions
Progress Tracking: Track completed lessons and performance
Self-Evaluation: Take quizzes to test knowledge and receive immediate feedback
Payment Integration: Securely pay for premium courses via Stripe
Personal Dashboard: Monitor enrollment status and achievements

2) For Instructors/Admins
Course Management: Create, edit, and organize courses, chapters, and lessons
Quiz Creation: Develop assessments with various question types
Student Management: View student progress and quiz performance
Payment Tracking: Monitor transactions and revenue

## Technology Stack

Backend: Flask (Python)
Database: PostgreSQL
ORM: SQLAlchemy
Authentication: Flask-Login
Forms: Flask-WTF, WTForms
Payment Processing: Stripe API
Frontend: Bootstrap, HTML, CSS, JavaScript




## Project Structure


/
├── app.py              # Main Flask application setup
├── main.py             # Application entry point
├── models.py           # Database models
├── forms.py            # WTForms definitions
├── routes/             # Route handlers
│   ├── admin.py        # Admin routes
│   ├── auth.py         # Authentication routes
│   ├── courses.py      # Course viewing routes
│   ├── payments.py     # Payment processing
│   └── quiz.py         # Quiz functionality
├── templates/          # Jinja2 HTML templates
│   ├── admin/          # Admin interface templates
│   ├── auth/           # Login/registration templates
│   └── student/        # Student-facing templates
├── static/             # Static assets
│   ├── css/            # Stylesheets
│   └── js/             # JavaScript files
└── scripts/            # Utility scripts
    ├── make_admin.py   # Script to promote a user to admin
    └── make_admin.sql  # SQL to promote a user to admin



## Creating Courses

As an admin, you can:
1. Create courses with pricing options
2. Add chapters to organize content
3. Add lessons with various content types (text, video, PDF)
4. Create quizzes to assess student understanding

## Stripe Integration

The platform uses Stripe Checkout for payment processing. When creating paid courses:
1. You can use a Stripe Price ID (if you have products set up in Stripe)
2. Alternatively, the system can create on-the-fly payment items

For testing, use Stripe's test cards (e.g., 4242 4242 4242 4242).

