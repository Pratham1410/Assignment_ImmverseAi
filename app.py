import os
import shutil
import gradio as gr
import pandas as pd
from main import process_all_pdfs

# Set up PDF processing folder
PDF_FOLDER = "pdf"
os.makedirs(PDF_FOLDER, exist_ok=True)
os.environ["PDF_FOLDER"] = PDF_FOLDER

def clear_pdf_folder():
    for f in os.listdir(PDF_FOLDER):
        file_path = os.path.join(PDF_FOLDER, f)
        if os.path.isfile(file_path):
            os.remove(file_path)

def extract_zip_to_pdf_folder(zip_file):
    import zipfile
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(PDF_FOLDER)

def process_single_pdf(file):
    clear_pdf_folder()
    file_path = os.path.join(PDF_FOLDER, os.path.basename(file))
    shutil.copy(file, file_path)
    df = process_all_pdfs()
    return df

def process_zip(zip_file):
    clear_pdf_folder()
    zip_path = os.path.join(PDF_FOLDER, os.path.basename(zip_file))
    shutil.copy(zip_file, zip_path)
    extract_zip_to_pdf_folder(zip_path)
    df = process_all_pdfs()
    return df

def process_folder_upload(files):
    clear_pdf_folder()
    for f in files:
        file_path = os.path.join(PDF_FOLDER, os.path.basename(f))
        shutil.copy(f, file_path)
    df = process_all_pdfs()
    return df

with gr.Blocks() as demo:
    gr.Markdown("## 📚 Automated Book Metadata Cataloging System")

    with gr.Tab("📄 Upload Single PDF"):
        single_pdf = gr.File(label="Upload a PDF", file_types=[".pdf"])
        single_btn = gr.Button("Process PDF")
        single_table = gr.Dataframe(label="Extracted Metadata")
        single_btn.click(process_single_pdf, inputs=single_pdf, outputs=single_table)

    with gr.Tab("🗂️ Upload ZIP of PDFs"):
        zip_upload = gr.File(label="Upload ZIP", file_types=[".zip"])
        zip_btn = gr.Button("Process ZIP")
        zip_table = gr.Dataframe(label="Extracted Metadata")
        zip_btn.click(process_zip, inputs=zip_upload, outputs=zip_table)

    with gr.Tab("📁 Upload Folder (Multiple PDFs)"):
        folder_upload = gr.File(label="Select Multiple PDFs", file_types=[".pdf"], file_count="multiple")
        folder_btn = gr.Button("Process Folder PDFs")
        folder_table = gr.Dataframe(label="Extracted Metadata")
        folder_btn.click(process_folder_upload, inputs=folder_upload, outputs=folder_table)

demo.launch()
