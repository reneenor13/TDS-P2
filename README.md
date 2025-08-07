#  TDS Project 2 – Data Analyst Agent

A public API that uses an LLM (GPT-4o-mini via AI Proxy) to analyze user-uploaded data and respond to questions using CSVs, images, and prompts.

##  How It Works

- Upload `questions.txt`, optional `data.csv`, and optional `image.png`
- Returns JSON with:
  - LLM-generated answer
  - Base64-encoded plot (if CSV given)

##  API Endpoint

POST `/api/` with `multipart/form-data`:
- `questions` (required)
- `data` (optional CSV)
- `image` (optional PNG/JPG)

##  Deployment on Render

1. Connect this repo to Render
2. Runtime: Python 3.11
3. Start command:  
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 10000
