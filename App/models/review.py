from App.database import db

import datetime
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import JSON


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    sentiment = db.Column(db.String, nullable=False)
    text = db.Column(db.String(1000), nullable=False)
    votes = db.relationship("Vote", backref="Review", lazy=True, cascade="all, delete-orphan")
    
    def __init__(self, staff_id, student_id, sentiment, text):
        self.staff_id = staff_id
        self.student_id = student_id
        self.timestamp = datetime.datetime.now().replace(microsecond=0)
        self.sentiment = sentiment
        self.text = text
    
    def to_json(self):
        return {
            "id": self.id,
            "staff_id": self.staff_id,
            "student_id": self.student_id,
            "timestamp": self.timestamp.strftime("%d/%m/%Y %H:%M"),
            "sentiment":self.sentiment,
            "text": self.text,
            "num_upvotes": self.get_num_upvotes(),
            "num_downvotes": self.get_num_downvotes(),
        }
        
    def get_all_votes_json(self):
        return {
            "num_upvotes": self.get_num_upvotes(),
            "num_downvotes": self.get_num_downvotes(),
        }
        # votes=[]
        # for v in self.votes:
        #     votes.append(v.to_json())
        # return votes
    
    def get_upvotes(self):
        upvotes=[]
        for vote in self.votes:
            if vote.type=="up":
                upvotes.append(vote)
        return upvotes
    
    def get_downvotes(self):
        downvotes=[]
        for vote in self.votes:
            if vote.type=="down":
                downvotes.append(vote)
        return downvotes
    
    def get_num_upvotes(self):
        count = 0
        upvotes=self.get_upvotes()
        if upvotes:
            for vote in upvotes:
                count+=1
        return count
    
    def get_num_downvotes(self):
        count = 0
        downvotes=self.get_downvotes()
        if downvotes:
            for vote in downvotes:
                count+=1
        return count
    
    def get_num_votes(self):
        return self.get_num_upvotes() + self.get_num_downvotes()