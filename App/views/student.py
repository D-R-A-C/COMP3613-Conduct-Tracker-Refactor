from flask import Blueprint, jsonify, request,redirect, url_for, render_template, flash
from flask_jwt import jwt_required, current_identity
from flask_login import login_required, current_user

from App.controllers import (
    create_student,
    get_student,
    get_all_students,
    get_students_by_name,
    get_all_users,
    get_all_student_reviews,
    update_student,
    delete_student,
)


student_views = Blueprint("student_views", __name__, template_folder="../templates")

# Create student given name, programme and faculty
# Must be an admin to access this route
@student_views.route("/api/students", methods=["POST"])
@jwt_required()
def create_student_action():
    if current_identity.is_admin():
        data = request.json
        student = create_student(
            firstName=data["firstName"], lastName=data["lastName"], programme=data["programme"], faculty=data["faculty"]
        )
        if student:
            return jsonify(student.to_json()), 201
        return jsonify({"error": "student not created"}), 400
    return jsonify({"error": "unauthorized"}), 401


# Add student page
# Must be an admin to access this route
@student_views.route("/students/new", methods=["POST", "GET"])
@login_required
def create_student_page():
    if request.method== "POST":
        if current_user.is_admin():
            data = request.form
            student = create_student(
                firstName=data["firstName"], lastName=data["lastName"], programme=data["programme"], faculty=data["faculty"]
            )
            if student:
                flash("student created successfully")
            else:
                flash("student not created")
    return render_template("add-student.html", student=None, data=None)


# Updates student given student id, name, programme and faculty
# Must be an admin to access this route
@student_views.route("/api/students/<int:student_id>", methods=["PUT"])
@jwt_required()
def update_student_action(student_id):
    if current_identity.is_admin():
        data = request.json
        student = update_student(
            student_id,
            firstName=data["firstName"],
            lastName=data["lastName"],
            programme=data["programme"],
            faculty=data["faculty"],
        )
        if student:
            return jsonify(student.to_json()), 200
        return jsonify({"error": "student not updated"}), 400
    return jsonify({"error": "unauthorized"}), 401


# Update student page
# Must be an admin to access this route
@student_views.route("/dashboard/<int:student_id>", methods=["POST", "GET"])
@login_required
def update_student_page(student_id):
    if current_user.is_admin():
        if request.method == "POST":
            data = request.form
            student = update_student(
                student_id,
                firstName=data["firstName"],
                lastName=data["lastName"],
                programme=data["programme"],
                faculty=data["faculty"],
            )
            if student:
                flash("student updated")
            else:
                flash("student not updated")
    return render_template("index.html", students=get_all_students(), edited_student=get_student(student_id))

# Lists all students
@student_views.route("/api/students", methods=["GET"])
@jwt_required()
def get_all_students_action():
    students = get_all_students()
    if students:
        return jsonify([student.to_json() for student in students]), 200
    return jsonify({"error": "students not found"}), 404


# Dashboard page
@student_views.route("/dashboard", methods=["GET"])
@login_required
def dashboard_page():
    return render_template("index.html", students=get_all_students(), selected_student="")


# View student and reviews page --> search
@student_views.route("/dashboard", methods=["POST"])
@login_required
def search_student_page():
    data=request.form
    keyword=data["keyword"]
    students=[]
    student=None
    # Search by id
    try:
        int(keyword)
        student_id = int(keyword)
        student = get_student(student_id)
        if student:
            students.append(student)
        return render_template("index.html", students=students, selected_student="")
    except ValueError:
        # search by name
        name = data["keyword"]
        students = get_students_by_name(name)
        return render_template("index.html", students=students, selected_student="")


# Gets a student given student id
@student_views.route("/api/students/<int:student_id>", methods=["GET"])
@jwt_required()
def get_student_action(student_id):
    student = get_student(student_id)
    if student:
        return jsonify(student.to_json()), 200
    return jsonify({"error": "student not found"}), 404


# Gets a student given their name
@student_views.route("/api/students/name", methods=["GET"])
@jwt_required()
def get_student_by_name_action():
    data = request.json
    students = get_students_by_name(data["firstName"], data["lastName"])
    if students:
        return jsonify([student.to_json() for student in students]), 200
    return jsonify({"error": "student not found"}), 404


# Deletes a student given student id
# Must be an admin to access this route
@student_views.route("/api/students/<int:student_id>", methods=["DELETE"])
@jwt_required()
def delete_student_action(student_id):
    if current_identity.is_admin():
        outcome = delete_student(student_id)
        if outcome:
            return jsonify({"message": "student deleted"}), 200
        return jsonify({"error": "student not deleted"}), 400
    return jsonify({"error": "unauthorized"}), 401


# Deletes a student given student id page
# Must be an admin to access this route
@student_views.route("/students/<int:student_id>", methods=["GET"])
@login_required
def delete_student_page(student_id):
    if current_user.is_admin():
        outcome = delete_student(student_id)
        if outcome:
            flash("student deleted")
        else:
            flash("student not deleted")
    return render_template("index.html", students=get_all_students())



# Lists all reviews for a given student.
@student_views.route("/api/students/<int:student_id>/reviews", methods=["GET"])
@jwt_required()
def get_all_student_reviews_action(student_id):
    reviews = get_all_student_reviews(student_id)
    return jsonify(reviews), 200


# Page - Lists all reviews for a given student.
@student_views.route("/students/<int:student_id>/reviews", methods=["GET"])
@login_required
def get_all_student_reviews_page(student_id):
    all_students = get_all_students()
    student = get_student(student_id)
    users=get_all_users()
    return render_template("index.html", students=all_students, selected_student=student, users=users)