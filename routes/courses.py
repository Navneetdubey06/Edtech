from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from models import User, Course, Chapter, Lesson, Enrollment, Progress
from routes.auth import student_login_required
from app import db
from forms import ProfileForm
from datetime import datetime

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/dashboard')
@student_login_required
def student_dashboard():
    user = User.query.get(session['user_id'])
    enrollments = Enrollment.query.filter_by(user_id=user.id).all()
    
    courses_data = []
    for enrollment in enrollments:
        course = Course.query.get(enrollment.course_id)
        if course:
            # Calculate progress percentage
            total_lessons = 0
            completed_lessons = 0
            
            for chapter in course.chapters:
                lessons = Lesson.query.filter_by(chapter_id=chapter.id).all()
                total_lessons += len(lessons)
                
                for lesson in lessons:
                    progress = Progress.query.filter_by(
                        user_id=user.id,
                        lesson_id=lesson.id
                    ).first()
                    
                    if progress and progress.completed:
                        completed_lessons += 1
            
            progress_percentage = 0
            if total_lessons > 0:
                progress_percentage = (completed_lessons / total_lessons) * 100
            
            courses_data.append({
                'course': course,
                'enrollment': enrollment,
                'progress': progress_percentage
            })
    
    return render_template('student/dashboard.html', courses_data=courses_data, user=user)

@courses_bp.route('/profile', methods=['GET', 'POST'])
@student_login_required
def profile():
    user = User.query.get(session['user_id'])
    form = ProfileForm(obj=user)
    
    if form.validate_on_submit():
        # Check if username is changed and already exists
        if form.username.data != user.username and User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'danger')
            return render_template('student/profile.html', form=form, user=user)
        
        # Check if email is changed and already exists
        if form.email.data != user.email and User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return render_template('student/profile.html', form=form, user=user)
        
        user.username = form.username.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('courses.profile'))
    
    return render_template('student/profile.html', form=form, user=user)

@courses_bp.route('/courses')
@student_login_required
def course_catalog():
    courses = Course.query.all()
    user_id = session['user_id']
    
    # Check which courses the user is already enrolled in
    user_enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    enrolled_course_ids = [e.course_id for e in user_enrollments]
    
    return render_template('student/course_catalog.html', 
                           courses=courses, 
                           enrolled_course_ids=enrolled_course_ids)

@courses_bp.route('/course/<int:course_id>')
@student_login_required
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    user_id = session['user_id']
    
    # Check if user is enrolled
    enrollment = Enrollment.query.filter_by(
        user_id=user_id,
        course_id=course_id
    ).first()
    
    is_enrolled = enrollment is not None
    
    # Get chapters and lessons
    chapters = Chapter.query.filter_by(course_id=course_id).order_by(Chapter.order).all()
    
    return render_template('student/course_detail.html', 
                           course=course, 
                           chapters=chapters, 
                           is_enrolled=is_enrolled)

@courses_bp.route('/course/<int:course_id>/chapter/<int:chapter_id>/lesson/<int:lesson_id>')
@student_login_required
def course_content(course_id, chapter_id, lesson_id):
    user_id = session['user_id']
    
    # Check if user is enrolled
    enrollment = Enrollment.query.filter_by(
        user_id=user_id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        flash('You need to enroll in this course to access its content.', 'warning')
        return redirect(url_for('courses.course_detail', course_id=course_id))
    
    # Get course, chapter, and lesson
    course = Course.query.get_or_404(course_id)
    chapter = Chapter.query.get_or_404(chapter_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Make sure the lesson belongs to the chapter and the chapter belongs to the course
    if lesson.chapter_id != chapter.id or chapter.course_id != course.id:
        abort(404)
    
    # Get user progress for this lesson
    progress = Progress.query.filter_by(
        user_id=user_id,
        lesson_id=lesson_id
    ).first()
    
    # If there's no progress record for this lesson, create one
    if not progress:
        progress = Progress(
            user_id=user_id,
            lesson_id=lesson_id,
            completed=False,
            last_accessed=datetime.utcnow()
        )
        db.session.add(progress)
    else:
        # Update last_accessed time
        progress.last_accessed = datetime.utcnow()
    
    # Update enrollment's last_accessed time
    enrollment.last_accessed = datetime.utcnow()
    
    db.session.commit()
    
    # Get all lessons for navigation
    all_chapters = Chapter.query.filter_by(course_id=course_id).order_by(Chapter.order).all()
    chapter_lessons = {}
    for ch in all_chapters:
        chapter_lessons[ch.id] = Lesson.query.filter_by(chapter_id=ch.id).order_by(Lesson.order).all()
    
    # Find previous and next lessons for navigation
    prev_lesson, next_lesson = None, None
    all_lessons = []
    for ch in all_chapters:
        lessons = Lesson.query.filter_by(chapter_id=ch.id).order_by(Lesson.order).all()
        all_lessons.extend(lessons)
    
    for i, l in enumerate(all_lessons):
        if l.id == lesson_id:
            if i > 0:
                prev_lesson = all_lessons[i-1]
            if i < len(all_lessons) - 1:
                next_lesson = all_lessons[i+1]
            break
    
    return render_template('student/course_content.html',
                           course=course,
                           chapter=chapter,
                           lesson=lesson,
                           progress=progress,
                           all_chapters=all_chapters,
                           chapter_lessons=chapter_lessons,
                           prev_lesson=prev_lesson,
                           next_lesson=next_lesson)

@courses_bp.route('/course/<int:course_id>/chapter/<int:chapter_id>/lesson/<int:lesson_id>/complete', methods=['POST'])
@student_login_required
def complete_lesson(course_id, chapter_id, lesson_id):
    user_id = session['user_id']
    
    # Check if user is enrolled
    enrollment = Enrollment.query.filter_by(
        user_id=user_id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        flash('You need to enroll in this course to mark lessons as complete.', 'warning')
        return redirect(url_for('courses.course_detail', course_id=course_id))
    
    # Get user progress for this lesson
    progress = Progress.query.filter_by(
        user_id=user_id,
        lesson_id=lesson_id
    ).first()
    
    # If there's no progress record for this lesson, create one
    if not progress:
        progress = Progress(
            user_id=user_id,
            lesson_id=lesson_id,
            completed=True,
            last_accessed=datetime.utcnow()
        )
        db.session.add(progress)
    else:
        # Mark as completed
        progress.completed = True
        progress.last_accessed = datetime.utcnow()
    
    db.session.commit()
    
    # Check if all lessons in the course are completed
    course_completed = True
    for chapter in Chapter.query.filter_by(course_id=course_id).all():
        for lesson in Lesson.query.filter_by(chapter_id=chapter.id).all():
            lesson_progress = Progress.query.filter_by(
                user_id=user_id,
                lesson_id=lesson.id
            ).first()
            
            if not lesson_progress or not lesson_progress.completed:
                course_completed = False
                break
        
        if not course_completed:
            break
    
    # If all lessons are completed, mark the enrollment as completed
    if course_completed:
        enrollment.completed = True
        db.session.commit()
        flash('Congratulations! You have completed this course.', 'success')
    
    flash('Lesson marked as complete!', 'success')
    return redirect(url_for('courses.course_content', course_id=course_id, chapter_id=chapter_id, lesson_id=lesson_id))
