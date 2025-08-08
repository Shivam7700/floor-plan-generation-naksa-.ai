import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# --- Configuration ---
# Assumes the vector database folder is in the same directory as this script.
DB_FAISS_PATH = r"D:\Undergraduate_Ai\Sem-7\Naksa2.0\Chat_house_diffusion\chathousediffusion\vastru-rag\vastu_faiss_index"

def setup_retriever():
    """
    Sets up and returns the Vastu knowledge base retriever.
    This should be called once when the application starts to load the models
    and database into memory for efficiency.
    """
    if not os.path.exists(DB_FAISS_PATH):
        raise FileNotFoundError(
            f"Vastu database not found at '{DB_FAISS_PATH}'. "
            "Please run your 'create_vastu_db.py' script first to build it."
        )

    print("Loading Vastu knowledge base and local embedding model...")
    
    # Initialize the same embedding model used to create the database
    embeddings = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-MiniLM-L6-v2',
        model_kwargs={'device': 'cpu'}
    )
    
    # Load the local FAISS database from disk
    # 'allow_dangerous_deserialization=True' is needed for LangChain's security measures with local files.
    db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    
    # Configure the database as a retriever to find the top 4 most relevant chunks
    return db.as_retriever(search_kwargs={'k': 4})

# --- Global Engine Initialization ---
# The retriever is initialized once when this file is first imported.
# This prevents reloading the models and database on every single request.
retriever = setup_retriever()
print("Vastu RAG engine initialized successfully and is ready.")


def get_vastu_context(query: str) -> str:
    """
    Takes a user's query, retrieves the most relevant Vastu rules from the database,
    and formats them into a single string to be used as context in a prompt.
    
    Args:
        query (str): The user's input prompt (e.g., "design a 3 bedroom house").

    Returns:
        str: A formatted string containing the retrieved Vastu rules.
    """
    # Use the globally initialized retriever to find relevant documents
    docs = retriever.invoke(query)
    
    if not docs:
        return "No specific Vastu rules found for this query. Please rely on general architectural principles."
    
    # Combine the content of the retrieved document chunks into a single, clean string
    formatted_context = "\n- ".join([doc.page_content for doc in docs])
    return formatted_context