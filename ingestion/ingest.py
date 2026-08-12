import argparse
import json
import os
import csv
from pathlib import Path

def process_pdf(file_path):
    import pdfplumber
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return [{"source_type": "pdf", "source_id": Path(file_path).name, "raw_text": text.strip()}]

def process_html(file_path):
    from bs4 import BeautifulSoup
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
    return [{"source_type": "html", "source_id": Path(file_path).name, "raw_text": text.strip()}]

def process_csv(file_path):
    results = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            text = ", ".join(row)
            results.append({"source_type": "csv", "source_id": f"{Path(file_path).name}_row_{i}", "raw_text": text.strip()})
    return results

def ingest_file(file_path):
    if not os.path.exists(file_path):
        return [{"error": f"File not found: {file_path}"}]
    
    ext = Path(file_path).suffix.lower()
    try:
        if ext == '.pdf':
            return process_pdf(file_path)
        elif ext in ['.htm', '.html']:
            return process_html(file_path)
        elif ext == '.csv':
            return process_csv(file_path)
        else:
            return [{"error": f"Unsupported file type: {ext}"}]
    except Exception as e:
        return [{"error": f"Failed to process file: {str(e)}"}]

def main():
    parser = argparse.ArgumentParser(description="Ingest PDF, HTML, or CSV files and output normalized JSON.")
    parser.add_argument("file_path", help="Path to the file to ingest")
    args = parser.parse_args()
    
    results = ingest_file(args.file_path)
    for res in results:
        print(json.dumps(res))

if __name__ == "__main__":
    main()
