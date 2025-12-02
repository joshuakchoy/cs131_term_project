from flask import Blueprint, render_template
from flask_login import login_required
import os

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
    return render_template("main/assignments.html")

@bp.route("/analytics")
def analytics():
    return render_template("main/analytics.html")

