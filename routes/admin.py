from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort, jsonify
from models import User, Course, Chapter, Lesson, Quiz, Question, Enrollment, Payment, ROLE_ADMIN
from routes.auth import admin_login_required
from app import db
from forms import CourseForm, ChapterForm, LessonForm, QuizForm, QuestionForm
from werkzeug.security import generate_password_hash
import json
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_login_required
def dashboard():
    # Get counts for dashboard
    course_count = Course.query.count()
    student_count = User.query.filter_by(role=0).count()  # 0 = student role
    enrollment_count = Enrollment.query.count()
    payment_count = Payment.query.filter_by(status='completed').count()
    
    # Get recent enrollments
    recent_enrollments = (
        Enrollment.query
        .order_by(Enrollment.enrolled_date.desc())
        .limit(10)
        .all()
    )
    
    # Prepare enrollment data with user and course details
    enrollment_data = []
    for enrollment in recent_enrollments:
        user = User.query.get(enrollment.user_id)
        course = Course.query.get(enrollment.course_id)
        
        if user and course:
            enrollment_data.append({
                'enrollment': enrollment,
                'user': user,
                'course': course
            })
    
    # Get recent payments
    recent_payments = (
        Payment.query
        .filter_by(status='completed')
        .order_by(Payment.created_at.desc())
        .limit(10)
        .all()
    )
    
    # Prepare payment data with user and course details
    payment_data = []
    for payment in recent_payments:
        user = User.query.get(payment.user_id)
        course = Course.query.get(payment.course_id)
        
        if user and course:
            payment_data.append({
                'payment': payment,
                'user': user,
                'course': course
            })
    
    return render_template('admin/dashboard.html',
                           course_count=course_count,
                           student_count=student_count,
                           enrollment_count=enrollment_count,
                           payment_count=payment_count,
                           enrollment_data=enrollment_data,
                           payment_data=payment_data)

@admin_bp.route('/courses')
@admin_login_required
def course_management():
    courses = Course.query.all()
    return render_template('admin/course_management.html', courses=courses)

@admin_bp.route('/courses/create', methods=['GET', 'POST'])
@admin_login_required
def course_create():
    form = CourseForm()
    
    if form.validate_on_submit():
        course = Course(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            stripe_price_id=form.stripe_price_id.data,
            image_url=form.image_url.data,
            created_by=session['user_id']
        )
        
        db.session.add(course)
        db.session.commit()
        
        flash('Course created successfully!', 'success')
        return redirect(url_for('admin.course_management'))
    
    return render_template('admin/course_create.html', form=form)

@admin_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@admin_login_required
def course_edit(course_id):
    course = Course.query.get_or_404(course_id)
    form = CourseForm(obj=course)
    
    if form.validate_on_submit():
        course.title = form.title.data
        course.description = form.description.data
        course.price = form.price.data
        course.stripe_price_id = form.stripe_price_id.data
        course.image_url = form.image_url.data
        course.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Course updated successfully!', 'success')
        return redirect(url_for('admin.course_management'))
    
    return render_template('admin/course_edit.html', form=form, course=course)

@admin_bp.route('/courses/<int:course_id>/delete', methods=['POST'])
@admin_login_required
def course_delete(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Delete all chapters and lessons first (cascading delete)
    for chapter in Chapter.query.filter_by(course_id=course_id).all():
        Lesson.query.filter_by(chapter_id=chapter.id).delete()
        db.session.delete(chapter)
    
    # Delete enrollments and payments
    Enrollment.query.filter_by(course_id=course_id).delete()
    Payment.query.filter_by(course_id=course_id).delete()
    
    db.session.delete(course)
    db.session.commit()
    
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('admin.course_management'))

@admin_bp.route('/courses/<int:course_id>/chapters')
@admin_login_required
def chapter_management(course_id):
    course = Course.query.get_or_404(course_id)
    chapters = Chapter.query.filter_by(course_id=course_id).order_by(Chapter.order).all()
    
    return render_template('admin/course_edit.html', course=course, chapters=chapters)

