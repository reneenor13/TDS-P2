from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-pro")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/ask")
async def ask(question: str = Form(...)):
    try:
        response = model.generate_content(question)
        return {"answer": response.text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/upload")
async def upload(question: str = Form(...), file: UploadFile = File(None)):
    try:
        content = ""
        if file:
            content = (await file.read()).decode("utf-8")

        full_prompt = f"{question}\n\nFile Content:\n{content}"
        response = model.generate_content(full_prompt)
        return {"answer": response.text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
