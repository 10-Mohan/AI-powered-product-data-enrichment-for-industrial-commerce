import pytest
import os
import json
from pathlib import Path
import sys

# Add parent dir to path to import ingestion
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.ingest import ingest_file

SAMPLES_DIR = Path(__file__).parent.parent / 'data' / 'samples'

def test_ingest_pdf():
    pdf_path = SAMPLES_DIR / 'sample.pdf'
    assert pdf_path.exists(), "Sample PDF not found"
    
    result = ingest_file(str(pdf_path))
    assert len(result) == 1
    assert result[0]['source_type'] == 'pdf'
    assert result[0]['source_id'] == 'sample.pdf'
    assert 'Sample PDF Document' in result[0]['raw_text']

def test_ingest_html():
    html_path = SAMPLES_DIR / 'sample.html'
    assert html_path.exists(), "Sample HTML not found"
    
    result = ingest_file(str(html_path))
    assert len(result) == 1
    assert result[0]['source_type'] == 'html'
    assert result[0]['source_id'] == 'sample.html'
    assert 'Sample HTML Document' in result[0]['raw_text']
    assert 'This is a paragraph of text.' in result[0]['raw_text']

def test_ingest_csv():
    csv_path = SAMPLES_DIR / 'sample.csv'
    assert csv_path.exists(), "Sample CSV not found"
    
    result = ingest_file(str(csv_path))
    assert len(result) == 3
    
    assert result[0]['source_type'] == 'csv'
    assert result[0]['source_id'] == 'sample.csv_row_0'
    assert result[0]['raw_text'] == 'id, name, description'
    
    assert result[1]['source_type'] == 'csv'
    assert result[1]['source_id'] == 'sample.csv_row_1'
    assert result[1]['raw_text'] == '1, Test Item, This is a test description.'

def test_missing_file():
    result = ingest_file("nonexistent.pdf")
    assert len(result) == 1
    assert "error" in result[0]
    assert "File not found" in result[0]["error"]

def test_unsupported_file():
    unsupported_path = SAMPLES_DIR / 'sample.txt'
    with open(unsupported_path, 'w') as f:
        f.write("test")
    
    result = ingest_file(str(unsupported_path))
    assert len(result) == 1
    assert "error" in result[0]
    assert "Unsupported file type" in result[0]["error"]
    
    os.remove(unsupported_path)

def test_empty_pdf_handled_gracefully():
    empty_pdf_path = SAMPLES_DIR / 'empty.pdf'
    with open(empty_pdf_path, 'wb') as f:
        pass # Empty file
    
    result = ingest_file(str(empty_pdf_path))
    assert len(result) == 1
    assert "error" in result[0]
    
    os.remove(empty_pdf_path)
