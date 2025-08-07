from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Init app
app = FastAPI()

# Allow all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Route to serve homepage
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# --- AI Logic Function ---
def ask_gemini(prompt: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


# --- Endpoint for chat (single question only) ---
@app.post("/api/ask")
async def ask_endpoint(question: str = Form(...)):
    if not question.strip():
        return JSONResponse({"answer": "Please provide a question."}, status_code=400)
    answer = ask_gemini(question)
    return {"answer": answer}


# --- Endpoint for file upload and question ---
@app.post("/api/upload")
async def upload_endpoint(
    question: str = Form(...),
    file: UploadFile = File(None),
):
    try:
        file_text = ""
        if file:
            content = await file.read()
            try:
                file_text = content.decode("utf-8")
            except UnicodeDecodeError:
                file_text = f"[File {file.filename} is not a text file or cannot be decoded]"
        
        prompt = f"{file_text}\n\nUser question: {question}"
        answer = ask_gemini(prompt)
        return {"answer": answer}
    except Exception as e:
        return JSONResponse({"answer": f"Error: {str(e)}"}, status_code=500)
