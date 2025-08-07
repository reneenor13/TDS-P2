import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def ask_gemini(questions, context="", image_bytes=None):
    model = genai.GenerativeModel("gemini-pro-vision" if image_bytes else "gemini-pro")

    if image_bytes:
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(image_bytes))
        parts = [context + "\n" + questions, img]
    else:
        parts = context + "\n" + questions

    response = model.generate_content(parts)
    return response.text
