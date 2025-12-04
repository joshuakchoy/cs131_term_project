from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
import os
from ..forms import CreateAssignmentForm, CreateCourseForm, EnrollStudentForm
from ..models import db, Assignment, Course, User, Enrollment

bp = Blueprint("main", __name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

@bp.route("/")
def default():
    return redirect(url_for("auth.login"))

@bp.route("/home")
def index():
    return render_template("main/home.html")

@bp.route("/grades")
def grades():
    return render_template("main/grades.html")

@bp.route("/classes")
@login_required
def classes():
    if current_user.role == "instructor":
        # Show courses taught by this instructor
        courses = Course.query.filter_by(teacher=current_user.id).all()
    else:
        # Show courses enrolled by this student
        enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
        courses = [e.course for e in enrollments]
    return render_template("main/classes.html", courses=courses)

@bp.route("/assignments")
def assignments():
    assignments = Assignment.query.order_by(Assignment.id.desc()).all()
    return render_template("main/assignments.html", assignments=assignments)

@bp.route("/create_assignment", methods=["GET", "POST"])
@login_required
def create_assignment():
    # only instructors can create assignments
    if getattr(current_user, "role", None) != "instructor":
        flash("Access denied: instructors only.", "danger")
        return redirect(url_for("main.index"))

    form = CreateAssignmentForm()
    # Populate course choices with courses owned by the current user (instructor)
    courses = Course.query.filter_by(teacher=current_user.id).all()
    form.course_id.choices = [(c.id, c.title) for c in courses]

    if not form.course_id.choices:
        flash("You don't have any courses yet. Create a course first.", "info")

    if form.validate_on_submit():
        # convert date object to ISO string for storing in the String column
        due_val = form.due_date.data
        if hasattr(due_val, "strftime"):
            due_str = due_val.strftime("%Y-%m-%d")
        else:
            due_str = due_val

        assignment = Assignment(
            title=form.title.data,
            description=form.description.data,
            due_date=due_str,
            course_id=form.course_id.data
        )
        db.session.add(assignment)
        db.session.commit()
        flash("Assignment created successfully!", "success")
        return redirect(url_for("main.assignments"))
    return render_template("main/create_assignment.html", form=form)

@bp.route("/create_course", methods=["GET", "POST"])
@bp.route("/create_course", methods=["GET", "POST"])
@login_required
def create_course():
    # only instructors can create courses
    if getattr(current_user, "role", None) != "instructor":
        flash("Access denied: instructors only.", "danger")
        return redirect(url_for("main.index"))

    form = CreateCourseForm()

    if form.validate_on_submit():
        course = Course(
            title=form.name.data,
            code=form.code.data,
            description=form.description.data,
            teacher=current_user.id
        )
        db.session.add(course)
        db.session.commit()
        flash("Course created successfully!", "success")
        return redirect(url_for("main.classes"))
    return render_template("main/create_course.html", form=form)

@bp.route("/analytics")
def analytics():
    return render_template("main/analytics.html")


@bp.route("/teacher_portal")
@login_required
def teacher_portal():
    # Only allow instructors to view the teacher portal
    if getattr(current_user, "role", None) != "instructor":
        flash("Access denied: instructor only.", "danger")
        return redirect(url_for("main.index"))
    
    # Get all students and courses taught by the instructor
    students = User.query.filter_by(role="student").all()
    courses = Course.query.filter_by(teacher=current_user.id).all()
    form = EnrollStudentForm()
    return render_template("main/teacher_portal.html", students=students, courses=courses, form=form)


@bp.route("/course/<int:course_id>")
@login_required
def view_course(course_id):
    """View course details and manage students (instructor only)"""
    course = Course.query.get_or_404(course_id)
    
    # Check if user is the instructor of this course
    if course.teacher != current_user.id:
        flash("You do not have permission to view this course.", "danger")
        return redirect(url_for("main.classes"))
    
    # Get all enrolled students
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    students = [e.student for e in enrollments]
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    
    form = EnrollStudentForm()
    return render_template("main/view_course.html", course=course, students=students, assignments=assignments, form=form)


@bp.route("/course/<int:course_id>/enroll", methods=["POST"])
@login_required
def enroll_student(course_id):
    """Add a student to a course"""
    course = Course.query.get_or_404(course_id)
    
    # Check if user is the instructor of this course
    if course.teacher != current_user.id:
        flash("You do not have permission to modify this course.", "danger")
        return redirect(url_for("main.classes"))
    
    form = EnrollStudentForm()
    if form.validate_on_submit():
        # Find student by username or email
        student = User.query.filter(
            (User.username == form.student_identifier.data) |
            (User.email == form.student_identifier.data)
        ).first()
        
        if not student:
            flash("Student not found.", "danger")
            return redirect(url_for("main.teacher_portal"))
        
        if student.role != "student":
            flash("This user is not a student.", "danger")
            return redirect(url_for("main.teacher_portal"))
        
        # Check if student is already enrolled
        existing = Enrollment.query.filter_by(student_id=student.id, course_id=course_id).first()
        if existing:
            flash(f"{student.username} is already enrolled in this course.", "info")
            return redirect(url_for("main.teacher_portal"))
        
        # Create enrollment
        enrollment = Enrollment(student_id=student.id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
        flash(f"{student.username} has been added to the course.", "success")
        return redirect(url_for("main.teacher_portal"))
    
    flash("Form validation failed.", "danger")
    return redirect(url_for("main.view_course", course_id=course_id))

