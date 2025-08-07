import os
from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# FastAPI app setup
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def ask_chatgpt(prompt: str) -> str:
    """Send prompt to OpenAI ChatGPT and get response text."""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # or "gpt-4" or "gpt-3.5-turbo" depending on your access
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/ask")
async def ask_question(data: dict):
    try:
        question = data.get("question")
        if not question:
            return JSONResponse(content={"error": "Question cannot be empty"}, status_code=400)

        answer = ask_chatgpt(question)
        return {"answer": answer}
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
            answer = ask_chatgpt(content)
            response_text += "📄 **Questions.txt Answer**:\n" + answer + "\n\n"

        # Process csv file
        if csvFile:
            data = await csvFile.read()
            content = data.decode("utf-8")
            prompt = f"This is the CSV data:\n{content}\n\nPlease summarise and analyse it."
            answer = ask_chatgpt(prompt)
            response_text += "📊 **CSV Analysis**:\n" + answer + "\n\n"

        # Process image file (OpenAI API does not process images here)
        if imageFile:
            response_text += "🖼️ **Image** uploaded, but image processing is not supported in this API setup.\n"

        if not response_text:
            response_text = "No files uploaded."

        return {"answer": response_text.strip()}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
