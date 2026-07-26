import numpy as np
import librosa
try:
    import noisereduce as nr
    _HAS_NOISEREDUCE = True
except Exception:
    nr = None
    _HAS_NOISEREDUCE = False
from scipy.signal import butter, filtfilt

def preprocess_audio_titan(audio_path, has_calibration=False):
    """
    PHASE 1: AUDIO ACQUISITION & PHASE 2: CLINICAL PREPROCESSING
    """
    # Auto-detect if this is a browser recording with 1.5s room calibration prefix.
    # Browser recordings are around 5 seconds (4.5s - 5.5s) and not in dataset.
    actual_duration = librosa.get_duration(path=audio_path)
    if not has_calibration:
        if (4.5 <= actual_duration <= 5.5) or ("358129d972574482a4dfee1ed9016a24" in audio_path):
            if "dataset" not in audio_path:
                has_calibration = True

    duration = 6.0 if has_calibration else 4.0
    y_full, sr = librosa.load(audio_path, sr=16000, mono=True, duration=duration)

    if len(y_full) < sr * 0.5:
        return np.zeros(sr * 2), sr

    # ── PHASE 2: CLINICAL PREPROCESSING (Digital Signal Purification - DSP) ──
    CALIB_SECS = 1.5
    calib_samples = int(sr * CALIB_SECS)

    # Step 2.2: Spectral Gating (Removes background noise)
    if has_calibration and len(y_full) > calib_samples + int(sr * 1.0):
        # BROWSER RECORDING: first 1.5s = exact room noise floor
        y_noise = y_full[:calib_samples]
        y = y_full[calib_samples:]
        print(f"🎙️ V74 Calibration: noise_rms={np.sqrt(np.mean(y_noise**2)):.5f}")
        if _HAS_NOISEREDUCE:
            y = nr.reduce_noise(y=y, y_noise=y_noise, sr=sr, prop_decrease=0.40)
        else:
            print("⚠️ noisereduce not available, skipping noise reduction (calibrated).")
    else:
        # UPLOADED FILE: use full signal, estimate noise statistically
        y = y_full
        if _HAS_NOISEREDUCE:
            y = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.40, stationary=True)
        else:
            print("⚠️ noisereduce not available, skipping noise reduction (uploaded).")

    # Limit to 4 seconds of voice
    y = y[:sr * 4]

    # Step 2.1: Normalization (Sets audio to 0.7 peak amplitude)
    peak = np.max(np.abs(y))
    if peak > 0.001:
        y = librosa.util.normalize(y) * 0.7

    # Step 2.3: Silence Masking (Eliminates non-speaking parts via gated silencer)
    rms_step = int(sr * 0.05)
    for i in range(0, len(y), rms_step):
        chunk = y[i:i+rms_step]
        if len(chunk) > 0 and np.max(np.abs(chunk)) < 0.005:
            y[i:i+rms_step] = 0

    # Step 2.4: Bandpass Filter (60Hz - 3500Hz) (Keeps only voice frequencies)
    nyq = 0.5 * sr
    b, a = butter(4, [60 / nyq, 3500 / nyq], btype='band')
    y = filtfilt(b, a, y)

    y_trim, _ = librosa.effects.trim(y, top_db=30)
    if len(y_trim) < 4096:
        y_trim = y

    return np.clip(y_trim, -1.0, 1.0), sr

def extract_mel_spectrogram(y, sr, n_mels=128, n_frames=128):
    """
    PHASE 3: FEATURE EXTRACTION
    A. Neural Features (CNN Input):
      - Mel Spectrogram: Converts audio into 128x128 image
      - Spectral Padding: Pads short audio to fixed length
      - Log-DB Scaling: Converts to dB for better feature clarity
    """
    # • Mel Spectrogram: Converts audio to melspectrogram (n_mels=128)
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels, fmax=sr/2)
    
    # • Log-DB Scaling: Converts to dB for better feature clarity
    S_dB = librosa.power_to_db(S, ref=np.max)
    
    # • Spectral Padding: Pads short audio to fixed length (n_frames=128)
    if S_dB.shape[1] < n_frames:
        S_dB = np.pad(S_dB, ((0, 0), (0, n_frames - S_dB.shape[1])), mode='constant', constant_values=-80.0)
    else:
        S_dB = S_dB[:, :n_frames]
        
    S_norm = (S_dB + 80.0) / 80.0
    return np.clip(S_norm, 0.0, 1.0).astype(np.float32)

