import json
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./products.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class DBProduct(Base):
    __tablename__ = "products"

    product_id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    category = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    description = Column(String, nullable=False)
    
    specifications_json = Column(Text, nullable=False)
    pricing_json = Column(Text, nullable=False)
    images_json = Column(Text, nullable=False)
    source_documents_json = Column(Text, nullable=False)
    field_confidence_json = Column(Text, nullable=False)
    enrichment_flags_json = Column(Text, nullable=False)

    @property
    def specifications(self):
        return json.loads(self.specifications_json) if self.specifications_json else None

    @specifications.setter
    def specifications(self, value):
        self.specifications_json = json.dumps(value) if value is not None else None

    @property
    def pricing(self):
        return json.loads(self.pricing_json) if self.pricing_json else None

    @pricing.setter
    def pricing(self, value):
        self.pricing_json = json.dumps(value) if value is not None else None

    @property
    def images(self):
        return json.loads(self.images_json) if self.images_json else None

    @images.setter
    def images(self, value):
        self.images_json = json.dumps(value) if value is not None else None

    @property
    def source_documents(self):
        return json.loads(self.source_documents_json) if self.source_documents_json else None

    @source_documents.setter
    def source_documents(self, value):
        self.source_documents_json = json.dumps(value) if value is not None else None

    @property
    def field_confidence(self):
        return json.loads(self.field_confidence_json) if self.field_confidence_json else None

    @field_confidence.setter
    def field_confidence(self, value):
        self.field_confidence_json = json.dumps(value) if value is not None else None

    @property
    def enrichment_flags(self):
        return json.loads(self.enrichment_flags_json) if self.enrichment_flags_json else None

    @enrichment_flags.setter
    def enrichment_flags(self, value):
        self.enrichment_flags_json = json.dumps(value) if value is not None else None
