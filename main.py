import os
from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env if available
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize Gemini model
model = genai.GenerativeModel("gemini-pro")

# FastAPI app setup
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/ask")
async def ask_question(data: dict):
    try:
        question = data.get("question")
        if not question:
            return JSONResponse(content={"error": "Question cannot be empty"}, status_code=400)

        response = model.generate_content(question)
        return {"answer": response.text}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/upload")
async def upload_files(
    questionsFile: UploadFile = None,
    csvFile: UploadFile = None,
    imageFile: UploadFile = None
):
    try:
        response_text = ""

        # Process questions.txt
        if questionsFile:
            text = await questionsFile.read()
            content = text.decode("utf-8")
            response = model.generate_content(content)
            response_text += "📄 **Questions.txt Answer**:\n" + response.text + "\n\n"

        # Process csv file
        if csvFile:
            data = await csvFile.read()
            content = data.decode("utf-8")
            response = model.generate_content(f"This is the CSV data:\n{content}\n\nSummarise and analyse it.")
            response_text += "📊 **CSV Analysis**:\n" + response.text + "\n\n"

        # Process image file (Gemini doesn't support image input via Python SDK yet)
        if imageFile:
            response_text += "🖼️ **Image** uploaded, but Gemini's image input is not supported in Python SDK yet.\n"

        if not response_text:
            response_text = "No files uploaded."

        return {"answer": response_text.strip()}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
