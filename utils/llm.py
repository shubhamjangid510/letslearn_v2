# utils/llm.py
from openai import OpenAI
import os 

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# def ask_llm(question, context, memory=[]):
#     # Get current date and day
#     now = datetime.now()
#     today_str = now.strftime("%A, %d %B %Y")

#        # Use last 10 messages (5 pairs) for chat history memory
#     chat_history = [m for m in memory if m['role'] in ['user', 'assistant']][-10:]
#     memory_prompt = ""
#     for i in range(0, len(chat_history), 2):
#         if i + 1 < len(chat_history):
#             user_msg = chat_history[i]['content']
#             assistant_msg = chat_history[i + 1]['content']
#             memory_prompt += f"\nQ{i//2+1}: {user_msg}\nA{i//2+1}: {assistant_msg}"
#         else:
#             memory_prompt += f"\nQ{i//2+1}: {chat_history[i]['content']}\nA{i//2+1}: [No response]"
    
#     print(f"Memory Creatd->{memory_prompt}")

#     system_prompt = f"""
#         You are LearnBot, an assistant that answers strictly based on the provided document context and the chat history memory.
#         Your name is LearnBot.

#         If a user greets you, respond with your name and optionally mention today's date ({today_str}).

#         You are not allowed to use any external or prior knowledge.
#         If the answer is not found in the provided content or the memory, respond:
#         "I'm sorry, I couldn't find that information. Can you please rephrase the question or ask a different question."

#         Do not speculate, assume, or generate filler content.
#     """

#     user_prompt = f"Chat History:\n{memory_prompt}\n\nDocument Context:\n{context}\n\nQuestion: {question}\nAnswer:"

#     completion = client.chat.completions.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system", "content": system_prompt.strip()},
#             {"role": "user", "content": user_prompt.strip()}
#         ]
#     )
#     return completion.choices[0].message.content.strip()



def ask_llm(question, context, memory=[]):
    now = datetime.now()
    today_str = now.strftime("%A, %d %B %Y")

    # Last 5 chat pairs (10 messages)
    chat_history = [m for m in memory if m['role'] in ['user', 'assistant']][-10:]
    memory_prompt = ""
    for i in range(0, len(chat_history), 2):
        if i + 1 < len(chat_history):
            memory_prompt += f"\nQ{i//2+1}: {chat_history[i]['content']}\nA{i//2+1}: {chat_history[i + 1]['content']}"
        else:
            memory_prompt += f"\nQ{i//2+1}: {chat_history[i]['content']}\nA{i//2+1}: [No response]"

    system_prompt = f"""
    You are LearnBot, an assistant that answers strictly based on the provided document context and the chat history memory.
    Your name is LearnBot.

    Today is {today_str}.

    Rules:
    - You must only answer based on the provided document chunks and memory.
    - If information is not found, say:
      "I'm sorry, I couldn't find that information. Can you please rephrase the question or ask a different question?"
    - When referencing a document chunk, always format the page number as a Markdown link: [Page X](URL). For example, say "See [Page 5](https://example.com/page5)".
    - Never invent information. Do not hallucinate, speculate, or generate unrelated content.
    """

    user_prompt = f"Chat History:\n{memory_prompt}\n\nDocument Context:\n{context}\n\nQuestion: {question}\nAnswer:"

    completion = client.chat.completions.create(
        model=os.environ["MODEL"],
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()}
        ]
    )

    return completion.choices[0].message.content.strip()



def reframe_question_with_memory(messages, current_question):
    from datetime import datetime
    client = OpenAI()
    today_str = datetime.now().strftime("%A, %d %B %Y")

    # Get last 5 user/assistant messages
    chat_history = [m for m in messages if m['role'] in ['user', 'assistant']][-10:]  # 5 pairs = 10 messages

    memory = "\n".join([
        f"{m['role'].capitalize()}: {m['content']}"
        for m in chat_history
    ])

    system_prompt = f"""You are a helpful assistant named LearnBot.
Do NOT answer. Your only task is to rewrite the user's question using the previous conversation as context.

If the question is already self-contained, keep it unchanged.
NEVER include an answer. Only return a clean, rewritten question."""

    user_prompt = f"""Conversation history:
{memory}

Current question:
{current_question}

Rewritten question (self-contained):"""

    completion = client.chat.completions.create(
        model=os.environ["MODEL"],
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()}
        ]
    )
    print(f"[REWRITTEN QUESTION] => {completion.choices[0].message.content.strip()}")


    return completion.choices[0].message.content.strip()