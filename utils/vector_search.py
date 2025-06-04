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

def get_relevant_chunks(query, class_name, messages=None):
    
    if messages:
        query = reframe_question_with_memory(messages, query)
        
    emb = client.embeddings.create(input=query, model="text-embedding-ada-002").data[0].embedding
    emb_vector = Vector(emb) 
    with get_connection() as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, chunk_text FROM document_chunks
                WHERE document_id IN (
                    SELECT id FROM documents WHERE class = %s
                )
                ORDER BY embedding <=> (%s::vector)
                LIMIT 5
            """, (class_name, emb_vector))
            
            return [dict(zip(['id', 'chunk_text'], row)) for row in cur.fetchall()]
