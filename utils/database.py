# utils/database.py
import psycopg2
import uuid
import psycopg2.extras

psycopg2.extras.register_uuid()  # Register UUID type support for psycopg2


def get_connection():
    return psycopg2.connect(
        dbname="postgres", user="postgres.ygqewtznptiefamevipk", password="95zzEjoEidDTyi3T", host="aws-0-ap-south-1.pooler.supabase.com")

# def init_db():
#     with get_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute("""
#                 CREATE EXTENSION IF NOT EXISTS vector;
#                 CREATE TABLE IF NOT EXISTS users (
#     id UUID PRIMARY KEY,
#     name TEXT NOT NULL,
#     email TEXT UNIQUE NOT NULL,
#     password_hash TEXT NOT NULL,
#     role TEXT NOT NULL,
#     class TEXT,
#     status TEXT DEFAULT 'active',
#     created_at TIMESTAMP DEFAULT now(),
#     updated_at TIMESTAMP DEFAULT now()
# );
#                 CREATE TABLE IF NOT EXISTS documents (
#     id UUID PRIMARY KEY,
#     file_name TEXT,
#     file_path TEXT,
#     class TEXT,
#     uploaded_by UUID,
#     status TEXT DEFAULT 'active',
#     created_at TIMESTAMP DEFAULT now(),
#     updated_at TIMESTAMP DEFAULT now()
# );
#                 CREATE TABLE IF NOT EXISTS document_chunks (
#     id UUID PRIMARY KEY,
#     document_id UUID,
#     chunk_text TEXT,
#     embedding vector(1536),
#     page_number INT,
#     status TEXT DEFAULT 'active',
#     created_at TIMESTAMP DEFAULT now(),
#     updated_at TIMESTAMP DEFAULT now()
# );
#                 CREATE INDEX IF NOT EXISTS chunk_vector_idx ON document_chunks USING ivfflat (embedding vector_cosine_ops);
#                 CREATE TABLE IF NOT EXISTS chats (
#     id UUID PRIMARY KEY,
#     user_id UUID,
#     title TEXT,
#     status TEXT DEFAULT 'active',
#     created_at TIMESTAMP DEFAULT now(),
#     updated_at TIMESTAMP DEFAULT now()
# );
#                 CREATE TABLE IF NOT EXISTS chat_messages (
#     id UUID PRIMARY KEY,
#     chat_id UUID REFERENCES chats(id),
#     question TEXT,
#     answer TEXT,
#     context_chunk_ids UUID[],
#     status VARCHAR DEFAULT 'active',
#     created_at TIMESTAMP DEFAULT now(),
#     updated_at TIMESTAMP DEFAULT now()
# );
#             """)
#             conn.commit()

def create_chat(user_id, title):
    chat_id = str(uuid.uuid4())
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO chats VALUES (%s, %s, %s)", (chat_id, user_id, title))
            conn.commit()
    return chat_id

def add_message(chat_id, question, answer, context_ids):
    msg_id = str(uuid.uuid4())
    # Convert string UUIDs to actual UUID type
    # ✅ Convert only if not already UUID
    # def normalize_id(x):
    #     if isinstance(x, uuid.UUID):
    #         return x
    #     try:
    #         return uuid.UUID(str(x))
    #     except Exception:
    #         raise ValueError(f"Invalid UUID: {x}")

    # uuid_list = [normalize_id(i) for i in context_ids]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO chat_messages (id, chat_id, question, answer)
                VALUES (%s, %s, %s, %s)
            """, (msg_id, chat_id, question, answer))
            conn.commit()

def get_chat_history(chat_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT question, answer FROM chat_messages WHERE chat_id=%s ORDER BY created_at ASC", (chat_id,))
            return [dict(zip(['question', 'answer'], row)) for row in cur.fetchall()]



def get_user_chats(user_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title FROM chats WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
            return [dict(zip(['id', 'title'], row)) for row in cur.fetchall()]
