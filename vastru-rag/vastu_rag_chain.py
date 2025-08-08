# vastu_rag_chain.py

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
import json

# --- Configuration ---
DB_FAISS_PATH = "vastu_faiss_index"

# 1. Set up the components
print("Loading Vastu knowledge base and models...")
embeddings = HuggingFaceEmbeddings(
    model_name='sentence-transformers/all-MiniLM-L6-v2',
    model_kwargs={'device': 'cpu'}
)
db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
retriever = db.as_retriever(search_kwargs={'k': 4}) # Retrieve top 4 relevant chunks
llm = ChatOllama(model="llama3") # Connect to local Llama 3 via Ollama

# 2. Define the detailed prompt template
prompt_template = """
You are an expert architectural assistant specializing in Vastu Shastra.
Your task is to convert a user's request into a structured JSON floor plan that strictly follows Vastu principles.

**CONTEXT - VASTU SHASTRA RULES:**
{context}

**INSTRUCTIONS:**
1.  Carefully analyze the user's request below.
2.  Strictly apply the Vastu Shastra rules from the CONTEXT to the user's request.
3.  **Vastu rules are more important than the user's specific location requests.** If the user asks for a room in a location that violates Vastu, you MUST place it in the correct Vastu location and can optionally add a note.
4.  Generate ONLY a JSON object as the output, with no other text, explanation, or markdown.
5.  The JSON must describe the rooms, their type, location, size, and connections, following the required schema.
    - 'location' must be one of: ["north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest", "center"]
    - 'size' can be one of: ["S", "M", "L", "XL"]

**USER'S REQUEST:**
{question}

**JSON OUTPUT:**
"""
prompt = PromptTemplate(
    template=prompt_template, input_variables=['context', 'question']
)

# 3. Create the RAG Chain
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def get_vastu_json(user_query: str) -> dict:
    """
    Takes a user query, runs it through the Vastu RAG chain,
    and returns a parsed JSON dictionary.
    """
    print(f"Generating Vastu-compliant plan for: '{user_query}'")
    llm_output = rag_chain.invoke(user_query)
    print("LLM Raw Output:\n", llm_output)
    
    try:
        # The LLM might sometimes return the JSON wrapped in ```json ... ```
        # This cleanup helps to parse it reliably.
        if "```json" in llm_output:
            clean_output = llm_output.split("```json\n")[1].split("```")
        else:
            clean_output = llm_output
        
        parsed_json = json.loads(clean_output)
        return parsed_json
    except (json.JSONDecodeError, IndexError) as e:
        print(f"Error: Failed to parse LLM output into JSON. Error: {e}")
        print("Returning an empty dict.")
        return {}

# Example of how to use this module
if __name__ == '__main__':
    # Make sure Ollama is running in the background
    test_query = "Design a 2-bedroom house for me. I need a kitchen and a place for prayer."
    vastu_compliant_plan = get_vastu_json(test_query)

    if vastu_compliant_plan:
        print("\n--- Parsed JSON ---")
        print(json.dumps(vastu_compliant_plan, indent=2))