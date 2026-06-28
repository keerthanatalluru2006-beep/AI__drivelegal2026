# 🚦 DriveLegal AI

An AI-powered traffic law assistant for Indian citizens, built for the **Road Safety Hackathon 2026** organised by CoERS, RBG Labs, IIT Madras.

## 🎯 Problem Statement
Citizens often lack easy access to clear, location-specific information about traffic laws, penalties, and enforcement procedures. DriveLegal AI solves this by providing instant, simplified legal guidance.

## ✨ Features

| Feature | Description |
|---|---|
| 💬 AI Legal Chatbot | Ask any traffic law question and get instant AI-powered answers with legal citations |
| ⚖️ Fine Predictor | Predict exact fines and penalties for any traffic violation |
| 📷 Challan Analyzer | Upload a challan photo — OCR extracts text, AI identifies violation and explains it |
| 🌐 Multilingual Support | Supports English, Hindi, Telugu, and Tamil |
| 🎤 Voice Assistant | Speak your question, hear the answer read aloud |

## 🏗️ System Architecture

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, JavaScript (Web Speech API for voice)
- **Backend**: FastAPI (Python)
- **AI**: Google Gemini 2.5 Flash API
- **Database**: PostgreSQL
- **OCR**: Tesseract OCR + Pillow

## 🚀 Setup Instructions

### Prerequisites
- Python 3.12+
- PostgreSQL 18
- Tesseract OCR ([Download](https://github.com/UB-Mannheim/tesseract/wiki))
- Google Gemini API key ([Get one](https://aistudio.google.com/app/apikey))

### Installation

1. **Clone the repository**
```bash
   git clone https://github.com/keerthanatalluru2006-beep/AI__drivelegal2026.git
   cd AI__drivelegal2026
```

2. **Create and activate virtual environment**
```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
   pip install fastapi uvicorn google-genai python-dotenv pytesseract pillow python-multipart psycopg2-binary sqlalchemy
```

4. **Set up environment variables**
   Create a `.env` file in the project root:

   5. **Set up PostgreSQL database**
   - Create a database named `drivelegal` in PostgreSQL
   - Update `DB_PASSWORD` in `setup_database.py` and `main.py` with your PostgreSQL password
   - Run the setup script:
```bash
   python setup_database.py
```

6. **Run the backend server**
```bash
   uvicorn main:app --reload
```

7. **Open the frontend**
   Open `frontend/index.html` in your browser (Chrome recommended for voice features)

## 📱 Usage

- **Chat Tab**: Type or speak a traffic law question
- **Fine Predictor Tab**: Enter a violation to get exact fine, legal section, and extra penalties
- **Challan Analyzer Tab**: Upload a photo of your traffic challan for instant analysis
- Use the **language dropdown** to switch between English, Hindi, Telugu, and Tamil
- Click **🎤** to use voice input, **🔊** to hear responses read aloud

## 📋 Supported Violations (Database)

- No Helmet, No Seatbelt, Triple Riding
- Red Light Jumping, Drunk Driving, Overspeeding
- No License, Using Phone While Driving
- No Insurance, Wrong Side Driving

## 🔗 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/ask` | POST | AI Legal Chatbot |
| `/predict-fine` | POST | Fine Predictor |
| `/analyze-challan` | POST | Challan Analyzer (image upload) |

## 👩‍💻 Developed By
Talluru Keerthana — Road Safety Hackathon 2026, IIT Madras