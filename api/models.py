from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict

class Dimensions(BaseModel):
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    unit: Optional[str] = None

class Weight(BaseModel):
    value: Optional[float] = None
    unit: Optional[str] = None

class Specifications(BaseModel):
    dimensions: Dimensions
    weight: Weight
    material: Optional[str] = None
    color: Optional[str] = None
    power_rating: Optional[str] = None
    certifications: List[str]

class Pricing(BaseModel):
    value: Optional[float] = None
    currency: Optional[str] = None

class ConfidenceDetail(BaseModel):
    score: float
    source: str
    reasoning: str

class ProductBase(BaseModel):
    product_id: str
    name: str
    category: str
    brand: str
    description: str
    specifications: Specifications
    pricing: Pricing
    images: List[str]
    source_documents: List[str]
    field_confidence: Dict[str, ConfidenceDetail]
    enrichment_flags: List[str]

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    model_config = ConfigDict(from_attributes=True)
