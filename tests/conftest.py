"""
Pytest configuration and fixtures
"""
import pytest
import os
import tempfile
from app import create_app
from app.models import db, User, Course, Assignment


@pytest.fixture(scope='function')
def app():
    """Create and configure a test app instance"""
    db_fd, db_path = tempfile.mkstemp()
    
    test_app = create_app()
    test_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
    })
    
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Test client for making requests"""
    return app.test_client()


@pytest.fixture
def student_user(app):
    """Create a test student user"""
    with app.app_context():
        user = User(
            username='teststudent',
            email='student@test.com',
            role='student'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def teacher_user(app):
    """Create a test teacher user"""
    with app.app_context():
        user = User(
            username='testteacher',
            email='teacher@test.com',
            role='instructor'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def ta_user(app):
    """Create a test TA user"""
    with app.app_context():
        user = User(
            username='testta',
            email='ta@test.com',
            role='ta'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def authenticated_client(client, student_user):
    """Client with authenticated student session"""
    client.post('/auth/login', data={
        'username': 'teststudent',
        'password': 'password123'
    })
    return client


@pytest.fixture
def authenticated_teacher_client(client, teacher_user):
    """Client with authenticated teacher session"""
    client.post('/auth/login', data={
        'username': 'testteacher',
        'password': 'password123'
    })
    return client


@pytest.fixture
def authenticated_ta_client(client, ta_user):
    """Client with authenticated TA session"""
    client.post('/auth/login', data={
        'username': 'testta',
        'password': 'password123'
    })
    return client


@pytest.fixture
def sample_course(app, teacher_user):
    """Create a sample course"""
    with app.app_context():
        # Re-query the teacher user in the current session
        teacher = User.query.filter_by(username='testteacher').first()
        course = Course(
            title='Test Course',
            code='CS101',
            description='A test course',
            teacher=teacher.id
        )
        db.session.add(course)
        db.session.commit()
        course_id = course.id
    
    # Return the course ID instead of the object to avoid detached instance issues
    with app.app_context():
        return Course.query.get(course_id)


@pytest.fixture
def sample_assignment(app, sample_course):
    """Create a sample assignment"""
    with app.app_context():
        # Re-query the course in the current session
        course = Course.query.filter_by(code='CS101').first()
        assignment = Assignment(
            title='Test Assignment',
            description='A test assignment',
            due_date='2025-12-31',
            assignment_type='homework',
            course_id=course.id
        )
        db.session.add(assignment)
        db.session.commit()
        assignment_id = assignment.id
    
    # Return the assignment ID instead of the object
    with app.app_context():
        return Assignment.query.get(assignment_id)
