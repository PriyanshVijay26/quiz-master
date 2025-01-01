from flask import Flask,send_from_directory
from flask_login import LoginManager, login_required, current_user, UserMixin, login_user, logout_user 
from flask_security import Security, SQLAlchemyUserDatastore

from worker import celery_init_app
from flask_cors import CORS

import flask_excel as excel
from flask_sqlalchemy import SQLAlchemy
from celery.schedules import crontab
#from tasks import monthly_reminder, daily_remainder
#from cache import cache
from resources import api
from flask_uploads import UploadSet, configure_uploads, IMAGES, DOCUMENTS, patch_request_class
import secrets

db = SQLAlchemy()
from models import *
from sample_data import initialize_sample_data
from datastorefile import datastore

app = Flask(__name__)  # Create the Flask app instance first

# Now create the UploadSets and configure Flask-Uploads
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads/images' 
app.config['UPLOADED_DOCUMENTS_DEST'] = 'uploads/documents'
app.config['UPLOADED_VIDEOS_DEST'] = 'uploads/videos'

photos = UploadSet('photos', IMAGES)
documents = UploadSet('documents', extensions=('pdf', 'doc', 'docx'))
videos = UploadSet('videos', ['mp4', 'mov', 'avi']) 

configure_uploads(app, (photos, documents, videos))
patch_request_class(app, 16 * 1024 * 1024) 

def create_app():
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'  # Specify the login view

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appdb.sqlite3'
    app.config['SECRET_KEY'] = secrets.token_hex(16)
    app.config['SECURITY_PASSWORD_SALT'] = 'thisnameispriyansh'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSR_ENABLED'] = False
    app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Authentication-Token'
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_HOST'] = 'localhost'
    app.config['CACHE_REDIS_PORT'] = 6379
    app.config['CACHE_REDIS_DB'] = 3
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    #cache.init_app(app)


    CORS(app)


    # Initialize SQLAlchemy 
    db.init_app(app)  
    app.static_folder = 'uploads' 
    
    @app.route('/uploads/images/<path:filename>')
    def uploaded_image(filename):
        return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)

    @app.route('/uploads/documents/<path:filename>')
    def uploaded_document(filename):
        return send_from_directory(app.config['UPLOADED_DOCUMENTS_DEST'], filename)

    @app.route('/uploads/videos/<path:filename>')
    def uploaded_video(filename):
        return send_from_directory(app.config['UPLOADED_VIDEOS_DEST'], filename)
    api.init_app(app)
    excel.init_excel(app)
    app.security = Security(app, datastore)

    return app

# ... (rest of your code) ...

app = create_app()
celery_app = celery_init_app(app)


'''
@celery_app.on_after_configure.connect
def celery_job(sender,**kwargs):
    #sender.add_periodic_task(crontab(hour=12, minute=21, day_of_month=5), monthly_reminder.s())
    #sender.add_periodic_task(crontab(hour=12, minute=21), daily_remainder.s())

    #for testing
    #sender.add_periodic_task(60,monthly_reminder.s())
    #sender.add_periodic_task(40,daily_remainder.s())
'''


# ... (rest of your code) ...
if __name__ == '__main__':
    initialize_sample_data()
    app.run(debug=True)