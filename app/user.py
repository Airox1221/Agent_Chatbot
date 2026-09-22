"""
  user object to store user-specific data such as uploaded documents and chat history.
  This class is used to manage user sessions and maintain state across multiple requests in the FastAPI
"""

import os
from app.embeding import text_embedding
from app.vector import create_index, query_index , delete_vector
from app.pdf_parser import extract_text_from_pdf
from app.grok_llm import groq_query
import configparser
import datetime


config = configparser.ConfigParser()
config.read("config.ini")

chunk_size = config["parameter"].getint("chunk_size")
chunk_overlap = config["parameter"].getint("chunk_overlap")
temperature = config["parameter"].getfloat("temperature")



class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.documents_path :str = None
        self.chat_history = []
        self.vector_index_path : str = None
        self.metadata_path : str = None

    def generate_vector_db(self , documents_path : str ):
        """
        Generate a vector database for the user based on the uploaded PDF documents.
        Args:
            documents_path (str): The path to the uploaded PDF documents.
        Returns:
            None
        
        """
  
        os.makedirs(f"db/{self.user_id}", exist_ok=True)
        metadata_path = f"db/{self.user_id}/metadata.json"
        vector_index_path = f"db/{self.user_id}/vector.index"
        self.documents_path = documents_path
        text = extract_text_from_pdf(self.documents_path)
        embeddings = text_embedding(text , chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        index, metadata = create_index(embeddings , index_file_path=vector_index_path , metadata_path=metadata_path)

        self.metadata_path = metadata_path
        self.vector_index_path = vector_index_path
        print(f"Vector database generated for user {self.user_id}. Index saved to {vector_index_path}, metadata saved to {metadata_path}.")
        print(f"-----------------used chunk size = {chunk_size} and overlap = {chunk_overlap}  ---------------")
        return f"Vector database generated for user {self.user_id}. Index saved to {vector_index_path}, metadata saved to {metadata_path}."

    def query(self, query: str , Top : int = 3 ):
        """
        Query the user's vector database with a given query and return the top results.
        Args:
            query (str): The query to be sent to the chatbot.
            Top (int): The number of top results to return. Default is 3.
        Returns:
            list: A list of the top results from the vector database.
        """
        if self.vector_index_path is None or self.metadata_path is None:
            raise ValueError("Vector database not generated. Please generate the vector database first.")
        

        query_embedding = text_embedding(query)  
        indices, chunk_texts = query_index(query_embedding, Path=self.vector_index_path , METADATA_PATH=self.metadata_path , Top=Top)
        context = " ".join(chunk_texts)
        answer = groq_query(context, query ,temperature=temperature)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.chat_history.append({"query": query, "answer": answer, "timestamp": timestamp})
        print(f"--------used top = {Top}  and Temp = {temperature} -------------------")

        return answer

    def user_delete(self ):
        if self.vector_index_path != None or self.metadata_path != None :
            delete_vector(f"db/{self.user_id}")
