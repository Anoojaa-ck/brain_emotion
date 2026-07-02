 MINDTRACE — AI-Powered Multimodal Mental Health Monitoring

[![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00?logo=tensorflow)](https://tensorflow.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**MINDTRACE (BrainEmotion)** is a Django-based platform that fuses **EEG brain signals**, **facial expression recognition**, **NLP-based text emotion analysis**, and **heart rate data** into a single stress-assessment dashboard.

> Built for researchers and clinicians exploring multimodal biomarkers for depression and emotional well-being.

---

## Features

- **EEG Emotion Classification** — GRU-based deep learning model (trained on NEGATIVE/NEUTRAL/POSITIVE sentiment data) predicts 3 emotion states — angry, happy, or sad — from 2500+ EEG feature vectors.
- **Facial Emotion Recognition (FER)** — Detects facial expressions from diary photos using MTCNN + FER (TensorFlow backend).
- **Text Emotion Analysis (NLP)** — Transformer-based model (`j-hartmann/emotion-english-distilroberta-base`) extracts emotion from diary text entries.
- **Heart Rate Monitoring** — Stores heart rate data from mobile app integration as a physiological stress indicator.
- **Stress Index Computation** — Weighted fusion (40% EEG, 30% diary emotions, 30% heart rate) producing a 0–100% stress score.
- **Admin Dashboard (MINDTRACE)** — Full analytics panel with per-user trends, emotion breakdowns, and activity timelines.
- **Android App Backend** — RESTful JSON API for mobile app integration (authentication, diary CRUD, emotion uploads, heart rate logging).

---

## Tech Stack

| Tier | Technology |
|------|-----------|
| **Backend** | Django 6.0, Django REST Framework |
| **Database** | MySQL |
| **Deep Learning** | TensorFlow / Keras (GRU), scikit-learn, SciPy, PyWavelets |
| **NLP** | Hugging Face Transformers, PyTorch, DistilRoBERTa |
| **Computer Vision** | FER (with MTCNN), OpenCV |
| **Frontend** | Bootstrap 5, DataTables, jQuery, Chart.js-style graphs |
| **ASGI / WSGI** | ASGI + WSGI configured for production deployment |

---

## Architecture

User (Mobile App)
    │
    ├─ EEG text file ──► GRU Emotion Classifier ──┐
    ├─ Diary + Photo ──► FER (face) + DistilRoBERTa (text) ──┤
    └─ Heart rate ──► Heart rate data ──────────────────────┘
                            │
                    Stress Index (weighted fusion)
                            │
                    Admin Dashboard (MINDTRACE)

---

## Getting Started

### Prerequisites

- Python 3.12+
- MySQL server
- (Optional) CUDA-capable GPU for faster training

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/brainemotion.git
   cd brainemotion
2. Create a virtual environment
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
3. Install dependencies
pip install django tensorflow keras numpy pandas scikit-learn scipy pywavelets
pip install transformers torch torchvision
pip install fer opencv-python
pip install mysqlclient matplotlib seaborn
4. Configure the database  
Edit brainemotion/settings.py to match your MySQL credentials:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'brainemotion',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
5. Create the database
CREATE DATABASE brainemotion;
6. Run migrations
python manage.py migrate
7. Create Django groups  
Two groups are expected: Admin and Users (referenced in the views).
8. Start the development server
python manage.py runserver
9. Access the admin panel  
Open http://localhost:8000/myapp/loginpage_get/ (http://localhost:8000/myapp/loginpage_get/)
Project Structure
brainemotion/
├── brainemotion/              # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── myapp/                     # Main application
│   ├── views.py               # All API endpoints
│   ├── models.py              # Users, Brainemotion, Diary, heartbeat, Review
│   ├── urls.py                # Route definitions
│   ├── training.py            # GRU model training script
│   ├── pred.py                # EEG prediction module
│   ├── k.py                   # Standalone text emotion script
│   ├── _best_model.h5         # Pre-trained GRU weights
│   └── emotions.csv           # EEG training dataset
├── templates/Admin/           # Admin dashboard templates
├── media/                     # User uploads
├── manage.py
└── README.md
API Overview
All endpoints are prefixed with /myapp/. The API is designed for integration with an Android mobile application.
Endpoint
loginpage_get/, loginpage_post/
userlogin_post/
usersignup_post/
user_upload_text_post/
diarycontents/
viewdiarycontent/
user_emotion_count/
user_emotion_count_daily/
get_user_graph_data/<id>/
heartbeat_post/
user_sendreview_post/
Model Training
To re-train the EEG emotion classifier:
python myapp/training.py
This loads emotions.csv (NEGATIVE / NEUTRAL / POSITIVE sentiment labels), builds a 3-class GRU classifier, and saves the best weights to _best_model.h5. The prediction module (pred.py) maps output indices to ['angry', 'happy', 'sad'] labels.
Security Notes
- CSRF middleware is currently disabled — enable it in production.
- Email credentials in settings.py are hardcoded — move them to environment variables.
- DEBUG = True should be set to False in production.
License
Distributed under the MIT License. See LICENSE for more information.
Contact
Team MINDTRACE — Kozhikode, Kerala, India  
Email: projectbrain2025@gmail.com

