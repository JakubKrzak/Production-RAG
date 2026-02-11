from openai import OpenAI, OpenAIError
from schemas import DocumentChunk
from dotenv import load_dotenv

load_dotenv()

class LLM_server():
    def __init__(self, llm_model="gpt-4o-mini", embedding_model="text-embedding-3-small",  dim: int = 1536):
        self.client = OpenAI()
        self.llm_model=llm_model
        self.embedding_model=embedding_model
        self.dim = dim

    def embeddings_chunks(self, chunks: list[DocumentChunk]) -> list[list[float]]:
        if len(chunks) < 0:
            raise ValueError("Chunks len < 0")
        
        text = [item.text for item in chunks]
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )

        except OpenAIError as e:
            print(f"OpenAI connection error: {e}")
            raise e
                       
        except Exception as e:
            raise ValueError(f"Error {e}")
                

        vectors = [item.embedding for item in response.data]
        current_dim = len(vectors[0])
        if current_dim != self.dim:
            raise ValueError(f"dimensions not match, current_dim: {current_dim}, expeced_dim: {self.dim}, embed_model: {self.embedding_model}")
        
        return vectors
    
    def query_embedding(self, user_question: str) -> list[float]:
        """
        
        Function change user question to a vectors list[float]
        checks the correct dimension and return vectors,

        """
        try:
            response = self.client.embeddings.create(
            model=self.embedding_model,
            input=[user_question]
            )
            vectors = response.data[0].embedding

            if len(vectors) != self.dim:
                raise ValueError(f"Vectors dimensions({len(vectors)}) is not correct, expected {self.dim}")

            return vectors
        
        except OpenAIError as e:
            raise OpenAIError(F"OPENAI error {e}")
        except Exception as e:
            raise ValueError(f"Error {e}")
        
    def create_context(self, hits: list[str]) -> str:
        if not hits:
            raise RuntimeError("No hits")
        try:
            context = ""
            for i, hit in enumerate(hits, start=1):
                metadata = hit.payload.get("metadata", {})

                page = metadata.get("page_label", "unknow")
                file_name = metadata.get("file_name", "unknow")
                text = hit.payload.get("text", "")
        
                context += f"\nContext {i}:\n File name: {file_name}, page {page}\n Text: {text}\n"
        
            return context
        
        except Exception as e:
            raise RuntimeError(f"Error {e}") from e
        
    def llm_response(self, user_question: str, context: str) -> str:
        system_prompt = (
            "You are a professional assistant specializing in document analysis. "
            "Answer the user's question using only the provided CONTEXT. "
        )

        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"context:{context}\n question: {user_question}"
                    }
                ],
                temperature=0.3
            )
            if not response.choices:
                raise RuntimeError("OpenAI returned nothing")
            
            res = response.choices[0].message.content
            if res is None:
                raise RuntimeError(f"OpenAI return empty messages")
                
            return res
        
        except OpenAIError as e:
            raise RuntimeError("OpenAI request failed") from e



    
    
 
        
