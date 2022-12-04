from flask import Blueprint, redirect, url_for, render_template, request, send_from_directory
from flask_jwt import current_identity

index_views = Blueprint("index_views", __name__, template_folder="../templates")

@index_views.route("/", methods=["GET"])
def index_page():
    return render_template("auth/signup.html", data=None)

# Load Favicon
@index_views.route('/favicon.ico')
def favicon():
    return url_for('static', filename='image/favicon.ico')