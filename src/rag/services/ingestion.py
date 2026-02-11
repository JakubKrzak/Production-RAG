from data_loader import load_chunk_pdf
from llm_service import LLM_server
from data_base import QdrantStorage
from dotenv import load_dotenv

load_dotenv()

class Ingestion():
    def __init__(self, data_base: str, llm: str):
        self.db = data_base
        self.llm = llm
    
    def ingestion_pdf(self, pdf_path):
        chunks_pdf = load_chunk_pdf(path=pdf_path)
        chunks_embedding = self.llm.embeddings_chunks(chunks_pdf)
        if self.db.upsert_chunks(chunks=chunks_pdf, vectors=chunks_embedding):
            return f"Pdf dodany do bazy dziala wszytsko "

