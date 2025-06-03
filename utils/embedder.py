# utils/embedder.py
from openai import OpenAI
import fitz
import uuid
from utils.database import get_connection

from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def embed_and_store(filepath, filename, class_name, uploaded_by):
    doc_id = str(uuid.uuid4())
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO documents VALUES (%s, %s, %s, %s, %s)",
                        (doc_id, filename, filepath, class_name, uploaded_by))

            # Read and chunk PDF
            doc = fitz.open(filepath)
            for page in doc:
                text = page.get_text()
                chunks = [text[i:i+500] for i in range(0, len(text), 500)]
                for chunk in chunks:
                    emb = client.embeddings.create(input=chunk, model="text-embedding-ada-002").data[0].embedding
                    chunk_id = str(uuid.uuid4())
                    cur.execute("INSERT INTO document_chunks VALUES (%s, %s, %s, %s, %s)",
                                (chunk_id, doc_id, chunk, emb, page.number))
        conn.commit()