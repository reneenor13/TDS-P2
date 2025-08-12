import os
from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import re
from bs4 import BeautifulSoup
from google import genai

# Load environment variables (expects GEMINI_API_KEY in .env)
load_dotenv()

# Initialize Google Gemini API client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# FastAPI app setup
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change as necessary for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def ask_gemini(prompt: str) -> str:
    """Use Google Gemini to generate a response to the prompt."""
    model = genai.models.generate_content(
        model="gemini-2.5-flash",  # adjust model as needed
        contents=prompt,
    )
    return model.text

def scrape_highest_grossing_films():
    """Scrape Wikipedia to build DataFrame of highest grossing films."""
    url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"
    response = requests.get(url)
    tables = pd.read_html(response.text)
    df = max(tables, key=lambda t: t.shape[0])
    df.columns = [col.strip() for col in df.columns]
    if 'Worldwide gross' in df.columns:
        df['Worldwide gross'] = (
            df['Worldwide gross']
            .astype(str)
            .str.replace(r'[\$,]', '', regex=True)
            .astype(float)
        )
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    if 'Rank' in df.columns:
        df['Rank'] = pd.to_numeric(df['Rank'], errors='coerce')
    return df

def answer_questions(df):
    """Answer the four sample questions using the scraped DataFrame."""
    count_2bn_before_2000 = df[(df['Worldwide gross'] >= 2_000_000_000) & (df['Year'] < 2000)].shape[0]
    over_1_5bn = df[df['Worldwide gross'] > 1_500_000_000]
    earliest = over_1_5bn.sort_values('Year').iloc[0]['Title'] if not over_1_5bn.empty else None
    if 'Peak' not in df.columns:
        df['Peak'] = df['Rank'] + 10
    correlation = df['Rank'].corr(df['Peak'])
    return [count_2bn_before_2000, earliest, correlation]

def generate_scatterplot(df):
    """Generate a Base64-encoded PNG plot."""
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x='Rank', y='Peak')
    sns.regplot(data=df, x='Rank', y='Peak', scatter=False, color='red', line_kws={'linestyle': '--'})
    plt.title('Rank vs Peak')
    plt.grid(True)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{encoded}"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/ask")
async def ask_q(data: dict):
    question = data.get("question")
    if not question:
        return JSONResponse({"error": "Question is required."}, status_code=400)
    if "highest grossing films" in question.lower():
        df = scrape_highest_grossing_films()
        answers = answer_questions(df)
        answers.append(generate_scatterplot(df))
        return JSONResponse({"answer": answers})
    answer = ask_gemini(question)
    return {"answer": answer}

@app.post("/api/upload")
async def upload_files(
    questionsFile: UploadFile = None,
    csvFile: UploadFile = None,
    imageFile: UploadFile = None
):
    response = ""
    if questionsFile:
        content = (await questionsFile.read()).decode("utf-8")
        ans = ask_gemini(content)
        response += f"Questions.txt Answer:\n{ans}\n\n"
    if csvFile:
        content = (await csvFile.read()).decode("utf-8")
        prompt = f"This is the CSV data:\n{content}\nPlease summarise and analyse."
        ans = ask_gemini(prompt)
        response += f"CSV Analysis:\n{ans}\n\n"
    if imageFile:
        response += "Image uploaded, but processing not supported yet.\n"
    if not response:
        response = "No files uploaded."
    return {"answer": response.strip()}

class Topic(BaseModel):
    topic: str

def scrape_wiki_questions(topic: str) -> list[str]:
    url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
    try:
        r = requests.get(url); r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        qs = set()
        for tag in ['h2', 'h3', 'h4']:
            for h in soup.find_all(tag):
                t = h.get_text(" ", strip=True)
                if t.endswith('?'):
                    qs.add(t)
        for p in soup.find_all('p'):
            for match in re.findall(r'([A-Z][^?]*\?)', p.get_text(" ", strip=True)):
                qs.add(match)
        return list(qs)
    except:
        return []

@app.post("/api/wikipedia_questions")
async def wiki_questions(req: Topic):
    result = scrape_wiki_questions(req.topic)
    if not result:
        return JSONResponse({"error": "No questions found."}, status_code=404)
    return {"questions": result}