def _compute_hnr_autocorr(y, sr, fmin=75, fmax=500):
    """
    Compute HNR via autocorrelation (clinical standard).
    Parkinson's voices: ~10-15 dB (noisy, breathy)
    Healthy voices:     ~20-25 dB (clean, harmonic)
    """
    frame_len = int(sr * 0.025)   # 25 ms frames
    hop_len   = int(sr * 0.010)   # 10 ms hop
    min_lag   = int(sr / fmax)
    max_lag   = int(sr / fmin)

    hnr_vals = []
    for start in range(0, len(y) - frame_len, hop_len):
        frame = y[start:start + frame_len]
        if np.max(np.abs(frame)) < 0.01:
            continue                          # skip silence

        # Normalised autocorrelation
        acf = np.correlate(frame, frame, mode='full')
        acf = acf[len(acf) // 2:]            # positive lags only
        acf = acf / (acf[0] + 1e-9)

        lag_end = min(max_lag, len(acf) - 1)
        if lag_end <= min_lag:
            continue

        r1 = float(np.max(acf[min_lag:lag_end]))
        r1 = np.clip(r1, 1e-6, 0.9999)
        hnr_db = 10.0 * np.log10(r1 / (1.0 - r1))
        hnr_vals.append(hnr_db)

    if hnr_vals:
        return float(np.median(hnr_vals))
    return 10.0   # conservative default (sounds Parkinson's-like)


def extract_plmpva_features(y, sr):
    """
    PHASE 3: FEATURE EXTRACTION
    B. Acoustic Biomarkers (SLA):
      - Pitch: Fundamental frequency of voice.
      - Jitter: Variation in frequency.
      - Shimmer: Variation in amplitude.
      - HNR: Signal clarity vs noise.
      - MFCC: Represents vocal tract features.
    """
    if len(y) < 2048:
        y = np.pad(y, (0, 2048 - len(y)))

    features = {}

    # • Pitch & Jitter & Shimmer calculation
    f0 = librosa.yin(y, fmin=50, fmax=500, sr=sr)
    rms_frames = librosa.feature.rms(y=y)[0]
    
    threshold = np.max(rms_frames) * 0.15
    voiced_mask = (rms_frames > threshold)
    valid_f0 = f0[:len(voiced_mask)][voiced_mask]
    valid_f0 = valid_f0[valid_f0 > 0]

    if len(valid_f0) > 4:
        periods = 1.0 / valid_f0
        diffs = np.abs(np.diff(periods))
        p_95 = np.percentile(diffs, 95)
        diffs_clean = diffs[diffs < p_95]
        
        jitter_pct = np.mean(diffs_clean) / (np.mean(periods) + 1e-9)
        rms_voiced = rms_frames[voiced_mask]
        shimmer = np.std(rms_voiced) / (np.mean(rms_voiced) + 1e-9)

        # • Jitter & Shimmer metrics
        features['jitter'] = float(jitter_pct)
        features['shimmer'] = float(shimmer)
    else:
        features['jitter'] = 0.003
        features['shimmer'] = 0.02
        valid_f0 = np.array([178.0])

    # • Pitch (Fundamental frequency of voice)
    features['feature01'] = float(np.median(valid_f0))
    features['feature02'] = features['jitter']
    features['feature04'] = features['shimmer']

    # • HNR: Signal clarity vs noise (Autocorrelation method — clinical standard)
    # Parkinson's patients have LOWER HNR (~10-15 dB) vs healthy (~20-25 dB)
    # because Parkinson's causes more breathiness/noise in the voice signal.
    hnr_db = _compute_hnr_autocorr(y, sr)
    features['hnr'] = float(hnr_db)
    features['feature05'] = float(hnr_db)

    # • MFCC: Represents vocal tract features (coefficients 1-40)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    for i in range(40):
        features[f'feature{str(6+i).zfill(2)}'] = float(np.mean(mfcc[i]))

    # Chroma & Contrast
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    features['feature46'] = float(np.mean(chroma))
    features['feature47'] = float(np.mean(librosa.feature.zero_crossing_rate(y)))

    return features
