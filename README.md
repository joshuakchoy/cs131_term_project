# cs131_term_project
Learning Management System for CS131 term project

A full-featured learning management system with user authentication, course management, assignment submission, messaging, and grading capabilities.

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/joshuakchoy/cs131_term_project.git
cd cs131_term_project
```

### 2. Create Virtual Environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
# Option A
python run.py

# Option B
export FLASK_APP=run.py  # Windows: set FLASK_APP=run.py
flask run
```

### 5. Access the Application
Visit `http://localhost:5000/` in your browser

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Files
```bash
pytest tests/test_models.py -v
pytest tests/test_routes.py -v
pytest tests/test_forms.py -v
```

### Test Coverage
The test suite includes 8 unit tests covering:
- **Models**: User authentication, course creation
- **Routes**: Login, protected routes, authentication
- **Forms**: Registration validation

All tests must pass before merging to main branch.

## Project Structure

```
repo/
  app/
    __init__.py
    config.py
    models.py
    forms.py
    auth/
      __init__.py
      routes.py
      templates/auth/login.html
    main/
      __init__.py
      routes.py
      templates/main/index.html
      templates/main/feature.html
    templates/base.html
    static/styles.css
  run.py
  requirements.txt
  README.md
  .gitignore
```

## Acceptance Checklist

- `flask run` (or `python run.py`) starts without exceptions.
- Visiting `/`, `/feature`, and `/auth/login` renders pages.
- WTForms form at `/auth/login` renders; POST validates and flashes **"Not implemented"**.
- `Flask-Login` installed and imported; `User` model mixes in `UserMixin` for auth props.
- SQLAlchemy models import without error; SQLite URI provided in `config.py`.
- Base template includes a nav and `{% block content %}`; child templates extend it.
- README includes install/run and a screenshot of a rendered page.

## MVP Features (to be implemented) 
- Instructor can create assignments.
- Instructor or TA can grade assignments.
- Students can access assignments.
- Students can submit assignments.
- All users can have a direct line of messaging communication between each other.
- Assignments can be graded by instructor and viewed by all users.
- One place for notification of assignment posting and grading, new messages and announcements.
- Grades for all courses are visible on one page.
- Assignments for all courses are visible on one page.
- Instructors can post announcements to the entire class.
- Must be able to create instructor, TA, or student accounts.
- Must be able to create a class and add students to a class.

## Test Coverage

### Models (3 tests)
1. **test_user_password_hashing** - Verifies password hashing and verification works correctly
2. **test_user_creation_with_role** - Tests creating users with different roles (student, instructor)
3. **test_course_creation** - Tests course creation and instructor relationship

### Routes (4 tests)
4. **test_login_page_accessible** - Verifies login page loads successfully
5. **test_login_with_valid_credentials** - Tests successful login with correct credentials
6. **test_assignments_requires_login** - Ensures protected routes require authentication
7. **test_authenticated_user_can_access_assignments** - Verifies authenticated users can access assignments

### Forms (1 test)
8. **test_registration_form_validates_matching_passwords** - Tests form validation for matching passwords

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_models.py

# Run specific test
pytest tests/test_models.py::TestUserModel::test_user_password_hashing
```

## Test Files
- `conftest.py` - Pytest configuration and fixtures
- `test_models.py` - Model tests
- `test_routes.py` - Route/view tests
- `test_forms.py` - Form validation tests
- `pytest.ini` - Pytest configuration

## Test Results
✅ **All 8 tests passing**

## Technologies Used

- **Backend**: Flask 3.0+, Python
- **Database**: SQLAlchemy 2.0+ with SQLite
- **Authentication**: Flask-Login 0.6+
- **Forms**: WTForms 3.1+, Flask-WTF 1.2+
- **Testing**: Pytest 7.4+, pytest-flask, pytest-cov
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Icons**: Google Material Symbols
- **File Uploads**: Secure file handling with werkzeug

## Database Models

### User
- Username, email, password (hashed)
- Role: student, instructor, or TA
- Relationships: courses taught, courses enrolled, submissions, TA assignments, messages

### Course
- Title, description, course code
- Instructor (foreign key to User)
- Relationships: assignments, enrollments, announcements, TA assignments

### Assignment
- Title, description, due date
- Course (foreign key)
- Relationships: submissions

### Submission
- Student, assignment references
- Content (text), file path
- Submission timestamp, grade

### Enrollment
- Links students to courses

### Message
- Sender, recipient references
- Subject, body, timestamp
- Read/unread status

### Announcement
- Course, author references
- Title, content, timestamp

### TAAssignment
- Links TAs to courses they assist with

## Features Implemented

### Authentication & User Management
- ✅ User registration with role selection (Student, Instructor, TA)
- ✅ Login/logout functionality
- ✅ Password hashing and secure authentication
- ✅ Password reset functionality
- ✅ Role-based access control

### Course Management
- ✅ Instructors can create courses
- ✅ Students can enroll in courses
- ✅ Course listing and details view
- ✅ Course thumbnails and descriptions
- ✅ TA assignment to courses
- ✅ Enrollment management through teacher portal

### Assignment System
- ✅ Instructors can create assignments with due dates
- ✅ Students can view assignments for enrolled courses
- ✅ Students can submit assignments (text + file upload)
- ✅ Assignment resubmission capability
- ✅ Submission tracking and status indicators
- ✅ File uploads (PDF, DOC, DOCX, TXT, ZIP, code files)
- ✅ Instructors can view all submissions per assignment
- ✅ Assignment sorting (by due date, by course)
- ✅ Completion badges for submitted assignments
- ✅ Download submitted files

### Messaging & Communication
- ✅ Direct messaging between users
- ✅ Inbox and sent messages
- ✅ Message composition with subject and body
- ✅ Read/unread status tracking
- ✅ Floating messaging hub (overlay interface)
- ✅ Course-wide announcements by instructors
- ✅ Message notifications

### Grading
- ✅ Instructors can view student submissions
- ✅ Grade tracking per assignment
- ✅ Grades page showing all course grades by student

### User Interface
- ✅ Responsive sidebar navigation with Material Design icons
- ✅ Collapsible sidebar with state persistence
- ✅ Modal dialogs for course management
- ✅ Flash messages for user feedback
- ✅ Custom styling with CSS
- ✅ Floating message button overlay
- ✅ Clickable assignment cards
- ✅ Visual completion indicators

### Teacher Portal
- ✅ Dashboard for instructors
- ✅ Course overview with enrollment statistics
- ✅ Student enrollment management via modal interface
- ✅ Quick access to create assignments/courses
- ✅ View all courses taught
- ✅ Manage students in courses

### Analytics
- ✅ Analytics page structure (ready for future metrics)

## Login Page

![Rendered page](registration.png)

## Student Page Sample
![Rendered page](homescreen.png)
- Easy access to messages and tabs via sidebar


## UI Sketches

![Rendered page](sketch.png)
## User Roles

### Instructor
- Create and manage courses
- Create and grade assignments
- View all student submissions
- Post announcements to classes
- Manage TAs for their courses
- Send messages to students and TAs

### Student
- Enroll in courses
- View and submit assignments
- Track grades across all courses
- Receive announcements and messages
- Resubmit assignments before due date
- View assignment completion status

### Teaching Assistant (TA)
- Assist with grading assignments
- Access course materials
- Communicate with students
- View submissions for assigned courses

## Team Roles

- **Backend & Models**: Joshua Choy
- **Frontend & Styling**: Jan David Ella
- **Testing & QA**: Jan David Ella, Joshua Choy


