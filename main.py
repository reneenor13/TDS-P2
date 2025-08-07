# main.py
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "fastapi",
#   "uvicorn",
#   "python-multipart",
#   "aiofiles",
#   "pandas",
#   "matplotlib",
#   "openai",
#   "jinja2"
# ]
# ///

import os
import base64
import io
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import matplotlib.pyplot as plt
import openai

openai.api_key = os.getenv("AIPROXY_TOKEN")
openai.api_base = "https://api.proxy.sanand.workers.dev/v1"
model = "gpt-4o-mini"

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/")
async def analyze(
    questions: UploadFile = File(...),
    data: UploadFile = File(None),
    image: UploadFile = File(None)
):
    q_text = (await questions.read()).decode()
    summary = ""

    # Handle CSV
    if data:
        df = pd.read_csv(data.file)
        summary += f"CSV Shape: {df.shape}\n\nColumns:\n{df.dtypes.to_string()}\n\nHead:\n{df.head().to_string(index=False)}"

    # Handle Image
    image_data = None
    if image:
        image_data = base64.b64encode(await image.read()).decode("utf-8")

    # Construct messages
    messages = [
        {"role": "system", "content": "You are a data analyst who answers data and image-based questions."},
        {"role": "user", "content": f"Questions:\n{q_text}"},
    ]
    if summary:
        messages.append({"role": "user", "content": f"Here is a summary of the CSV file:\n{summary}"})

    # Call OpenAI
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=1000,
    )

    answer = response.choices[0].message["content"]

    # Optional plot
    image_uri = None
    if data:
        plt.figure()
        df.select_dtypes(include='number').hist(figsize=(8, 5))
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        image_uri = "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")

    return JSONResponse({
        "answer": answer,
        "plot": image_uri
    })
