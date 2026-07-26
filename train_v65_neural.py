import os
import librosa
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks
from sklearn.model_selection import train_test_split
import sys

sys.path.append(".")
from app.ml.features import extract_mel_spectrogram, preprocess_audio_titan

def augment_audio(y, sr):
    """
    V65 Data Augmentation (Step 4B).
    Creates variations of the voice to improve neural robustness.
    """
    augmentations = [y]
    # Add White Noise
    augmentations.append(y + 0.005 * np.random.normal(0, 1, len(y)))
    # Pitch Shift (+/- 2 semitones)
    augmentations.append(librosa.effects.pitch_shift(y=y, sr=sr, n_steps=2))
    # Time Stretch (Slow down a bit)
    augmentations.append(librosa.effects.time_stretch(y=y, rate=0.9))
    return augmentations

def build_v65_cnn_dataset():
    """
    Step 5B: Spectrogram Data Builder
    """
    hc_dir = "dataset/healthy/HC_AH"
    pd_dir = "dataset/parkinsons/PD_AH"
    
    images = []
    labels = []
    
    print("🧠 V65 CNN: Extracting Clinical Power-Spectrograms (Augmented)...")
    
    # ── 1. LOAD HEALTHY (Balanced 8x Augmentation) ──
    for f in os.listdir(hc_dir):
        if f.endswith(".wav"):
            try:
                y, sr = preprocess_audio_titan(os.path.join(hc_dir, f))
                for _ in range(8):
                    y_aug = augment_audio(y, sr)[np.random.randint(4)]
                    img = extract_mel_spectrogram(y_aug, sr)
                    images.append(img)
                    labels.append(0)
            except: pass

    # ── 2. LOAD PARKINSONS (Balanced 8x Augmentation) ──────────────────────────
    pd_files = [os.path.join(pd_dir, f) for f in os.listdir(pd_dir) if f.endswith(".wav")]
    for path in pd_files:
        try:
            y, sr = preprocess_audio_titan(path)
            for _ in range(8):
                y_aug = augment_audio(y, sr)[np.random.randint(4)]
                img = extract_mel_spectrogram(y_aug, sr)
                images.append(img)
                labels.append(1)
        except: pass

    X = np.array(images).reshape(-1, 128, 128, 1)
    y = np.array(labels)
    print(f"📊 V65 Neural Data ready: {X.shape} | Parkinson={len(y[y==1])} | Healthy={len(y[y==0])}")
    return X, y

def train_v65_cnn(X, y):
    """
    Step 5B: Neural Architecture (CNN)
    Step 6: Neural Training
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)
    
    # ── Architecture ──
    model = models.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 1)),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.2), # Step 5B: Prevent overfitting
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid') # Binary Output: Risk 0-1
    ])
    
    model.compile(
    optimizer='adam',
    loss=tf.keras.losses.BinaryFocalCrossentropy(),
    metrics=['accuracy']
)
    
    # Early Stopping (Step 6)
    early_stop = callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    
    print("V65 Training: Burning Neural Paths...")
    model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=20, batch_size=32, callbacks=[early_stop])
    
    os.makedirs("ml_model", exist_ok=True)
    model.save("ml_model/clinical_v65_cnn.h5")
    print("V65 CNN Clinical Model Saved.")

if __name__ == "__main__":
    X, y = build_v65_cnn_dataset()
    train_v65_cnn(X, y)
