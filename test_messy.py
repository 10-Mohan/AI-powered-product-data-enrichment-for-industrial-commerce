import requests
import time
import subprocess
import os
import sys
import json

server = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--port", "8000"], cwd=os.getcwd())

# Wait for server to be ready
for _ in range(10):
    try:
        if requests.get("http://127.0.0.1:8000/products").status_code == 200:
            break
    except requests.exceptions.ConnectionError:
        time.sleep(1)

try:
    raw_text = """==AQ-T PUMP SERIE==
Pr0d_ID: X-912A  // AQUATECH-HEAVY
cat: PMP / Submers.
dsc: Hvy duty st. steel pump. 15.5kilos. 
Dims approx 45x20x30 cm. Pwr is like 2kW?? Not sure about certifications, maybe CE.
Cost is around 450 bucks US.
Img1: www.aq.com/1.png
Enrich: none"""

    print("\n--- EXTRACT OUTPUT ---")
    r1 = requests.post("http://127.0.0.1:8000/extract", json={"raw_text": raw_text})
    extracted_json = r1.json()
    print(json.dumps(extracted_json, indent=2))
    
    print("\n--- ENRICH OUTPUT ---")
    r2 = requests.post("http://127.0.0.1:8000/enrich", json=extracted_json)
    enriched_json = r2.json()
    print(json.dumps(enriched_json, indent=2))

finally:
    server.terminate()
