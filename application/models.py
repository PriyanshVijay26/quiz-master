from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from datetime import datetime
db = SQLAlchemy()

# Define the many-to-many relationship between Users and Roles
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)  # Username
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)  # Add a unique identifier for the user model
    confirmed_at = db.Column(db.DateTime())
    full_name = db.Column(db.String(255))
    qualification = db.Column(db.String(255))
    dob = db.Column(db.Date())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    auth_token = db.Column(db.String(255), unique=True, nullable=True)
    
    
    def get_token_from_storage(self):
        return self.auth_token
    def __repr__(self):
        return '<User %r>' % self.username
    def __str__(self):
        return self.email

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    subject = db.relationship("Subject", backref=db.backref("chapters", lazy="dynamic"))

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'name': self.name,
            'description': self.description
        }

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'))
    date_of_quiz = db.Column(db.DateTime())
    time_duration = db.Column(db.String(5))  # HH:MM format
    remarks = db.Column(db.String(255))
    chapter = db.relationship("Chapter", backref=db.backref("quizzes", lazy="dynamic"))

    def __str__(self):
        return f"Quiz {self.id} - {self.chapter.name}"

    def to_dict(self):
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'date_of_quiz': self.date_of_quiz,
            'time_duration': self.time_duration,
            'remarks': self.remarks
        }

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    question_statement = db.Column(db.Text)
    option1 = db.Column(db.String(255))
    option2 = db.Column(db.String(255))
    option3 = db.Column(db.String(255))
    option4 = db.Column(db.String(255))
    correct_option = db.Column(db.Integer) 
    quiz = db.relationship("Quiz", backref=db.backref("questions", lazy="dynamic"))

    def __str__(self):
        return self.question_statement

    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'question_statement': self.question_statement,
            'option1': self.option1,
            'option2': self.option2,
            'option3': self.option3,
            'option4': self.option4,
            'correct_option': self.correct_option,
        }


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    time_stamp_of_attempt = db.Column(db.DateTime())
    total_scored = db.Column(db.Integer)
    remarks = db.Column(db.String(255))  # You can store the user selected options
    quiz = db.relationship("Quiz", backref=db.backref("scores", lazy="dynamic"))
    user = db.relationship("User", backref=db.backref("scores", lazy="dynamic"))

    def __str__(self):
        return f"Score {self.id} - User: {self.user.email}, Quiz: {self.quiz.id}"

    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'user_id': self.user_id,
            'time_stamp_of_attempt': self.time_stamp_of_attempt,
            'total_scored': self.total_scored,
            'remarks': self.remarks,
        }


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    photo_url = db.Column(db.String(255))  # Store the URL of the photo

    def __str__(self):
        return f"Photo {self.id} - Question: {self.question_id}"

    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'photo_url': self.photo_url,
        }



class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')

    def __str__(self):
        return f"ChatMessage {self.id} - From: {self.sender.email} To: {self.recipient.email}"

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'message': self.message,
            'timestamp': self.timestamp,
        }