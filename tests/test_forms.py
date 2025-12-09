"""
Unit tests for forms validation
"""
import pytest
from app.forms import RegistrationForm, LoginForm


class TestRegistrationForm:
    """Test registration form validation"""
    
    def test_registration_form_validates_matching_passwords(self, app):
        """Test 8: Verify registration form requires matching passwords"""
        with app.app_context():
            # Test with matching passwords
            form = RegistrationForm(
                username='newuser',
                email='new@test.com',
                password='password123',
                password_confirm='password123',
                role='student'
            )
            assert form.validate() is True
            
            # Test with non-matching passwords
            form_invalid = RegistrationForm(
                username='newuser2',
                email='new2@test.com',
                password='password123',
                password_confirm='differentpassword',
                role='student'
            )
            assert form_invalid.validate() is False
            assert 'password_confirm' in form_invalid.errors
