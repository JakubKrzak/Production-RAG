from rag.loaders.data_loader import load_chunk_pdf
from dotenv import load_dotenv

load_dotenv()

class Ingestion():
    def __init__(self, data_base: str, llm: str):
        self.db = data_base
        self.llm = llm
    
    async def ingestion_pdf(self, pdf_path):
        collection_exists = await self.db.check_collection_exists()

        if not collection_exists:
            await self.db.create_collection()
        
        chunks_pdf = load_chunk_pdf(path=pdf_path)
        vectors_chunks = await self.llm.embeddings_chunks(chunks_pdf)

        points = self.db.create_points(chunks=chunks_pdf, vectors=vectors_chunks)
        return await self.db.upsert_points(points=points)
