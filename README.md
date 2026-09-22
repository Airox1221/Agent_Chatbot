# Agent Chatbot

Agent Chatbot is a local document question-answering application. A user creates a chat, uploads a PDF, and asks questions about that document. The application extracts text from the PDF, creates embeddings through Hugging Face, stores the embeddings in a per-user FAISS index, retrieves relevant chunks for each question, and sends the retrieved context to a Groq-hosted language model.

The project includes a FastAPI backend and a browser-based frontend served by the same application.

## Features

- Create separate chat users with generated IDs.
- Upload a PDF for a chat.
- Extract PDF text with PyMuPDF.
- Generate embeddings with a Hugging Face inference model.
- Store a separate FAISS vector index for each user.
- Ask questions using retrieved document context.
- Persist chat history as serialized user objects.
- Load user objects lazily when an endpoint needs them.
- Browse previous chats in the web interface.
- Delete a chat and its vector database.

## Technology Stack

- Python 3.11 or newer
- FastAPI and Uvicorn
- PyMuPDF for PDF parsing
- Hugging Face Inference API for embeddings
- FAISS for vector search
- LangChain Groq integration for LLM requests
- Vanilla HTML, CSS, and JavaScript frontend
- `uv` for dependency and environment management

## Project Structure

```text
.
├── app/
│   ├── embeding.py          # Hugging Face embedding requests and text chunking
│   ├── grok_llm.py         # Groq model initialization and generation
│   ├── pdf_parser.py       # PDF text extraction
│   ├── user.py             # Per-user document and chat behavior
│   ├── vector.py           # FAISS index and metadata operations
│   └── server/
│       └── api.py          # FastAPI application and routes
├── static/
│   ├── index.html          # Web application page
│   ├── css/style.css       # Frontend styles
│   └── js/script.js        # Frontend API calls and chat behavior
├── db/                     # Generated per-user FAISS data
├── data/                   # Saved user objects and chat history
├── uploads/                # Uploaded PDF files
├── config.ini              # Server and retrieval settings
├── main.py                 # Application launcher
├── pyproject.toml          # Project metadata and dependencies
└── .env                    # Local API credentials; do not commit
```

The `db`, `data`, and `uploads` directories are runtime directories. Their generated contents are ignored by Git; `.gitkeep` files preserve the directory structure.

## Requirements

Install the following before running the project:

- Python 3.11 or newer
- `uv` (recommended) or a standard Python virtual environment
- A Hugging Face access token with inference access
- A Groq API key

The embedding and LLM requests require an internet connection.

## Installation

Open a terminal in the repository root:

```powershell
uv sync
```

If `uv` is not installed, install it using the official instructions, then run `uv sync` again. The project dependencies are declared in `pyproject.toml`.

To use an existing virtual environment instead, install the project dependencies with:

```powershell
python -m pip install -e .
```

## Environment Configuration

Create a `.env` file in the repository root. Do not commit this file.

```dotenv
HF_TOKEN=your_huggingface_token
GROQ_API_KEY=your_groq_api_key
EMBED_MODEL=BAAI/bge-small-en-v1.5
MODEL_NAME=qwen/qwen3.8-27b
DIM=384
```

Variable reference:

| Variable | Purpose | Default/current value |
| --- | --- | --- |
| `HF_TOKEN` | Authenticates Hugging Face embedding requests | Required |
| `GROQ_API_KEY` | Authenticates Groq requests | Required |
| `EMBED_MODEL` | Hugging Face embedding model | Required by current code; use `BAAI/bge-small-en-v1.5` |
| `MODEL_NAME` | Groq chat model | `qwen/qwen3.8-27b` |
| `DIM` | FAISS vector dimension | `384` |

`DIM` must match the dimension returned by the configured embedding model. The bundled `BAAI/bge-small-en-v1.5` configuration uses 384 dimensions.

The repository also contains `.env_demo` as a template, but replace every placeholder with a real value. In particular, `DIM` must be a number, not descriptive text.

## Application Configuration

Server and retrieval settings are stored in `config.ini`:

```ini
[server]
host = 127.0.0.1
port = 8000
reload = true

[parameter]
chunk_size = 300
chunk_overlap = 70
temperature = 0.4
top = 3
```

`main.py` currently reads the server settings. `app/user.py` reads `chunk_size`, `chunk_overlap`, and `temperature`. The `top` setting is present in `config.ini`.

## Running the Application

Start the application from the repository root so relative paths such as `data/`, `db/`, `uploads/`, and `static/` resolve correctly:

```powershell
uv run python main.py
```

The configured development server runs at:

