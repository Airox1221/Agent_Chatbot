from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uuid
from app.user import User
import pickle
import configparser


config = configparser.ConfigParser()
config.read("config.ini")

top = config["parameter"].getint("top")

users = {}
user_list = []  # List to store user IDs
app = FastAPI()



def list_users():
    """
    List all user IDs currently stored in the users dictionary.
    Returns:
        list: A list of user IDs.
    """
    path = "data"
    if not os.path.exists(path):
        os.makedirs(path)
    files = [os.path.splitext(file)[0] for file in os.listdir("data") if file.endswith(".pkl")]
    return files
    

def save_user(user_id: str, user: User):
    """
    Save a user object to the users dictionary.
    Args:
        user_id (str): The ID of the user.
        user (User): The User object to be saved.
    """
    users[user_id] = user
    with open(f"data/{user_id}.pkl", "wb") as file:
        pickle.dump(user, file)

def load_user(user_id: str):
    """
    Load a user object from the users dictionary.
    Args:
        user_id (str): The ID of the user.

    Returns:
        User: The User object corresponding to the given user_id, or None if not found.
    """
    if user_id in users:
        return users[user_id]
    try:
        with open(f"data/{user_id}.pkl", "rb") as file:
            user = pickle.load(file)
            users[user_id] = user
            return user
    except FileNotFoundError:
        return None



##    --------- API STARTS -----------



# Serve CSS, JavaScript, images, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home():
    return FileResponse("static/index.html")




# Create a new user and return the user ID
@app.post("/new_user")
async def new_user():
    """
    Create a new user and return the user ID.
    Returns:
        dict: A dictionary containing the new user ID.
    """
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    user = User(user_id)
    save_user(user_id, user)
    return {"message": "User created successfully", "user_id": user_id }






@app.post("/upload")
async def upload_pdf(user_id: str, file: UploadFile = File(...) ):
    """
    Upload a PDF file and save it to the "uploads" directory
    Args:
        file (UploadFile): The PDF file to be uploaded.
    Returns:
        dict: A dictionary containing the filename and content type of the uploaded file.
    """

    user = load_user(user_id)
    if user is None:
        return {"error": " create a chat first."}
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", file.filename)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    result = user.generate_vector_db(file_path)  # Generate vector database for the user based on the uploaded PDF
    save_user(user_id, user)  # Save the updated user object with the generated vector database
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "user_id": user_id,
        "message": f"{result}"
    }


@app.post("/send")
async def send_msg(user_id : str , query : str ):
    """
    Send a query to the chatbot and get a response based on the uploaded PDF documents.
    Args:
        user_id (str): The ID of the user sending the query.
        query (str): The query to be sent to the chatbot.
    Returns:
        dict: A dictionary containing the chatbot's response to the query.
    """
    user = load_user(user_id)
    if user is None:
        return {"error": " Please upload a PDF first."}
    if user.documents_path == None:
        return {"error": " Please upload a PDF first."}

    answer = user.query(query , Top = top)
    save_user(user_id, user)  # Save the updated user object
    return {"answer": answer}


# To delete the user id object and the vector DB also 

@app.delete("/delete_chat")
async def delete_chat(userid: str):
    """Delete a user's saved chat and remove it from the memory cache.
    Args:
        userid (str): unique user id of the user to be deleted
    """

    user_path = os.path.join("data", f"{userid}.pkl")

    if not os.path.isfile(user_path):
        return {"error": "Chat not found."}

    user = load_user(userid)
    if user is not None:
        user.user_delete()

    os.remove(user_path)
    users.pop(userid, None)
    return {"message": "Chat deleted successfully.", "user_id": userid}



@app.get("/history")
async def get_history(user_id: str):
    """
    Get the chat history for a specific user.
    Args:
        user_id (str): The ID of the user whose chat history is to be retrieved.
    Returns:
        list: A list of dictionaries containing the query, answer, and timestamp for each interaction.
    """
    user = load_user(user_id)
    if user is None:
        return {"error": "User not found. Please upload a PDF first."}
    return user.chat_history


@app.get("/all_users")
async def get_all_users():
    """
    Get a list of all user IDs.
    Returns:
        list: A list of all user IDs.
    """

    return {"users": list_users()}