
# 📘 Automated Cataloguing System

Automatically extract metadata from scanned or digital PDF books and generate a structured Excel catalog — ideal for libraries, archives, and digital repositories.

---

## 🚀 Try It Live

👉 [Click here to use the app on Hugging Face Spaces](https://huggingface.co/spaces/thamesh24/Assignment_ImmverseAI)

---

## 🧠 Project Overview

This project processes a folder of PDF books and extracts key bibliographic information such as:

- **Book Title**
- **Author**
- **Editor**
- **Year of Publishing**
- **Publisher**
- **Language**
- *(Optional)* Number of Pages
- *(Optional)* Format (default: PDF)

All metadata is compiled into a structured Excel file (`book_catalog_output.xlsx`).

---

## 🔄 Pipeline Overview

```
PDF Files
  ↓
Convert First 3 Pages to Images
  ↓
Preprocessing (Grayscale + Resize + Contrast)
  ↓
OCR using Google Vision API
  ↓
Extracted Text
  ↓
Metadata Extraction via LLaMA-3.3-70B (Groq)
  ↓
Export to Excel
```

---

## 🧪 Models & Tools Evaluated

During development, the following tools were tested:

- PaddleOCR ❌
- Tesseract ❌
- EasyOCR ❌
- Kareken ❌
- Fine-tuned TrOCR on [Indic-HW dataset](https://cvit.iiit.ac.in/research/projects/cvit-projects/indic-hw-data) ❌
- EasyOCR + TrOCR fusion ❌

✅ **Final working pipeline:**

- **OCR**: Google Vision API  
- **LLM**: LLaMA-3.3-70B-Versatile (via Groq API)

---

## 🛠️ Preprocessing Steps

To improve OCR accuracy:

- Convert to **Grayscale**
- Apply **Auto-Contrast**
- **Resize (2×)** to enhance resolution

---

## 🖥️ Script Execution Summary

- Processes all `.pdf` files in the `pdf/` directory
- OCR is applied to the **first 3 pages** of each book
- Extracted text is sent to LLM for metadata extraction
- Outputs a structured **Excel catalog**

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/Pratham1410/Assignment_ImmverseAi.git
cd Assignment_ImmverseAi

# Install dependencies
pip install -r requirements.txt

# Add your API credentials
touch .env
# Then add your GOOGLE_APPLICATION_CREDENTIALS and GROQ_API_KEY inside the .env file
```

---

## 📁 Output Example

```
output/
├── book_catalog_output.xlsx       # Final Excel catalog
├── logs/
│   └── llm_conversations_log.json
└── extracted_texts/
    └── <pdf_name>_extracted.txt
```

---

## 📄 License

MIT License. Free to use and modify.
