import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
import openai

# --- Config ---
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# --- Init ChromaDB ---
client = chromadb.Client()
collection = client.get_or_create_collection("knowledge_base")

# --- Step 1: Extract Text from File ---
def extract_text(file_path):
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        return [(i + 1, page.extract_text()) for i, page in enumerate(reader.pages) if page.extract_text()]
    
    elif file_path.endswith(".txt") or file_path.endswith(".md"):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            return [(1, text)]  # Treat entire file as "Page 1"
    else:
        raise ValueError("Unsupported file type")

# --- Step 2: Chunk Text ---
def chunk_text(pages):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunked = []

    for page_number, text in pages:
        chunks = splitter.split_text(text)
        for chunk in chunks:
            chunked.append((chunk, page_number))

    return chunked

# --- Step 3: Store in ChromaDB with Embeddings ---
def store_in_chromadb(chunks, filename, document_id):
    documents = []
    embeddings = []
    metadatas = []
    ids = []

    for i, (chunk, page_number) in enumerate(chunks):
        embedding = EMBEDDING_MODEL.encode(chunk, convert_to_numpy=True).tolist()
        documents.append(chunk)
        embeddings.append(embedding)
        metadatas.append({
            "source": filename,
            "page": page_number,
            "chunk_index": i,
            "document_id": document_id
        })
        ids.append(f"{document_id}-{i}")

    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

# --- Step 4: Retrieve Top-k Relevant Chunks ---
def retrieve_relevant_chunks(query, k=5):
    query_vector = EMBEDDING_MODEL.encode(query, convert_to_numpy=True).tolist()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=k,
        include=["documents", "metadatas"]
    )
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    return docs, metas

# --- Step 5: Prompt Construction for RAG ---
def build_prompt(context_chunks, question):
    context_text = "\n\n".join(context_chunks)
    prompt = f"""
        You are a helpful assistant. Use only the information from the context below to answer the question. 
        If the answer is not contained in the context, respond with "I'm not sure based on the provided information."

        Context:
        {context_text}

        Question: {question}
        Answer:
        """
    return prompt.strip()
