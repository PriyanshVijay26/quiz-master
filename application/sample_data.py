from models import db, User, Role, Subject, Chapter, Quiz, Question, Photo, ChatMessage
from flask_security.utils import hash_password
from datetime import datetime
from werkzeug.security import generate_password_hash
def initialize_sample_data():
    """Initializes the database with sample data."""
    from main import app  # Import your Flask app instance
    with app.app_context():
        # Create all tables
        db.create_all()

        # Create roles if they don't exist
        if not Role.query.filter_by(name='admin').first():
            admin_role = Role(name='admin', description='Administrator')
            db.session.add(admin_role)
        if not Role.query.filter_by(name='user').first():
            user_role = Role(name='user', description='User')
            db.session.add(user_role)
        db.session.commit()

        # Create admin user if it doesn't exist
        if not User.query.filter_by(email='admin@example.com').first():
            admin_user = User(
                email='admin@example.com',
                password=generate_password_hash('adminpassword'),
                full_name='Admin User',
                active=True,
                fs_uniquifier='fs_admin_uniquifier',
                roles=[Role.query.filter_by(name='admin').first()]
            )
            db.session.add(admin_user)
            db.session.commit()

        # Create subjects if they don't exist
        if not Subject.query.filter_by(name='Mathematics').first():
            math_subject = Subject(name='Mathematics', description='The study of numbers, shapes, and patterns')
            db.session.add(math_subject)
        if not Subject.query.filter_by(name='Science').first():
            science_subject = Subject(name='Science', description='The study of the natural world')
            db.session.add(science_subject)
        if not Subject.query.filter_by(name='History').first():
            history_subject = Subject(name='History', description='The study of past events')
            db.session.add(history_subject)
        db.session.commit()

        # Create chapters if they don't exist
        if not Chapter.query.filter_by(name='Algebra').first():
            algebra_chapter = Chapter(subject_id=math_subject.id, name='Algebra', description='The study of mathematical symbols and the rules for manipulating these symbols')
            db.session.add(algebra_chapter)
        if not Chapter.query.filter_by(name='Calculus').first():
            calculus_chapter = Chapter(subject_id=math_subject.id, name='Calculus', description='The study of continuous change')
            db.session.add(calculus_chapter)
        if not Chapter.query.filter_by(name='Geometry').first():
            geometry_chapter = Chapter(subject_id=math_subject.id, name='Geometry', description='The study of shapes, sizes, positions, and dimensions')
            db.session.add(geometry_chapter)
        if not Chapter.query.filter_by(name='Physics').first():
            physics_chapter = Chapter(subject_id=science_subject.id, name='Physics', description='The study of matter and its motion through space and time')
            db.session.add(physics_chapter)
        if not Chapter.query.filter_by(name='Chemistry').first():
            chemistry_chapter = Chapter(subject_id=science_subject.id, name='Chemistry', description='The study of the composition, structure, properties, and reactions of matter')
            db.session.add(chemistry_chapter)
        if not Chapter.query.filter_by(name='Biology').first():
            biology_chapter = Chapter(subject_id=science_subject.id, name='Biology', description='The study of living organisms')
            db.session.add(biology_chapter)
        if not Chapter.query.filter_by(name='Ancient History').first():
            ancient_history_chapter = Chapter(subject_id=history_subject.id, name='Ancient History', description='The study of the distant past, from the earliest humans to the fall of the Roman Empire')
            db.session.add(ancient_history_chapter)
        if not Chapter.query.filter_by(name='Medieval History').first():
            medieval_history_chapter = Chapter(subject_id=history_subject.id, name='Medieval History', description='The study of the Middle Ages, from the fall of the Roman Empire to the Renaissance')
            db.session.add(medieval_history_chapter)
        if not Chapter.query.filter_by(name='Modern History').first():
            modern_history_chapter = Chapter(subject_id=history_subject.id, name='Modern History', description='The study of the modern era, from the Renaissance to the present day')
            db.session.add(modern_history_chapter)
        db.session.commit()

        # Create quizzes if they don't exist
        if not Quiz.query.filter_by(remarks='Basic algebra quiz').first():
            algebra_quiz_1 = Quiz(chapter_id=algebra_chapter.id, date_of_quiz=datetime(2024, 5, 3), time_duration='00:30', remarks='Basic algebra quiz')
            db.session.add(algebra_quiz_1)
        if not Quiz.query.filter_by(remarks='Advanced algebra quiz').first():
            algebra_quiz_2 = Quiz(chapter_id=algebra_chapter.id, date_of_quiz=datetime(2024, 5, 10), time_duration='00:30', remarks='Advanced algebra quiz')
            db.session.add(algebra_quiz_2)
        # ... add more quizzes with similar checks ...
        db.session.commit()

        # Create questions if they don't exist
        if not Question.query.filter_by(question_statement='What is the value of x in the equation 2x + 5 = 11?').first():
            question_1 = Question(
                quiz_id=algebra_quiz_1.id,
                question_statement='What is the value of x in the equation 2x + 5 = 11?',
                option1='3',
                option2='4',
                option3='5',
                option4='6',
                correct_option=1
            )
            db.session.add(question_1)
        if not Question.query.filter_by(question_statement='Simplify: (3x + 2) - (x - 5)').first():
            question_2 = Question(
                quiz_id=algebra_quiz_1.id,
                question_statement='Simplify: (3x + 2) - (x - 5)',
                option1='2x + 7',
                option2='2x - 3',
                option3='4x + 7',
                option4='4x - 3',
                correct_option=1
            )
            db.session.add(question_2)
        # ... add more questions with similar checks ...
        db.session.commit()

        # Create photos if they don't exist
        if not Photo.query.filter_by(photo_url='/path/to/photo1.jpg').first():  # Replace with actual photo URL
            photo_1 = Photo(question_id=question_1.id, photo_url='/path/to/photo1.jpg')
            db.session.add(photo_1)
        # ... add more photos with similar checks ...
        db.session.commit()

        # Create chat messages if they don't exist
        if not ChatMessage.query.filter_by(message='Hello!').first():
            chat_message_1 = ChatMessage(sender_id=admin_user.id, recipient_id=1, message='Hello!')
            db.session.add(chat_message_1)
        # ... add more chat messages with similar checks ...
        db.session.commit()

if __name__ == '__main__':
    initialize_sample_data()