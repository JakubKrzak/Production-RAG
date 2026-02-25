from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import os
from pathlib import Path
import shutil
import json

from rag.services.schemas import QuestionReq, QuestionRes
from rag.services.llm_service import LLM_server
from rag.storage.data_base import QdrantStorage
from rag.services.retrival import Retrival
from rag.services.ingestion import Ingestion

from dotenv import load_dotenv


load_dotenv()
db = QdrantStorage("regulamin")
ai = LLM_server()

pipeline_ingestion = Ingestion(db, ai)
pipeline_retrival = Retrival(db, ai)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
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
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only .pdf files are allowed")
    
    upload_folder = "data"
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, file.filename)

    try:
        with open(file_path, mode="wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    
    #Pipeline ingestion
    await pipeline_ingestion.ingestion_pdf(pdf_path=file_path)

    return {"messages": "File was save", "filename": file.filename, "file path": file_path}
    
    

