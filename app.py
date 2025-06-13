# streamlit_chatbot_app/main.py
import streamlit as st
from utils.auth import authenticate_user
from components.admin_upload import admin_upload_page
from components.student_chat import student_chat_page
from utils.database import get_chat_history


st.set_page_config(page_title="LearnBot", layout="wide", initial_sidebar_state="collapsed", page_icon="favicon.png")

# Initialize DB tables on startup
# init_db()

if 'user' not in st.session_state:
    st.session_state.user = None
    

if 'chat_id' not in st.session_state:
    st.session_state.chat_id = None
else:
    pass    



# Hide Streamlit default menu and footer

hide_streamlit_style = """

    <style>

    #MainMenu {visibility: hidden;}

    footer {visibility: hidden;}

    # header {visibility: hidden;}

    </style>

    """

st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# ---------- LOGIN LOGIC ----------
if not st.session_state.user:
    # Create 3 columns: empty | form | empty (centered layout)
    col1, col2, col3 = st.columns([2, 3, 2])
    
    with col2:
        st.title("📚 Let's Learn Together!!!")
        with st.form("login_form"):
            st.subheader("🔐 Login")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                user = authenticate_user(email, password)
                if user:
                    st.session_state.user = user
                    st.success(f"Welcome, {user['name']} ({user['role']})")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

# ---------- MAIN PAGES ----------
else:
    user = st.session_state.user
    
    #Sidebar Layout

    with st.sidebar:

        st.image("logo_png.png")

        st.markdown(f"### {user['name']}")
        if st.button("🔓 Logout"):
            st.session_state.user = None
            st.session_state.chat_id = None
            st.rerun()

        if user['role'] == 'student':

            if st.button("➕ New Chat"):

                st.session_state.chat_id = None
                st.session_state.messages=[]
                st.session_state.welcome_shown = False
                

                st.rerun()



            from utils.database import get_user_chats

            st.markdown("---")

            st.markdown("#### 🗂️ Your Chats")

            chats = get_user_chats(user['id'])

            for chat in chats:

                if st.button(chat['title'], key=chat['id']):

                    st.session_state.chat_id = chat['id']
                    st.session_state.messages = []

                    # 🔁 Load messages from DB for this chat
                    history = get_chat_history(chat['id'])
                    for msg in history:
                        st.session_state.messages.append({"role": "user", "content": msg["question"]})
                        st.session_state.messages.append({"role": "assistant", "content": msg["answer"]})

                    st.rerun()

    if user['role'] == 'admin':
        tab1, tab2 = st.tabs(["📤 Upload Documents", "📁 View Documents"])
        with tab1:
            admin_upload_page(user)
        with tab2:
            st.write("To be implemented: list and manage documents")

    elif user['role'] == 'student':
        student_chat_page(user)

    


# # pages/admin_upload.py
# import streamlit as st
# import uuid
# import os
# import tempfile
# from utils.embedder import embed_and_store

# UPLOAD_DIR = "data/uploads/"

# os.makedirs(UPLOAD_DIR, exist_ok=True)

# def admin_upload_page(user):
#     st.subheader("📤 Upload and Index Documents")
#     uploaded_file = st.file_uploader("Upload PDF or Text file", type=["pdf", "txt"])
#     class_selected = st.selectbox("Select Class", ["10th", "11th", "12th"])

#     if uploaded_file and st.button("Upload & Index"):
#         temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{uploaded_file.name}")
#         with open(temp_path, "wb") as f:
#             f.write(uploaded_file.read())

#         embed_and_store(temp_path, uploaded_file.name, class_selected, user['id'])
#         st.success(f"Document '{uploaded_file.name}' uploaded and indexed for class {class_selected}.")


# # pages/student_chat.py
# import streamlit as st
# import uuid
# from utils.vector_search import get_relevant_chunks
# from utils.llm import ask_llm
# from utils.database import create_chat, add_message, get_chat_history


# def student_chat_page(user):
#     st.subheader("💬 Chat with your ClassBot")
#     chat_id = st.session_state.get("chat_id")

#     if not chat_id:
#         chat_title = st.text_input("Enter a name for this chat:")
#         if st.button("Start Chat") and chat_title:
#             chat_id = create_chat(user['id'], chat_title)
#             st.session_state.chat_id = chat_id
#             st.rerun()

#     else:
#         chat_history = get_chat_history(chat_id)
#         for msg in chat_history:
#             with st.chat_message("user"):
#                 st.markdown(msg['question'])
#             with st.chat_message("assistant"):
#                 st.markdown(msg['answer'])

