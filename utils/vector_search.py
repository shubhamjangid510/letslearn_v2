# utils/vector_search.py
from utils.database import get_connection
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np
from pgvector import Vector
from utils.llm import reframe_question_with_memory


from pgvector.psycopg2 import register_vector
from psycopg2 import sql

load_dotenv()

client = OpenAI()

# def get_relevant_chunks(query, class_name, messages=None):
    
#     if messages:
#         query = reframe_question_with_memory(messages, query)
        
#     emb = client.embeddings.create(input=query, model="text-embedding-ada-002").data[0].embedding
#     emb_vector = Vector(emb) 
#     with get_connection() as conn:
#         register_vector(conn)
#         with conn.cursor() as cur:
#             cur.execute("""
#                 SELECT id, chunk_text FROM document_chunks
#                 WHERE document_id IN (
#                     SELECT id FROM documents WHERE class = %s
#                 )
#                 ORDER BY embedding <=> (%s::vector)
#                 LIMIT 5
#             """, (class_name, emb_vector))
            
#             return [dict(zip(['id', 'chunk_text'], row)) for row in cur.fetchall()]

def get_relevant_chunks(query, class_name, messages=None):
    if messages:
        query = reframe_question_with_memory(messages, query)

    emb = client.embeddings.create(input=query, model="text-embedding-ada-002").data[0].embedding
    emb_vector = Vector(emb)

    with get_connection() as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    dc.id,
                    dc.chunk_text,
                    dc.page_number,
                    d.document_url
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                WHERE d.class = %s
                ORDER BY dc.embedding <=> (%s::vector)
                LIMIT 5
            """, (class_name, emb_vector))

            results = []
            for row in cur.fetchall():
                chunk_id, chunk_text, page_number, file_url = row
                page_link = f"{file_url}#page={page_number}"
                results.append({
                    "id": chunk_id,
                    "chunk_text": chunk_text,
                    "page_number": page_number,
                    "pdf_url": page_link
                })
            return results