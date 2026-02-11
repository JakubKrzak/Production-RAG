from pydantic import BaseModel
from typing import Any

class DocumentChunk(BaseModel):
    chunk_id: str
    text: str
    metadata: dict[str, Any]