#         user_input = st.chat_input("Ask a question")
#         if user_input:
#             # Embed and retrieve relevant context
#             context_chunks = get_relevant_chunks(user_input, user['class'])
#             context_text = "\n".join(chunk['chunk_text'] for chunk in context_chunks)

#             # Ask LLM
#             answer = ask_llm(user_input, context_text)

#             # Store both messages
#             add_message(chat_id, user_input, answer, [chunk['id'] for chunk in context_chunks])

#             st.chat_message("user").markdown(user_input)
#             st.chat_message("assistant").markdown(answer)


# # utils/auth.py
# import psycopg2
# import hashlib
# from utils.database import get_connection

# def authenticate_user(email, password):
#     conn = get_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT id, name, email, role, class FROM users WHERE email=%s AND password_hash=%s",
#                 (email, hashlib.sha256(password.encode()).hexdigest()))
#     row = cur.fetchone()
#     cur.close()
#     conn.close()
#     if row:
#         return dict(zip(['id', 'name', 'email', 'role', 'class'], row))
#     return None


# # utils/database.py
# import psycopg2
# import uuid

# def get_connection():
#     return psycopg2.connect(
#         dbname="chatbotdb", user="postgres", password="postgres", host="localhost")

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
#     timestamp TIMESTAMP DEFAULT now(),
#     context_chunk_ids UUID[],
#     status TEXT DEFAULT 'active',
#     created_at TIMESTAMP DEFAULT now(),
#     updated_at TIMESTAMP DEFAULT now()
# );
#             """)
#             conn.commit()

# def create_chat(user_id, title):
#     chat_id = str(uuid.uuid4())
#     with get_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute("INSERT INTO chats VALUES (%s, %s, %s)", (chat_id, user_id, title))
#             conn.commit()
#     return chat_id

# def add_message(chat_id, question, answer, context_ids):
#     msg_id = str(uuid.uuid4())
#     with get_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute("""
#                 INSERT INTO chat_messages (id, chat_id, question, answer, context_chunk_ids)
#                 VALUES (%s, %s, %s, %s, %s)
#             """, (msg_id, chat_id, question, answer, context_ids))
#             conn.commit()

# def get_chat_history(chat_id):
#     with get_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute("SELECT question, answer FROM chat_messages WHERE chat_id=%s ORDER BY timestamp ASC", (chat_id,))
#             return [dict(zip(['question', 'answer'], row)) for row in cur.fetchall()]


# # utils/embedder.py
# from openai import OpenAI
# import fitz
# import uuid
# from utils.database import get_connection

# client = OpenAI()

# def embed_and_store(filepath, filename, class_name, uploaded_by):
#     doc_id = str(uuid.uuid4())
#     with get_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute("INSERT INTO documents VALUES (%s, %s, %s, %s, %s)",
#                         (doc_id, filename, filepath, class_name, uploaded_by))

#             # Read and chunk PDF
#             doc = fitz.open(filepath)
#             for page in doc:
#                 text = page.get_text()
#                 chunks = [text[i:i+500] for i in range(0, len(text), 500)]
#                 for chunk in chunks:
#                     emb = client.embeddings.create(input=chunk, model="text-embedding-ada-002").data[0].embedding
#                     chunk_id = str(uuid.uuid4())
#                     cur.execute("INSERT INTO document_chunks VALUES (%s, %s, %s, %s, %s)",
#                                 (chunk_id, doc_id, chunk, emb, page.number))
#         conn.commit()


# # utils/vector_search.py
# from utils.database import get_connection
# from openai import OpenAI
# client = OpenAI()

# def get_relevant_chunks(query, class_name):
#     emb = client.embeddings.create(input=query, model="text-embedding-ada-002").data[0].embedding
#     with get_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute("""
#                 SELECT id, chunk_text FROM document_chunks
#                 WHERE document_id IN (
#                     SELECT id FROM documents WHERE class = %s
#                 )
#                 ORDER BY embedding <=> %s
#                 LIMIT 5
#             """, (class_name, emb))
#             return [dict(zip(['id', 'chunk_text'], row)) for row in cur.fetchall()]


# # utils/llm.py
# from openai import OpenAI
# client = OpenAI()

# def ask_llm(question, context):
#     prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
#     completion = client.chat.completions.create(
#         model="gpt-4",
#         messages=[{"role": "system", "content": "You are a helpful assistant."},
#                   {"role": "user", "content": prompt}]
#     )
#     return completion.choices[0].message.content.strip()
