# utils/llm.py
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def ask_llm(question, context):
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content.strip()