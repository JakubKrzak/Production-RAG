from llm_service import LLM_server
from data_base import QdrantStorage
from dotenv import load_dotenv

class Retrival():
    def __init__(self, data_base: str, llm: str):
        self.db = data_base
        self.llm = llm
    
    def retrival(self, user_question: str) -> str:
        user_question_embedding = self.llm.query_embedding(user_question=user_question)
        hits = self.db.search_similarity(vectors = user_question_embedding, top_k=5)
        context = self.llm.create_context(hits=hits)
        answer = self.llm.llm_response(user_question=user_question, context=context)
        print(answer)