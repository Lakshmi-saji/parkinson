from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String(10), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    role = db.Column(db.String(20), default='registered')  # 'registered' or 'guest'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    voice_samples = db.relationship('VoiceSample', backref='user', lazy=True, cascade='all, delete-orphan')
    predictions = db.relationship('Prediction', backref='user', lazy=True, cascade='all, delete-orphan')
    patient_details = db.relationship('PatientDetails', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class PatientDetails(db.Model):
    """Stores detailed pre-screening answers linked to a user or session."""
    __tablename__ = 'patient_details'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Null for guests
    session_id = db.Column(db.String(100), nullable=True) # For guest users

    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    tremors = db.Column(db.String(50), nullable=True)
    slowness = db.Column(db.String(50), nullable=True)
    rigidity = db.Column(db.String(50), nullable=True)
    family_history = db.Column(db.String(50), nullable=True)
    medication = db.Column(db.String(100), nullable=True)
    duration = db.Column(db.String(100), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PatientDetails id={self.id}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
