from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
import pandas as pd

# Get Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY in environment.")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# FastAPI app setup
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

# Mount static files (index.html, style.css, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/", StaticFiles(directory="static", html=True), name="frontend")

# In-memory storage for uploaded content
session_data = {"csv": None, "text": None}


# ✅ Route: Upload files
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
            prompt_parts.append("CSV Preview:\n" + csv_preview)

        if session_data["text"] is not None:
            prompt_parts.append("Text file content:\n" + session_data["text"].decode())

        prompt = "\n\n".join(prompt_parts)

        response = model.generate_content(prompt)
        return {"answer": response.text}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
