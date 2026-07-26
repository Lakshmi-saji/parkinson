import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'parkinson-detection-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'parkinson.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    MODEL_PATH = os.path.join(BASE_DIR, 'ml_model', 'parkinson_model.pkl')
    SCALER_PATH = os.path.join(BASE_DIR, 'ml_model', 'scaler.pkl')
    REPORTS_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'reports')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload
    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'm4a', 'flac'}
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = 'csrf-secret-parkinson-2024'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
