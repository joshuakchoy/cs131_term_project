from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import EmailField, PasswordField, SubmitField, StringField, RadioField, SelectField, TextAreaField, FloatField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
from app.models import User

class LoginForm(FlaskForm): # Login form for users
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Log In")

class RegistrationForm(FlaskForm): # Registration form for new users
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    password_confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match")])
    role = RadioField("Role", choices=[("student", "Student"), ("instructor", "Instructor"), ("ta", "Teaching Assistant")], validators=[DataRequired()])
    submit = SubmitField("Create Account")

class ForgotPasswordForm(FlaskForm): # Form to request password reset
    email = EmailField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

class ResetPasswordForm(FlaskForm): # Form to reset password
    password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    password_confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match")])
    submit = SubmitField("Reset Password")

class CreateAssignmentForm(FlaskForm): # Form to create a new assignment
    title = StringField("Assignment Title", validators=[DataRequired(), Length(max=128)])
    description = StringField("Description", validators=[DataRequired(), Length(max=512)])
    due_date = DateField("Due Date", format="%Y-%m-%d", validators=[DataRequired()])
    assignment_type = SelectField("Type", choices=[('homework', 'Homework'), ('quiz', 'Quiz'), ('exam', 'Exam')], validators=[DataRequired()])
    course_id = SelectField("Course", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Create Assignment")

class CreateCourseForm(FlaskForm): # Form to create a new course
    name = StringField("Course Name", validators=[DataRequired(), Length(max=128)])
    code = StringField("Course Code", validators=[DataRequired(), Length(max=32)])
    description = StringField("Course Description", validators=[DataRequired(), Length(max=512)])
    image_url = StringField("Course Image URL (optional)", validators=[Length(max=255)])
    submit = SubmitField("Create Course")

class EnrollStudentForm(FlaskForm): # Form to enroll a student in a course
    student_identifier = StringField("Student Username or Email", validators=[DataRequired(), Length(min=3, max=120)])
    submit = SubmitField("Add Student")

class SubmitAssignmentForm(FlaskForm):# Form to submit an assignment
    content = TextAreaField("Submission Notes (optional)")
    file = FileField("Upload File", validators=[FileAllowed(['pdf', 'doc', 'docx', 'txt', 'zip', 'py', 'java', 'cpp', 'c'], 'Only documents and code files allowed!')])
    submit = SubmitField("Submit Assignment")

class ComposeMessageForm(FlaskForm): # Form to compose a message
    recipient_id = SelectField("To", coerce=int, validators=[DataRequired()])
    subject = StringField("Subject", validators=[DataRequired(), Length(max=128)])
    body = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send Message")

class AnnouncementForm(FlaskForm): # Form to post an announcement
    course_id = SelectField("Course", coerce=int, validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired(), Length(max=128)])
    content = TextAreaField("Announcement", validators=[DataRequired()])
    submit = SubmitField("Post Announcement")

class AssignTAForm(FlaskForm): # Form to assign a TA to a course
    ta_id = SelectField("Teaching Assistant", coerce=int, validators=[DataRequired()])
    course_id = SelectField("Course", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Assign TA")

class GradeSubmissionForm(FlaskForm): # Form to grade a submission
    grade = FloatField("Grade", validators=[DataRequired(), NumberRange(min=0, max=100, message="Grade must be between 0 and 100")])
    feedback = TextAreaField("Feedback (optional)")
    submit = SubmitField("Save Grade")
