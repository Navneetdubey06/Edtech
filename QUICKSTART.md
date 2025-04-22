# Learning Portal Quick Start Guide

This guide will help you quickly get the Learning Portal up and running on Replit.

## Current Environment Setup

Your learning portal is already configured with:
- Flask web application framework
- PostgreSQL database integration
- Stripe payment processing
- Course management system
- Quiz functionality
- User authentication

## Getting Started in 5 Steps

### 1. Start the Application
The application is already running. If you need to restart it, use the "Run" button in Replit.

### 2. Create an Admin Account
1. Go to `/register` in the webview
2. Fill out the registration form with:
   - Username
   - Email
   - First Name
   - Last Name
   - Password (at least 8 characters)
   - Confirm Password
3. Click "Register"

### 3. Promote Your Account to Admin
Run this SQL command to give yourself admin privileges:

```sql
UPDATE users SET role = 1 WHERE email = 'your_email@example.com';
```

Replace 'your_email@example.com' with the email you used to register.

### 4. Log in as Admin
1. Go to `/admin/login`
2. Enter your email and password
3. Click "Login"

### 5. Create and Manage Content
As an admin, you can now:
- Create courses (including paid courses)
- Add chapters and lessons to courses
- Create quizzes and questions
- Manage users
- View payment transactions

## Testing Payments

To test the payment system:
1. Create a course with a price (e.g., $9.99)
2. For Stripe integration, you can either:
   - Set a Stripe Price ID (if you have one)
   - Leave it blank to create on-the-fly payment items
3. Register a student account (use a different email)
4. Browse courses and attempt to enroll in a paid course
5. Use Stripe's test card number: 4242 4242 4242 4242
   - Any future expiration date
   - Any 3-digit CVC
   - Any ZIP code

## Key URLs
- Homepage: `/`
- Student Registration: `/register`
- Student Login: `/login`
- Admin Login: `/admin/login`
- Student Dashboard: `/dashboard`
- Admin Dashboard: `/admin/dashboard`
- Course Catalog: `/courses`

## Environment Variables
The following environment variables are already set up:
- `DATABASE_URL`: Connection string for the PostgreSQL database
- `STRIPE_SECRET_KEY`: Your Stripe API key for payment processing
- `SESSION_SECRET`: Secret key for session management

## Need Help?

If you encounter any issues:
1. Check the application logs in the Replit console
2. Review the SETUP_GUIDE.md file for more detailed information
3. Visit the Stripe documentation for payment integration help:
   https://stripe.com/docs/checkout