from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify, abort
from models import User, Course, Chapter, Quiz, Question, QuizAttempt, Enrollment
from routes.auth import student_login_required, admin_login_required
from app import db
from forms import QuizForm, QuestionForm, QuizAttemptForm
from datetime import datetime
import json

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/course/<int:course_id>/chapter/<int:chapter_id>/quiz/<int:quiz_id>')
@student_login_required
def take_quiz(course_id, chapter_id, quiz_id):
    user_id = session['user_id']
    
    # Check if user is enrolled
    enrollment = Enrollment.query.filter_by(
        user_id=user_id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        flash('You need to enroll in this course to take quizzes.', 'warning')
        return redirect(url_for('courses.course_detail', course_id=course_id))
    
    # Get quiz and questions
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Make sure the quiz belongs to the chapter and the chapter belongs to the course
    chapter = Chapter.query.get_or_404(chapter_id)
    if quiz.chapter_id != chapter.id or chapter.course_id != course_id:
        abort(404)
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if not questions:
        flash('This quiz has no questions yet.', 'warning')
        return redirect(url_for('courses.course_detail', course_id=course_id))
    
    # Create a form with dynamic fields for each question
    form = QuizAttemptForm()
    form.quiz_id.data = quiz_id
    
    # Check if the user has already taken this quiz
    previous_attempts = QuizAttempt.query.filter_by(
        user_id=user_id,
        quiz_id=quiz_id
    ).order_by(QuizAttempt.started_at.desc()).all()
    
    return render_template('student/quiz.html',
                           course_id=course_id,
                           chapter_id=chapter_id,
                           quiz=quiz,
                           questions=questions,
                           form=form,
                           previous_attempts=previous_attempts)

@quiz_bp.route('/course/<int:course_id>/chapter/<int:chapter_id>/quiz/<int:quiz_id>/submit', methods=['POST'])
@student_login_required
def submit_quiz(course_id, chapter_id, quiz_id):
    user_id = session['user_id']
    
    # Check if user is enrolled
    enrollment = Enrollment.query.filter_by(
        user_id=user_id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        flash('You need to enroll in this course to take quizzes.', 'warning')
        return redirect(url_for('courses.course_detail', course_id=course_id))
    
    # Get quiz and questions
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    # Create a new quiz attempt
    quiz_attempt = QuizAttempt(
        user_id=user_id,
        quiz_id=quiz_id,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow()
    )
    
    # Process submitted answers
    answers = {}
    total_points = 0
    earned_points = 0
    
    for question in questions:
        answer_key = f'question_{question.id}'
        answer = request.form.get(answer_key, '')
        answers[str(question.id)] = answer
        
        total_points += question.points
        
        # Check if answer is correct
        if question.question_type == 'mcq':
            if answer == question.correct_answer:
                earned_points += question.points
        elif question.question_type == 'true_false':
            if answer.lower() == question.correct_answer.lower():
                earned_points += question.points
        elif question.question_type == 'short_answer':
            # For short answer, we'll do a simple case-insensitive match
            # In a real-world application, you might want more sophisticated matching
            if answer.lower() == question.correct_answer.lower():
                earned_points += question.points
    
    # Calculate score (percentage)
    score = round((earned_points / total_points) * 100) if total_points > 0 else 0
    
    # Update quiz attempt
    quiz_attempt.answers = json.dumps(answers)
    quiz_attempt.score = score
    quiz_attempt.passed = score >= quiz.passing_score
    
    db.session.add(quiz_attempt)
    db.session.commit()
    
    return redirect(url_for('quiz.quiz_results', attempt_id=quiz_attempt.id))

@quiz_bp.route('/quiz_results/<int:attempt_id>')
@student_login_required
def quiz_results(attempt_id):
    user_id = session['user_id']
    
    # Get quiz attempt
    quiz_attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    # Make sure the attempt belongs to the user
    if quiz_attempt.user_id != user_id:
        abort(403)
    
    # Get quiz and questions
    quiz = Quiz.query.get_or_404(quiz_attempt.quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    
    # Get chapter and course for navigation
    chapter = Chapter.query.get_or_404(quiz.chapter_id)
    course = Course.query.get_or_404(chapter.course_id)
    
    # Parse answers
    answers = json.loads(quiz_attempt.answers) if quiz_attempt.answers else {}
    
    return render_template('student/quiz_results.html',
                           quiz_attempt=quiz_attempt,
                           quiz=quiz,
                           questions=questions,
                           answers=answers,
                           chapter=chapter,
                           course=course)

@quiz_bp.route('/admin/chapters/<int:chapter_id>/quizzes/create', methods=['GET', 'POST'])
@admin_login_required
def quiz_create(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    course = Course.query.get_or_404(chapter.course_id)
    
    form = QuizForm()
    
    if form.validate_on_submit():
        quiz = Quiz(
            chapter_id=chapter_id,
            title=form.title.data,
            description=form.description.data,
            passing_score=form.passing_score.data
        )
        
        db.session.add(quiz)
        db.session.commit()
        
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('admin.course_edit', course_id=course.id))
    
    return render_template('admin/quiz_create.html', form=form, chapter=chapter, course=course)

@quiz_bp.route('/admin/quizzes/<int:quiz_id>/edit', methods=['GET', 'POST'])
@admin_login_required
def quiz_edit(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    chapter = Chapter.query.get_or_404(quiz.chapter_id)
    course = Course.query.get_or_404(chapter.course_id)
    
    form = QuizForm(obj=quiz)
    
    if form.validate_on_submit():
        quiz.title = form.title.data
        quiz.description = form.description.data
        quiz.passing_score = form.passing_score.data
        
        db.session.commit()
        
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('admin.course_edit', course_id=course.id))
    
    # Get questions for this quiz
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    return render_template('admin/quiz_edit.html', 
                           form=form, 
                           quiz=quiz, 
                           chapter=chapter, 
                           course=course,
                           questions=questions)

@quiz_bp.route('/admin/quizzes/<int:quiz_id>/delete', methods=['POST'])
@admin_login_required
def quiz_delete(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    chapter = Chapter.query.get_or_404(quiz.chapter_id)
    course = Course.query.get_or_404(chapter.course_id)
    
    # Delete all questions first
    Question.query.filter_by(quiz_id=quiz_id).delete()
    
    # Delete quiz attempts
    QuizAttempt.query.filter_by(quiz_id=quiz_id).delete()
    
    db.session.delete(quiz)
    db.session.commit()
    
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('admin.course_edit', course_id=course.id))

@quiz_bp.route('/admin/quizzes/<int:quiz_id>/questions/create', methods=['GET', 'POST'])
@admin_login_required
def question_create(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    chapter = Chapter.query.get_or_404(quiz.chapter_id)
    course = Course.query.get_or_404(chapter.course_id)
    
    form = QuestionForm()
    
    if form.validate_on_submit():
        # Process options if this is a multiple choice question
        options = None
        if form.question_type.data == 'mcq':
            options_text = form.options.data
            if options_text:
                options = [option.strip() for option in options_text.split('\n') if option.strip()]
        
        question = Question(
            quiz_id=quiz_id,
            text=form.text.data,
            question_type=form.question_type.data,
            options=json.dumps(options) if options else None,
            correct_answer=form.correct_answer.data,
            points=form.points.data
        )
        
        db.session.add(question)
        db.session.commit()
        
        flash('Question created successfully!', 'success')
        return redirect(url_for('quiz.quiz_edit', quiz_id=quiz_id))
    
    return render_template('admin/quiz_create.html', 
                           form=form, 
                           quiz=quiz,
                           chapter=chapter,
                           course=course,
                           is_question=True)

@quiz_bp.route('/admin/questions/<int:question_id>/edit', methods=['GET', 'POST'])
@admin_login_required
def question_edit(question_id):
    question = Question.query.get_or_404(question_id)
    quiz = Quiz.query.get_or_404(question.quiz_id)
    chapter = Chapter.query.get_or_404(quiz.chapter_id)
    course = Course.query.get_or_404(chapter.course_id)
    
    # Prepare form with existing data
    form = QuestionForm(obj=question)
    
    # If options are stored as JSON, convert to newline-separated text for form
    if question.options and form.options.data is None:
        options = json.loads(question.options)
        if options:
            form.options.data = '\n'.join(options)
    
    if form.validate_on_submit():
        # Process options if this is a multiple choice question
        options = None
        if form.question_type.data == 'mcq':
            options_text = form.options.data
            if options_text:
                options = [option.strip() for option in options_text.split('\n') if option.strip()]
        
        question.text = form.text.data
        question.question_type = form.question_type.data
        question.options = json.dumps(options) if options else None
        question.correct_answer = form.correct_answer.data
        question.points = form.points.data
        
        db.session.commit()
        
        flash('Question updated successfully!', 'success')
        return redirect(url_for('quiz.quiz_edit', quiz_id=quiz.id))
    
    return render_template('admin/quiz_edit.html', 
                           form=form, 
                           question=question,
                           quiz=quiz,
                           chapter=chapter,
                           course=course,
                           is_question=True)

@quiz_bp.route('/admin/questions/<int:question_id>/delete', methods=['POST'])
@admin_login_required
def question_delete(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    
    db.session.delete(question)
    db.session.commit()
    
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('quiz.quiz_edit', quiz_id=quiz_id))
