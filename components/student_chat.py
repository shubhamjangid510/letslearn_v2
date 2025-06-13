# # pages/student_chat.py
# import streamlit as st
# import uuid
# from utils.vector_search import get_relevant_chunks
# from utils.llm import ask_llm
# from utils.database import create_chat, add_message, get_chat_history


# def student_chat_page(user):
#     import streamlit as st
#     from utils.database import get_chat_history, create_chat, add_message
#     from utils.vector_search import get_relevant_chunks
#     from utils.llm import ask_llm

#     if "messages" not in st.session_state:
#         st.session_state.messages = []

#     chat_id = st.session_state.get("chat_id")

#     # Load chat history if selected from sidebar
#     if chat_id and not st.session_state.messages:
#         history = get_chat_history(chat_id)
#         for msg in history:
#             st.session_state.messages.append({"role": "user", "content": msg["question"]})
#             st.session_state.messages.append({"role": "assistant", "content": msg["answer"]})

#     # Display loaded messages
#     for msg in st.session_state.messages:
#         with st.chat_message(msg["role"]):
#             st.markdown(msg["content"])

#     # Accept new input
#     user_input = st.chat_input("Ask a question")
#     if user_input:
#         # Auto-create chat from first question
#         if not chat_id:
#             title = user_input[:200]
#             chat_id = create_chat(user["id"], title)
#             st.session_state.chat_id = chat_id
        
#         # Display user message instantly
#         st.chat_message("user").markdown(user_input)
        
#         with st.chat_message("assistant"):
#             with st.spinner("🧠 Generating response..."):
#                 messages = st.session_state.messages
#                 context_chunks = get_relevant_chunks(user_input, user["class"], messages)
#                 # context_text = "\n".join(chunk["chunk_text"] for chunk in context_chunks)
#                 context_text = "\n\n".join([
#                 f"{chunk['chunk_text']}\n(Source: Page {chunk['page_number']}, {chunk['pdf_url']})"
#                 for chunk in context_chunks
#             ])
#                 answer = ask_llm(user_input, context_text, messages)  # ⚡️ Can replace with streaming if needed
#                 st.markdown(answer)
#         st.session_state.messages.append({"role": "user", "content": user_input})
#         st.session_state.messages.append({"role": "assistant", "content": answer})

#         # answer = ask_llm(user_input, context_text)

#         # Store messages in DB
#         add_message(chat_id, user_input, answer, [chunk["id"] for chunk in context_chunks])

#         # Update in-memory messages
#         # st.session_state.messages.append({"role": "user", "content": user_input})

#         # # Display newly added messages
#         # st.chat_message("user").markdown(user_input)
#         # st.chat_message("assistant").markdown(answer)


#-----------------------------------------------------------------------------------------------------

# import streamlit as st
# import uuid
# import tempfile
# import openai
# from utils.vector_search import get_relevant_chunks
# from utils.llm import ask_llm
# from utils.database import create_chat, add_message, get_chat_history

# import speech_recognition as sr


# # openai.api_key = st.secrets["OPENAI_API_KEY"]

# def student_chat_page(user):
#     if "messages" not in st.session_state:
#         st.session_state.messages = []

#     chat_id = st.session_state.get("chat_id")

#     # Load chat history if selected from sidebar
#     if chat_id and not st.session_state.messages:
#         history = get_chat_history(chat_id)
#         for msg in history:
#             st.session_state.messages.append({"role": "user", "content": msg["question"]})
#             st.session_state.messages.append({"role": "assistant", "content": msg["answer"]})

#     # Display loaded messages
#     for msg in st.session_state.messages:
#         with st.chat_message(msg["role"]):
#             st.markdown(msg["content"])

#     # Chat input (always appears at bottom)
#     col1, col2 = st.columns([12, 1])
#     with col1:
#         user_input = st.chat_input("Ask a question")
#     with col2:
#         audio_value = st.audio_input("", label_visibility="collapsed", key="audio_input")

#     if audio_value and not user_input:
#         with st.spinner("🔄 Transcribing your voice..."):
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
#                 tmp.write(audio_value.read())
#                 tmp.flush()
#                 with open(tmp.name, "rb") as f:
#                     transcript = openai.audio.transcriptions.create(
#                         model="whisper-1",
#                         file=f
#                     )
#                     user_input = transcript.text

#     if user_input:
#         with st.chat_message("user"):
#             st.markdown(user_input)

#         if not chat_id:
#             title = user_input[:200]
#             chat_id = create_chat(user["id"], title)
#             st.session_state.chat_id = chat_id

