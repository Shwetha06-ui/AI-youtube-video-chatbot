try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_text_chunks(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
    """
    Splits transcript text into smaller, overlapping chunks suitable for embedding and retrieval.
    
    Args:
        text (str): The full cleaned transcript text.
        chunk_size (int): Target character count per chunk.
        chunk_overlap (int): Overlap character count between adjacent chunks.
        
    Returns:
        list[str]: List of text chunk strings.
    """
    if not text:
        return []
        
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    return chunks

def create_vector_store(chunks: list, api_key: str):
    """
    Generates Google Gemini embeddings for text chunks and indexes them using FAISS vector store.
    Tries embedding models in order of compatibility across Gemini API versions.
    
    Args:
        chunks (list[str]): Text chunks.
        api_key (str): Google Gemini API Key.
        
    Returns:
        FAISS: In-memory FAISS vector store instance.
    """
    if not chunks:
        raise ValueError("Cannot create vector store: text chunks list is empty.")
        
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("A valid Google Gemini API Key is required to create embeddings.")
        
    candidate_models = [
        "models/embedding-001",
        "embedding-001",
        "models/text-embedding-004",
        "text-embedding-004"
    ]
    
    last_exception = None
    for model_name in candidate_models:
        try:
            embeddings = GoogleGenerativeAIEmbeddings(
                model=model_name,
                google_api_key=api_key
            )
            # Build FAISS vector store from texts
            vector_store = FAISS.from_texts(texts=chunks, embedding=embeddings)
            return vector_store
        except Exception as e:
            last_exception = e
            continue

    raise Exception(f"Failed to create FAISS vector store with Gemini embedding models: {str(last_exception)}")
