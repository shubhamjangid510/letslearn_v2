# pages/admin_upload.py
import streamlit as st
import uuid
import os
import tempfile
from utils.embedder import embed_and_store

UPLOAD_DIR = "data/uploads/"

os.makedirs(UPLOAD_DIR, exist_ok=True)

def admin_upload_page(user):
    st.subheader("📤 Upload and Index Documents")
    uploaded_file = st.file_uploader("Upload PDF or Text file", type=["pdf", "txt"])
    class_selected = st.selectbox("Select Class", ["10th", "11th", "12th"])

    if uploaded_file and st.button("Upload & Index"):
        temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{uploaded_file.name}")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())

        embed_and_store(temp_path, uploaded_file.name, class_selected, user['id'])
        st.success(f"Document '{uploaded_file.name}' uploaded and indexed for class {class_selected}.")
