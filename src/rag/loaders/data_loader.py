from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from schemas import DocumentChunk
from pathlib import Path
from dotenv import load_dotenv

def load_chunk_pdf(path: str) -> list[DocumentChunk]:
    """
    Load file pdf from 'path' and split its to chunks
    
    Function usues LlamaIndex 'PDFReader' to read the PDF and SentencesSplitter create nodes.
    Each node is converted into 'DocumentChunk' contained:
        -chunk_id: unique node identifier
        -text: chunk content
        -metadata: documents metadata(page_number, file_name)

    Returns:
        A list of 'DocumentChunk' 
    """
    splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)
    reader = PDFReader()

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Not found file on path: {path}")
    if not p.is_file():
        raise IsADirectoryError(f"Path is not a file")
    
    try:
        docs = reader.load_data(file=path)
        nodes= splitter.get_nodes_from_documents(documents=docs)
    
        chunks = []
        for node in nodes:
            chunk = DocumentChunk(
                chunk_id=node.id_,
                text=node.text,
                metadata=node.metadata
            )
            chunks.append(chunk)

        return chunks
    
    except Exception as e:
        raise ValueError(f"Error {e}")
    

        