```text
http://127.0.0.1:8000/
```

Open that URL in a browser. The application automatically serves the frontend from `static/index.html`.

For a direct Uvicorn launch:

```powershell
uv run uvicorn app.server.api:app --host 127.0.0.1 --port 8000 --reload
```

The `reload = true` setting is useful during development. Disable reload for a production-style process.

## Typical User Flow

1. Open the web application.
2. Click **New Chat**. This calls `POST /new_user` and returns a user ID.
3. Select a PDF and click **Upload PDF**.
4. The server extracts text, creates embeddings, and writes the user’s FAISS index.
5. Enter a question and click **Send**, or press Enter.
6. The server retrieves relevant chunks and sends them to the Groq model.
7. The question, answer, and timestamp are added to the user’s chat history.
8. Select a previous chat to load its history, or delete it with the trash button.

## API Reference

The backend is defined in `app/server/api.py`. Query parameters are used by the current frontend.

### `GET /`

Serves the frontend page.

### `GET /static/{path}`

Serves frontend assets such as CSS and JavaScript.

### `POST /new_user`

Creates and persists a new user.

Example response:

```json
{
	"message": "User created successfully",
	"user_id": "user_856ea176"
}
```

### `POST /upload?user_id={user_id}`

Uploads a PDF using a multipart form field named `file` and builds the user’s vector database.

PowerShell example:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/upload?user_id=user_856ea176" `
	-F "file=@C:\path\to\document.pdf"
```

### `POST /send?user_id={user_id}&query={question}`

Queries the selected user’s document.

```powershell
curl.exe -X POST "http://127.0.0.1:8000/send?user_id=user_856ea176&query=What%20is%20this%20document%20about?"
```

Example response:

```json
{
	"answer": "..."
}
```

### `GET /history?user_id={user_id}`

Returns the saved chat history:

```json
[
	{
		"query": "What is this document about?",
		"answer": "...",
		"timestamp": "2026-09-22 12:30:00"
	}
]
```

### `GET /all_users`

Lists user IDs based on the `.pkl` files found in `data/`:

```json
{
	"users": ["user_856ea176"]
}
```

### `DELETE /delete_chat?userid={user_id}`

Deletes the saved user object and the user’s `db/{user_id}/` vector directory.

```powershell
curl.exe -X DELETE "http://127.0.0.1:8000/delete_chat?userid=user_856ea176"
```

The current delete implementation does not remove the corresponding uploaded PDF from `uploads/`.

## Data and Persistence

Each user has state in several locations:

```text
data/{user_id}.pkl
db/{user_id}/vector.index
db/{user_id}/metadata.json
uploads/{filename}
```

- `data/{user_id}.pkl` stores the serialized `User` object, including chat history and paths.
- `db/{user_id}/vector.index` stores the FAISS index.
- `db/{user_id}/metadata.json` maps vector positions to extracted text chunks.
- `uploads/{filename}` stores the uploaded source PDF.

At startup, `/all_users` discovers IDs by scanning `data/`. Individual user objects are loaded when requested by an API route. The application also keeps loaded objects in the process-local `users` dictionary.

Do not load pickle files from untrusted sources. Python pickle deserialization can execute arbitrary code.

## Retrieval and Response Flow

```text
PDF upload
		-> PyMuPDF text extraction
		-> text chunking
		-> Hugging Face embeddings
		-> FAISS index + JSON metadata

User question
		-> Hugging Face query embedding
		-> FAISS nearest-neighbor search
		-> retrieved text context
		-> Groq chat model
		-> saved chat history
```

The current text chunking function accepts `chunk_overlap`, but reassigning the loop variable inside a Python `range` loop does not change the next range value. As a result, the configured overlap is not currently applied as intended.

## Troubleshooting

### `401`, `403`, or authentication errors

Check `HF_TOKEN` and `GROQ_API_KEY` in `.env`. Make sure the tokens are valid and available to the selected services.

### FAISS dimension errors

Make sure `DIM` matches the embedding model output. For `BAAI/bge-small-en-v1.5`, use `DIM=384`.

### The application cannot find files or folders

Start the server from the repository root. The application uses relative paths throughout the codebase.

### A question cannot be answered

Confirm that a readable, text-based PDF was uploaded successfully. Image-only PDFs do not currently have OCR support. Also check the server logs for embedding or Groq API errors.

### The browser cannot reach the API

The frontend uses a mixture of absolute URLs pointing to `http://localhost:8000` and relative URLs. Use the configured local server URL, or update `API_BASE_URL` and the relative requests consistently when deploying elsewhere.


