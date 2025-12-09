"""
Unit tests for database models
"""
import pytest
from app.models import User, Course, Assignment


class TestUserModel:
    """Test User model functionality"""
    
    def test_user_password_hashing(self, app):
        """Test 1: Verify password hashing works correctly"""
        with app.app_context():
            from app.models import db
            user = User(username='testuser', email='test@test.com', role='student')
            user.set_password('mypassword')
            
            # Password should be hashed, not stored as plain text
            assert user.password_hash != 'mypassword'
            assert user.check_password('mypassword') is True
            assert user.check_password('wrongpassword') is False
    
    def test_user_creation_with_role(self, app):
        """Test 2: Verify users can be created with different roles"""
        with app.app_context():
            from app.models import db
            
            student = User(username='student1', email='s@test.com', role='student')
            student.set_password('pass123')
            db.session.add(student)
            
            teacher = User(username='teacher1', email='t@test.com', role='instructor')
            teacher.set_password('pass123')
            db.session.add(teacher)
            
            db.session.commit()
            
            assert User.query.filter_by(role='student').count() == 1
            assert User.query.filter_by(role='instructor').count() == 1


class TestCourseModel:
    """Test Course model functionality"""
    
    def test_course_creation(self, app, teacher_user):
        """Test 3: Verify courses can be created with instructor relationship"""
        with app.app_context():
            from app.models import db
            
            # Get teacher within the same session
            teacher = User.query.filter_by(username='testteacher').first()
            
            course = Course(
                title='Test Course',
                description='A test course',
                code='TEST101',
                teacher=teacher.id
            )
            db.session.add(course)
            db.session.commit()
            
            # Verify course was created
            found_course = Course.query.filter_by(code='TEST101').first()
            assert found_course is not None
            assert found_course.title == 'Test Course'
            assert found_course.instructor.id == teacher.id
