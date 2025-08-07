import os
from dotenv import load_dotenv
import openai
import pandas as pd
import requests
import duckdb
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

# Load environment variables
load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_openai(prompt: str, model: str = "gpt-4o") -> str:
    """
    Send a prompt to OpenAI's chat model and return the response text.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"


def scrape_tables_from_url(url: str) -> pd.DataFrame:
    """
    Scrape all HTML tables from a URL and return the largest table as a DataFrame.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    tables = pd.read_html(response.text)
    if not tables:
        raise ValueError(f"No HTML tables found at the URL: {url}")
    # Return the largest table
    return max(tables, key=lambda df: df.size)


def run_sql_on_dataframe(df: pd.DataFrame, sql_query: str) -> any:
    """
    Run a SQL query on a pandas DataFrame using DuckDB.
    """
    con = duckdb.connect(database=':memory:')
    con.register("data_table", df)
    try:
        result = con.execute(sql_query).fetchall()
        return result
    finally:
        con.close()


def generate_scatterplot_base64(df: pd.DataFrame, x_col: str, y_col: str, regression_line: bool = False) -> str:
    """
    Generate a scatterplot with optional regression line and return it as a base64 encoded PNG.
    """
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x=x_col, y=y_col)
    if regression_line:
        sns.regplot(data=df, x=x_col, y=y_col, scatter=False, color='red', line_kws={'linestyle': '--'})
    plt.title(f'Plot of {y_col} vs. {x_col}')
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.grid(True)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return f"data:image/png;base64,{image_base64}"
