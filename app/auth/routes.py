from flask import Blueprint, render_template, request, flash, redirect, url_for
from ..forms import LoginForm
import os

bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            flash("Not implemented", "warning")
            return redirect(url_for("auth.login"))
        else:
            flash("Please correct the errors below.", "danger")
    return render_template("auth/login.html", form=form)
