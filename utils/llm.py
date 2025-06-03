# utils/llm.py
from openai import OpenAI

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def ask_llm(question, context):
    
     # Get current date and day
    now = datetime.now()
    today_str = now.strftime("%A, %d %B %Y") 
    system_prompt = f"""
                You are LearnBot, an assistant that answers strictly based on the provided context only.
                Your name is LearnBot.
                If a user asks for a greeting or date, include today's date ({today_str}) and introduce yourself as LearnBot.

                You are not allowed to use any external or prior knowledge.
                If the answer is not found in the provided content, respond:
                "I'm sorry, I couldn't find that information. Can you please rephrase the question or ask a different question."

                Do not speculate, assume, or generate filler content.
"""
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": system_prompt.strip()},
                  {"role": "user", "content": user_prompt.strip()}]
    )
    print(f"Sysmtm message->{system_prompt}")
    print(f"\n\n-------\n\nuser [promt->{user_prompt}--------------\n\n]")
    return completion.choices[0].message.content.strip()