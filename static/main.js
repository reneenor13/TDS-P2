from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
import pandas as pd
import os

# ⛳ 1. Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY is not set.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# 🚀 2. FastAPI app setup
app = FastAPI()

# Allow static files (JS/CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory="templates")

# CORS (during dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session data
session_data = {"csv": None, "text": None}

# 🏠 3. Homepage route
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 📤 4. Upload endpoint
@app.post("/api/upload")
async def upload(
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

# 💬 5. Ask question endpoint
@app.post("/api/ask")
async def ask(request: Request):
    try:
        data = await request.json()
        question = data.get("question", "").strip()
        if not question:
            return {"error": "No question provided."}

        prompt_parts = [question]

        if session_data["csv"] is not None:
            preview = session_data["csv"].head(5).to_string()
            prompt_parts.append("CSV Data:\n" + preview)

        if session_data["text"] is not None:
            prompt_parts.append("Text Data:\n" + session_data["text"].decode())

        prompt = "\n\n".join(prompt_parts)

        response = model.generate_content(prompt)
        return {"answer": response.text}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
