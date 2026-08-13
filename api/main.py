from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import os
import json
from pydantic import BaseModel
from google import genai

from . import models, database

# Create tables
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Products API")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ExtractRequest(BaseModel):
    raw_text: str

@app.post("/extract")
def extract_product_data(req: ExtractRequest):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment variable is not set")
    
    try:
        with open("schema.json", "r") as f:
            schema_str = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not read schema.json")

    prompt = f"""You are extracting structured product data from raw industrial product text.

Given the raw text below, output ONLY valid JSON matching this schema:
{schema_str}

Rules:
- If a field cannot be determined from the text, set it to null — never guess a number or spec.
- When a field value is abbreviated, informal, or ambiguous (e.g. 'PMP' for a category, 'st. steel' for a material), normalize it to a clean standard value AND always add a field_confidence entry — do not normalize silently without flagging it, and do not skip normalization for fields other than material.
- For every field set with medium or low certainty, add an entry in field_confidence with a numeric score (0-1), the source snippet it came from, and a one-line reasoning string explaining the inference.
- High-certainty fields (explicitly stated in the text) don't need a field_confidence entry.
- Do not include markdown formatting, code fences, or commentary — output raw JSON only.

RAW TEXT:
{req.raw_text}"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        output_text = response.text.strip()
        if output_text.startswith("```json"):
            output_text = output_text[7:]
        if output_text.startswith("```"):
            output_text = output_text[3:]
        if output_text.endswith("```"):
            output_text = output_text[:-3]
            
        return json.loads(output_text.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Extraction failed: {str(e)}")

@app.post("/enrich")
def enrich_product_data(product: models.Product):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment variable is not set")
    
    prompt = f"""You are validating and enriching a structured product record for an industrial commerce catalog.

Given the product JSON below, check for:
1. Internal inconsistencies (e.g. a "power_rating" that doesn't match the stated category, a weight implausible for the stated dimensions/material)
2. Fields that are null but could be reasonably inferred from OTHER fields already present in the record (not from outside knowledge) — if you infer a value, add it to field_confidence with reasoning citing which other field led to the inference
3. Fields that remain null and cannot be inferred — leave them null, do not guess

For each issue found, add a string to enrichment_flags describing the issue in plain language (e.g. "Weight seems low for stated dimensions and material — verify").

Do not modify high-confidence fields already explicitly stated in the source. Only touch null fields or add flags.

Output ONLY the updated JSON, same schema, no commentary.

PRODUCT JSON:
{product.model_dump_json(indent=2)}"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        output_text = response.text.strip()
        if output_text.startswith("```json"):
            output_text = output_text[7:]
        if output_text.startswith("```"):
            output_text = output_text[3:]
        if output_text.endswith("```"):
            output_text = output_text[:-3]
            
        return json.loads(output_text.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Enrichment failed: {str(e)}")

@app.post("/products", response_model=models.Product, status_code=201)
def create_product(product: models.ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(database.DBProduct).filter(database.DBProduct.product_id == product.product_id).first()
    if db_product:
        raise HTTPException(status_code=400, detail="Product ID already registered")
    
    db_item = database.DBProduct(
        product_id=product.product_id,
        name=product.name,
        category=product.category,
        brand=product.brand,
        description=product.description,
    )
    db_item.specifications = product.specifications.model_dump() if product.specifications else None
    db_item.pricing = product.pricing.model_dump() if product.pricing else None
    db_item.images = product.images
    db_item.source_documents = product.source_documents
    db_item.field_confidence = {k: v.model_dump() for k, v in product.field_confidence.items()} if product.field_confidence else None
    db_item.enrichment_flags = product.enrichment_flags
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/products", response_model=List[models.Product])
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = db.query(database.DBProduct).offset(skip).limit(limit).all()
    return products

@app.get("/products/{product_id}", response_model=models.Product)
def read_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(database.DBProduct).filter(database.DBProduct.product_id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/products/{product_id}/confidence")
def read_product_confidence(product_id: str, db: Session = Depends(get_db)):
    product = db.query(database.DBProduct).filter(database.DBProduct.product_id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product.field_confidence or {}

# Mount static files at the end so it doesn't override API routes
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
