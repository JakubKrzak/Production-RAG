from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from rag.services.llm_service import LLM_server
from rag.storage.data_base import QdrantStorage
from rag.services.retrival import Retrival


load_dotenv()
db = QdrantStorage("RAG-DOC")
ai = LLM_server()
pipeline = Retrival(db, ai)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500", "http://localhost:5500",
        "http://127.0.0.1:5501", "http://localhost:5501",
        "http://127.0.0.1:5502", "http://localhost:5502",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"messages": "API works"}

class QuestionReq(BaseModel):
    question: str

class QuestionRes(BaseModel):
    answer: str

@app.post("/question", response_model=QuestionRes)
def ask_question(payload: QuestionReq):
    answer = pipeline.retrival(payload.question)
    return {"answer": answer}