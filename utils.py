import os
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd
import requests
import duckdb
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def ask_gemini(prompt: str, model: str = "gemini-1.5-flash") -> str:
    """
    Send a prompt to Google's Gemini model and return the response text.
    """
    try:
        model_client = genai.GenerativeModel(model)
        response = model_client.generate_content(prompt)
        return response.text.strip()
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


# Add these functions to your utils.py

def generate_sales_bar_chart(df: pd.DataFrame) -> str:
    """Generate sales bar chart with blue bars."""
    plt.figure(figsize=(10, 6))
    
    sales_by_region = df.groupby('Region')['Sales'].sum()
    bars = plt.bar(sales_by_region.index, sales_by_region.values, color='blue', alpha=0.8, edgecolor='black', linewidth=0.5)
    
    # Ensure axes are visible and properly labeled
    plt.xlabel('Region', fontsize=12, fontweight='bold')
    plt.ylabel('Total Sales', fontsize=12, fontweight='bold')
    plt.title('Total Sales by Region', fontsize=14, fontweight='bold', pad=20)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    # Make sure axes are visible
    ax = plt.gca()
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=80, facecolor='white')
    plt.close()
    buf.seek(0)
    
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    return encoded

def generate_cumulative_sales_chart(df: pd.DataFrame) -> str:
    """Generate cumulative sales chart with red line."""
    plt.figure(figsize=(10, 6))
    
    df_sorted = df.sort_values('Date')
    cumulative_sales = df_sorted['Sales'].cumsum()
    
    plt.plot(df_sorted['Date'], cumulative_sales, color='red', linewidth=2.5, marker='o', markersize=4)
    
    # Ensure axes are visible and properly labeled
    plt.xlabel('Date', fontsize=12, fontweight='bold')
    plt.ylabel('Cumulative Sales', fontsize=12, fontweight='bold')
    plt.title('Cumulative Sales Over Time', fontsize=14, fontweight='bold', pad=20)
    
    # Make sure axes are visible
    ax = plt.gca()
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=80, facecolor='white')
    plt.close()
    buf.seek(0)
    
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    return encoded

def generate_bar_chart_base64(df: pd.DataFrame, x_col: str, y_col: str, color='blue', title=None) -> str:
    """Generic bar chart generator."""
    plt.figure(figsize=(10, 6))
    
    if df[x_col].dtype == 'object':  # Categorical x-axis
        data_grouped = df.groupby(x_col)[y_col].sum()
        bars = plt.bar(data_grouped.index, data_grouped.values, color=color, alpha=0.8, edgecolor='black', linewidth=0.5)
    else:
        bars = plt.bar(df[x_col], df[y_col], color=color, alpha=0.8, edgecolor='black', linewidth=0.5)
    
    # Styling
    plt.xlabel(x_col, fontsize=12, fontweight='bold')
    plt.ylabel(y_col, fontsize=12, fontweight='bold')
    plt.title(title or f'{y_col} by {x_col}', fontsize=14, fontweight='bold', pad=20)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    # Ensure visible axes
    ax = plt.gca()
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=80, facecolor='white')
    plt.close()
    buf.seek(0)
    
    return base64.b64encode(buf.read()).decode('utf-8')

def generate_line_chart_base64(df: pd.DataFrame, x_col: str, y_col: str, color='red', title=None) -> str:
    """Generic line chart generator."""
    plt.figure(figsize=(10, 6))
    
    df_sorted = df.sort_values(x_col)
    plt.plot(df_sorted[x_col], df_sorted[y_col], color=color, linewidth=2.5, marker='o', markersize=4)
    
    # Styling
    plt.xlabel(x_col, fontsize=12, fontweight='bold')
    plt.ylabel(y_col, fontsize=12, fontweight='bold')
    plt.title(title or f'{y_col} over {x_col}', fontsize=14, fontweight='bold', pad=20)
    
    # Ensure visible axes
    ax = plt.gca()
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    if df_sorted[x_col].dtype == 'datetime64[ns]' or 'date' in x_col.lower():
        plt.xticks(rotation=45)
    
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=80, facecolor='white')
    plt.close()
    buf.seek(0)
    
    return base64.b64encode(buf.read()).decode('utf-8')
