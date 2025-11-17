from flask import Blueprint, render_template
import os

bp = Blueprint("main", __name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

@bp.route("/")
def index():
    return render_template("main/index.html")

@bp.route("/feature")
def feature():
    return render_template("main/features.html")
