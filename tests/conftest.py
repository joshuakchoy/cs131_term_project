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
