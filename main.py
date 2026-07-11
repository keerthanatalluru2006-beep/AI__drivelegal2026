import os
import psycopg2
import pytesseract
from PIL import Image
from fastapi import File, UploadFile
import io
from violations_data import find_violation
from dotenv import load_dotenv
import google as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load the API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Create a client to talk to Gemini
client = genai.Client(api_key=api_key)
# Tell pytesseract where Tesseract is installed on this Windows machine
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# IMPORTANT: replace with your actual postgres password (same one used in setup_database.py)
import urllib.parse

DATABASE_URL = os.getenv("DATABASE_URL")

def find_violation_db(user_text: str):
    # Use DATABASE_URL from environment (Render) or fall back to local config
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
# Create the FastAPI app (this is our server)
app = FastAPI()

# Allow our future frontend (running in a browser) to talk to this server
# Without this, browsers block the request for security reasons
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# This defines what a question from the user looks like
# It must contain a "question" field that is text
class Question(BaseModel):
    question: str
    language: str = "English"

# This is our system prompt — instructions that tell Gemini HOW to behave
# as our DriveLegal assistant, every single time it answers
SYSTEM_PROMPT = """You are DriveLegal AI, an assistant that helps Indian citizens 
understand traffic laws, violations, fines, and their rights under the Motor 
Vehicles Act. Always answer clearly and simply, mention the exact fine amount 
in rupees if applicable, and cite the relevant section of law if you know it. 
Keep answers concise and easy to understand for someone with no legal background."""

# This creates an endpoint: a specific "address" people can send requests to
# Here it's "/ask" and it only accepts POST requests (sending data TO the server)
@app.post("/ask")
def ask_question(q: Question):
    language_instruction = f"\n\nIMPORTANT: Respond entirely in {q.language} language, regardless of what language the question is asked in."
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{SYSTEM_PROMPT}{language_instruction}\n\nUser question: {q.question}"
    )
    return {"answer": response.text}

# A simple test endpoint to check the server is alive
@app.get("/")
def home():
    return {"message": "DriveLegal AI backend is running!"}

@app.post("/predict-fine")
def predict_fine(q: Question):
    # First, check our local database for a known violation
    local_match = find_violation_db(q.question)

    if local_match:
        return {
            "source": "database",
            "violation": local_match["violation"],
            "fine": local_match["fine"],
            "section": local_match["section"],
            "extra_penalty": local_match["extra_penalty"]
        }

    # If not found locally, fall back to Gemini AI
    ai_prompt = f"""A user described this traffic violation: "{q.question}"

    Respond ONLY in this exact JSON format, nothing else, no markdown. Write all text VALUES in {q.language} language, but keep the JSON keys in English exactly as shown:
    {{"violation": "name of violation", "fine": "fine amount in rupees", "section": "relevant Motor Vehicles Act section", "extra_penalty": "any extra penalty or None"}}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=ai_prompt
    )

    import json
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
    # Step 1: Read the uploaded image file into memory
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))

    # Step 2: Run OCR to extract any text from the image
    extracted_text = pytesseract.image_to_string(image)

    if not extracted_text.strip():
        return {
            "error": "Could not read any text from this image. Please upload a clearer photo of the challan."
        }

    # Step 3: Check our local database first for a quick match
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

    # Step 4: If not found locally, ask Gemini to read and interpret the challan text
    ai_prompt = f"""This text was extracted from a photo of an Indian traffic challan (ticket) using OCR, so it may contain errors or messy formatting:

    "{extracted_text}"

    Based on this, identify the most likely traffic violation. Respond ONLY in this exact JSON format, nothing else, no markdown:
    {{"violation": "name of violation", "fine": "fine amount in rupees", "section": "relevant Motor Vehicles Act section", "extra_penalty": "any extra penalty or None", "payment_guidance": "brief step-by-step on how to pay this challan in India"}}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=ai_prompt
    )

    import json
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