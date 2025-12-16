from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    # information
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False) # student or instructor
    password_hash = db.Column(db.String(255), nullable=False)

    # relationships
    courses_taught = db.relationship('Course', back_populates='instructor', lazy=True)
    courses_enrolled = db.relationship('Enrollment', back_populates='student', lazy=True)
    submissions = db.relationship('Submission', back_populates='student', lazy=True)
    ta_assignments = db.relationship('TAAssignment', back_populates='ta', lazy=True)

    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password) 

    def get_reset_token(self, expires_in=3600): #For password reset
        """Generate a password reset token (valid for 1 hour by default)"""
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}) 

    @staticmethod
    def verify_reset_token(token, max_age=3600):
        """Verify a password reset token and return the user if valid"""
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=max_age)
            user_id = data['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"<User {self.username}>"

class Course(db.Model):
    # information
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=True)
    code = db.Column(db.String(32), unique=True, nullable=False)
    teacher = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)  # optional course image

    # relationships
    instructor = db.relationship('User', back_populates='courses_taught')
    assignments = db.relationship('Assignment', back_populates='course', lazy=True, cascade="all, delete-orphan")
    enrollments = db.relationship('Enrollment', back_populates='course', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Course {self.title}>"

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    # relationships
    student = db.relationship('User', back_populates='courses_enrolled')
    course = db.relationship('Course', back_populates='enrollments')

    def __repr__(self):
        return f"<Enrollment StudentID: {self.student_id}, CourseID: {self.course_id}>"

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.String(64), nullable=False)
    assignment_type = db.Column(db.String(32), nullable=False, default='homework')
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True)

    # relationships
    course = db.relationship('Course', back_populates='assignments')
    submissions = db.relationship('Submission', back_populates='assignment', lazy=True)

    def __repr__(self):
        return f"<Assignment {self.title}>"
    
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=True)  # Optional text content
    file_path = db.Column(db.String(255), nullable=True)  # Path to uploaded file
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    grade = db.Column(db.Float, nullable=True)

    # relationships
    assignment = db.relationship('Assignment', back_populates='submissions')
    student = db.relationship('User', back_populates='submissions')

    def __repr__(self):
        return f"<Submission AssignmentID: {self.assignment_id}, StudentID: {self.student_id}>"

class TAAssignment(db.Model):
    """Tracks which TAs are assigned to which courses"""
    id = db.Column(db.Integer, primary_key=True)
    ta_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    # relationships
    ta = db.relationship('User', back_populates='ta_assignments')
    course = db.relationship('Course', backref='ta_assignments')
    
    def __repr__(self):
        return f"<TAAssignment TA: {self.ta_id}, Course: {self.course_id}>"

class Message(db.Model):
    """One-on-one messages between users"""
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(128), nullable=False)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    
    # relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='messages_sent')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='messages_received')
    
    def __repr__(self):
        return f"<Message from {self.sender_id} to {self.recipient_id}>"

class Announcement(db.Model):
    """Course-wide announcements from instructors/TAs"""
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # relationships
    course = db.relationship('Course', backref='announcements')
    author = db.relationship('User', backref='announcements_posted')
    
    def __repr__(self):
        return f"<Announcement {self.title} in Course {self.course_id}>"