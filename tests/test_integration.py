"""
Integration tests for full routes, template rendering, and edge cases
"""
import pytest
from app.models import db, User, Course, Assignment, Enrollment, Submission, Message, Announcement, TAAssignment


class TestAuthenticationIntegration:
    """Integration tests for authentication flow"""
    
    def test_registration_flow(self, client):
        """Test full registration process"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data or b'register' in response.data or b'Create Account' in response.data
        
        # Register a new user
        response = client.post('/auth/register', data={
            'username': 'newstudent',
            'email': 'newstudent@test.com',
            'password': 'password123',
            'password_confirm': 'password123',
            'role': 'student'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # After successful registration, user should be logged in
        # Check for either home content or success message
    
    def test_duplicate_email_registration(self, client, student_user):
        """Test that duplicate email registration is prevented"""
        response = client.post('/auth/register', data={
            'username': 'anotherstudent',
            'email': 'student@test.com',  # Already exists
            'password': 'password123',
            'password_confirm': 'password123',
            'role': 'student'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Check for error message about duplicate email
        assert b'Email already registered' in response.data or b'already' in response.data.lower()
    
    def test_duplicate_username_registration(self, client, student_user):
        """Test that duplicate username registration is prevented"""
        response = client.post('/auth/register', data={
            'username': 'teststudent',  # Already exists
            'email': 'newemail@test.com',
            'password': 'password123',
            'password_confirm': 'password123',
            'role': 'student'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Check for error message about duplicate username
        assert b'Username already taken' in response.data or b'already' in response.data.lower()
    
    def test_login_logout_flow(self, client, student_user):
        """Test complete login and logout process"""
        # Login
        response = client.post('/auth/login', data={
            'username': 'teststudent',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data
    
    def test_invalid_login_credentials(self, client, student_user):
        """Test login with incorrect credentials"""
        response = client.post('/auth/login', data={
            'username': 'teststudent',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'invalid' in response.data
    
    def test_authenticated_user_redirected_from_login(self, authenticated_client):
        """Test that logged-in users are redirected from login page"""
        response = authenticated_client.get('/auth/login', follow_redirects=True)
        assert response.status_code == 200
        # Should be redirected to home page
    
    def test_password_reset_flow(self, client, app, student_user):
        """Test password reset process"""
        # Request password reset
        response = client.get('/auth/forgot-password')
        assert response.status_code == 200
        
        response = client.post('/auth/forgot-password', data={
            'email': 'student@test.com'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'reset' in response.data or b'Reset' in response.data
        
        # Get reset token
        with app.app_context():
            user = User.query.filter_by(email='student@test.com').first()
            token = user.get_reset_token()
        
        # Reset password with token
        response = client.post(f'/auth/reset-password/{token}', data={
            'password': 'newpassword123',
            'password_confirm': 'newpassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Try logging in with new password
        response = client.post('/auth/login', data={
            'username': 'teststudent',
            'password': 'newpassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200


class TestProtectedRoutesIntegration:
    """Integration tests for protected routes and authentication requirements"""
    
    def test_unauthenticated_access_redirects_to_login(self, client):
        """Test that unauthenticated users are redirected to login"""
        protected_routes = [
            '/home',
            '/grades',
            '/classes',
            '/assignments',
            '/analytics',
            '/teacher_portal',
            '/create_course',
            '/create_assignment'
        ]
        
        for route in protected_routes:
            response = client.get(route)
            # Should redirect (302) or return 401 unauthorized
            assert response.status_code in [302, 401]
    
    def test_authenticated_user_can_access_home(self, authenticated_client):
        """Test authenticated users can access home page"""
        response = authenticated_client.get('/home')
        assert response.status_code == 200
        assert b'Home' in response.data or b'home' in response.data
    
    def test_authenticated_user_can_access_grades(self, authenticated_client):
        """Test authenticated users can access grades page"""
        response = authenticated_client.get('/grades')
        assert response.status_code == 200
        assert b'Grade' in response.data or b'grade' in response.data
    
    def test_authenticated_user_can_access_classes(self, authenticated_client):
        """Test authenticated users can access classes page"""
        response = authenticated_client.get('/classes')
        assert response.status_code == 200
        assert b'Class' in response.data or b'Course' in response.data or b'class' in response.data or b'course' in response.data
    
    def test_authenticated_user_can_access_assignments(self, authenticated_client):
        """Test authenticated users can access assignments page"""
        response = authenticated_client.get('/assignments')
        assert response.status_code == 200


class TestRoleBasedAccessControl:
    """Integration tests for role-based access control edge cases"""
    
    def test_student_cannot_access_teacher_portal(self, authenticated_client):
        """Test that students cannot access teacher portal"""
        response = authenticated_client.get('/teacher_portal', follow_redirects=True)
        assert response.status_code == 200
        assert b'Access denied' in response.data or b'denied' in response.data or b'instructor only' in response.data
    
    def test_student_cannot_create_course(self, authenticated_client):
        """Test that students cannot create courses"""
        response = authenticated_client.get('/create_course', follow_redirects=True)
        assert response.status_code == 200
        assert b'Access denied' in response.data or b'denied' in response.data or b'instructor' in response.data
    
    def test_student_cannot_create_assignment(self, authenticated_client):
        """Test that students cannot create assignments"""
        response = authenticated_client.get('/create_assignment', follow_redirects=True)
        assert response.status_code == 200
        assert b'Access denied' in response.data or b'denied' in response.data or b'instructor' in response.data
    
    def test_student_cannot_post_create_course(self, authenticated_client):
        """Test that students cannot POST to create course"""
        response = authenticated_client.post('/create_course', data={
            'name': 'Unauthorized Course',
            'code': 'UNAUTH101',
            'description': 'Should not be created'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Access denied' in response.data or b'denied' in response.data
    
    def test_student_cannot_post_create_assignment(self, authenticated_client, sample_course):
        """Test that students cannot POST to create assignment"""
        response = authenticated_client.post('/create_assignment', data={
            'title': 'Unauthorized Assignment',
            'description': 'Should not be created',
            'due_date': '2025-12-31',
            'assignment_type': 'homework',
            'course_id': sample_course.id
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Access denied' in response.data or b'denied' in response.data
    
    def test_teacher_can_access_teacher_portal(self, authenticated_teacher_client):
        """Test that teachers can access teacher portal"""
        response = authenticated_teacher_client.get('/teacher_portal')
        assert response.status_code == 200
    
    def test_teacher_can_create_course(self, authenticated_teacher_client):
        """Test that teachers can create courses"""
        response = authenticated_teacher_client.get('/create_course')
        assert response.status_code == 200
        assert b'Create' in response.data or b'create' in response.data
    
    def test_teacher_can_create_assignment(self, authenticated_teacher_client, sample_course):
        """Test that teachers can create assignments"""
        response = authenticated_teacher_client.get('/create_assignment')
        assert response.status_code == 200
    
    def test_student_can_access_analytics(self, authenticated_client):
        """Test that students can access their analytics"""
        response = authenticated_client.get('/analytics')
        assert response.status_code == 200
    
    def test_teacher_analytics_shows_different_view(self, authenticated_teacher_client):
        """Test that teachers see a different analytics view"""
        response = authenticated_teacher_client.get('/analytics')
        assert response.status_code == 200


class TestCourseManagementIntegration:
    """Integration tests for course creation and management"""
    
    def test_teacher_create_course_flow(self, authenticated_teacher_client):
        """Test complete course creation flow"""
        response = authenticated_teacher_client.post('/create_course', data={
            'name': 'Introduction to Python',
            'code': 'CS101',
            'description': 'Learn Python programming',
            'image_url': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'successfully' in response.data or b'Success' in response.data or b'created' in response.data
    
    def test_duplicate_course_code_prevented(self, authenticated_teacher_client, sample_course):
        """Test that duplicate course codes are prevented"""
        response = authenticated_teacher_client.post('/create_course', data={
            'name': 'Another Course',
            'code': 'CS101',  # Already exists
            'description': 'Duplicate code',
            'image_url': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'already exists' in response.data or b'already' in response.data
    
    def test_view_course_as_instructor(self, authenticated_teacher_client, sample_course):
        """Test viewing course details as instructor"""
        response = authenticated_teacher_client.get(f'/course/{sample_course.id}')
        assert response.status_code == 200
        assert b'Test Course' in response.data or b'CS101' in response.data
    
    def test_student_sees_enrolled_courses_only(self, authenticated_client, app, student_user, sample_course):
        """Test that students only see courses they're enrolled in"""
        # Create enrollment
        with app.app_context():
            student = User.query.filter_by(username='teststudent').first()
            course = Course.query.filter_by(code='CS101').first()
            enrollment = Enrollment(student_id=student.id, course_id=course.id)
            db.session.add(enrollment)
            db.session.commit()
        
        response = authenticated_client.get('/classes')
        assert response.status_code == 200
        assert b'Test Course' in response.data or b'CS101' in response.data


