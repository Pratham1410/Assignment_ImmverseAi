import os
import io
import json
import fitz
import requests
import pandas as pd
import tempfile
from PIL import Image, ImageOps
from dotenv import load_dotenv
from pdf2image import convert_from_path
from google.cloud import vision

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON"):
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as f:
        f.write(os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON"))
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f.name

client = vision.ImageAnnotatorClient()

PDF_FOLDER = os.getenv("PDF_FOLDER", "pdf")

def gentle_preprocess(pil_image):
    gray = pil_image.convert("L")
    enhanced = ImageOps.autocontrast(gray)
    resized = enhanced.resize((gray.width * 2, gray.height * 2), resample=Image.LANCZOS)
    return resized

def extract_text_from_image(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    vision_img = vision.Image(content=img_byte_arr.getvalue())
    response = client.document_text_detection(image=vision_img)
    if response.error.message:
        raise Exception(f"API Error: {response.error.message}")
    return response.full_text_annotation.text

def extract_metadata_with_groq(text, pdf_name):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = """
You are a highly accurate metadata extraction system for scanned books with noisy OCR. Extract the following fields in clean JSON:

{
  "Book Title": "",
  "Author": "",
  "Editor": "",
  "Year of Publishing": "",
  "Publisher": "",
  "Language": ""
}

Instructions:
- Use the first recognizable title as "Book Title" if the structure suggests a collection or table of contents.
- Infer intelligently if exact values are missing.
- Use "Unknown" only when absolutely no clue is found.
- Output only valid JSON. No extra text or explanation.
"""

    messages = [
        { "role": "system", "content": system_prompt },
        { "role": "user", "content": f"Extract metadata from this book content:\n{text}" }
    ]

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.3,
        "response_format": { "type": "json_object" }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        return json.loads(result['choices'][0]['message']['content'])
    except Exception as e:
        print(f"Metadata extraction failed for {pdf_name}: {e}")
        return {
            "Book Title": "Unknown",
            "Author": "Unknown",
            "Editor": "Unknown",
            "Year of Publishing": "Unknown",
            "Publisher": "Unknown",
            "Language": "Unknown"
        }

def get_page_count(pdf_path):
    try:
        return len(fitz.open(pdf_path))
    except:
        return "Unknown"

def get_first_3_pages_as_images(pdf_path):
    try:
        return convert_from_path(pdf_path, first_page=1, last_page=3)
    except Exception as e:
        print(f"Error converting {pdf_path}: {e}")
        return []

def process_all_pdfs():
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]
    metadata_records = []

    for pdf in pdf_files:
        full_path = os.path.join(PDF_FOLDER, pdf)
        print(f"Processing: {pdf}")
        images = get_first_3_pages_as_images(full_path)

        text_content = ""
        for i, img in enumerate(images):
            try:
                preprocessed_img = gentle_preprocess(img)
                page_text = extract_text_from_image(preprocessed_img)
                text_content += f"\n--- Page {i+1} ---\n{page_text}"
            except Exception as e:
                print(f"OCR failed on page {i+1} of {pdf}: {e}")

        metadata = extract_metadata_with_groq(text_content, pdf)
        metadata["Number of Pages"] = get_page_count(full_path)
        metadata["Format"] = "PDF"

        metadata_records.append(metadata)

    return pd.DataFrame(metadata_records)
