from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField, RadioField, SelectField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Log In")

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    password_confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match")])
    role = RadioField("Role", choices=[("student", "Student"), ("instructor", "Instructor")], validators=[DataRequired()])
    submit = SubmitField("Create Account")

class CreateAssignmentForm(FlaskForm):
    title = StringField("Assignment Title", validators=[DataRequired(), Length(max=128)])
    description = StringField("Description", validators=[DataRequired(), Length(max=512)])
    due_date = DateField("Due Date", format="%Y-%m-%d", validators=[DataRequired()])
    course_id = SelectField("Course", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Create Assignment")

class CreateCourseForm(FlaskForm):
    name = StringField("Course Name", validators=[DataRequired(), Length(max=128)])
    code = StringField("Course Code", validators=[DataRequired(), Length(max=32)])
    description = StringField("Course Description", validators=[DataRequired(), Length(max=512)])
    submit = SubmitField("Create Course")

class EnrollStudentForm(FlaskForm):
    student_identifier = StringField("Student Username or Email", validators=[DataRequired(), Length(min=3, max=120)])
    submit = SubmitField("Add Student")