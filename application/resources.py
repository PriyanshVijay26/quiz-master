from flask import Flask, jsonify, request,make_response,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from flask_security import Security, SQLAlchemyUserDatastore, auth_token_required, current_user,auth_required, roles_required
from datetime import datetime
from flask_restful import Api, Resource
from models import *
from flask_security import Security, SQLAlchemyUserDatastore
from datastorefile import datastore
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from pyuploadcare import Uploadcare
import os

api = Api()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


UPLOADCARE_PUBLIC_KEY = os.environ.get('UPLOADCARE_PUBLIC_KEY')
UPLOADCARE_SECRET_KEY = os.environ.get('UPLOADCARE_SECRET_KEY')

print("UPLOADCARE_PUBLIC_KEY:", UPLOADCARE_PUBLIC_KEY)
print("UPLOADCARE_SECRET_KEY:", UPLOADCARE_SECRET_KEY)




class UserRegistration(Resource):
    def post(self):
        """
        Register a new user using Flask-Security's user datastore.
        """
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        qualification = data.get('qualification')
        dob = data.get('dob')

        if not email or not password:
            return make_response(jsonify({'message': 'Email and password are required'}), 400)  # Use make_response

        existing_user = datastore.find_user(email=email)
        if existing_user:
            return make_response(jsonify({'message': 'User with this email already exists'}), 409)  # Use make_response

        try:
            # Use user_datastore.create_user to create the user
            datastore.create_user(
                email=email,
                password=generate_password_hash(password),
                full_name=full_name,
                qualification=qualification,
                dob=datetime.strptime(dob, '%Y-%m-%d').date(),
                active=True,
                roles=[Role.query.filter_by(name='user').first()]
            )
            db.session.commit()
            return make_response(jsonify({'message': 'User registered successfully'}), 201)

        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': 'Failed to register user', 'error': str(e)}), 500)

       
class UserLogin(Resource):
    def post(self):
        """
        Log in a user using Flask-Security and return a token.
        """
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return make_response(jsonify({'message': 'Email and password are required'}), 400)

        user = datastore.find_user(email=email)
        if not user or not check_password_hash(user.password, password):  # Use check_password_hash
            return make_response(jsonify({'message': 'Invalid credentials'}), 401)

        # Get user's roles
        roles = [role.name for role in user.roles]

        # Generate a token using Flask-Security
        token = user.get_auth_token()
        
        return make_response(jsonify({
            'message': 'Login successful',
            'user_id': user.id,
            'token': token,
            'roles': roles
        }), 200)






class SubjectResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self, subject_id=None):
        """Get subject(s) (Admin only).
        
        If subject_id is provided, get the subject with that ID.
        Otherwise, get all subjects.
        """
        try:
            if subject_id:
                subject = Subject.query.get_or_404(subject_id)
                return make_response(jsonify(subject.to_dict()), 200)
            else:
                subjects = Subject.query.all()
                return make_response(jsonify([subject.to_dict() for subject in subjects]), 200)
        except Exception as e:
            return make_response(jsonify({'message': 'Failed to retrieve subject(s)', 'error': str(e)}), 500)

    @auth_required('token')
    @roles_required('admin')
    def post(self):
        """Create a new subject (Admin only)."""
        if not current_user.has_role('admin'):
            return make_response(jsonify({'message': 'Unauthorized'}), 403)

        data = request.get_json()
        name = data.get('name')
        description = data.get('description')

        if not name:
            return make_response(jsonify({'message': 'Subject name is required'}), 400)

        new_subject = Subject(name=name, description=description)
        try:
            db.session.add(new_subject)
            db.session.commit()
            return make_response(jsonify({'message': 'Subject created', 'subject': new_subject.to_dict()}), 201)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': 'Failed to create subject', 'error': str(e)}), 500)

    @auth_required('token')
    @roles_required('admin')
    def put(self, subject_id):
        """Update an existing subject (Admin only)."""
        if not current_user.has_role('admin'):
            return make_response(jsonify({'message': 'Unauthorized'}), 403)

        subject = Subject.query.get_or_404(subject_id)
        data = request.get_json()
        subject.name = data.get('name', subject.name)
        subject.description = data.get('description', subject.description)
        try:
            db.session.commit()
            return make_response(jsonify({'message': 'Subject updated', 'subject': subject.to_dict()}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': 'Failed to update subject', 'error': str(e)}), 500)

    @auth_required('token')
    @roles_required('admin')
    def delete(self, subject_id):
        """Delete a subject (Admin only)."""
        if not current_user.has_role('admin'):
            return make_response(jsonify({'message': 'Unauthorized'}), 403)

        subject = Subject.query.get_or_404(subject_id)
        try:
            db.session.delete(subject)
            db.session.commit()
            return make_response(jsonify({'message': 'Subject deleted'}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': 'Failed to delete subject', 'error': str(e)}), 500)



class ChapterResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self, subject_id, chapter_id=None):
        """
        Get chapter(s) for a subject (Admin only).

        If chapter_id is provided, get the chapter with that ID within the subject.
        Otherwise, get all chapters for the subject.
        """
        try:
            if chapter_id:
                chapter = Chapter.query.filter_by(subject_id=subject_id, id=chapter_id).first_or_404()
                return make_response(jsonify(chapter.to_dict()), 200)
            else:
                chapters = Chapter.query.filter_by(subject_id=subject_id).all()
                return make_response(jsonify([chapter.to_dict() for chapter in chapters]), 200)
        except Exception as e:
            return make_response(jsonify({'message': 'Failed to retrieve chapter(s)', 'error': str(e)}), 500)

    @auth_required('token')
    @roles_required('admin')
    def post(self, subject_id):  # Add subject_id here
        """
        Create a new chapter (Admin only).
        """
        data = request.get_json()
        # subject_id = data.get('subject_id')  # No need to get it from data anymore
        name = data.get('name')
        description = data.get('description')

        if not name:  # You still need to check for the name
            return make_response(jsonify({'message': 'Chapter name is required'}), 400)

        subject = Subject.query.get(subject_id)
        if not subject:
            return make_response(jsonify({'message': 'Subject not found'}), 404)

        new_chapter = Chapter(subject_id=subject_id, name=name, description=description)
        try:
            db.session.add(new_chapter)
            db.session.commit()
            return make_response(jsonify({'message': 'Chapter created', 'chapter': new_chapter.to_dict()}), 201)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': 'Failed to create chapter', 'error': str(e)}), 500)



    @auth_required('token')
    @roles_required('admin')
    def put(self, subject_id, chapter_id):  # Add subject_id here
        """
        Update an existing chapter (Admin only).
        """
        chapter = Chapter.query.get_or_404(chapter_id)
        data = request.get_json()
        chapter.subject_id = data.get('subject_id', chapter.subject_id)
        chapter.name = data.get('name', chapter.name)
        chapter.description = data.get('description', chapter.description)
        try:
            db.session.commit()
            return make_response(jsonify({'message': 'Chapter updated', 'chapter': chapter.to_dict()}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': 'Failed to update chapter', 'error': str(e)}), 500)

    @auth_required('token')
    @roles_required('admin')
    def delete(self, subject_id, chapter_id):  # Add subject_id here
        """
        Delete a chapter (Admin only).
        """
        chapter = Chapter.query.get_or_404(chapter_id)
        try:
            db.session.delete(chapter)
            db.session.commit()
            return make_response(jsonify({'message': 'Chapter deleted'}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': 'Failed to delete chapter', 'error': str(e)}), 500)



class QuizResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self, subject_id, chapter_id, quiz_id=None):  # Add quiz_id as an optional argument
        """
        Get quizzes for a chapter (Admin only).
        If quiz_id is provided, get only that quiz. Otherwise, get all quizzes for the chapter.
        """
        try:
            if quiz_id:
                quiz = Quiz.query.filter_by(id=quiz_id, chapter_id=chapter_id).first_or_404()
                return make_response(jsonify(quiz.to_dict()), 200)
            else:
                quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
                return make_response(jsonify([quiz.to_dict() for quiz in quizzes]), 200)
        except Exception as e:
            return make_response(jsonify({'message': 'Failed to retrieve quizzes', 'error': str(e)}), 500)



    @auth_required('token')
    @roles_required('admin')
    def post(self, subject_id, chapter_id):  
        """
        Create a new quiz (Admin only).
        """
        data = request.get_json()
        date_of_quiz_str = data.get('date_of_quiz')  # Get date as string
        time_duration_str = data.get('time_duration')  # Get time duration as string
        remarks = data.get('remarks')

        try:
            # Convert date string to datetime object
            date_of_quiz = datetime.strptime(date_of_quiz_str, '%Y-%m-%d').date()  
        except ValueError:
            return make_response(jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400)

        try:
            # Convert time duration string to timedelta object
            hours, minutes = map(int, time_duration_str.split(':'))
            time_duration = timedelta(hours=hours, minutes=minutes)
        except ValueError:
            return make_response(jsonify({'message': 'Invalid time duration format. Use HH:MM'}), 400)

        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return make_response(jsonify({'message': 'Chapter not found'}), 404)

        new_quiz = Quiz(
            chapter_id=chapter_id,
            date_of_quiz=date_of_quiz,
            time_duration=str(time_duration),  # Store time duration as string
            remarks=remarks
        )
        try:
            db.session.add(new_quiz)
            db.session.commit()
            return make_response(jsonify({'message': 'Quiz created', 'quiz': new_quiz.to_dict()}), 201)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': 'Failed to create quiz', 'error': str(e)}), 500)

    @auth_required('token')
    @roles_required('admin')
    def put(self, subject_id, chapter_id, quiz_id):  
        """
        Update an existing quiz (Admin only).
        """
        quiz = Quiz.query.get_or_404(quiz_id)
        data = request.get_json()
        date_of_quiz_str = data.get('date_of_quiz', quiz.date_of_quiz)  # Get date as string
        time_duration_str = data.get('time_duration', quiz.time_duration)  # Get time duration as string
        remarks = data.get('remarks', quiz.remarks)

        try:
            # Convert date string to datetime object
            date_of_quiz = datetime.strptime(date_of_quiz_str, '%Y-%m-%d').date() 
        except ValueError:
            return make_response(jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400)

        try:
            # Convert time duration string to timedelta object
            hours, minutes = map(int, time_duration_str.split(':'))
            time_duration = timedelta(hours=hours, minutes=minutes)
        except ValueError:
            return make_response(jsonify({'message': 'Invalid time duration format. Use HH:MM'}), 400)

        quiz.date_of_quiz = date_of_quiz
        quiz.time_duration = str(time_duration)  # Store time duration as string
        quiz.remarks = remarks
        try:
            db.session.commit()
            return make_response(jsonify({'message': 'Quiz updated', 'quiz': quiz.to_dict()}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': 'Failed to update quiz', 'error': str(e)}), 500)

    @auth_required('token')
    @roles_required('admin')
    def delete(self, subject_id, chapter_id, quiz_id):  # Add subject_id and chapter_id
        """
        Delete a quiz (Admin only).
        """
        quiz = Quiz.query.get_or_404(quiz_id)
        try:
            db.session.delete(quiz)
            db.session.commit()
            return make_response(jsonify({'message': 'Quiz deleted'}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': 'Failed to delete quiz', 'error': str(e)}), 500)






class QuestionResource(Resource):
    @auth_required('token')
    def get(self, subject_id, chapter_id, quiz_id, question_id=None):  
        """
        Get a question by ID or all questions for a quiz.
        """
        try:
            if question_id:
                question = Question.query.filter_by(id=question_id, quiz_id=quiz_id).first_or_404()
                photo = Photo.query.filter_by(question_id=question_id).first()  # Get associated photo
                question_data = question.to_dict()
                if photo:
                    question_data['photo_url'] = photo.photo_url  # Add photo_url to question data
                return make_response(jsonify(question_data), 200)
            else:
                questions = Question.query.filter_by(quiz_id=quiz_id).all()
                questions_data = []
                for question in questions:
                    question_data = question.to_dict()
                    photo = Photo.query.filter_by(question_id=question.id).first()  # Get associated photo
                    if photo:
                        question_data['photo_url'] = photo.photo_url  # Add photo_url to question data
                    questions_data.append(question_data)
                return make_response(jsonify(questions_data), 200)
        except Exception as e:
            return make_response(jsonify({'message': 'Failed to retrieve questions', 'error': str(e)}), 500)

    
    @auth_required('token')
    @roles_required('admin')
    def post(self, subject_id, chapter_id, quiz_id):
        from flask_uploads import UploadNotAllowed
        from main import photos, documents, videos, datastore
        """
        Create a new question with an optional image (Admin only).
        """
        if 'file' not in request.files:
            return make_response(jsonify({'message': 'No file part'}), 400)
        file = request.files['file']
        if file.filename == '':
            return make_response(jsonify({'message': 'No selected file'}), 400)

        data = request.form  # Get data from form data
        
        question_statement = data.get('question_statement')
        option1 = data.get('option1')
        option2 = data.get('option2')
        option3 = data.get('option3')
        option4 = data.get('option4')
        correct_option = int(data.get('correct_option'))  # Convert to integer

        if not quiz_id or not question_statement or not correct_option:
            return make_response(jsonify({'message': 'Quiz ID, question statement, and correct option are required'}), 400)

        if not 1 <= correct_option <= 4:
            return make_response(jsonify({'message': 'Invalid correct option. It should be an integer between 1 and 4'}), 400)

        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return make_response(jsonify({'message': 'Quiz not found'}), 404)

        new_question = Question(
            quiz_id=quiz_id,
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option
        )
        try:
            db.session.add(new_question)
            db.session.commit()

            # Save the image using photos.save(...)
            if file and allowed_file(file.filename):
                filename = photos.save(file)
                photo_url = f"/uploads/images/{filename}"  # Construct the image URL

                new_photo = Photo(question_id=new_question.id, photo_url=photo_url)
                db.session.add(new_photo)
                db.session.commit()

            return make_response(jsonify({'message': 'Question created', 'question': new_question.to_dict()}), 201)
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Failed to create question', 'error': str(e)}), 500
    @auth_required('token')
    @roles_required('admin')
    def put(self, subject_id, chapter_id, quiz_id, question_id):
        from flask_uploads import UploadNotAllowed
        from main import photos, documents, videos, datastore
        """
        Update an existing question and optional image (Admin only).
        """
        question = Question.query.get_or_404(question_id)

        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = photos.save(file)  # Use photos.save(...)
                photo_url = f"/uploads/images/{filename}"  # Construct the image URL

                photo = Photo.query.filter_by(question_id=question.id).first()
                if photo:
                    photo.photo_url = photo_url
                else:
                    new_photo = Photo(question_id=question.id, photo_url=photo_url)
                    db.session.add(new_photo)

        data = request.form  # Get data from form data
        question.quiz_id = data.get('quiz_id', question.quiz_id)
        question.question_statement = data.get('question_statement', question.question_statement)
        question.option1 = data.get('option1', question.option1)
        question.option2 = data.get('option2', question.option2)
        question.option3 = data.get('option3', question.option3)
        question.option4 = data.get('option4', question.option4)
        correct_option = data.get('correct_option', question.correct_option) 
        if correct_option is not None:
            correct_option = int(correct_option)  # Convert to integer
            if not 1 <= correct_option <= 4:
                return make_response(jsonify({'message': 'Invalid correct option. It should be an integer between 1 and 4'}), 400)
            question.correct_option = correct_option

        try:
            db.session.commit()
            return make_response(jsonify({'message': 'Question updated', 'question': question.to_dict()}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': 'Failed to update question', 'error': str(e)}), 500)


    @auth_required('token')
    @roles_required('admin')
    def delete(self, subject_id, chapter_id, quiz_id, question_id): 
        """
        Delete a question and its associated image (Admin only).
        """
        question = Question.query.get_or_404(question_id)
        try:
            # Delete the associated photo first (if it exists) to avoid foreign key constraint errors
            photo = Photo.query.filter_by(question_id=question.id).first()
            if photo:
                db.session.delete(photo)

            db.session.delete(question)
            db.session.commit()
            return make_response(jsonify({'message': 'Question deleted'}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': 'Failed to delete question', 'error': str(e)}), 500)
        





class ScoreResource(Resource):
    @auth_required('token')
    @roles_required('user')
    def post(self):
        """
        Create a new score record when a user attempts a quiz.
        """
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        total_scored = data.get('total_scored')
        remarks = data.get('remarks')

        if not quiz_id or not total_scored:
            return jsonify({'message': 'Quiz ID and total score are required'}), 400

        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'message': 'Quiz not found'}), 404

        new_score = Score(
            quiz_id=quiz_id,
            user_id=current_user.id,  # Get the user ID from the current user
            time_stamp_of_attempt=datetime.utcnow(),  # Record the current time
            total_scored=total_scored,
            remarks=remarks
        )
        try:
            db.session.add(new_score)
            db.session.commit()
            return jsonify({'message': 'Score recorded', 'score': new_score.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Failed to record score', 'error': str(e)}), 500
        


class UserSubjectResource(Resource):  
    @auth_required('token')
    @roles_required('user')  
    def get(self, subject_id=None):  # Add optional subject_id argument
        """
        Get all subjects or a specific subject by ID (authenticated user with 'user' role).
        """
        try:
            if subject_id:
                subject = Subject.query.get_or_404(subject_id)
                return make_response(jsonify(subject.to_dict()), 200)
            else:
                subjects = Subject.query.all()
                return make_response(jsonify([subject.to_dict() for subject in subjects]), 200)
        except Exception as e:
            return make_response(jsonify({'message': 'Failed to retrieve subjects', 'error': str(e)}), 500)





class UserChapterResource(Resource):
    @auth_required('token')
    @roles_required('user')
    def get(self, subject_id, chapter_id=None):  # Add optional chapter_id argument
        """
        Get all chapters for a subject or a specific chapter by ID 
        (authenticated user with 'user' role).
        """
        try:
            if chapter_id:
                chapter = Chapter.query.filter_by(id=chapter_id, subject_id=subject_id).first_or_404()
                return make_response(jsonify(chapter.to_dict()), 200)
            else:
                chapters = Chapter.query.filter_by(subject_id=subject_id).all()
                return make_response(jsonify([chapter.to_dict() for chapter in chapters]), 200)
        except Exception as e:
            return make_response(jsonify({'message': 'Failed to retrieve chapters', 'error': str(e)}), 500)




class UserQuizResource(Resource):
    @auth_required('token')
    @roles_required('user')
    def get(self, subject_id, chapter_id, quiz_id=None):  # Add optional quiz_id argument
        """
        Get all quizzes for a chapter or a specific quiz by ID (authenticated user with 'user' role).
        """
        try:
            if quiz_id:
                quiz = Quiz.query.filter_by(id=quiz_id, chapter_id=chapter_id).first_or_404()
                return make_response(jsonify(quiz.to_dict()), 200)
            else:
                quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
                return make_response(jsonify([quiz.to_dict() for quiz in quizzes]), 200)
        except Exception as e:
            return make_response(jsonify({'message': 'Failed to retrieve quizzes', 'error': str(e)}), 500)
        


class UserQuestionResource(Resource):
    @auth_required('token')
    @roles_required('user')
    def get(self, subject_id, chapter_id, quiz_id, question_id=None):
        """
        Get a question by ID or all questions for a quiz (authenticated user with 'user' role).
        """
        try:
            if question_id:
                question = Question.query.filter_by(id=question_id, quiz_id=quiz_id).first_or_404()
                photo = Photo.query.filter_by(question_id=question_id).first()
                question_data = question.to_dict()
                if photo:
                    question_data['photo_url'] = photo.photo_url
                return make_response(jsonify(question_data), 200)
            else:
                questions = Question.query.filter_by(quiz_id=quiz_id).all()
                questions_data = []
                for question in questions:
                    question_data = question.to_dict()
                    photo = Photo.query.filter_by(question_id=question.id).first()
                    if photo:
                        question_data['photo_url'] = photo.photo_url
                    questions_data.append(question_data)
                return make_response(jsonify(questions_data), 200)
        except Exception as e:
            return make_response(jsonify({'message': 'Failed to retrieve questions', 'error': str(e)}), 500)



api.add_resource(UserQuestionResource,
                 '/api/user/subjects/<int:subject_id>/chapters/<int:chapter_id>/quizzes/<int:quiz_id>/questions',
                 '/api/user/subjects/<int:subject_id>/chapters/<int:chapter_id>/quizzes/<int:quiz_id>/questions/<int:question_id>')




api.add_resource(UserQuizResource, 
                 '/api/user/subjects/<int:subject_id>/chapters/<int:chapter_id>/quizzes',
                 '/api/user/subjects/<int:subject_id>/chapters/<int:chapter_id>/quizzes/<int:quiz_id>')



api.add_resource(UserChapterResource, 
                 '/api/user/subjects/<int:subject_id>/chapters',
                 '/api/user/subjects/<int:subject_id>/chapters/<int:chapter_id>')

api.add_resource(UserSubjectResource, '/api/user/subjects', '/api/user/subjects/<int:subject_id>')

api.add_resource(ScoreResource, '/api/scores')



api.add_resource(QuestionResource, 
                 '/api/subjects/<int:subject_id>/chapters/<int:chapter_id>/quizzes/<int:quiz_id>/questions',
                 '/api/subjects/<int:subject_id>/chapters/<int:chapter_id>/quizzes/<int:quiz_id>/questions/<int:question_id>')










api.add_resource(QuizResource, 
                 '/api/subjects/<int:subject_id>/chapters/<int:chapter_id>/quizzes',
                 '/api/subjects/<int:subject_id>/chapters/<int:chapter_id>/quizzes/<int:quiz_id>')


api.add_resource(ChapterResource, 
                 '/api/subjects/<int:subject_id>/chapters', 
                 '/api/subjects/<int:subject_id>/chapters/<int:chapter_id>')








api.add_resource(SubjectResource, '/api/subjects', '/api/subjects/<int:subject_id>')




api.add_resource(UserLogin, '/api/login')

api.add_resource(UserRegistration, '/api/register')