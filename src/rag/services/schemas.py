from pydantic import BaseModel
from typing import Any

#Schemas for creating documents and chunks
class DocumentChunk(BaseModel):
    chunk_id: str
    text: str
    metadata: dict[str, Any]

#Schemas for receiving question and answer
class QuestionReq(BaseModel):
    question: str

class QuestionRes(BaseModel):
    answer: str