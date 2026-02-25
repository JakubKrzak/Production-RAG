from rag.services.llm_service import LLM_server
from rag.storage.data_base import QdrantStorage
from dotenv import load_dotenv

class Retrival():
    def __init__(self, data_base, llm):
        self.db = data_base
        self.llm = llm
    
    async def retrival(self, user_question: str) -> str:

        user_question_embedding = await self.llm.query_embedding(user_question=user_question)
        hits = await self.db.search_similarity(vectors = user_question_embedding, top_k=5)
        context = self.llm.create_context(hits=hits)
        answer = await self.llm.llm_response(user_question=user_question, context=context)
        return answer