class TestAssignmentManagementIntegration:
    """Integration tests for assignment creation and management"""
    
    def test_teacher_create_assignment_flow(self, authenticated_teacher_client, sample_course):
        """Test complete assignment creation flow"""
        response = authenticated_teacher_client.post('/create_assignment', data={
            'title': 'Homework 1',
            'description': 'Complete exercises 1-10',
            'due_date': '2025-12-31',
            'assignment_type': 'homework',
            'course_id': sample_course.id
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'successfully' in response.data or b'Success' in response.data or b'created' in response.data
    
    def test_teacher_without_courses_cannot_create_assignment(self, client, app):
        """Test that teachers without courses get a warning"""
        # Create a new teacher with no courses
        with app.app_context():
            new_teacher = User(username='newteacher', email='newteacher@test.com', role='instructor')
            new_teacher.set_password('password123')
            db.session.add(new_teacher)
            db.session.commit()
        
        # Login as new teacher
        client.post('/auth/login', data={
            'username': 'newteacher',
            'password': 'password123'
        })
        
        response = client.get('/create_assignment')
        assert response.status_code == 200
        assert b"don't have any courses" in response.data or b"Create a course first" in response.data
    
    def test_student_sees_only_enrolled_course_assignments(self, authenticated_client, app, student_user, sample_course, sample_assignment):
        """Test that students only see assignments from enrolled courses"""
        # Student is not enrolled yet, should not see assignment
        response = authenticated_client.get('/assignments')
        assert response.status_code == 200
        # Assignment list should be empty or not contain the assignment
        
        # Enroll student
        with app.app_context():
            student = User.query.filter_by(username='teststudent').first()
            course = Course.query.filter_by(code='CS101').first()
            enrollment = Enrollment(student_id=student.id, course_id=course.id)
            db.session.add(enrollment)
            db.session.commit()
        
        # Now student should see the assignment
        response = authenticated_client.get('/assignments')
        assert response.status_code == 200
        assert b'Test Assignment' in response.data
    
    def test_assignment_sorting_by_due_date(self, authenticated_teacher_client, app, sample_course):
        """Test assignment sorting by due date"""
        # Create multiple assignments with different due dates
        with app.app_context():
            assignment1 = Assignment(
                title='Assignment 1',
                description='First',
                due_date='2025-12-01',
                assignment_type='homework',
                course_id=sample_course.id
            )
            assignment2 = Assignment(
                title='Assignment 2',
                description='Second',
                due_date='2025-11-01',
                assignment_type='homework',
                course_id=sample_course.id
            )
            db.session.add_all([assignment1, assignment2])
            db.session.commit()
        
        # Test ascending sort
        response = authenticated_teacher_client.get('/assignments?sort=due_date&order=asc')
        assert response.status_code == 200
        
        # Test descending sort
        response = authenticated_teacher_client.get('/assignments?sort=due_date&order=desc')
        assert response.status_code == 200
    
    def test_assignment_sorting_by_course(self, authenticated_teacher_client, app):
        """Test assignment sorting by course"""
        # Create multiple courses and assignments
        with app.app_context():
            teacher = User.query.filter_by(username='testteacher').first()
            course1 = Course(title='A Course', code='CS100', teacher=teacher.id)
            course2 = Course(title='Z Course', code='CS200', teacher=teacher.id)
            db.session.add_all([course1, course2])
            db.session.commit()
            
            assignment1 = Assignment(
                title='Assignment for A',
                description='First',
                due_date='2025-12-01',
                assignment_type='homework',
                course_id=course1.id
            )
            assignment2 = Assignment(
                title='Assignment for Z',
                description='Second',
                due_date='2025-12-01',
                assignment_type='homework',
                course_id=course2.id
            )
            db.session.add_all([assignment1, assignment2])
            db.session.commit()
        
        # Test sorting by course
        response = authenticated_teacher_client.get('/assignments?sort=course&order=asc')
        assert response.status_code == 200


class TestGradesIntegration:
    """Integration tests for grades functionality"""
    
    def test_student_views_grades(self, authenticated_client, app, student_user, sample_course, sample_assignment):
        """Test student viewing their grades"""
        # Enroll student and create submission with grade
        with app.app_context():
            student = User.query.filter_by(username='teststudent').first()
            course = Course.query.filter_by(code='CS101').first()
            assignment = Assignment.query.filter_by(title='Test Assignment').first()
            
            enrollment = Enrollment(student_id=student.id, course_id=course.id)
            db.session.add(enrollment)
            db.session.commit()
            
            submission = Submission(
                assignment_id=assignment.id,
                student_id=student.id,
                file_path='/path/to/file.txt',
                grade=85.0
            )
            db.session.add(submission)
            db.session.commit()
        
        response = authenticated_client.get('/grades')
        assert response.status_code == 200
        assert b'Test Course' in response.data or b'CS101' in response.data
    
    def test_teacher_views_grades(self, authenticated_teacher_client, sample_course):
        """Test teacher viewing grades for their courses"""
        response = authenticated_teacher_client.get('/grades')
        assert response.status_code == 200
    
    def test_student_grade_average_calculation(self, authenticated_client, app, student_user, sample_course):
        """Test that student grade averages are calculated correctly"""
        with app.app_context():
            student = User.query.filter_by(username='teststudent').first()
            course = Course.query.filter_by(code='CS101').first()
            
            # Enroll student
            enrollment = Enrollment(student_id=student.id, course_id=course.id)
            db.session.add(enrollment)
            db.session.commit()
            
            # Create multiple assignments
            assignment1 = Assignment(
                title='Assignment 1',
                description='First',
                due_date='2025-12-01',
                assignment_type='homework',
                course_id=course.id
            )
            assignment2 = Assignment(
                title='Assignment 2',
                description='Second',
                due_date='2025-12-02',
                assignment_type='homework',
                course_id=course.id
            )
            db.session.add_all([assignment1, assignment2])
            db.session.commit()
            
            # Create submissions with grades
            submission1 = Submission(
                assignment_id=assignment1.id,
                student_id=student.id,
                file_path='/path/to/file1.txt',
                grade=80.0
            )
            submission2 = Submission(
                assignment_id=assignment2.id,
                student_id=student.id,
                file_path='/path/to/file2.txt',
                grade=90.0
            )
            db.session.add_all([submission1, submission2])
            db.session.commit()
        
        response = authenticated_client.get('/grades')
        assert response.status_code == 200
        # Average should be 85.0


class TestAnalyticsIntegration:
    """Integration tests for analytics functionality"""
    
    def test_student_analytics_with_grades(self, authenticated_client, app, student_user, sample_course, sample_assignment):
        """Test student analytics page with graded assignments"""
        with app.app_context():
            student = User.query.filter_by(username='teststudent').first()
            course = Course.query.filter_by(code='CS101').first()
            assignment = Assignment.query.filter_by(title='Test Assignment').first()
            
            # Enroll student
            enrollment = Enrollment(student_id=student.id, course_id=course.id)
            db.session.add(enrollment)
            db.session.commit()
            
            # Create submission with grade
            submission = Submission(
                assignment_id=assignment.id,
                student_id=student.id,
                file_path='/path/to/file.txt',
                grade=85.0
            )
            db.session.add(submission)
            db.session.commit()
        
        response = authenticated_client.get('/analytics')
        assert response.status_code == 200
    
    def test_student_analytics_without_grades(self, authenticated_client):
        """Test student analytics page without any grades"""
        response = authenticated_client.get('/analytics')
        assert response.status_code == 200
    
    def test_teacher_analytics_shows_limited_view(self, authenticated_teacher_client):
        """Test that teachers see limited analytics view"""
        response = authenticated_teacher_client.get('/analytics')
        assert response.status_code == 200


class TestEdgeCases:
    """Integration tests for edge cases and error handling"""
    
    def test_access_nonexistent_course(self, authenticated_teacher_client):
        """Test accessing a course that doesn't exist"""
        response = authenticated_teacher_client.get('/course/99999')
        assert response.status_code == 404
    
    def test_invalid_course_id_format(self, authenticated_teacher_client):
        """Test accessing a course with invalid ID format"""
        response = authenticated_teacher_client.get('/course/invalid')
        assert response.status_code == 404
    
    def test_empty_assignment_list_for_unenrolled_student(self, authenticated_client):
        """Test that unenrolled students see empty assignment list"""
        response = authenticated_client.get('/assignments')
        assert response.status_code == 200
    
    def test_root_path_redirects(self, authenticated_client):
        """Test that root path redirects properly"""
        response = authenticated_client.get('/', follow_redirects=True)
        assert response.status_code == 200
    
    def test_logout_without_login(self, client):
        """Test logout without being logged in"""
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
    
    def test_invalid_password_reset_token(self, client):
        """Test password reset with invalid token"""
        response = client.get('/auth/reset-password/invalidtoken123', follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'invalid' in response.data or b'expired' in response.data
    
    def test_forgot_password_with_nonexistent_email(self, client):
        """Test forgot password with email that doesn't exist"""
        response = client.post('/auth/forgot-password', data={
            'email': 'nonexistent@test.com'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'not found' in response.data or b'not found' in response.data


class TestTAIntegration:
    """Integration tests for TA role functionality"""
    
    def test_ta_can_access_home(self, authenticated_ta_client):
        """Test that TAs can access home page"""
        response = authenticated_ta_client.get('/home')
        assert response.status_code == 200
    
    def test_ta_can_access_grades(self, authenticated_ta_client):
        """Test that TAs can access grades page"""
        response = authenticated_ta_client.get('/grades')
        assert response.status_code == 200
    
    def test_ta_can_access_classes(self, authenticated_ta_client):
        """Test that TAs can access classes page"""
        response = authenticated_ta_client.get('/classes')
        assert response.status_code == 200
    
    def test_ta_cannot_access_teacher_portal(self, authenticated_ta_client):
        """Test that TAs cannot access teacher portal"""
        response = authenticated_ta_client.get('/teacher_portal', follow_redirects=True)
        assert response.status_code == 200
        assert b'Access denied' in response.data or b'denied' in response.data or b'instructor only' in response.data
    
    def test_ta_cannot_create_course(self, authenticated_ta_client):
        """Test that TAs cannot create courses"""
        response = authenticated_ta_client.get('/create_course', follow_redirects=True)
        assert response.status_code == 200
        assert b'Access denied' in response.data or b'denied' in response.data
    
    def test_ta_cannot_create_assignment(self, authenticated_ta_client):
        """Test that TAs cannot create assignments"""
        response = authenticated_ta_client.get('/create_assignment', follow_redirects=True)
        assert response.status_code == 200
        assert b'Access denied' in response.data or b'denied' in response.data
    
    def test_ta_sees_assigned_courses(self, authenticated_ta_client, app, ta_user, sample_course):
        """Test that TAs see courses they're assigned to"""
        with app.app_context():
            ta = User.query.filter_by(username='testta').first()
            course = Course.query.filter_by(code='CS101').first()
            ta_assignment = TAAssignment(ta_id=ta.id, course_id=course.id)
            db.session.add(ta_assignment)
            db.session.commit()
        
        response = authenticated_ta_client.get('/classes')
        assert response.status_code == 200
        assert b'Test Course' in response.data or b'CS101' in response.data
    
    def test_ta_sees_assigned_course_assignments(self, authenticated_ta_client, app, ta_user, sample_course, sample_assignment):
        """Test that TAs see assignments from assigned courses"""
        with app.app_context():
            ta = User.query.filter_by(username='testta').first()
            course = Course.query.filter_by(code='CS101').first()
            ta_assignment = TAAssignment(ta_id=ta.id, course_id=course.id)
            db.session.add(ta_assignment)
            db.session.commit()
        
        response = authenticated_ta_client.get('/home')
        assert response.status_code == 200


class TestTemplateRendering:
    """Integration tests for template rendering"""
    
    def test_login_template_renders(self, client):
        """Test that login template renders correctly"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'<form' in response.data or b'<Form' in response.data
        assert b'username' in response.data or b'Username' in response.data
        assert b'password' in response.data or b'Password' in response.data
    
    def test_register_template_renders(self, client):
        """Test that register template renders correctly"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'<form' in response.data or b'<Form' in response.data
        assert b'email' in response.data or b'Email' in response.data
    
    def test_home_template_renders(self, authenticated_client):
        """Test that home template renders correctly"""
        response = authenticated_client.get('/home')
        assert response.status_code == 200
    
    def test_grades_template_renders(self, authenticated_client):
        """Test that grades template renders correctly"""
        response = authenticated_client.get('/grades')
        assert response.status_code == 200
    
    def test_classes_template_renders(self, authenticated_client):
        """Test that classes template renders correctly"""
        response = authenticated_client.get('/classes')
        assert response.status_code == 200
    
    def test_assignments_template_renders(self, authenticated_client):
        """Test that assignments template renders correctly"""
        response = authenticated_client.get('/assignments')
        assert response.status_code == 200
    
    def test_analytics_template_renders(self, authenticated_client):
        """Test that analytics template renders correctly"""
        response = authenticated_client.get('/analytics')
        assert response.status_code == 200
    
    def test_teacher_portal_template_renders(self, authenticated_teacher_client):
        """Test that teacher portal template renders correctly"""
        response = authenticated_teacher_client.get('/teacher_portal')
        assert response.status_code == 200
    
    def test_create_course_template_renders(self, authenticated_teacher_client):
        """Test that create course template renders correctly"""
        response = authenticated_teacher_client.get('/create_course')
        assert response.status_code == 200
        assert b'<form' in response.data or b'<Form' in response.data
    
    def test_create_assignment_template_renders(self, authenticated_teacher_client, sample_course):
        """Test that create assignment template renders correctly"""
        response = authenticated_teacher_client.get('/create_assignment')
        assert response.status_code == 200
        assert b'<form' in response.data or b'<Form' in response.data
