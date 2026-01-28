from pydantic import BaseModel, Field
from typing import Optional, List

class DocRecord(BaseModel):
    file_name: str
    doc_type: str = Field(default="boleto_comprovante")
    cpf: Optional[str] = None
    payer_name: Optional[str] = None
    beneficiary: Optional[str] = None
    linha_digitavel: Optional[str] = None
    barcode: Optional[str] = None
    total_value: Optional[float] = None
    payment_status: Optional[str] = None  # paid|unpaid|unknown
    payment_date: Optional[str] = None    # YYYY-MM-DD
    auth_code: Optional[str] = None
    notes: Optional[str] = None

class ExtractResult(BaseModel):
    record: DocRecord
    issues: List[str] = Field(default_factory=list)
    knowledge_sources: List[str] = Field(default_factory=list)
