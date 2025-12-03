from flask import Blueprint, render_template
from flask_login import login_required
import os
from ..forms import CreateAssignmentForm
from ..models import db, Assignment

bp = Blueprint("main", __name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

@bp.route("/")
@login_required
def default():
    return render_template("main/default.html")

@bp.route("/home")
@login_required
def index():
    return render_template("main/home.html")

@bp.route("/grades")
@login_required
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

@bp.route("/analytics")
def analytics():
    return render_template("main/analytics.html")

