import numpy as np
from sklearn.preprocessing import StandardScaler
from joblib import dump
import os

# Example clinical training features
# Format:
# [jitter, shimmer, hnr]

X_train = np.array([
    [0.003, 0.02, 25],
    [0.004, 0.03, 24],
    [0.005, 0.025, 23],
    [0.020, 0.10, 12],
    [0.018, 0.09, 14],
    [0.022, 0.11, 10]
])

# Create scaler
scaler = StandardScaler()

# Learn feature distribution
scaler.fit(X_train)

# Create folder if not exists
os.makedirs("ml_model", exist_ok=True)

# Save scaler
dump(scaler, "ml_model/scaler.pkl")

print("Scaler saved successfully.")