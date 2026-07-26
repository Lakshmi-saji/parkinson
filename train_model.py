import os
import pandas as pd
from joblib import dump
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

def build_dataset_features():
    print("=" * 60)
    print(" 🏥 NEUROVOICE V39: TRUE CLINICAL DATASET FEATURE TRAINING ")
    print("=" * 60)
    
    df_healthy = pd.DataFrame()
    if os.path.exists('dataset/plmpva_test-NoPDRS.csv'):
        df_healthy = pd.read_csv('dataset/plmpva_test-NoPDRS.csv')
        df_healthy['clinical_label'] = 0  # Healthy

    df_pd = pd.DataFrame()
    if os.path.exists('dataset/plmpva_test-WithPDRS.csv'):
        df_pd = pd.read_csv('dataset/plmpva_test-WithPDRS.csv')
        df_pd['clinical_label'] = 1  # Parkinson's
        
    df_train = pd.DataFrame()
    if os.path.exists('dataset/plmpva_train.csv'):
        df_train = pd.read_csv('dataset/plmpva_train.csv')
        df_train['clinical_label'] = 1  # Parkinson's Training Base

    dfs = [df for df in [df_healthy, df_pd, df_train] if not df.empty]
            
    if not dfs:
        print("❌ No CSV files found.")
        return
        
    master_df = pd.concat(dfs, ignore_index=True)
    master_df = master_df.dropna(subset=['feature01'])
    
    feature_cols = [f'feature{str(i).zfill(2)}' for i in range(1, 39)]
    X = master_df[feature_cols].copy()
    y = master_df['clinical_label']
    
    for col in feature_cols:
        X[col] = X[col].fillna(X[col].median())
        
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 🔹 Apply SMOTE to balance classes (Healthy vs Parkinson)
    from imblearn.over_sampling import SMOTE
    smote = SMOTE(random_state=42)
    X_smote, y_smote = smote.fit_resample(X_scaled, y)
    
    print(f"📊 Balanced Dataset (SMOTE): {len(y_smote)} total samples.")
    print(f"🟢 Healthy: {sum(y_smote==0)} | 🔴 Parkinson's: {sum(y_smote==1)}")
    
    # Reshape for CNN-LSTM: (samples, features, 1)
    X_reshaped = X_smote.reshape(X_smote.shape[0], X_smote.shape[1], 1)
    
    X_train, X_test, y_train, y_test = train_test_split(X_reshaped, y_smote, test_size=0.15, random_state=42, stratify=y_smote)
    
    print("\n[2/3] Building Deep Sequence Classifier (CNN-LSTM v45)...")
    
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Conv1D, MaxPooling1D, LSTM, Dense, Dropout, BatchNormalization
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

    model = Sequential([
        Conv1D(filters=32, kernel_size=3, activation='relu', input_shape=(38, 1)),
        BatchNormalization(),
        MaxPooling1D(pool_size=2),
        LSTM(64),
        Dropout(0.5),
        Dense(32, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), 
                  loss='binary_crossentropy', 
                  metrics=['accuracy'])
    
    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6)
    
    model.fit(
        X_train, y_train, 
        epochs=100, 
        batch_size=16, 
        validation_data=(X_test, y_test),
        callbacks=[early_stop, reduce_lr],
        verbose=1
    )
    
    # Evaluate
    y_pred_prob = model.predict(X_test)
    y_pred = (y_pred_prob > 0.5).astype(int).flatten()
    
    acc = accuracy_score(y_test, y_pred) * 100
    print(f"\n✅ CNN-LSTM v45 Dataset Classification Accuracy: {acc:.2f}%\n")
    print(classification_report(y_test, y_pred, target_names=["Healthy", "Parkinson's"]))

    os.makedirs('ml_model', exist_ok=True)
    model.save('ml_model/cnn_lstm_v45.keras')
    dump(scaler, 'ml_model/scaler_cnn_v45.pkl')
    print("✅ V45 CNN-LSTM Models Saved Successfully.")

if __name__ == "__main__":
    build_dataset_features()
