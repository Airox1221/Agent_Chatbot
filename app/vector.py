import faiss
from dotenv import load_dotenv
import os
from app.embeding import text_embedding
import json
import shutil

load_dotenv()

DIM = int(os.getenv("DIM", 384))  # Default to 384 if not set in .env


def create_index(vectors: list , index_file_path , metadata_path ,dim: int = DIM ,   ): 
    
    """
    Create a FAISS index from a list of vectors and save it to a file.

    Args:
        vectors (list): A list of vectors to be indexed. Each vector should be a NumPy array or a list of floats.
        dim (int): The dimensionality of the vectors. Default is 384.
        index_file_path (str): The file path where the index will be saved. Default is "vector.index".
        metadata_path (str): The file path where the metadata will be saved. Default is "metadata.json".

    both dim and index_file_path can be set in the .env file as DIM and VECTOR_INDEX_PATH respectively.
    Returns:
        index: The created FAISS index.
    """

    index = faiss.IndexFlatL2(dim)  # Create a flat (non-compressed) index
    metadata = {}
    for i, items in enumerate(vectors):
        vector = items["vector"].reshape(1, -1)  # Reshape the vector to be 2D for FAISS
        metadata[i] = items["chunk"]  # Store the chunk text in metadata
        index.add(vector)  # Add each vector to the index

    print(f"Total vectors indexed: {index.ntotal}")

    faiss.write_index(index, index_file_path)
    print(f"Index successfully written to {index_file_path}")

    # Store the metadata with the index
    with open(metadata_path, "w") as f:
        json.dump(metadata, f)

    return index , metadata



def query_index(query_vector , Path  , METADATA_PATH, Top : int = 3  ):

    """
    Query a FAISS index with a given vector and return the indices of the top results.
    Args:
        query_vector: The vector to query the index with. Should be a NumPy array of shape (dim,).
        Path (str): The file path of the loaded FAISS index.
        METADATA_PATH (str): The file path of the metadata.
        Top (int): The number of top results to return. Default is 3.
    Returns:
        indices: The indices of the top results in the index.
        chunk_texts: The texts of the top results.

    """
    index_loaded = faiss.read_index(Path)
    query_vector = query_vector[0]["vector"].reshape(1, -1)  # Reshape the query vector to be 2D for FAISS
    distances, indices = index_loaded.search(query_vector, Top)

    with open(METADATA_PATH, "r") as f:
      metadata = json.load(f)
    chunk_texts = [metadata.get(str(idx), "Unknown chunk") for idx in indices[0]]

    return indices, chunk_texts


def delete_vector(path:str):
    """
    to delete a Created Vector DB 
    Args :
        path (str): path to the Vector DB 
    """
    if os.path.exists(path):
        shutil.rmtree(path)
        print("Folder deleted successfully")
    else:
        print("Folder does not exist")




if __name__ == "__main__":
    # Test the create_index and query_index functions with sample data

    sample_text = "The Earth is a planet that orbits the Sun. It has air, water, and land, which make life possible. Plants use sunlight, water, and carbon dioxide to make their food through photosynthesis. Animals get energy by eating plants or other animals. The Earth's atmosphere also protects living things from harmful radiation."
    embeddings = text_embedding(sample_text)

    index, metadata = create_index(embeddings)

    query = "what this about?"
    query_embedding = text_embedding(query)  
    indices, chunk_texts = query_index(query_embedding, Top=3) 

    print(f"Query: {query}")
    print(f"Top indices: {indices}")
    print(f"Corresponding chunk texts: {chunk_texts}")