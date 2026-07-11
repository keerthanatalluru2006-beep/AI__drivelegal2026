import os
import io
import json
import psycopg2
import pytesseract
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

# Load the API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=api_key)

# Tell pytesseract where Tesseract is installed (Windows local only)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Database connection — uses Render's DATABASE_URL in cloud, local config otherwise
DATABASE_URL = os.getenv("DATABASE_URL")

def find_violation_db(user_text: str):
    if DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    else:
        conn = psycopg2.connect(
            host="localhost",
            database="drivelegal",
            user="postgres",
            password=os.getenv("DB_PASSWORD", "drivelegal"),
            port="5432"
        )
    cursor = conn.cursor()
    cursor.execute("SELECT keyword, violation, fine, section, extra_penalty FROM violations")
    all_violations = cursor.fetchall()
    cursor.close()
    conn.close()

    user_text_lower = user_text.lower()
    for row in all_violations:
        keyword, violation, fine, section, extra_penalty = row
        if keyword in user_text_lower:
            return {
                "violation": violation,
                "fine": fine,
                "section": section,
                "extra_penalty": extra_penalty
            }
    return None

# Create the FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str
    language: str = "English"

SYSTEM_PROMPT = """You are DriveLegal AI, an assistant that helps Indian citizens 
understand traffic laws, violations, fines, and their rights under the Motor 
Vehicles Act. Always answer clearly and simply, mention the exact fine amount 
in rupees if applicable, and cite the relevant section of law if you know it. 
Keep answers concise and easy to understand for someone with no legal background."""

@app.get("/")
def home():
    return {"message": "DriveLegal AI backend is running!"}

@app.post("/ask")
def ask_question(q: Question):
    language_instruction = f"\n\nIMPORTANT: Respond entirely in {q.language} language, regardless of what language the question is asked in."
    prompt = f"{SYSTEM_PROMPT}{language_instruction}\n\nUser question: {q.question}"
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return {"answer": response.text}

@app.post("/predict-fine")
def predict_fine(q: Question):
    local_match = find_violation_db(q.question)
    if local_match:
        return {
            "source": "database",
            "violation": local_match["violation"],
            "fine": local_match["fine"],
            "section": local_match["section"],
            "extra_penalty": local_match["extra_penalty"]
        }

    ai_prompt = f"""A user described this traffic violation: "{q.question}"

Respond ONLY in this exact JSON format, nothing else, no markdown. Write all text VALUES in {q.language} language, but keep the JSON keys in English exactly as shown:
{{"violation": "name of violation", "fine": "fine amount in rupees", "section": "relevant Motor Vehicles Act section", "extra_penalty": "any extra penalty or None"}}
"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(ai_prompt)
    try:
        clean_text = response.text.strip().replace("```json", "").replace("```", "")
        ai_data = json.loads(clean_text)
        ai_data["source"] = "ai"
        return ai_data
    except:
        return {
            "source": "ai",
            "violation": "Unknown",
            "fine": "Could not determine",
            "section": "N/A",
            "extra_penalty": "N/A"
        }

@app.post("/analyze-challan")
async def analyze_challan(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))
    extracted_text = pytesseract.image_to_string(image)

    if not extracted_text.strip():
        return {
            "error": "Could not read any text from this image. Please upload a clearer photo of the challan."
        }

    local_match = find_violation_db(extracted_text)
    if local_match:
        return {
            "source": "database",
            "extracted_text": extracted_text.strip(),
            "violation": local_match["violation"],
            "fine": local_match["fine"],
            "section": local_match["section"],
            "extra_penalty": local_match["extra_penalty"],
            "payment_guidance": "Pay via the Parivahan e-Challan portal (echallan.parivahan.gov.in) using your challan number, or at the nearest traffic police office."
        }

    ai_prompt = f"""This text was extracted from a photo of an Indian traffic challan (ticket) using OCR, so it may contain errors or messy formatting:

"{extracted_text}"

Based on this, identify the most likely traffic violation. Respond ONLY in this exact JSON format, nothing else, no markdown:
{{"violation": "name of violation", "fine": "fine amount in rupees", "section": "relevant Motor Vehicles Act section", "extra_penalty": "any extra penalty or None", "payment_guidance": "brief step-by-step on how to pay this challan in India"}}
"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(ai_prompt)
    try:
        clean_text = response.text.strip().replace("```json", "").replace("```", "")
        ai_data = json.loads(clean_text)
        ai_data["source"] = "ai"
        ai_data["extracted_text"] = extracted_text.strip()
        return ai_data
    except:
        return {
            "source": "ai",
            "extracted_text": extracted_text.strip(),
            "violation": "Could not determine",
            "fine": "N/A",
            "section": "N/A",
            "extra_penalty": "N/A",
            "payment_guidance": "Please consult the original challan document or visit echallan.parivahan.gov.in"
        }