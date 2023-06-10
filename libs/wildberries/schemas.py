from typing import Optional

from pydantic import BaseModel


class ReviewSchema(BaseModel):
    id: str
    stars: int
    text: Optional[str] = None
    barcode: str
    brand: str
    has_complaint: bool
