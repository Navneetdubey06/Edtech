from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField, BooleanField, SelectField, IntegerField, RadioField, HiddenField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, URL
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class CourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    stripe_price_id = StringField('Stripe Price ID', validators=[Optional()])
    image_url = StringField('Image URL', validators=[Optional()])
    submit = SubmitField('Save Course')

class ChapterForm(FlaskForm):
    title = StringField('Chapter Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[Optional()])
    order = IntegerField('Order', validators=[DataRequired()])
    submit = SubmitField('Save Chapter')

class LessonForm(FlaskForm):
    title = StringField('Lesson Title', validators=[DataRequired(), Length(max=120)])
    content = TextAreaField('Content', validators=[Optional()])
    content_type = SelectField('Content Type', choices=[
        ('text', 'Text'), 
        ('video', 'Video'), 
        ('pdf', 'PDF')
    ])
    video_url = StringField('Video URL', validators=[Optional(), URL()])
    order = IntegerField('Order', validators=[DataRequired()])
    estimated_time = IntegerField('Estimated Time (minutes)', validators=[Optional()])
    submit = SubmitField('Save Lesson')

class QuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[Optional()])
    passing_score = IntegerField('Passing Score (%)', validators=[DataRequired()])
    submit = SubmitField('Save Quiz')

class QuestionForm(FlaskForm):
    text = TextAreaField('Question Text', validators=[DataRequired()])
    question_type = SelectField('Question Type', choices=[
        ('mcq', 'Multiple Choice'), 
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer')
    ])
    options = TextAreaField('Options (one per line, for Multiple Choice)', validators=[Optional()])
    correct_answer = StringField('Correct Answer', validators=[DataRequired()])
    points = IntegerField('Points', validators=[DataRequired()])
    submit = SubmitField('Save Question')

class QuizAttemptForm(FlaskForm):
    quiz_id = HiddenField('Quiz ID')
    submit = SubmitField('Submit Quiz')
    # Dynamic fields for questions will be added in the route

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')
