# utils/embedder.py
from openai import OpenAI
import fitz
import uuid
import os
import tiktoken
from dotenv import load_dotenv
from supabase import create_client
from utils.database import get_connection
from utils.utils import chunk_by_tokens

load_dotenv()

# Initialize OpenAI & Supabase clients
client = OpenAI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_NAME = "letslearntogether"

def upload_to_supabase(file_path, file_name):
    with open(file_path, "rb") as f:
        supabase.storage.from_(BUCKET_NAME).upload(file_name, f, {"content-type": "application/pdf"})
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{file_name}"

# def chunk_by_tokens(text, max_tokens=1000):
#     enc = tiktoken.get_encoding("cl100k_base")
#     tokens = enc.encode(text)
#     chunks = []
#     for i in range(0, len(tokens), max_tokens):
#         chunk_tokens = tokens[i:i+max_tokens]
#         chunk_text = enc.decode(chunk_tokens)
#         chunks.append(chunk_text)
#     return chunks

def embed_and_store(filepath, filename, class_name, uploaded_by):
    doc_id = str(uuid.uuid4())
    file_url = upload_to_supabase(filepath, filename)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO documents (id, file_name, file_path, document_url, class, uploaded_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (doc_id, filename, filepath, file_url, class_name, uploaded_by))

            doc = fitz.open(filepath)
            for page in doc:
                text = page.get_text()
                chunks = chunk_by_tokens(text, max_tokens=1000)
                for chunk in chunks:
                    emb = client.embeddings.create(input=chunk, model="text-embedding-ada-002").data[0].embedding
                    chunk_id = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO document_chunks (id, document_id, chunk_text, embedding, page_number)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (chunk_id, doc_id, chunk, emb, page.number + 1))  # +1 for user-friendly page number
        conn.commit()
