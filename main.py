from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/")
async def handle_upload(questions: UploadFile = File(...), data: UploadFile = File(None), image: UploadFile = File(None)):
    try:
        questions_content = await questions.read()
        questions_text = questions_content.decode("utf-8")

        response = f"Processed {len(questions_text.splitlines())} questions."
        return {"answer": response}

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


class ChatRequest(BaseModel):
    question: str

@app.post("/chat/")
async def chat(chat: ChatRequest):
    try:
        return {"answer": f"Great question! '{chat.question}' — this is a placeholder answer from the AI."}
    except Exception as e:
        return {"error": str(e)}
