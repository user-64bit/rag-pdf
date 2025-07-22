# Knowledge Assistant

A Django-based API that allows users to upload PDF or text documents and ask questions about their content using Retrieval-Augmented Generation (RAG) with OpenAI and ChromaDB.

## Features

- **Upload Documents**: Upload PDF or text files via the `/upload/` endpoint.
- **Ask Questions**: Query the content of uploaded documents using the `/ask-question/` endpoint.
- **Contextual Answers**: Answers are generated using relevant document chunks, with sources cited.
- **Web Upload Form**: Simple HTML form for uploading files.

## How It Works

1. **Upload**: Users upload PDF or text files. The system extracts text, splits it into chunks, generates embeddings, and stores them in ChromaDB.
2. **Ask**: Users ask questions. The system retrieves the most relevant chunks, constructs a prompt, and queries OpenAI’s API for an answer, citing sources.

## Endpoints

### 1. `/upload/` (POST)

- **Description**: Upload one or more PDF or text files.
- **Request**: `multipart/form-data` with `file` field (can be multiple).
- **Response**: JSON with upload status for each file.

**Example using `curl`:**
```bash
curl -F "file=@yourfile.pdf" http://127.0.0.1:8000/upload/
```

### 2. `/ask-question/` (POST)

- **Description**: Ask a question about the uploaded documents.
- **Request**: JSON body with a `question` field.
- **Response**: JSON with the answer and sources.

**Example using `curl`:**
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"question": "What is the main topic of the document?"}' \
     http://127.0.0.1:8000/ask-question/
```

## Web Upload Form

A simple HTML form (`upload.html`) is provided for manual uploads:
```html
<form method="POST" enctype="multipart/form-data" action="http://127.0.0.1:8000/upload/">
  <input type="file" name="file" multiple>
  <button type="submit">Upload</button>
</form>
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd knowledge_assistant
```

### 2. Install Dependencies

It’s recommended to use a virtual environment.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set Environment Variables

Create a `.env` file in the root directory and add your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Start the Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

## Project Structure

```
knowledge_assistant/
├── api/
│   ├── views.py         # API endpoints for upload and question answering
│   ├── utils.py         # Text extraction, chunking, embedding, retrieval
│   ├── models.py        # UploadedDocument model
│   ├── serializers.py   # Serializers for API responses
│   └── ...
├── knowledge_assistant/
│   ├── settings.py      # Django settings
│   └── ...
├── upload.html          # Simple file upload form
├── requirements.txt     # Python dependencies
└── manage.py
```

## Dependencies

- Django
- Django REST Framework
- PyPDF2
- langchain
- sentence-transformers
- chromadb
- openai
- (See `requirements.txt` for full list)

## Notes

- Only PDF and text (`.txt`, `.md`) files are supported.
- Answers are generated using OpenAI’s GPT models and are limited to the context of uploaded documents.
- ChromaDB is used for vector storage and retrieval.
