"""
Diagnostic script — uses same formula as updated predictor.py
(Jitter 25%, Shimmer 50%, HNR 25% — hybrid formula)
"""
import sys, os
sys.path.insert(0, '/Users/mac/Desktop/parkinson')
os.chdir('/Users/mac/Desktop/parkinson')
import numpy as np

def run_diagnosis(audio_path, label):
    print(f"\n{'='*60}")
    print(f"  TESTING: {label}")
    print(f"  File:    {audio_path}")
    print(f"{'='*60}")

    from app.ml.features import preprocess_audio_titan, extract_mel_spectrogram, extract_plmpva_features
    import tensorflow as tf

    y, sr = preprocess_audio_titan(audio_path, has_calibration=False)
    print(f"\n[Phase 1+2] Audio: len={len(y)}, sr={sr}, peak={np.max(np.abs(y)):.4f}")

    spec = extract_mel_spectrogram(y, sr)
    model = tf.keras.models.load_model("ml_model/clinical_v65_cnn.h5", compile=False)
    img = spec.reshape(1, 128, 128, 1).astype(np.float32)
    prob_neural = float(model.predict(img, verbose=0)[0][0])
    print(f"[Phase 4] CNN prob_neural: {prob_neural:.4f}")

    feats = extract_plmpva_features(y, sr)
    jitter  = float(feats.get('jitter',  0.007))
    shimmer = float(feats.get('shimmer', 0.035))
    hnr     = float(feats.get('hnr',     20.0))
    print(f"[Phase 3B] Jitter={jitter:.5f}  Shimmer={shimmer:.5f}  HNR={hnr:.2f}")

    # ── Predictor.py formula (Jitter 25%, Shimmer 50%, HNR 25%) ──────────────
    z_jitter  = (jitter  - 0.007) / 0.012
    z_shimmer = (shimmer - 0.035) / 0.05
    z_hnr     = (20.0 - hnr) / 10.0
    z_score   = (z_jitter * 0.25) + (z_shimmer * 0.50) + (z_hnr * 0.25)
    prob_sla  = 1 / (1 + np.exp(-z_score))
    print(f"[Phase 5] Z-jitter={z_jitter:.4f}  Z-shimmer={z_shimmer:.4f}  Z-hnr={z_hnr:.4f}  Z-combined={z_score:.4f}")
    print(f"[Phase 5] prob_sla={prob_sla:.4f}")

    prob_final = (prob_neural * 0.70) + (prob_sla * 0.30)
    print(f"[Phase 5] Hybrid = {prob_neural:.4f}×0.70 + {prob_sla:.4f}×0.30 = {prob_final:.4f}")

    if prob_final < 0.25:   risk = "Healthy"
    elif prob_final < 0.55: risk = "Low Risk"
    elif prob_final < 0.78: risk = "Medium Risk"
    else:                   risk = "High Risk"

    print(f"\n[Phase 6] FINAL: {prob_final:.4f}  =>  {risk}")

print("--- DIAGNOSING NEWLY ALIGNED PIPELINE ---")
run_diagnosis("app/static/uploads/358129d972574482a4dfee1ed9016a24.wav", "USER'S TARGET PARKINSON WAV")
run_diagnosis("app/static/uploads/56e0c38c52ab48679110be7685762fed.mp3", "MICHAEL J. FOX MP3")
run_diagnosis("app/static/uploads/d21ff4d247ca4e9c92a45f6abec7677c.mp3", "HEALTHY MP3")
