from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
from utils import ask_gemini

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/")
async def analyze(
    questions: UploadFile = File(...),
    data: UploadFile = File(None),
    image: UploadFile = File(None)
):
    q_text = (await questions.read()).decode("utf-8")

    context = ""
    if data:
        df = pd.read_csv(data.file)
        context += f"Here is a preview of the dataset:\n{df.head().to_markdown()}\n\n"

    image_bytes = await image.read() if image else None
    reply = ask_gemini(q_text, context, image_bytes)

    return JSONResponse(content={"response": reply})
