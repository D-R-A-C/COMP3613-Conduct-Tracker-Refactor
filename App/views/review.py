from flask import Blueprint, jsonify, request, render_template, flash
from flask_jwt import jwt_required, current_identity
from flask_login import login_required, current_user

from App.controllers import (
    create_review,
    get_review,
    get_all_reviews,
    vote_review,
    update_review,
    delete_review,
    get_all_students,
    get_student,
    get_all_users,
)

review_views = Blueprint("review_views", __name__, template_folder="../templates")


# Create review given user id, student id and text
@review_views.route("/api/reviews", methods=["POST"])
@jwt_required()
def create_review_action():
    data = request.json
    review = create_review(
        staff_id=data["staff_id"], student_id=data["student_id"], sentiment = data["sentiment"], text=data["text"]
    )
    if review:
        return jsonify(review.to_json()), 201
    return jsonify({"error": "review not created"}), 400


# Create review given user id, student id and text PAGE
@review_views.route("/reviews/<student_id>", methods=["POST"])
@login_required
def create_review_page(student_id):
    data = request.form
    review = create_review(
        staff_id=current_user.id, student_id=student_id, sentiment = data["sentiment"], text=data["text"]
    )
    if review:
        flash("review created")
    return render_template("index.html", students=get_all_students(), selected_student=get_student(review.student_id), reviews=get_all_reviews(), users=get_all_users())
    


# List all reviews
@review_views.route("/api/reviews", methods=["GET"])
@jwt_required()
def get_all_reviews_action():
    reviews = get_all_reviews()
    return jsonify([review.to_json() for review in reviews]), 200


# Gets review given review id
@review_views.route("/api/reviews/<int:review_id>", methods=["GET"])
@jwt_required()
def get_review_action(review_id):
    review = get_review(review_id)
    if review:
        return jsonify(review.to_json()), 200
    return jsonify({"error": "review not found"}), 404


# Upvotes/Downvotes post given post id and user id
@review_views.route("/api/reviews/<int:review_id>/<vote_type>", methods=["PUT"])
@jwt_required()
def vote_review_action(review_id, vote_type):
    review = get_review(review_id)
    if review:
        review = vote_review(review_id, current_identity.id, vote_type)
        return jsonify(review.to_json()), 200
    return jsonify({"error": "review not found"}), 404


# Upvotes/Downvotes post given post id and user id PAGE
@review_views.route("/reviews/<int:review_id>/<vote_type>", methods=["GET"])
@login_required
def vote_review_page(review_id, vote_type):
    review = get_review(review_id)
    if review:
        review = vote_review(review_id, current_user.id, vote_type)
    return render_template("index.html", students=get_all_students(), selected_student=get_student(review.student_id), reviews=get_all_reviews(), users=get_all_users())

# Updates post given post id and new text
# Only admins or the original reviewer can edit a review
@review_views.route("/api/reviews/<int:review_id>", methods=["PUT"])
@jwt_required()
def update_review_action(review_id):
    data = request.json
    review = get_review(review_id)
    if review:
        if current_identity.id == review.staff_id or current_identity.is_admin():
            update_review(review_id, data["sentiment"], text=data["text"])
            return jsonify({"message": "post updated successfully"}), 200
        else:
            return jsonify({"error": "Access denied"}), 403
    return jsonify({"error": "review not found"}), 404


# Updates post given post id and new text PAGE
# Only admins or the original reviewer can edit a review
@review_views.route("/review/<int:review_id>/edit", methods=["POST", "GET"])
@login_required
def update_review_page(review_id):
    review = get_review(review_id)
    selected_student= get_student(review.student_id)
    if review:
        if request.method == "POST":
            data = request.form
            if current_user.id == review.staff_id or current_user.is_admin():
                update_review(review_id, data["sentiment"], text=data["text"])
                flash("post updated successfully")
                return render_template("index.html", selected_student=selected_student, students=get_all_students(), reviews=get_all_reviews(), users=get_all_users())
    return render_template("update-review.html", review=review)


# Deletes post given post id
# Only admins or the original reviewer can delete a review
@review_views.route("/api/reviews/<int:review_id>", methods=["DELETE"])
@jwt_required()
def delete_review_action(review_id):
    review = get_review(review_id)
    if review:
        if current_identity.id == review.staff_id or current_identity.is_admin():
            delete_review(review_id)
            return jsonify({"message": "post deleted successfully"}), 200
        else:
            return jsonify({"error": "Access denied"}), 403
    return jsonify({"error": "review not found"}), 404


# Deletes post given post id
# Only admins or the original reviewer can delete a review PAGE
@review_views.route("/review/<int:review_id>", methods=["GET"])
@login_required
def delete_review_page(review_id):
    review = get_review(review_id)
    if review:
        if current_user.id == review.staff_id or current_user.is_admin():
            delete_review(review_id)
            flash("post deleted successfully")
    return render_template("index.html", students=get_all_students(), selected_student=get_student(review.student_id), reviews=get_all_reviews())


# Gets all votes for a given review
@review_views.route("/api/reviews/<int:review_id>/votes", methods=["GET"])
@jwt_required()
def get_review_votes_action(review_id):
    review = get_review(review_id)
    if review:
        return jsonify(review.get_all_votes_json()), 200
    return jsonify({"error": "review not found"}), 404

# Gets all votes for a given review PAGE
@review_views.route("/reviews/<int:review_id>/votes", methods=["GET"])
@login_required
def votes_log_page(review_id):
    return render_template("votes-log.html", review=get_review(review_id), users=get_all_users())
