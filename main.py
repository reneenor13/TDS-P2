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
def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


# --- Endpoint for chat ---
@app.post("/api/ask")
async def ask_endpoint(request: Request):
    try:
        data = await request.json()
        user_input = data.get("question", "")
        if not user_input:
            return JSONResponse({"answer": "Please provide a question."}, status_code=400)
        answer = ask_gemini(user_input)
        return {"answer": answer}
    except Exception as e:
        return JSONResponse({"answer": f"Error: {str(e)}"}, status_code=500)


# --- Endpoint for file upload and question ---
@app.post("/api/upload")
async def upload_endpoint(
    question: str = Form(...),
    questions_file: UploadFile = File(None),
    csv_file: UploadFile = File(None),
    image_file: UploadFile = File(None),
):
    try:
        # Build full context from files
        file_text = ""

        if questions_file:
            file_text += f"\n\n[Questions file: {questions_file.filename}]\n"
            file_text += (await questions_file.read()).decode("utf-8")

        if csv_file:
            file_text += f"\n\n[CSV file: {csv_file.filename}]\n"
            file_text += (await csv_file.read()).decode("utf-8")

        if image_file:
            file_text += f"\n\n[Image file: {image_file.filename}] - Note: image upload not supported in Gemini Pro (text-only)"

        prompt = f"{file_text}\n\nUser question: {question}"

        # Send to Gemini
        answer = ask_gemini(prompt)
        return {"answer": answer}
    except Exception as e:
        return JSONResponse({"answer": f"Error: {str(e)}"}, status_code=500)
