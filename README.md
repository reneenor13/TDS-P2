# Data Analyst Agent

**Author:** Renee Noronha (23f3003731@ds.study.iitm.ac.in)  
**Live API:** [https://tds-p2-xdfn.onrender.com/api/](https://tds-p2-xdfn.onrender.com/api/)

## Overview

AI-powered data analysis API that processes questions, CSV data, and images to generate insights and visualizations using Google Gemini 1.5 Pro.

## Features

- Multi-format Input: .txt (questions), .csv (datasets), .png/.jpg (images)
- AI Analysis: Google Gemini integration for intelligent responses
- Data Visualization: Automatic plot generation with base64 encoding
- Web Scraping: Dynamic data collection from external sources
- Fast Response: Processing within 5 minutes

## API Usage

### Primary Endpoint
```bash
POST https://tds-p2-xdfn.onrender.com/api/
```

### Example Request
```bash
curl -X POST https://tds-p2-xdfn.onrender.com/api/ \
  -F "questions.txt=@questions.txt" \
  -F "data.csv=@data.csv" \
  -F "image.png=@chart.png"
```

### Response Formats
- Array Response: [answer1, answer2, correlation_value, "data:image/png;base64,..."]
- Object Response: {"question1": "answer1", "question2": "answer2", "plot": "data:image/png;base64,..."}

## Sample Questions Handled

### Wikipedia Data Analysis
```
1. How many $2 bn movies were released before 2000?
2. Which is the earliest film that grossed over $1.5 bn?
3. What's the correlation between Rank and Peak?
4. Draw a scatterplot with dotted red regression line
```

### Legal Dataset Queries
```
1. Which high court disposed the most cases from 2019-2022?
2. What's the regression slope of registration-decision delay by year?
3. Plot year vs days of delay with regression line
```

## Technical Stack

- Backend: FastAPI with async processing
- AI: Google Gemini 1.5 Pro via AI Proxy
- Data: pandas, numpy for analysis
- Visualization: matplotlib with base64 encoding
- Deployment: Render cloud platform

## Key Capabilities

Web Scraping: Automated data collection from URLs  
Statistical Analysis: Correlations, regressions, aggregations  
Visualization: Scatterplots, bar charts, trend lines  
Multi-modal: Text, CSV, and image processing  
Base64 Encoding: Plots under 100KB for JSON responses  

## Performance

- Response Time: 30-180 seconds depending on complexity
- Timeout Limit: 5 minutes per request
- Retry Logic: 4 attempts with error handling
- File Support: CSV (50MB), Images (10MB), Text (1MB)

## License

MIT License © 2025 Renee Noronha
