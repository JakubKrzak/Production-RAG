from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from qdrant_client.http.exceptions import UnexpectedResponse
from rag.services.schemas import DocumentChunk
import pydantic
import os
from dotenv import load_dotenv

load_dotenv()

class QdrantStorage():
    def __init__(self, collection_name: str, dim: int = 1536):
        url = os.getenv("QDRANT_ENDP")
        api_key = os.getenv("QDRANT_API_KEY")
        
        if not url or not api_key:
            raise ValueError("QDRANT_ENDP and QDRANT_API_KEY must be set in .env file")
        
        self.client = AsyncQdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name
        self.dim = dim
    
    def test_connection_db(self):
        """
        
        Function testing connection with data base
        
        """
        try:
            if self.client.get_collections():
                print("Connection works with db")
        except Exception as e:
            raise SystemError("Connection Error")
    
    async def create_collection(self) -> None:
        exists = await self.client.collection_exists(collection_name=self.collection_name)
        if exists:
            return
        
        await self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE))
        
    async def check_collection_exists(self) -> bool:
        return await self.client.collection_exists(collection_name=self.collection_name)
    
    def delete_collection(self, collection_name):
        """
        
        Function to delete collections

        """
        try:
            if not self.client.collection_exists(collection_name=collection_name):
                print(f"Collection {collection_name} not found")
            else:
                self.client.delete_collection(collection_name=collection_name)
                print(f"Collection {collection_name} has been delated")
        
        except UnexpectedResponse as e:
            raise ValueError(f"error {e}")
    
    def create_points(self, chunks: list[DocumentChunk], vectors: list[list[float]]) -> list[PointStruct]:
        if not chunks or not vectors:
            return []
        
        if len(chunks) != len(vectors):
            raise ValueError(f"chunks {len(chunks)} | vectors {len(vectors)} not match")
        
        points = []
        for chunk, vector in zip(chunks, vectors):
            points.append(
                PointStruct(
                    id=chunk.chunk_id,
                    vector=vector,
                    payload=chunk.model_dump()
                )
            )
            
        return points
    
    async def upsert_points(self, points: list[PointStruct]):
        if not points:
            return
        
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
 
    async def search_similarity(self, vectors: list[float], top_k: int =5):
        if not vectors:
            raise ValueError(f"there are no vectors, current vecs: {len(vectors)}")
        
        try:
            response = await self.client.query_points(
                collection_name=self.collection_name,
                query=vectors,
                with_payload=True,
                limit=top_k
            )
            points = response.points
            return points
        
        except Exception as e:
            raise ValueError(f"Error {e}")


                
            
        