
## Parkinson's Disease Detection Using Voice Pattern Analysis

NEUROVOICE AI is a web-based application developed to analyze voice recordings and identify vocal patterns that may be associated with Parkinson's disease.

The project combines a custom-built **Convolutional Neural Network (CNN)** with **Scientific Likelihood Analysis (SLA)** to analyze voice characteristics and estimate a Parkinson's risk category.

The application provides a simple interface where users can record or upload their voice samples and receive an analysis result.

> **Disclaimer:** This project is an academic research prototype. It is not a medical diagnostic system and should not be used as a replacement for professional medical evaluation.

---

## 📌 Project Overview

Parkinson's disease is a neurological disorder that can affect movement, speech, and voice characteristics.

Changes in voice may include:

- Reduced voice intensity
- Changes in pitch
- Increased jitter
- Increased shimmer
- Reduced harmonic-to-noise ratio

NEUROVOICE AI analyzes these voice characteristics using audio processing techniques, deep learning, and mathematical analysis.

The system combines the results from the CNN model and SLA analysis to generate an estimated risk category.

---

## 🎯 Objectives

- Analyze voice recordings for patterns associated with Parkinson's disease.
- Process audio recordings using digital signal processing techniques.
- Extract meaningful voice characteristics.
- Use a custom CNN model to analyze Mel Spectrogram representations.
- Apply mathematical SLA analysis to voice features.
- Combine CNN and SLA results using a hybrid approach.
- Display the final estimated risk category through a web interface.

---

## ✨ Features

- Voice recording through the web interface.
- Audio file upload.
- Audio preprocessing and noise reduction.
- Voice feature extraction.
- Mel Spectrogram generation.
- Custom CNN-based voice analysis.
- SLA-based mathematical analysis.
- Hybrid CNN and SLA prediction.
- Estimated risk categories:
  - Healthy
  - Low Risk
  - Medium Risk
  - High Risk
- Flask-based web application.

---

## 🏗️ System Architecture

The application follows a pipeline-based architecture.

<img width="1672" height="941" alt="NeuroVoice AI System Architecture" src="https://github.com/user-attachments/assets/d94d2837-316e-4bec-b250-b49e498f0c82" />



---

## 🔬 Methodology

### 1. Audio Acquisition

The system accepts voice recordings through:

- Browser-based microphone recording.
- Uploaded audio files.

The audio is converted into a suitable format for processing.

The application uses **16 kHz, mono audio** as the standard input format for the analysis pipeline.

### 2. Audio Preprocessing

The input audio is processed to improve its quality and consistency.

Preprocessing includes:

- Resampling to 16 kHz.
- Conversion to mono audio.
- Noise reduction.
- Audio normalization.
- Silence detection.
- Bandpass filtering.
- Removal of unnecessary silence.

These operations help prepare the voice recording for feature extraction and model analysis.

### 3. Feature Extraction

The system extracts different characteristics from the processed voice recording.

Important voice features include:

| Feature | Description |
|---|---|
| Pitch | Represents the perceived frequency of the voice. |
| Jitter | Measures variations in consecutive voice pitch periods. |
| Shimmer | Measures variations in voice amplitude. |
| HNR | Harmonic-to-Noise Ratio measures the relationship between harmonic voice components and noise. |
| MFCC | Represents important spectral characteristics of the voice. |
| Chroma | Represents the distribution of energy across musical pitch classes. |
| Zero-Crossing Rate | Measures how frequently the audio signal changes sign. |

These features provide information about the characteristics of the voice signal.

### 4. Mel Spectrogram Generation

The preprocessed audio is converted into a Mel Spectrogram.

A Mel Spectrogram represents the frequency content of audio over time.

It provides a visual representation of how the voice signal changes across different frequencies.

The generated Mel Spectrogram is prepared as a **128 × 128 single-channel input** for the CNN model.

### 5. CNN-Based Voice Analysis

The project uses a custom-built **2D Convolutional Neural Network (CNN)**.

The CNN analyzes the Mel Spectrogram to learn patterns from voice recordings.

The model contains:

- Convolutional layers.
- ReLU activation functions.
- Max pooling layers.
- Dropout layers.
- Fully connected layers.
- Sigmoid output layer.

The model is trained using binary labels:

- `0` – Healthy voice sample.
- `1` – Parkinson's voice sample.

The sigmoid output represents the model's estimated probability for the Parkinson's class.

### 6. Scientific Likelihood Analysis (SLA)

SLA is a mathematical analysis component used to evaluate selected voice characteristics.

It compares extracted voice features with reference statistical values using Z-score analysis.

The project considers features such as:

- Jitter.
- Shimmer.
- Harmonic-to-Noise Ratio.

The Z-score is calculated using:


Z = (Observed Value - Reference Mean) / Reference Standard Deviation


The resulting feature scores are combined using weighted mathematical analysis.

A sigmoid function is then applied to obtain an SLA-based probability.

SLA provides a separate mathematical analysis of the extracted voice characteristics.

### 7. Hybrid Prediction

The final prediction combines the CNN output and SLA output.

The current hybrid calculation is:


Final Probability =
    (CNN Probability × 0.70)
    +
    (SLA Probability × 0.30)


The CNN contributes 70% of the combined score.

The SLA analysis contributes 30%.

This produces a hybrid probability used by the final classification stage.

### 8. Risk Classification

The final hybrid probability is converted into one of four categories.

The classification thresholds are configurable in the prediction code.

The categories are:

