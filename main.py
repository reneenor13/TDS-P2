from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask")
async def ask_ai(request: Request):
    data = await request.json()
    question = data.get("question", "")
    # TODO: replace this with your AI logic
    answer = f"Great question! '{question}' — this is a placeholder answer from the AI."
    return JSONResponse({"answer": answer})

# Optional: handle file uploads if you want
@app.post("/upload")
async def upload_files(
    csvFile: UploadFile | None = File(default=None),
    questionsFile: UploadFile | None = File(default=None),
):
    # Implement your file processing here
    # For now just acknowledge the upload
    return {"csv": csvFile.filename if csvFile else None,
            "questions": questionsFile.filename if questionsFile else None}
