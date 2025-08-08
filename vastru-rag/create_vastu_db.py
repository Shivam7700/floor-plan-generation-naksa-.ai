import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


PDF_PATH = "vastu-shastra.pdf"
PDF_PATH2 = "vasru-short.pdf"
DB_FAISS_PATH = 'vastu_faiss_index'

def create_vector_db():
    """
    Reads a PDF, splits it into chunks, creates embeddings,
    and saves them to a local FAISS vector database.
    """
    # 1. Load the PDF document
    if not os.path.exists(PDF_PATH):
        print(f"Error: PDF file not found at {PDF_PATH}")
        return
        
    print("Loading PDF document...")
    loader = PyPDFLoader(PDF_PATH2)
    documents = loader.load()
    print(f"Loaded {len(documents)} pages from the PDF.")

    # 2. Split the document into smaller chunks for better retrieval
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(documents)
    print(f"Split into {len(docs)} text chunks.")

    # 3. Set up the local embedding model
    # This model runs on your CPU and is great for this task.
    print("Initializing embedding model...")
    # Using a popular, efficient model from Hugging Face
    embeddings = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-MiniLM-L6-v2',
        model_kwargs={'device': 'cpu'}
    )

    # 4. Create the FAISS vector store from the chunks and embeddings
    print("Creating vector database...")
    db = FAISS.from_documents(docs, embeddings)

    # 5. Save the vector database to your local disk
    db.save_local(DB_FAISS_PATH)
    print(f"Vastu Shastra knowledge base created and saved at: {DB_FAISS_PATH}")

if __name__ == '__main__':
    create_vector_db()