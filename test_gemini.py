import os
from dotenv import load_dotenv
from google import genai

# Load the API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Create a client to talk to Gemini
client = genai.Client(api_key=api_key)

# Send a simple test question
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is the fine for not wearing a helmet while riding a two-wheeler in India?"
)

print("Gemini says:")
print(response.text)