from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
import os
from ..forms import CreateAssignmentForm, CreateCourseForm
from ..models import db, Assignment, Course

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
def classes():
    return render_template("main/classes.html")

@bp.route("/assignments")
def assignments():
    assignments = Assignment.query.order_by(Assignment.id.desc()).all()
    return render_template("main/assignments.html", assignments=assignments)

@bp.route("/create_assignment", methods=["GET", "POST"])
def create_assignment():
    form = CreateAssignmentForm()
    if form.validate_on_submit():
        assignment = Assignment(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data
        )
        db.session.add(assignment)
        db.session.commit()
        flash("Assignment created successfully!", "success")
        return redirect(url_for("main.assignments"))
    return render_template("main/create_assignment.html", form=form)

@bp.route("/create_course", methods=["GET", "POST"])
def create_course():
    form = CreateCourseForm()
    if form.validate_on_submit():
        course = Course(
            course_name=form.course_name.data,
            course_code=form.course_code.data,
            course_description=form.course_description.data
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
    return render_template("main/teacher_portal.html")

