# pages/student_chat.py
import streamlit as st
import uuid
from utils.vector_search import get_relevant_chunks
from utils.llm import ask_llm
from utils.database import create_chat, add_message, get_chat_history


def student_chat_page(user):
    import streamlit as st
    from utils.database import get_chat_history, create_chat, add_message
    from utils.vector_search import get_relevant_chunks
    from utils.llm import ask_llm

    if "messages" not in st.session_state:
        st.session_state.messages = []

    chat_id = st.session_state.get("chat_id")

    # Load chat history if selected from sidebar
    if chat_id and not st.session_state.messages:
        history = get_chat_history(chat_id)
        for msg in history:
            st.session_state.messages.append({"role": "user", "content": msg["question"]})
            st.session_state.messages.append({"role": "assistant", "content": msg["answer"]})

    # Display loaded messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Accept new input
    user_input = st.chat_input("Ask a question")
    if user_input:
        # Auto-create chat from first question
        if not chat_id:
            title = user_input[:200]
            chat_id = create_chat(user["id"], title)
            st.session_state.chat_id = chat_id
        
        # Display user message instantly
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("assistant"):
            with st.spinner("🧠 Generating response..."):
                context_chunks = get_relevant_chunks(user_input, user["class"])
                context_text = "\n".join(chunk["chunk_text"] for chunk in context_chunks)
                answer = ask_llm(user_input, context_text)  # ⚡️ Can replace with streaming if needed
                st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

        # answer = ask_llm(user_input, context_text)

        # Store messages in DB
        add_message(chat_id, user_input, answer, [chunk["id"] for chunk in context_chunks])

        # Update in-memory messages
        # st.session_state.messages.append({"role": "user", "content": user_input})

        # # Display newly added messages
        # st.chat_message("user").markdown(user_input)
        # st.chat_message("assistant").markdown(answer)