@admin_bp.route('/courses/<int:course_id>/chapters/create', methods=['GET', 'POST'])
@admin_login_required
def chapter_create(course_id):
    course = Course.query.get_or_404(course_id)
    form = ChapterForm()
    
    if form.validate_on_submit():
        chapter = Chapter(
            course_id=course_id,
            title=form.title.data,
            description=form.description.data,
            order=form.order.data
        )
        
        db.session.add(chapter)
        db.session.commit()
        
        flash('Chapter created successfully!', 'success')
        return redirect(url_for('admin.course_edit', course_id=course_id))
    
    return render_template('admin/course_edit.html', form=form, course=course)

@admin_bp.route('/chapters/<int:chapter_id>/edit', methods=['GET', 'POST'])
@admin_login_required
def chapter_edit(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    form = ChapterForm(obj=chapter)
    
    if form.validate_on_submit():
        chapter.title = form.title.data
        chapter.description = form.description.data
        chapter.order = form.order.data
        
        db.session.commit()
        
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('admin.course_edit', course_id=chapter.course_id))
    
    return render_template('admin/course_edit.html', form=form, chapter=chapter)

@admin_bp.route('/chapters/<int:chapter_id>/delete', methods=['POST'])
@admin_login_required
def chapter_delete(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    course_id = chapter.course_id
    
    # Delete all lessons first
    Lesson.query.filter_by(chapter_id=chapter_id).delete()
    
    db.session.delete(chapter)
    db.session.commit()
    
    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('admin.course_edit', course_id=course_id))

@admin_bp.route('/chapters/<int:chapter_id>/lessons/create', methods=['GET', 'POST'])
@admin_login_required
def lesson_create(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    form = LessonForm()
    
    if form.validate_on_submit():
        lesson = Lesson(
            chapter_id=chapter_id,
            title=form.title.data,
            content=form.content.data,
            content_type=form.content_type.data,
            video_url=form.video_url.data,
            order=form.order.data,
            estimated_time=form.estimated_time.data
        )
        
        db.session.add(lesson)
        db.session.commit()
        
        flash('Lesson created successfully!', 'success')
        return redirect(url_for('admin.course_edit', course_id=chapter.course_id))
    
    return render_template('admin/course_edit.html', form=form, chapter=chapter)

@admin_bp.route('/lessons/<int:lesson_id>/edit', methods=['GET', 'POST'])
@admin_login_required
def lesson_edit(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    chapter = Chapter.query.get_or_404(lesson.chapter_id)
    form = LessonForm(obj=lesson)
    
    if form.validate_on_submit():
        lesson.title = form.title.data
        lesson.content = form.content.data
        lesson.content_type = form.content_type.data
        lesson.video_url = form.video_url.data
        lesson.order = form.order.data
        lesson.estimated_time = form.estimated_time.data
        
        db.session.commit()
        
        flash('Lesson updated successfully!', 'success')
        return redirect(url_for('admin.course_edit', course_id=chapter.course_id))
    
    return render_template('admin/course_edit.html', form=form, lesson=lesson, chapter=chapter)

@admin_bp.route('/lessons/<int:lesson_id>/delete', methods=['POST'])
@admin_login_required
def lesson_delete(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    chapter = Chapter.query.get_or_404(lesson.chapter_id)
    
    db.session.delete(lesson)
    db.session.commit()
    
    flash('Lesson deleted successfully!', 'success')
    return redirect(url_for('admin.course_edit', course_id=chapter.course_id))

@admin_bp.route('/users')
@admin_login_required
def user_management():
    users = User.query.all()
    return render_template('admin/user_management.html', users=users)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_login_required
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.role = int(request.form.get('role', 0))
        
        # Only update password if provided
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.user_management'))
    
    return render_template('admin/user_edit.html', user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_login_required
def user_delete(user_id):
    if user_id == session['user_id']:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admin.user_management'))
    
    user = User.query.get_or_404(user_id)
    
    # Delete user's enrollments and payments
    Enrollment.query.filter_by(user_id=user_id).delete()
    Payment.query.filter_by(user_id=user_id).delete()
    
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.user_management'))

@admin_bp.route('/payments')
@admin_login_required
def payment_management():
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    
    payment_data = []
    for payment in payments:
        user = User.query.get(payment.user_id)
        course = Course.query.get(payment.course_id)
        
        if user and course:
            payment_data.append({
                'payment': payment,
                'user': user,
                'course': course
            })
    
    return render_template('admin/payment_management.html', payment_data=payment_data)
