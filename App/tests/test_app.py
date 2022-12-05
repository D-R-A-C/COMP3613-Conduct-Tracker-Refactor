import pytest, logging, unittest, os
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from App.main import create_app
from App.database import create_db
from App.models import *
from App.controllers.auth import authenticate
from App.controllers.user import (
    create_user,
    get_all_users,
    get_all_users_json,
    get_user,
    get_user_by_email,
    update_user,
    delete_user,
)
from App.controllers.student import (
    create_student,
    get_students_by_name,
    get_student,
    get_all_students,
    get_all_students_json,
    update_student,
    delete_student,
)

from App.controllers.review import (
    create_review,
    update_review,
    delete_review,
    get_review,
    get_review_json,
    get_all_reviews,
    get_all_reviews_json,
    vote_review
)

from wsgi import app


LOGGER = logging.getLogger(__name__)

"""
   Unit Tests
"""

# Unit tests for User model
class UserUnitTests(unittest.TestCase):
    def test_new_admin_user(self):
        user = User("bob@mail.com", "bobpass", "bob", "jones", 2) 
        assert user.access == 2

    def test_new_staff_user(self):
        user = User("bob@mail.com", "bobpass", "bob", "jones", 1) 
        assert user.access == 1

    def test_user_is_admin(self):
        user = User("bob@mail.com", "bobpass", "bob", "jones", 2)
        assert user.is_admin()

    def test_user_is_not_admin(self):
        user = User("bob@mail.com", "bobpass", "bob", "jones", 1) 
        assert not user.is_admin()

    # pure function no side effects or integrations called
    def test_user_to_json(self):
        user = User("bob@mail.com", "bobpass", "bob", "jones", 1) 
        user_json = user.to_json()
        self.assertDictEqual(user_json, {"access": 1, "id": None, "email": "bob@mail.com", "firstName": "bob", "lastName": "jones"})

    def test_hashed_password(self):
        password = "pass"
        hashed = generate_password_hash(password, method='sha256')
        user = User("bob@mail.com", password, "bob", "jones", 1) 
        assert user.password != password

    def test_check_password(self):
        password = "pass"
        user = User("bob@mail.com", password, "bob", "jones", 1) 
        assert user.check_password(password) != password


# Unit tests for Student model
class StudentUnitTests(unittest.TestCase):
    def test_new_student(self):
        student = Student("bob", "jones", "FST", "Computer Science")
        assert (
            student.firstName == "bob"
            and student.lastName == "jones"
            and student.faculty == "FST"
            and student.programme == "Computer Science"
        )

    def test_student_to_json(self):
        student = Student("bob", "jones", "FST", "Computer Science")
        student_json = student.to_json()
        self.assertDictEqual(
            student_json,
            {
                "faculty": "FST",
                "id": None,
                "karma": 0,
                "firstName": "bob",
                "lastName": "jones",
                "programme": "Computer Science",
            },
        )

    def test_get_student_karma(self):
        student = Student("bob", "jones", "FST", "Computer Science")
        self.assertEqual(student.get_karma(), 0)


# Unit tests for Review model
class ReviewUnitTests(unittest.TestCase):
    def test_new_review(self):
        user = User("bob@mail.com", "bobpass", "bob", "jones", 1)
        student = Student("bob", "jones", "FST", "Computer Science")
        review = Review(user.id, student.id, "positive", "good review")
        student.reviews.append(review)
        assert review.student_id == None, review.staff_id == None
        assert review.sentiment =="positive", review.text == "good review"

    def test_review_to_json(self):
        user = User("bob@mail.com", "bobpass", "bob", "jones", 1)
        student = Student("bob", "jones", "FST", "Computer Science")
        review = Review(user.id, student.id, "positive", "good review")
        student.reviews.append(review)
        review_json = review.to_json()
        self.assertDictEqual(
            review_json,
            {
                "id": None,
                "staff_id": user.id,
                "student_id": student.id,
                "text": "good review",
                "sentiment": "positive",
                "timestamp": datetime.datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M"),
                "num_upvotes": 0,
                "num_downvotes": 0
            },
        )
        
# Unit tests for Vote model
class VoteUnitTests(unittest.TestCase):
    def test_new_upvote(self):
        user = User("bob@mail.com", "bobpass", "bob", "jones", 1)
        student = Student("bob", "jones", "FST", "Computer Science")
        review = Review(user.id, student.id, "positive", "good review")
        student.reviews.append(review)
        vote = Vote(user.id, review.id, "up")
        assert vote.review_id == None, vote.staff_id == None
        assert vote.type=="up"
        
    def test_new_downvote(self):
        user = User("bob@mail.com", "bobpass", "bob", "jones", 1)
        student = Student("bob", "jones", "FST", "Computer Science")
        review = Review(user.id, student.id, "positive", "good review")
        student.reviews.append(review)
        vote = Vote(user.id, review.id, "down")
        assert vote.review_id == None, vote.staff_id == None
        assert vote.type=="down"


