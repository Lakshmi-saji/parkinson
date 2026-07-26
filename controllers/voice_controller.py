import os
import uuid
import numpy as np
from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, jsonify, current_app, send_file, session)
from flask_login import current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.voice_model import VoiceSample, Features, Prediction
from app.ml.features import preprocess_audio_titan, extract_plmpva_features
from app.ml.predictor import predictor
import traceback

voice_bp = Blueprint('voice', __name__)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'm4a', 'flac', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_id():
    return current_user.id if current_user.is_authenticated else None

@voice_bp.route('/analyze', methods=['POST'])
def analyze():
    user_id = get_user_id()
    audio_source = request.form.get('source', 'upload')
    audio_file = request.files.get('audio_data') if audio_source == 'record' else request.files.get('audio_file')

    if not audio_file or audio_file.filename == '':
        flash('No audio file provided.', 'error')
        return redirect(url_for('main.dashboard'))

    upload_folder = current_app.config['UPLOAD_FOLDER']
    ext = audio_file.filename.rsplit('.', 1)[-1].lower() if '.' in audio_file.filename else 'webm'
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(upload_folder, unique_name)
    audio_file.save(save_path)

    sample = VoiceSample(
        user_id=user_id,
        filename=audio_file.filename or f"recording.{ext}",
        file_path=save_path,
        file_size=os.path.getsize(save_path),
        source=audio_source
    )
    db.session.add(sample)
    db.session.flush()

    # V74: Pass calibration flag — only browser recordings have the 1.5s noise prefix
    y, sr = preprocess_audio_titan(save_path, has_calibration=(audio_source == 'record'))
    sample.duration = len(y) / sr
    sample.sample_rate = sr

    plm_features = extract_plmpva_features(y, sr)
    
    # 🔹 Map extracted features to DB model (V55 — Percentage scale for UI)
    feature_dict = {
        'mdvp_fo':          float(plm_features.get('feature01', 0.0)),
        'mdvp_jitter_pct':  float(plm_features.get('jitter', 0.0)) * 100.0, # e.g. 1.2%
        'mdvp_jitter_abs':  float(plm_features.get('jitter', 0.0)) / max(float(plm_features.get('feature01', 120.0)), 1.0),
        'mdvp_shimmer':     float(plm_features.get('shimmer', 0.0)) * 100.0,
        'mdvp_shimmer_db':  20.0 * np.log10(1.0 + float(plm_features.get('shimmer', 0.0)) + 1e-9),
        'hnr':              float(plm_features.get('hnr', 0.0)),
        'nhr':              1.0 / (float(plm_features.get('hnr', 10.0)) + 1e-9),
        'ppe':              float(plm_features.get('feature35', 0.0))
    }
    
    # Add MFCCs for UI if needed
    for i in range(6, 19):
        feature_dict[f'mfcc_{i-5}'] = float(plm_features.get(f'feature{str(i).zfill(2)}', 0.0))

    feat = Features(voice_sample_id=sample.id, **feature_dict)
    db.session.add(feat)
    db.session.flush()

    # Pass PLM Features to True Dataset Predictor (V74.3: forward calibration flag)
    result = predictor.predict(save_path, plm_features, has_calibration=(audio_source == 'record'))

    #V69 Clinical Intake Capture
    from flask import session
    q_data = session.get('questionnaire', {})

    # V65.6/V69 Persistence Mapping
    pred = Prediction(
        user_id=user_id,
        voice_sample_id=sample.id,
        risk_level=result.get('risk_level', 'Unknown'),
        confidence_score=result.get('confidence_score', 0.0),
        parkinson_probability=result.get('parkinson_probability', 0.0),
        healthy_probability=result.get('healthy_probability', 1.0),
        model_used=result.get('model_used', 'V65 Neural Pro'),
        
        # Clinical Intake (V69)
        patient_age=q_data.get('age', 'N/A'),
        patient_gender=q_data.get('gender', 'N/A'),
        symptom_tremors=q_data.get('tremors', 'Not reported'),
        symptom_slowness=q_data.get('slowness', 'Not reported'),
        symptom_rigidity=q_data.get('rigidity', 'Not reported'),
        symptom_walking=q_data.get('walking', 'Not reported'),
        symptom_smell=q_data.get('smell', 'Not reported'),
        symptom_handwriting=q_data.get('handwriting', 'Not reported'),
        symptom_sleep=q_data.get('sleep', 'Not reported'),
        symptom_family_history=q_data.get('family_history', 'Not reported'),
        symptom_additional=q_data.get('additional', '')
    )
    db.session.add(pred)
    db.session.commit()

    return redirect(url_for('voice.results', prediction_id=pred.id))

@voice_bp.route('/results/<int:prediction_id>')
def results(prediction_id):
    pred = Prediction.query.get_or_404(prediction_id)
    sample = VoiceSample.query.get(pred.voice_sample_id)
    features = Features.query.filter_by(voice_sample_id=pred.voice_sample_id).first()
    return render_template('results.html', prediction=pred, sample=sample, features=features.to_dict() if features else {})

@voice_bp.route('/download-report/<int:prediction_id>', methods=['GET'])
def download_report(prediction_id):
    """
    V65.5 Final Export: Generates a clinical PDF report.
    """
    prediction = Prediction.query.get_or_404(prediction_id)
    features = Features.query.filter_by(voice_sample_id=prediction.voice_sample_id).first()
    
    # ── Map Prediction & Features for PDF ──
    from app.utils.pdf_generator import generate_medical_report
    
    # Pack clinical data for PDF (V69)
    patient_data = {
        'age': prediction.patient_age,
        'gender': prediction.patient_gender,
        'additional': prediction.symptom_additional or '',
        'symptoms': {
            'Tremors': prediction.symptom_tremors,
            'Slowness of Movement': prediction.symptom_slowness,
            'Muscle Rigidity': prediction.symptom_rigidity,
            'Walking & Gait': prediction.symptom_walking,
            'Sense of Smell': prediction.symptom_smell,
            'Handwriting Changes': prediction.symptom_handwriting,
            'Sleep Patterns': prediction.symptom_sleep,
            'Family History': prediction.symptom_family_history
        }
    }
    
    # Features were mapped for PDF display
    from flask import send_file
    pdf_buffer = generate_medical_report(prediction, features, patient_data)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"NeuroVoice_Report_{prediction.id}.pdf",
        mimetype='application/pdf'
    )
