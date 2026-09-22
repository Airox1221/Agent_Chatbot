from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
model_name = os.getenv("MODEL_NAME", "qwen/qwen3.8-27b")  # Default to "qwen/qwen3.8-27b" if not set in .env

def get_groq_model(model_name: str = model_name, temperature: float = 0.4, max_retries: int = 2):
    """
    Initialize and return a ChatGroq model instance using the API key from environment variables.
    Args:
        model_name (str): The name of the model to use. Default is "qwen/qwen3.8-27b". can be set in the .env file as MODEL_NAME.
        temperature (float): The temperature for the model's randomness. Default is 0.4 
        max_retries (int): The maximum number of retries for the model's API calls. Default is 2.

    
    Returns:
        ChatGroq: An instance of the ChatGroq model.
    """
    model = ChatGroq(
        model=model_name,
        temperature=temperature,
        max_retries=max_retries
    )
    return model




def groq_query(context: str, question: str , temperature: float = 0.4):
    """
    Query the Groq model with a given context and question.
    Args:
        context (str): The context to provide to the model.
        question (str): The question to ask the model.
        temperature (float): The temperature for the model's randomness.
    Returns:
        response.content: The content of the model's response.

    """
    model = get_groq_model( temperature=temperature )


    messages = [
        ("system", "You are a helpful AI assistant. Answer the questions based on the context provided."),
        ("human", f"Question: {question}\nContext: {context}"),
    ]
    response = model.invoke(messages, temperature=temperature)
    return response.content


if __name__ == "__main__":
    # Test the Groq model query function with a sample context and question
    
    
    from embeding import text_embedding
    from vector import create_index, query_index
    from pdf_parser import extract_text_from_pdf

    text = extract_text_from_pdf("test/functionalsample.pdf")

    embeddings = text_embedding(text , chunk_size=300, chunk_overlap=70)

    index, metadata = create_index(embeddings)

    query = "what this about?"
    query_embedding = text_embedding(query)  
    indices, chunk_texts = query_index(query_embedding, Top=3)

    context = " ".join(chunk_texts)
    answer = groq_query(context, query)
    print(f"Answer: {answer}")
    