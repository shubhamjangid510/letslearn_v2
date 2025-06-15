import streamlit as st
from supabase import create_client
import os
from openai import OpenAI

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

client = OpenAI()

def fetch_chapter_content(chapter_name, page_range=None):
    # 1. Get document_id for chapter
    doc_res = supabase.table("documents").select("id").eq("chapter_name", chapter_name).execute()
    if not doc_res.data:
        return None, None
    document_id = doc_res.data[0]["id"]

    # 2. Get all chunks for that document
    chunk_query = supabase.table("document_chunks").select("*").eq("document_id", document_id)
    if page_range:
        chunk_query = chunk_query.in_("page_num", page_range)

    chunks_res = chunk_query.execute()
    if not chunks_res.data:
        return document_id, None

    # Join content
    chunks = sorted(chunks_res.data, key=lambda x: x["page_number"])
    joined_text = "\n".join([f"[Page {c['page_number']}]\n{c['chunk_text']}" for c in chunks])
    # print(joined_text)
    return document_id, joined_text


def generate_mcqs(content, temperature=0.7):
    prompt = f"""
You are an expert education assistant. Based on the content below, generate 10 multiple-choice questions.

For each question:
- Start with a single line question like: **Q1. What is...?**
- Give four options in this format:
  (a) Option A
  (b) Option B ✅
  (c) Option C
  (d) Option D
- Mark the correct option with ✅.
- On a new line, start with **Explanation:** followed by a 1-line explanation.
- Separate each question block using only a line with three dashes: `---`

Content:
\"\"\"
{content}
\"\"\"
"""
    response = client.chat.completions.create(
        model=os.environ["MODEL"],
        messages=[
            {"role": "user", "content": prompt.strip()}
        ]
    )

    usage = response.usage

    return response.choices[0].message.content.strip()



def parse_mcq_output(raw_output):
    import re

    questions = []
    blocks = re.split(r"\n\s*---\s*\n", raw_output.strip())  # separate by '---'

    for block in blocks:
        lines = block.strip().split("\n")
        question_text = ""
        options = {}
        correct = None
        explanation = ""

        # Extract question
        for i, line in enumerate(lines):
            if re.match(r"^\*\*?Q\d+\.\**?\s*", line.strip(), re.IGNORECASE):
                question_text = re.sub(r"^\*\*?Q\d+\.\**?\s*", "", line.strip("**")).strip()
                lines = lines[i+1:]
                break

        # Extract options
        for line in lines:
            opt_match = re.match(r"\(?([a-d])\)?\s*[\.\)]?\s*(.+)", line.strip())
            if opt_match:
                key, val = opt_match.groups()
                if "✅" in val:
                    correct = key
                    val = val.replace("✅", "").strip()
                options[key] = val.strip()

        # Extract explanation
        for line in lines:
            if "Explanation" in line:
                explanation = re.sub(r"^.*Explanation\s*[:\-]?\s*", "", line, flags=re.IGNORECASE).strip()
                break

        if question_text and options and correct:
            questions.append({
                "question": question_text,
                "options": options,
                "correct": correct,
                "explanation": explanation
            })

    return questions


# def mcq_generator_page():
#     st.title(f"🧠 Practice Questions - {st.session_state.get('selected_chapter_title', '')}")
    
#     if "generated_mcqs" not in st.session_state:
#         st.warning("No questions available.")
#         return

#     responses = {}
#     submitted = st.button("Submit Answers")

#     for i, q in enumerate(st.session_state.generated_mcqs):
#         st.markdown(f"**Q{i+1}. {q['question']}**")
#         selected = st.radio(
#             f"Select an option for Q{i+1}",
#             options=["a", "b", "c", "d"],
#             key=f"q{i}_selected",
#             label_visibility="collapsed"
#         )
#         responses[i] = selected

#         if submitted:
#             correct = q["correct"]
#             explanation = q["explanation"]

#             if selected == correct:
#                 st.markdown(f"<span style='color:green;'>✅ Correct: ({correct}) {q['options'][correct]}</span>", unsafe_allow_html=True)
#             else:
#                 st.markdown(f"<span style='color:red;'>❌ Your Answer: ({selected}) {q['options'][selected]}</span>", unsafe_allow_html=True)
#                 st.markdown(f"<span style='color:green;'>✅ Correct: ({correct}) {q['options'][correct]}</span>", unsafe_allow_html=True)

#             st.markdown(f"**Explanation:** {explanation}")
#             st.markdown("---")

#     if submitted:
#         st.success("✅ Submitted!")

#     if st.button("🔙 Back to Dashboard"):
#         st.session_state.page_mode = "dashboard"
#         st.rerun()
