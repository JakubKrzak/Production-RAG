from rag.loaders.data_loader import load_chunk_pdf
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

class Ingestion():
    def __init__(self, data_base: str, llm: str):
        self.db = data_base
        self.llm = llm
    
    def ingestion_pdf(self, pdf_path):
        collection_exists = self.db.check_collection_exists()
        if not collection_exists:
            self.db.create_collection()
        
        chunks_pdf = load_chunk_pdf(path=pdf_path)
        
        chunks_embedding = self.llm.embeddings_chunks(chunks_pdf)
        
        if self.db.upsert_chunks(chunks=chunks_pdf, vectors=chunks_embedding):
            return f"PDF {pdf_path} has been ingested"

