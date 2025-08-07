from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()  # Load .env file if exists

app = FastAPI()

# Allow frontend to talk to backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/", StaticFiles(directory="static", html=True), name="frontend")

# ✅ Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("Missing GOOGLE_API_KEY in environment variables.")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Store uploaded data (in-memory)
session_data = {"csv": None, "text": None}


# ✅ Route: Upload data + optional question
@app.post("/api/upload")
async def upload_files(
    questionsFile: UploadFile = File(None),
    csvFile: UploadFile = File(None),
    imageFile: UploadFile = File(None)
):
    try:
        if csvFile:
            df = pd.read_csv(csvFile.file)
            session_data["csv"] = df

        if questionsFile:
            session_data["text"] = await questionsFile.read()

        return {"answer": "Files uploaded successfully. You can now ask a question."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ✅ Route: Ask a question
@app.post("/api/ask")
async def ask_question(request: Request):
    try:
        body = await request.json()
        question = body.get("question", "").strip()

        if not question:
            return {"error": "No question provided."}

        prompt_parts = [question]

        if session_data["csv"] is not None:
            csv_preview = session_data["csv"].head(5).to_string()
            prompt_parts.append("Here’s a preview of the data:\n" + csv_preview)

        if session_data["text"] is not None:
            prompt_parts.append("Here’s some context from the text file:\n" + session_data["text"].decode())

        prompt = "\n\n".join(prompt_parts)

        response = model.generate_content(prompt)
        return {"answer": response.text}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