"""
    Integration Tests
"""

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app.config.update({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///test.db"})
    create_db(app)
    yield app.test_client()
    os.unlink(os.getcwd() + "/App/test.db")


# Integration tests for User model
class UsersIntegrationTests(unittest.TestCase):    
    def test_authenticate(self):
        test_user = create_user("bob@mail.com", "bobpass", "bob", "jones", 1)
        assert authenticate(test_user.email, "bobpass") != None

    def test_create_admin(self):
        test_admin = create_user("rick@mail.com", "rickpass", "rick", "smith", 2)
        assert test_admin.email == "rick@mail.com" and test_admin.is_admin()

    def test_create_user(self):
        test_user = create_user("john@mail.com", "johnpass", "john", "doe", 1)
        assert test_user.email == "john@mail.com" and not test_user.is_admin()
        
    def test_get_user(self):
        test_user = create_user("johnny@mail.com", "johnnypass", "johnny", "kim", 1)
        user = get_user(test_user.id)
        assert test_user.email == user.email

    def test_get_all_users_json(self):
        test_user = create_user("james@mail.com", "pass", "james", "doe", 1)
        test_admin = create_user("ricky@mail.com", "rickypass", "ricky", "smith", 2)
        users = get_all_users()
        users_json = get_all_users_json()
        assert users_json == [user.to_json() for user in users]

    def test_update_user(self):
        user = create_user("danny@mail.com", "dannypass", "danny", "lee", 1)
        update_user(user.id, "dan@mail.com",)
        assert get_user(user.id).email == "dan@mail.com"

    def test_delete_user(self):
        user = create_user("bobby@mail.com", "bobbypass", "bobby", "park", 1)
        uid = user.id
        delete_user(uid)
        assert get_user(uid) is None


# Integration tests for Student model
class StudentIntegrationTests(unittest.TestCase):
    def test_create_student(self):
        test_student = create_student("bob", "jones", "cs","fst")
        student = get_student(test_student.id)
        assert test_student.firstName == student.firstName

    def test_get_students_by_name(self):
        test_student = create_student("bob", "jones", "cs","fst")
        students = get_students_by_name("bob", "jones")
        assert students[0].firstName == "bob" and students[0].lastName == "jones"

    def test_get_all_students_json(self):
        test_student = create_student("bob", "jones", "cs","fst")
        students = get_all_students()
        students_json = get_all_students_json()
        assert students_json == [student.to_json() for student in students]

    # tests updating a student's name, programme and/or faculty
    def test_update_student(self):
        student = create_student("bob", "jones", "cs", "fst")
        update_student(student.id, "bobby", "joseph", "it", "fst")
        assert get_student(student.id).firstName == "bobby"
        assert get_student(student.id).lastName == "joseph"
        assert get_student(student.id).programme == "it"
        assert get_student(student.id).faculty == "fst"

    def test_delete_student(self):
        student = create_student("bob", "jones", "fst", "cs")
        sid = student.id
        delete_student(sid)
        assert get_student(sid) is None


# Integration tests for Review model
class ReviewIntegrationTests(unittest.TestCase):
    def test_create_review(self):
        admin = create_user("dave@mail.com", "davepass", "dave", "lee", 2)
        student = create_student("bob", "jones", "cs", "fst")
        test_review = create_review(admin.id, student.id, "positive", "good")
        review = get_review(test_review.id)
        assert test_review.text == review.text

    def test_update_review(self):
        admin = create_user("davey@mail.com", "davepass", "davey", "singh", 2)
        student = create_student("bob", "jones", "cs", "fst")
        test_review = create_review(admin.id, student.id, "positive", "good")
        test_review = update_review(test_review.id, "negative", "bad")
        assert test_review.text == "bad"

    def test_delete_review(self):
        admin = create_user("sunny@mail.com", "pass", "sunny", "singh", 2)
        student = create_student("bob", "jones", "cs", "fst")
        test_review = create_review(admin.id, student.id, "positive", "good")
        assert delete_review(test_review.id) ==True

    def test_get_review_json(self):
        admin = create_user("darrius@mail.com", "pass", "darrius", "doe", 2)
        student = create_student("bob", "jones", "cs", "fst")
        test_review = create_review(admin.id, student.id, "positive", "good")
        review_json = get_review_json(test_review.id)
        assert review_json == test_review.to_json()

    def test_get_all_reviews_json(self):
        admin = create_user("donald@mail.com", "donald", "donald", "richards", 2)
        student = create_student("bob", "jones", "cs", "fst")
        reviews = get_all_reviews()
        reviews_json = get_all_reviews_json()
        assert reviews_json == [review.to_json() for review in reviews]

    def test_upvote_review(self):
        user = create_user("dani@mail.com", "dani", "dani", "rampersad", 2)
        student = create_student("bob", "jones", "cs", "fst")
        test_review = create_review(user.id, student.id, "positive", "good")
        test_review = vote_review(test_review.id, user.id, "up")
        assert test_review.get_num_upvotes() == 1

    def test_downvote_review(self):
        user = create_user("darla@mail.com", "pass", "darla", "jenkins", 2)
        student = create_student("bob", "jones", "cs", "fst")
        test_review = create_review(user.id, student.id, "positive", "good")
        test_review = vote_review(test_review.id, user.id, "down")
        assert test_review.get_num_downvotes() == 1