| Category | Description |
|---|---|
| Healthy | Lower estimated Parkinson's-associated voice score. |
| Low Risk | Lower-level estimated risk category. |
| Medium Risk | Intermediate estimated risk category. |
| High Risk | Higher estimated risk category. |

These categories represent the application's estimated output and are not clinical diagnoses.

---

## 🛠️ Technologies Used

### Frontend

- HTML
- CSS
- JavaScript

### Backend

- Python
- Flask

### Deep Learning

- TensorFlow
- Keras
- Custom 2D CNN

### Audio Processing

- Librosa
- NumPy
- SciPy
- SoundFile
- noisereduce (optional, depending on installation)

### Development Tools

- Visual Studio Code
- Python virtual environment
- Git
- GitHub

---

## 📂 Project Structure

The following is the expected project structure. Actual filenames may differ depending on the current implementation.


NEUROVOICE-AI/
│
├── app.py
│
├── feature.py
│
├── predictor.py
│
├── requirements.txt
│
├── ml_model/
│   └── clinical_v65_cnn.h5
│
├── dataset/
│   ├── healthy/
│   │   └── HC_AH/
│   │
│   └── parkinsons/
│       └── PD_AH/
│
├── templates/
│   ├── index.html
│   ├── login.html
│   └── result.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── uploads/
│
└── README.md


### Important Files

| File | Purpose |
|---|---|
| `app.py` | Flask application and web routes. |
| `feature.py` | Audio preprocessing and feature extraction. |
| `predictor.py` | CNN prediction, SLA analysis, and hybrid classification. |
| `requirements.txt` | Python dependencies. |
| `ml_model/clinical_v65_cnn.h5` | Trained CNN model. |
| `dataset/` | Training audio dataset. |
| `templates/` | HTML pages. |
| `static/` | CSS, JavaScript, and images. |
| `uploads/` | Uploaded audio files, if used by the application. |

---



## 📊 Dataset

The project uses voice recordings containing healthy and Parkinson's voice samples.

The dataset is organized into two main categories:

dataset/
│
├── healthy/
│
└── parkinsons/


The healthy category contains voice recordings from healthy participants.

The Parkinson's category contains voice recordings from participants with Parkinson's disease.

The dataset is used to train the CNN model to distinguish between the two voice classes.

**Dataset information, sample counts, participant details, and source citations should be added according to the actual dataset used in the project.**

---

## 🧪 Model Training

The CNN model is trained using Mel Spectrogram representations of voice recordings.

The training process includes:

1. Loading healthy and Parkinson's voice samples.
2. Preprocessing the audio.
3. Generating Mel Spectrograms.
4. Assigning binary labels.
5. Training the CNN model.
6. Evaluating model performance.
7. Saving the trained model.

The trained model is saved as:


ml_model/clinical_v65_cnn.h5


The application loads this model during prediction.

---

Screenshots

<img width="1225" height="834" alt="Screenshot 2026-10-30 at 19 34 22" src="https://github.com/user-attachments/assets/5fd95c47-3a84-4137-a771-d58325ccf963" />

<img width="1232" height="976" alt="Screenshot 2026-10-30 at 19 34 33" src="https://github.com/user-attachments/assets/6a335f2c-2599-420e-8817-6c7515235e03" />

<img width="1720" height="996" alt="Screenshot 2026-10-30 at 19 34 42" src="https://github.com/user-attachments/assets/7f83538c-aaf6-451b-a522-4554b4076a3c" />

<img width="1725" height="984" alt="Screenshot 2026-10-30 at 19 35 42" src="https://github.com/user-attachments/assets/8e475b2f-12b4-4cd1-9c74-27f72d4cc16c" />






## 🔐 Privacy and Security

Voice recordings may contain personal information.

The application should:

- Process uploaded audio securely.
- Restrict access to stored recordings.
- Avoid exposing user recordings publicly.
- Remove temporary recordings when no longer required.
- Avoid storing sensitive information unnecessarily.

Storage and deletion behavior depends on the application's actual implementation.

---

## ⚠️ Limitations

- This project is an academic research prototype.
- Voice analysis alone cannot confirm Parkinson's disease.
- Voice characteristics may vary due to age, environment, recording equipment, language, and other factors.
- The model's performance depends on the quality and representativeness of the training dataset.
- The SLA reference values require appropriate validation.
- The hybrid probability is not automatically a clinically calibrated probability.
- The four risk categories are generated using classification thresholds.
- The application has not been established as a clinically validated diagnostic tool.

The system should be evaluated using independent test data before making claims about accuracy or real-world medical performance.

---

## 🔮 Future Enhancements

- Improve the quality and diversity of the voice dataset.
- Evaluate the model using independent participants.
- Add more robust model validation.
- Improve probability calibration.
- Add multilingual voice support.
- Improve audio recording quality checks.
- Add secure user history and report generation.
- Improve accessibility and user interface design.
- Integrate additional validated clinical information, where appropriate.
- Conduct clinical evaluation before considering real-world medical use.

---

## 👩‍💻 Project Purpose

This project was developed as an academic application of:

- Artificial Intelligence.
- Deep Learning.
- Digital Signal Processing.
- Audio Feature Extraction.
- Mathematical and Statistical Analysis.
- Web Application Development.

It demonstrates how voice signal processing and machine learning can be combined in a research-oriented screening prototype.

---

## 📄 License

Add the appropriate license for your project before publishing the repository.

If no license has been selected, the project should not be assumed to be open source for reuse.

---

## 🙏 Acknowledgements

Thanks to the researchers and dataset contributors whose work supports Parkinson's voice analysis research.

