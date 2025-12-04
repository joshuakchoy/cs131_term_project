from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Log In")

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    password_confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match")])
    role = StringField("Role (student or instructor)", validators=[DataRequired(), Length(max=32)])
    submit = SubmitField("Create Account")

class CreateAssignmentForm(FlaskForm):
    title = StringField("Assignment Title", validators=[DataRequired(), Length(max=128)])
    description = StringField("Description", validators=[DataRequired(), Length(max=512)])
    due_date = StringField("Due Date", validators=[DataRequired()])
    submit = SubmitField("Create Assignment")

class CreateCourseForm(FlaskForm):
    name = StringField("Course Name", validators=[DataRequired(), Length(max=128)])
    code = StringField("Course Code", validators=[DataRequired(), Length(max=32)])
    description = StringField("Course Description", validators=[DataRequired(), Length(max=512)])
    submit = SubmitField("Create Course")