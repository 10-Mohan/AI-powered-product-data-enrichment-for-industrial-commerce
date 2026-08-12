import requests
import time
import subprocess
import os
import sys

# Start the uvicorn server
server = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--port", "8000"], cwd=os.getcwd())
time.sleep(5) # wait for server to start

try:
    # 1. Test POST /products
    print("Testing POST /products...")
    valid_data = {
      "product_id": "string_id_123",
      "name": "string",
      "category": "string",
      "brand": "string",
      "description": "string",
      "specifications": {
        "dimensions": {
          "length": 1.0,
          "width": 2.0,
          "height": 3.0,
          "unit": "cm"
        },
        "weight": {
          "value": 1.5,
          "unit": "kg"
        },
        "material": "metal",
        "color": "red",
        "power_rating": "100W",
        "certifications": ["CE"]
      },
      "pricing": {
        "value": 100.5,
        "currency": "USD"
      },
      "images": ["url1", "url2"],
      "source_documents": ["doc1.pdf"],
      "field_confidence": {
        "name": {
          "score": 0.9,
          "source": "ocr",
          "reasoning": "clear text"
        }
      },
      "enrichment_flags": ["verified"]
    }
    r = requests.post("http://127.0.0.1:8000/products", json=valid_data)
    print(r.status_code, r.json())
    assert r.status_code == 201

    # 2. Test invalid POST
    print("Testing invalid POST /products...")
    invalid_data = {
        "product_id": "string_id_456",
        "name": "Widget B"
        # missing almost everything required
    }
    r = requests.post("http://127.0.0.1:8000/products", json=invalid_data)
    print(r.status_code, r.json())
    assert r.status_code == 422 # Unprocessable Entity (FastAPI standard)

    # 3. Test GET /products
    print("Testing GET /products...")
    r = requests.get("http://127.0.0.1:8000/products")
    print(r.status_code, r.json())
    assert r.status_code == 200
    assert len(r.json()) > 0

    # 4. Test GET /products/{product_id}
    print("Testing GET /products/string_id_123...")
    r = requests.get("http://127.0.0.1:8000/products/string_id_123")
    print(r.status_code, r.json())
    assert r.status_code == 200
    assert r.json()["product_id"] == "string_id_123"

    # 5. Test GET /products/{product_id}/confidence
    print("Testing GET /products/string_id_123/confidence...")
    r = requests.get("http://127.0.0.1:8000/products/string_id_123/confidence")
    print(r.status_code, r.json())
    assert r.status_code == 200
    assert r.json()["name"]["score"] == 0.9
    
    print("ALL TESTS PASSED")

finally:
    server.terminate()
