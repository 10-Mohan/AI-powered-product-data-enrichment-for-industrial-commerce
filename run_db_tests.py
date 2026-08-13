import requests
import time
import subprocess
import os
import sys
import json

# Start fresh
if os.path.exists("products.db"):
    os.remove("products.db")

server = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--port", "8000"], cwd=os.getcwd())

# Wait for server to be ready
for _ in range(10):
    try:
        if requests.get("http://127.0.0.1:8000/products").status_code == 200:
            break
    except requests.exceptions.ConnectionError:
        time.sleep(1)

try:
    clean_json = {
      "product_id": "PROD-9988",
      "name": "Industrial Water Pump Model X2",
      "category": "Pumps",
      "brand": "AquaTech",
      "description": "High capacity submersible water pump for industrial applications. Features a durable stainless steel housing and automated flow control.",
      "specifications": {
        "dimensions": {
          "length": 45,
          "width": 20,
          "height": 30,
          "unit": "cm"
        },
        "weight": {
          "value": 15.5,
          "unit": "kg"
        },
        "material": "Stainless Steel",
        "color": "Silver",
        "power_rating": "2000W",
        "certifications": ["ISO 9001", "CE", "UL Listed"]
      },
      "pricing": {
        "value": 450.00,
        "currency": "USD"
      },
      "images": ["http://aquatech.com/img/x2-front.jpg"],
      "source_documents": ["http://aquatech.com/docs/x2-manual.pdf"],
      "field_confidence": {},
      "enrichment_flags": ["Verified"]
    }

    sparse_json = {
      "product_id": "PROD-334",
      "name": "AquaTech Submersible Pump",
      "category": "Pumps",
      "brand": "AquaTech",
      "description": "For industrial use.",
      "specifications": {
        "dimensions": {
          "length": None,
          "width": None,
          "height": None,
          "unit": None
        },
        "weight": {
          "value": None,
          "unit": None
        },
        "material": None,
        "color": None,
        "power_rating": None,
        "certifications": []
      },
      "pricing": {
        "value": 450,
        "currency": "USD"
      },
      "images": [],
      "source_documents": [],
      "field_confidence": {
        "brand": {
          "score": 0.85,
          "source": "AquaTech Submersible Pump",
          "reasoning": "Inferred 'AquaTech' as the brand from the start of the product name string."
        },
        "category": {
          "score": 0.6,
          "source": "Submersible Pump",
          "reasoning": "Inferred implicit category of 'Pumps' based on the product name, but not explicitly stated."
        }
      },
      "enrichment_flags": []
    }

    messy_json = {
      "product_id": "X-912A",
      "name": "AQ-T PUMP SERIE",
      "category": "PMP / Submers.",
      "brand": "AQUATECH-HEAVY",
      "description": "Hvy duty st. steel pump.",
      "specifications": {
        "dimensions": {
          "length": 45,
          "width": 20,
          "height": 30,
          "unit": "cm"
        },
        "weight": {
          "value": 15.5,
          "unit": "kg"
        },
        "material": "stainless steel",
        "color": None,
        "power_rating": "2kW",
        "certifications": ["CE"]
      },
      "pricing": {
        "value": 450,
        "currency": "USD"
      },
      "images": ["www.aq.com/1.png"],
      "source_documents": [],
      "field_confidence": {
        "name": {
          "score": 0.6,
          "source": "==AQ-T PUMP SERIE==",
          "reasoning": "Extracted as product name, but appears to be a generic series label."
        },
        "brand": {
          "score": 0.7,
          "source": "AQUATECH-HEAVY",
          "reasoning": "Inferred brand from the comment next to the Product ID."
        },
        "specifications.material": {
          "score": 0.9,
          "source": "st. steel",
          "reasoning": "Resolved common abbreviation 'st. steel' to 'stainless steel'."
        },
        "specifications.dimensions": {
          "score": 0.5,
          "source": "Dims approx 45x20x30 cm.",
          "reasoning": "Dimensions are explicitly stated as 'approx' (approximate), reducing certainty."
        },
        "specifications.power_rating": {
          "score": 0.4,
          "source": "Pwr is like 2kW??",
          "reasoning": "Power rating is highly uncertain due to phrasing 'like' and question marks."
        },
        "specifications.certifications": {
          "score": 0.3,
          "source": "maybe CE",
          "reasoning": "Certification is heavily uncertain due to the word 'maybe'."
        },
        "pricing.currency": {
          "score": 0.9,
          "source": "bucks US",
          "reasoning": "Interpreted informal 'bucks US' as standard currency code USD."
        }
      },
      "enrichment_flags": []
    }
    
    print("Saving Clean...")
    requests.post("http://127.0.0.1:8000/products", json=clean_json)
    
    print("Saving Sparse...")
    requests.post("http://127.0.0.1:8000/products", json=sparse_json)
    
    print("Saving Messy...")
    requests.post("http://127.0.0.1:8000/products", json=messy_json)
    
    print("Testing Duplicate Submission for Clean...")
    r = requests.post("http://127.0.0.1:8000/products", json=clean_json)
    print("Duplicate Status:", r.status_code)
    print("Duplicate Response:", r.json())
    
    print("\n--- GET /products ---")
    r = requests.get("http://127.0.0.1:8000/products")
    print(json.dumps(r.json(), indent=2))

finally:
    server.terminate()
