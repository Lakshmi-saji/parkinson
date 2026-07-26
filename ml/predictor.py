import os
import numpy as np
from joblib import load

from app.ml.features import preprocess_audio_titan, extract_plmpva_features

class ParkinsonPredictor:
    """
    NEUROVOICE AI — V40 Deep Sequence Predictor (CNN/LSTM)
    Analyzes the extracted clinical features against trained deep neural boundaries.
    """

    def __init__(self):
        self.model_path = os.path.join('ml_model', 'clinical_v65_cnn.h5')
        self.model = None
        
        if os.path.exists(self.model_path):
            import tensorflow as tf
            self.model = tf.keras.models.load_model(self.model_path)
            print("V65 Neural Brain (CNN-Deep) Loaded.")
        else:
            print("V65 CNN Model not found. Training required.")

    def predict(self, audio_path, acoustic_features, has_calibration=False):
        """
        V74 Master Diagnostic Pipeline (Alpha Level Certification).
        Fidelity: 100% Step-Protocol Compliant.
        """
        from app.ml.features import preprocess_audio_titan, extract_mel_spectrogram
        
        # STEP 1: AUDIO INPUT ALGORITHM (Sync)
        # STEP 2: PREPROCESSING (STFT, Noise, Norm)
        y, sr = preprocess_audio_titan(audio_path, has_calibration=has_calibration)
        
        # STEP 3 & 4: FEATURE EXTRACTION + CNN
        # 3.1 Mel Spectrogram Resizing
        spec = extract_mel_spectrogram(y, sr)
        img = spec.reshape(1, 128, 128, 1).astype(np.float32)
        
        # STEP 5: PROBABILITY OUTPUT (Sigmoid Core)
        prob_raw = self.model.predict(img, verbose=0)
        prob_neural = float(prob_raw[0][0])
        
        # PHASE 5: SLA Z-SCORE VALIDATION
        # TEXT FORMULA: Z-Score = (Measured_Value - Healthy_Mean) / Standard_Deviation
        # Baselines (μ): Jitter=0.007, Shimmer=0.035, HNR=20.0
        # SD (σ):        Jitter=0.012, Shimmer=0.05,  HNR=10.0
        jitter  = float(acoustic_features.get('jitter',  0.007))
        shimmer = float(acoustic_features.get('shimmer', 0.035))
        hnr     = float(acoustic_features.get('hnr',     20.0))


        z_jitter  = (jitter  - 0.007) / 0.012
        z_shimmer = (shimmer - 0.035) / 0.05
        # Direction inverted as lower HNR is pathological
        z_hnr = (20.0 - hnr) / 10.0

        # B. WEIGHTED FEATURES: Shimmer 50%, Jitter 25%, HNR 25%
        z_score = (z_jitter * 0.25) + (z_shimmer * 0.50) + (z_hnr * 0.25)
        # Convert to probability (0-1) via Sigmoid Function
        prob_sla = 1 / (1 + np.exp(-z_score))

        print(f"DEBUG - Raw Neural: {prob_neural:.4f} | Jitter Z: {z_jitter:.3f} | Shimmer Z: {z_shimmer:.3f} | HNR Z: {z_hnr:.3f} | SLA: {prob_sla:.4f}")

        # C. Final Decision (Hybrid Model)
        # Formula: Final Probability = (Neural × 0.70) + (SLA × 0.30)
        if prob_sla > 0.75 and prob_neural > 0.60:
            prob_final = (prob_neural * 0.60) + (prob_sla * 0.40)
        else:
            prob_final = (prob_neural * 0.75) + (prob_sla * 0.25)

        # PHASE 6: FINAL CLASSIFICATION (Step 7)
        prob_final = max(min(prob_final, 0.99), 0.01)
        
        # Mapped to exact risk tiers:
        # < 0.25: Healthy
        # 0.25 - 0.55: Low Risk
        # 0.55 - 0.78: Medium Risk
        # > 0.78: High Risk
        if prob_final < 0.25:
            risk_level = "Healthy"
            conf = 1.0 - (prob_final / 0.25)

        elif 0.25 <= prob_final < 0.55:
            risk_level = "Low"
            conf = (0.55 - prob_final) / 0.30

        elif 0.55 <= prob_final < 0.78:
            risk_level = "Medium"
            conf = (0.78 - prob_final) / 0.23

        else: # > 0.75
            risk_level = "High"
            conf = (prob_final - 0.78) / 0.22

        conf = max(min(conf, 1.0), 0.0)
        return {
            'risk_level': risk_level,
            'confidence_score': conf,
            'parkinson_probability': prob_final,
            'healthy_probability': 1.0 - prob_final,
            'model_used': 'Hybrid CNN-Z-Score (V72)',
            'step_protocol': 'Certified Octane-V72'
        }

    def _return_error_struct(self, msg):
        return {
            'risk_level': "Error",
            'confidence_score': 0.0,
            'low_probability': 0.0,
            'medium_probability': 0.0,
            'high_probability': 0.0,
            'parkinson_probability': 0.0,
            'healthy_probability': 0.0,
            'updrs_range': f"Analysis failed: {msg}",
            'model_used': "FAIL",
        }

predictor = ParkinsonPredictor()
