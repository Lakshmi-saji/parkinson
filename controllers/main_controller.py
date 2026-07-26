from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from flask_login import current_user, login_required
from app.models.user import User, PatientDetails
from app.models.voice_model import Prediction, VoiceSample
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/questionnaire')
def questionnaire():
    """Interactive pre-screening chat UI."""
    return render_template('questionnaire.html')

@main_bp.route('/questionnaire_submit', methods=['POST'])
def questionnaire_submit():
    """Stores the pre-screening chat details securely before voice upload."""
    age = request.form.get('age')
    gender = request.form.get('gender')
    tremors = request.form.get('tremors')
    slowness = request.form.get('slowness')
    rigidity = request.form.get('rigidity')
    family_history = request.form.get('family_history')
    
    # Session Capture (V69)
    session['questionnaire'] = {
        'age': age,
        'gender': gender,
        'tremors': tremors,
        'slowness': slowness,
        'rigidity': rigidity,
        'walking': request.form.get('walking', 'Not reported'),
        'smell': request.form.get('smell', 'Not reported'),
        'handwriting': request.form.get('handwriting', 'Not reported'),
        'sleep': request.form.get('sleep', 'Not reported'),
        'family_history': family_history,
        'additional': request.form.get('additional', '')
    }

    user_id = current_user.id if current_user.is_authenticated else None
    
    # We store it in Session for the immediate PDF/Analysis (V69)
    # We also create the DB record for historical reference
    from app.models.user import PatientDetails
    details = PatientDetails(
        user_id=user_id,
        age=int(age) if age and age.isdigit() else None,
        gender=gender,
        tremors=tremors,
        slowness=slowness,
        rigidity=rigidity,
        family_history=family_history
    )
    db.session.add(details)
    db.session.commit()
    session['patient_details_id'] = details.id
    
    flash("Screening profile established! Ready for voice analysis.", "success")
        
    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
def dashboard():
    recent_predictions = []
    total_screenings = 0
    last_risk = None

    if current_user.is_authenticated:
        recent_predictions = (
            Prediction.query
            .filter_by(user_id=current_user.id)
            .order_by(Prediction.created_at.desc())
            .limit(5)
            .all()
        )
        total_screenings = Prediction.query.filter_by(user_id=current_user.id).count()
        if recent_predictions:
            last_risk = recent_predictions[0].risk_level

    return render_template(
        'dashboard.html',
        recent_predictions=recent_predictions,
        total_screenings=total_screenings,
        last_risk=last_risk
    )

@main_bp.route('/history')
@login_required
def history():
    predictions = (
        Prediction.query
        .filter_by(user_id=current_user.id)
        .order_by(Prediction.created_at.desc())
        .all()
    )
    return render_template('history.html', predictions=predictions)

@main_bp.route('/about')
def about():
    return render_template('about.html')
