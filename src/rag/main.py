from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import os
from pathlib import Path
import shutil

from rag.services.schemas import QuestionReq, QuestionRes
from rag.services.llm_service import LLM_server
from rag.storage.data_base import QdrantStorage
from rag.services.retrival import Retrival
from rag.services.ingestion import Ingestion


load_dotenv()
db = QdrantStorage("policy_home")
ai = LLM_server()

pipeline_ingestion = Ingestion(db, ai)
pipeline_retrival = Retrival(db, ai)

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

@app.post("/question", response_model=QuestionRes)
async def ask_question(payload: QuestionReq):
    """Function receives user question, 
        pass it to retrival pipeline and return answer"""
    
    answer = await pipeline_retrival.retrival(payload.question)
    return {"answer": answer}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(('.pdf')):
        raise HTTPException(status_code=400, detail="document format is not pdf")
    
    upload_folder = "data"
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)

    with open(file_path, "wb+") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    BackgroundTasks.add_task(pipeline_ingestion.ingestion_pdf, file_path)

    return {"message": "Ingestion finish"}

