from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify, current_app, abort
from models import User, Course, Enrollment, Payment
from routes.auth import student_login_required
from app import db
import stripe
import os
from datetime import datetime

payments_bp = Blueprint('payments', __name__)

# Set Stripe API key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

@payments_bp.route('/enroll/<int:course_id>')
@student_login_required
def enroll(course_id):
    user_id = session['user_id']
    course = Course.query.get_or_404(course_id)
    
    # Check if user is already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        user_id=user_id,
        course_id=course_id
    ).first()
    
    if existing_enrollment:
        flash('You are already enrolled in this course!', 'warning')
        return redirect(url_for('courses.course_detail', course_id=course_id))
    
    # Check if course is free or paid
    if course.price <= 0:
        # For free courses, directly create enrollment
        enrollment = Enrollment(
            user_id=user_id,
            course_id=course_id,
            enrolled_date=datetime.utcnow()
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        flash('You have successfully enrolled in this course!', 'success')
        return redirect(url_for('courses.course_detail', course_id=course_id))
    else:
        # For paid courses, redirect to payment page
        return redirect(url_for('payments.payment_page', course_id=course_id))

@payments_bp.route('/payment/<int:course_id>')
@student_login_required
def payment_page(course_id):
    user_id = session['user_id']
    course = Course.query.get_or_404(course_id)
    user = User.query.get_or_404(user_id)
    
    # Check if user is already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        user_id=user_id,
        course_id=course_id
    ).first()
    
    if existing_enrollment:
        flash('You are already enrolled in this course!', 'warning')
        return redirect(url_for('courses.course_detail', course_id=course_id))
    
    return render_template('student/payment.html', course=course, user=user)

@payments_bp.route('/create-checkout-session', methods=['POST'])
@student_login_required
def create_checkout_session():
    course_id = request.form.get('course_id')
    if not course_id:
        return jsonify({'error': 'Missing course_id'}), 400
    
    course = Course.query.get_or_404(int(course_id))
    user_id = session['user_id']
    
    # Get domain for success and cancel URLs
    YOUR_DOMAIN = request.host_url.rstrip('/')
    
    # Create a new payment record
    payment = Payment(
        user_id=user_id,
        course_id=course.id,
        amount=course.price,
        currency='USD',
        status='pending'
    )
    
    db.session.add(payment)
    db.session.commit()
    
    # Use Stripe Price ID if available, otherwise create line items directly
    if course.stripe_price_id:
        line_items = [
            {
                'price': course.stripe_price_id,
                'quantity': 1,
            }
        ]
    else:
        line_items = [
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': course.title,
                        'description': course.description[:255] if course.description else '',
                    },
                    'unit_amount': int(course.price * 100),  # Stripe uses cents
                },
                'quantity': 1,
            }
        ]
    
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=f"{YOUR_DOMAIN}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{YOUR_DOMAIN}/payment/cancel?payment_id={payment.id}",
            client_reference_id=str(payment.id),
            customer_email=User.query.get(user_id).email,
            metadata={
                'payment_id': payment.id,
                'course_id': course.id,
                'user_id': user_id
            }
        )
        
        # Update payment record with checkout session ID
        payment.stripe_checkout_id = checkout_session.id
        db.session.commit()
        
        return redirect(checkout_session.url, code=303)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/payment/success')
@student_login_required
def payment_success():
    session_id = request.args.get('session_id')
    if not session_id:
        flash('Invalid payment session.', 'danger')
        return redirect(url_for('courses.course_catalog'))
    
    try:
        # Retrieve the checkout session
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # Get the payment from the database
        payment = Payment.query.filter_by(stripe_checkout_id=session_id).first()
        
        if not payment:
            # Try to get from metadata if not found directly
            payment_id = checkout_session.metadata.get('payment_id')
            if payment_id:
                payment = Payment.query.get(int(payment_id))
            
            if not payment:
                flash('Payment record not found.', 'danger')
                return redirect(url_for('courses.course_catalog'))
        
        # Update payment status
        payment.status = 'completed'
        payment.stripe_payment_id = checkout_session.payment_intent
        
        # Create enrollment
        enrollment = Enrollment.query.filter_by(
            user_id=payment.user_id,
            course_id=payment.course_id
        ).first()
        
        if not enrollment:
            enrollment = Enrollment(
                user_id=payment.user_id,
                course_id=payment.course_id,
                enrolled_date=datetime.utcnow()
            )
            db.session.add(enrollment)
        
        db.session.commit()
        
        course = Course.query.get(payment.course_id)
        
        flash('Payment successful! You are now enrolled in the course.', 'success')
        return render_template('student/payment_success.html', course=course)
    
    except Exception as e:
        flash(f'Error processing payment: {str(e)}', 'danger')
        return redirect(url_for('courses.course_catalog'))

@payments_bp.route('/payment/cancel')
@student_login_required
def payment_cancel():
    payment_id = request.args.get('payment_id')
    
    if payment_id:
        payment = Payment.query.get(int(payment_id))
        if payment:
            payment.status = 'failed'
            db.session.commit()
            
            course = Course.query.get(payment.course_id)
            return render_template('student/payment_cancel.html', course=course)
    
    flash('Payment was cancelled.', 'warning')
    return redirect(url_for('courses.course_catalog'))

@payments_bp.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'error': str(e)}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error': str(e)}), 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        fulfill_order(session)
    
    return jsonify({'status': 'success'})

def fulfill_order(session):
    # Get the payment from the database
    payment_id = session.get('client_reference_id')
    if not payment_id:
        payment_id = session.metadata.get('payment_id')
    
    if payment_id:
        payment = Payment.query.get(int(payment_id))
        if payment:
            # Update payment status
            payment.status = 'completed'
            payment.stripe_payment_id = session.payment_intent
            
            # Create enrollment
            enrollment = Enrollment.query.filter_by(
                user_id=payment.user_id,
                course_id=payment.course_id
            ).first()
            
            if not enrollment:
                enrollment = Enrollment(
                    user_id=payment.user_id,
                    course_id=payment.course_id,
                    enrolled_date=datetime.utcnow()
                )
                db.session.add(enrollment)
            
            db.session.commit()
