import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import numpy as np

load_dotenv()
token = os.getenv("HF_TOKEN")
model_name = os.getenv("EMBED_MODEL")

# Load the Hugging Face token from environment variables 

def embed_model(text: str , token = token):
    client = InferenceClient(
        provider="hf-inference",
        api_key=token,
    )

    result = client.feature_extraction(
        f"{text}",
        model=model_name,
    )
    return result

# Convert Text to embeddings using the Hugging Face model

def text_embedding(text: str , chunk_size:int = 70 , chunk_overlap:int = 10):

    """
    Convert text into embeddings using the Hugging Face model.
    The text is split into chunks of specified size with overlap, and each chunk is converted to an embedding vector.

    Args:
        text (str): The input text to be converted into embeddings.
        chunk_size (int): The size of each text chunk. Default is 50.
        chunk_overlap (int): The number of overlapping characters between consecutive chunks. Default is 10

    Returns:
        list: A list of dictionaries, each containing a text chunk and its corresponding embedding vector.
        {
            "chunk": str,  # The text chunk
            "vector": list  # The embedding vector for the chunk
        }

    """
    vector_list = []
    
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        vector = embed_model(chunk).astype(np.float32)  # Convert the result to a NumPy array of type float32
        vector_list.append({
            "chunk": chunk,
            "vector": vector
        })

        i -= chunk_overlap  # Move back by chunk_overlap to create overlap

    return vector_list



if __name__ == "__main__":

    # Test the embedding function with a sample text

    text = "Validation passed: the module imports successfully and reports no editor errors. Running the actual request still returns 403, so the configured Hugging Face token needs"

    embeddings = text_embedding(text)
    print(len(embeddings))
    print(embeddings[0].get("chunk"))  # Print the first chunk and its vector's data type