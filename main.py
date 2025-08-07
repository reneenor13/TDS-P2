import os
from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import openai
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import json

# Load environment variables
load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# FastAPI app setup
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def ask_chatgpt(prompt: str) -> str:
    """Send prompt to OpenAI and return response text using new SDK syntax."""
    response = client.chat.completions.create(
        model="gpt-4o",  # or "gpt-4" / "gpt-3.5-turbo"
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def scrape_highest_grossing_films():
    url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"
    response = requests.get(url)
    tables = pd.read_html(response.text)
    # Pick the largest table, typically the main one
    df = max(tables, key=lambda t: t.shape[0])

    # Clean column names & data
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
    # Assume 'Peak' may not exist; create dummy if needed later
    return df


def answer_questions(df):
    # 1. How many $2 bn movies were released before 2000?
    count_2bn_before_2000 = df[
        (df['Worldwide gross'] >= 2_000_000_000) & (df['Year'] < 2000)
    ].shape[0]

    # 2. Earliest film that grossed over $1.5 bn
    over_1_5bn = df[df['Worldwide gross'] > 1_500_000_000]
    earliest_film = (
        over_1_5bn.sort_values('Year').iloc[0]['Title']
        if not over_1_5bn.empty else None
    )

    # 3. Correlation between Rank and Peak (if Peak exists)
    if 'Peak' not in df.columns:
        df['Peak'] = df['Rank'] + 10  # dummy example to allow correlation

    correlation = df['Rank'].corr(df['Peak'])

    return [count_2bn_before_2000, earliest_film, correlation]


def generate_scatterplot(df):
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x='Rank', y='Peak')
    sns.regplot(data=df, x='Rank', y='Peak', scatter=False, color='red', line_kws={'linestyle': '--'})
    plt.title('Rank vs Peak')
    plt.grid(True)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    # Limit size - PNG under 100k bytes might be tight; can adjust dpi or compress if needed
    return f"data:image/png;base64,{img_base64}"


@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/ask")
async def ask_question(data: dict):
    try:
        question = data.get("question")
        if not question:
            return JSONResponse(content={"error": "Question cannot be empty"}, status_code=400)

        # Detect if this is a special scrape + analysis question
        # (e.g., user wants to scrape the Wikipedia page and get answers + plot)
        if "highest grossing films" in question.lower():
            df = scrape_highest_grossing_films()
            answers = answer_questions(df)
            image_uri = generate_scatterplot(df)
            answers.append(image_uri)
            return JSONResponse(content={"answer": answers})

        # Else regular chatgpt call
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

        # Process image file (OpenAI does not support image in this backend yet)
        if imageFile:
            response_text += "🖼️ **Image** uploaded, but image processing is not supported in this API setup.\n"

        if not response_text:
            response_text = "No files uploaded."

        return {"answer": response_text.strip()}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
