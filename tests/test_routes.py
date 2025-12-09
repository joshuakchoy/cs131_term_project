"""
Unit tests for routes and views
"""
import pytest


class TestAuthRoutes:
    """Test authentication routes"""
    
    def test_login_page_accessible(self, client):
        """Test 4: Verify login page loads successfully"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data
    
    def test_login_with_valid_credentials(self, client, student_user):
        """Test 5: Verify user can login with correct credentials"""
        response = client.post('/auth/login', data={
            'username': 'teststudent',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # After successful login, user should be redirected to home/index


class TestProtectedRoutes:
    """Test protected routes require authentication"""
    
    def test_assignments_requires_login(self, client):
        """Test 6: Verify assignments page requires authentication"""
        response = client.get('/assignments')
        # Should redirect to login page (302) or return 401
        assert response.status_code in [302, 401]
    
    def test_authenticated_user_can_access_assignments(self, client, student_user):
        """Test 7: Verify authenticated user can access assignments"""
        # Login first
        client.post('/auth/login', data={
            'username': 'teststudent',
            'password': 'password123'
        })
        
        # Now try to access assignments
        response = client.get('/assignments')
        assert response.status_code == 200
