Tools in Data Science – Project 2
Title: Data Analyst Agent (Google AI Integration)
Author: Renee Noronha – 23f3003731@ds.study.iitm.ac.in
1. Overview
This project implements a publicly accessible API and web-based interface that allows users to upload data (CSV), images, and question files to receive AI-generated insights. The backend is built using FastAPI, integrated with Google AI (Gemini 1.5 Pro) via the AI Proxy for natural language processing, and can generate analytical responses and visualisations.
2. Features
- Accepts multiple file types:   - `.txt` – list of questions for analysis   - `.csv` – structured dataset for analysis and plotting   - `.png` / `.jpg` – image inputs for AI interpretation - Provides:   - Google AI-generated answers based on user queries   - Base64-encoded plots from CSV data - Web-based frontend for user interaction without requiring API knowledge - Fully deployed on Render with public access
3. API Documentation
3.1 Upload Files Endpoint: POST /api/upload Form Data Parameters: questionsFile (.txt, required) – File containing questions csvFile (.csv, optional) – Dataset for analysis imageFile (.png/.jpg, optional) – Image file for AI-based interpretation  Example (Terminal): curl -X POST https://your-app.onrender.com/api/upload \   -F "questionsFile=@$HOME/Downloads/questions.txt" \   -F "csvFile=@$HOME/Downloads/data.csv"  3.2 Ask a Question Directly Endpoint: POST /api/ask JSON Body: {   "question": "What is the trend in sales over the last year?" }
4. Frontend Interface
- Hosted alongside the backend - `index.html` + `style.css` + `main.js` allow:   - File uploads   - Direct question entry   - Real-time display of AI responses
5. Deployment Instructions
Environment: Python 3.11 Dependencies: pip install -r requirements.txt Start Command: uvicorn main:app --host 0.0.0.0 --port 10000 Hosting Platform: Render Public URL: (Insert your deployed Render URL here)
6. File Structure
project-root/ │── main.py               # FastAPI backend │── utils.py              # Helper functions │── requirements.txt      # Python dependencies │── templates/index.html  # Frontend HTML │── static/style.css      # Frontend styling │── static/main.js        # Frontend JS │── LICENSE               # MIT License │── README.md             # Project documentation
7. License
MIT License © 2025 Renee Noronha
