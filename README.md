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


## Screenshot

![Rendered page](login.png)


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
