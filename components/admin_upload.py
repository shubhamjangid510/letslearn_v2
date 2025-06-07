# # pages/admin_upload.py
# import streamlit as st
# import uuid
# import os
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


import os
import uuid
import streamlit as st
from utils.embedder import embed_and_store

UPLOAD_DIR = "data/uploads/"

os.makedirs(UPLOAD_DIR, exist_ok=True)

def admin_upload_page(user):
    st.subheader("📤 Upload and Index Documents")

    uploaded_files = st.file_uploader(
        "Upload PDF or Text files", 
        type=["pdf", "txt"], 
        accept_multiple_files=True
    )

    class_selected = st.selectbox("Select Class", ["10th", "11th", "12th"])

    if uploaded_files and st.button("Upload & Index All"):
        for uploaded_file in uploaded_files:
            file_placeholder = st.empty()  # Reserve space for status
            with file_placeholder.container():
                st.write(f"🔄 Processing: **{uploaded_file.name}**")

            temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{uploaded_file.name}")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())

            try:
                with st.spinner(f"Indexing '{uploaded_file.name}'..."):
                    embed_and_store(temp_path, uploaded_file.name, class_selected, user['id'])
                file_placeholder.success(f"✅ Done: **{uploaded_file.name}** uploaded and indexed.")
            except Exception as e:
                file_placeholder.error(f"❌ Failed: **{uploaded_file.name}** - {e}")
