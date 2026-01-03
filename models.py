from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(UserMixin, db.Model):
    """User model for storing user accounts."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    display_name = db.Column(db.String(150))
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Relationships
    quiz_results = db.relationship('QuizResult', backref='user', lazy='dynamic')
    interview_results = db.relationship('InterviewResult', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class QuizResult(db.Model):
    """QuizResult model for storing user's quiz scores."""
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(150), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    level = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Store the full quiz data for review
    quiz_data_json = db.Column(db.Text, nullable=True) # Stores JSON of questions
    user_answers_json = db.Column(db.Text, nullable=True) # Stores JSON of user answers

class InterviewResult(db.Model):
    """Stores results from mock interviews."""
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(150), nullable=False)
    level = db.Column(db.String(50))
    question_text = db.Column(db.Text, nullable=False)
    user_answer = db.Column(db.Text)
    ai_feedback = db.Column(db.Text)
    ai_score = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