#         with st.spinner("🧠 Generating response..."):
#             messages = st.session_state.messages
#             context_chunks = get_relevant_chunks(user_input, user["class"], messages)
#             context_text = "\n\n".join([
#                 f"{chunk['chunk_text']}\n(Source: Page {chunk['page_number']}, {chunk['pdf_url']})"
#                 for chunk in context_chunks
#             ])
#             answer = ask_llm(user_input, context_text, messages)

#         with st.chat_message("assistant"):
#             st.markdown(answer)

#         st.session_state.messages.append({"role": "user", "content": user_input})
#         st.session_state.messages.append({"role": "assistant", "content": answer})

#         add_message(chat_id, user_input, answer, [chunk["id"] for chunk in context_chunks])


## ------------------------------------------------------------------------------------------------------


import time
import streamlit as st
import os 
import uuid
import tempfile
import openai
from utils.vector_search import get_relevant_chunks
from utils.llm import ask_llm
from utils.database import create_chat, add_message, get_chat_history

from dotenv import load_dotenv

load_dotenv()

import speech_recognition as sr

def student_chat_page(user):
    chat_container_height = 630
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    if "welcome_shown" not in st.session_state:
        st.session_state.welcome_shown = False

    if "audio_key" not in st.session_state:
        st.session_state.audio_key = str(uuid.uuid4())  # dynamic key for resetting

    chat_id = st.session_state.get("chat_id")
    
    def stream_message_in_container(message, delay=0.00005):
        placeholder = st.empty()
        full_msg = ""

        for char in message:
            full_msg += char
            styled_html = f"""
                <div style="font-size: 20px; line-height: 1.6; font-weight: 500;">
                    {full_msg}
                </div>
            """
            placeholder.markdown(styled_html, unsafe_allow_html=True)
            time.sleep(delay)

        return full_msg
    
    if chat_id is None and not st.session_state.welcome_shown:
        chat_container_height = 520
        welcome_text = (
            "Hello! 👋 I’m LearnBot — your personal study companion.\n\n"
            "I’m here to help you learn effectively."
            "Ask me anything based on your study material, and I’ll guide you with precise, context-aware answers.\n\n"
            "Let’s get started! 🚀"
        )
        stream_message_in_container(welcome_text)
        st.session_state.welcome_shown = True
    


    # Load chat history if selected from sidebar
    if chat_id and not st.session_state.messages:
        history = get_chat_history(chat_id)
        for msg in history:
            st.session_state.messages.append({"role": "user", "content": msg["question"]})
            st.session_state.messages.append({"role": "assistant", "content": msg["answer"]})
    
            
    chat_container = st.container(height=chat_container_height, border=False)
    
    # Display loaded messages
    for msg in st.session_state.messages:
        with chat_container:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Chat input (always appears at bottom)
    # col1, col2 = st.columns([12, 1])
    # with col1:
    user_input = st.chat_input("Ask a question")
    # with col2:
    audio_value = st.audio_input(label = "Record Your Question by clicking on microphone button.", label_visibility="visible", key=st.session_state.audio_key)

    if audio_value and not user_input:
        with chat_container:
            with st.spinner("🗣️ Transcribing your Speech..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio_value.read())
                    tmp.flush()
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(tmp.name) as source:
                        audio = recognizer.record(source)
                    try:
                        user_input = recognizer.recognize_google(audio)
                    except sr.UnknownValueError:
                        st.error("Could not understand the audio.")
                        user_input = ""
                    except sr.RequestError as e:
                        st.error(f"Speech API error: {e}")
                        user_input = "Please Provide the question again."
                
                st.session_state.audio_key = str(uuid.uuid4())
                
                
        if not chat_id:
            title = user_input[:200]
            chat_id = create_chat(user["id"], title)
            st.session_state.chat_id = chat_id

    if user_input:
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)

        if not chat_id:
            title = user_input[:200]
            chat_id = create_chat(user["id"], title)
            st.session_state.chat_id = chat_id
        
        with chat_container:
            with st.spinner("🧠 Generating response..."):
                messages = st.session_state.messages
                context_chunks = get_relevant_chunks(user_input, user["class"], messages)
                context_text = "\n\n".join([
                    f"{chunk['chunk_text']}\n(Source: Page {chunk['page_number']}, {chunk['pdf_url']})"
                    for chunk in context_chunks
                ])
                answer = ask_llm(user_input, context_text, messages)
            
        with chat_container:
            with st.chat_message("assistant"):
                st.markdown(answer)

        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": answer})

        add_message(chat_id, user_input, answer, [chunk["id"] for chunk in context_chunks])

###------------------------------------------------------------------------------------------------------------------------------
