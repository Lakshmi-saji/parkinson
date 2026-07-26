from app import db
from datetime import datetime

class VoiceSample(db.Model):
    __tablename__ = 'voice_samples'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    duration = db.Column(db.Float, nullable=True)       # seconds
    sample_rate = db.Column(db.Integer, nullable=True)
    file_size = db.Column(db.Integer, nullable=True)    # bytes
    source = db.Column(db.String(20), default='upload') # 'upload' or 'record'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    features = db.relationship('Features', backref='voice_sample', lazy=True, uselist=False, cascade='all, delete-orphan')
    predictions = db.relationship('Prediction', backref='voice_sample', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<VoiceSample {self.filename}>'


class Features(db.Model):
    __tablename__ = 'features'

    id = db.Column(db.Integer, primary_key=True)
    voice_sample_id = db.Column(db.Integer, db.ForeignKey('voice_samples.id'), nullable=False)

    # Pitch features (MDVP)
    mdvp_fo = db.Column(db.Float, nullable=True)      # Average vocal fundamental frequency
    mdvp_fhi = db.Column(db.Float, nullable=True)     # Maximum vocal fundamental frequency
    mdvp_flo = db.Column(db.Float, nullable=True)     # Minimum vocal fundamental frequency

    # Jitter features
    mdvp_jitter_pct = db.Column(db.Float, nullable=True)  # MDVP:Jitter(%)
    mdvp_jitter_abs = db.Column(db.Float, nullable=True)  # MDVP:Jitter(Abs)
    mdvp_rap = db.Column(db.Float, nullable=True)         # MDVP:RAP
    mdvp_ppq = db.Column(db.Float, nullable=True)         # MDVP:PPQ
    jitter_ddp = db.Column(db.Float, nullable=True)       # Jitter:DDP

    # Shimmer features
    mdvp_shimmer = db.Column(db.Float, nullable=True)     # MDVP:Shimmer
    mdvp_shimmer_db = db.Column(db.Float, nullable=True)  # MDVP:Shimmer(dB)
    shimmer_apq3 = db.Column(db.Float, nullable=True)     # Shimmer:APQ3
    shimmer_apq5 = db.Column(db.Float, nullable=True)     # Shimmer:APQ5
    mdvp_apq = db.Column(db.Float, nullable=True)         # MDVP:APQ
    shimmer_dda = db.Column(db.Float, nullable=True)      # Shimmer:DDA

    # Noise-to-ratio features
    nhr = db.Column(db.Float, nullable=True)              # NHR
    hnr = db.Column(db.Float, nullable=True)              # HNR

    # Nonlinear dynamical complexity
    rpde = db.Column(db.Float, nullable=True)
    dfa = db.Column(db.Float, nullable=True)
    spread1 = db.Column(db.Float, nullable=True)
    spread2 = db.Column(db.Float, nullable=True)
    d2 = db.Column(db.Float, nullable=True)
    ppe = db.Column(db.Float, nullable=True)

    # MFCCs (13 coefficients)
    mfcc_1  = db.Column(db.Float, nullable=True)
    mfcc_2  = db.Column(db.Float, nullable=True)
    mfcc_3  = db.Column(db.Float, nullable=True)
    mfcc_4  = db.Column(db.Float, nullable=True)
    mfcc_5  = db.Column(db.Float, nullable=True)
    mfcc_6  = db.Column(db.Float, nullable=True)
    mfcc_7  = db.Column(db.Float, nullable=True)
    mfcc_8  = db.Column(db.Float, nullable=True)
    mfcc_9  = db.Column(db.Float, nullable=True)
    mfcc_10 = db.Column(db.Float, nullable=True)
    mfcc_11 = db.Column(db.Float, nullable=True)
    mfcc_12 = db.Column(db.Float, nullable=True)
    mfcc_13 = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'mdvp_fo': self.mdvp_fo or 0.0,
            'mdvp_fhi': self.mdvp_fhi or 0.0,
            'mdvp_flo': self.mdvp_flo or 0.0,
            'mdvp_jitter_pct': self.mdvp_jitter_pct or 0.0,
            'mdvp_jitter_abs': self.mdvp_jitter_abs or 0.0,
            'mdvp_rap': self.mdvp_rap or 0.0,
            'mdvp_ppq': self.mdvp_ppq or 0.0,
            'jitter_ddp': self.jitter_ddp or 0.0,
            'mdvp_shimmer': self.mdvp_shimmer or 0.0,
            'mdvp_shimmer_db': self.mdvp_shimmer_db or 0.0,
            'shimmer_apq3': self.shimmer_apq3 or 0.0,
            'shimmer_apq5': self.shimmer_apq5 or 0.0,
            'mdvp_apq': self.mdvp_apq or 0.0,
            'shimmer_dda': self.shimmer_dda or 0.0,
            'nhr': self.nhr or 0.0,
            'hnr': self.hnr or 0.0,
            'rpde': self.rpde or 0.0,
            'dfa': self.dfa or 0.0,
            'spread1': self.spread1 or 0.0,
            'spread2': self.spread2 or 0.0,
            'd2': self.d2 or 0.0,
            'ppe': self.ppe or 0.0,
            'mfcc_1': self.mfcc_1 or 0.0,
            'mfcc_2': self.mfcc_2 or 0.0,
            'mfcc_3': self.mfcc_3 or 0.0,
            'mfcc_4': self.mfcc_4 or 0.0,
            'mfcc_5': self.mfcc_5 or 0.0,
            'mfcc_6': self.mfcc_6 or 0.0,
            'mfcc_7': self.mfcc_7 or 0.0,
            'mfcc_8': self.mfcc_8 or 0.0,
            'mfcc_9': self.mfcc_9 or 0.0,
            'mfcc_10': self.mfcc_10 or 0.0,
            'mfcc_11': self.mfcc_11 or 0.0,
            'mfcc_12': self.mfcc_12 or 0.0,
            'mfcc_13': self.mfcc_13 or 0.0,
        }


class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    voice_sample_id = db.Column(db.Integer, db.ForeignKey('voice_samples.id'), nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)          # 'Healthy', 'Low', 'Medium', 'High'
    confidence_score = db.Column(db.Float, nullable=False)         # 0.0 - 1.0
    parkinson_probability = db.Column(db.Float, default=0.0)
    healthy_probability = db.Column(db.Float, default=0.0)
    model_used = db.Column(db.String(50), default='V65 Neural Pro')
    
    # 🔹 Clinical Patient Vitals (V69)
    patient_age = db.Column(db.String(10), nullable=True)
    patient_gender = db.Column(db.String(20), nullable=True)
    symptom_tremors = db.Column(db.String(500), default='Not reported')
    symptom_slowness = db.Column(db.String(500), default='Not reported')
    symptom_rigidity = db.Column(db.String(500), default='Not reported')
    symptom_walking = db.Column(db.String(500), default='Not reported')
    symptom_smell = db.Column(db.String(500), default='Not reported')
    symptom_handwriting = db.Column(db.String(500), default='Not reported')
    symptom_sleep = db.Column(db.String(500), default='Not reported')
    symptom_family_history = db.Column(db.String(500), default='Not reported')
    symptom_additional = db.Column(db.Text, nullable=True)


    report_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Prediction {self.risk_level} ({self.confidence_score:.2%})>'
