from src.loaders.data_loader import load_chunk_pdf
from src.services.llm_service import LLM_server
from src.storage.data_base import QdrantStorage
from src.services.retrival import  Retrival
from dotenv import load_dotenv

def main():
    load_dotenv()
    db = QdrantStorage("RAG-DOC")
    ai = LLM_server()
    retrival = Retrival(db, ai)
    
    print("RAG system based on PDF")
    
    while True:
        user_question = input("Ask your question: ")
        if user_question.lower() in ["exit"]:
            break
        anserw = retrival.retrival(user_question)
        print(anserw)

    
if __name__ == "__main__":
    main()