import streamlit as st

def practice_questions_page():
    st.title(f"🧠 Practice Questions - {st.session_state.get('selected_chapter_title', '')}")

    if "generated_mcqs" not in st.session_state:
        st.warning("⚠️ No questions found.")
        return

    responses = {}
    all_answered = True

    # Check if the user has submitted properly (answered all)
    submitted = st.session_state.get("submit_clicked", False)
    valid_submission = st.session_state.get("valid_submission", False)

    for i, q in enumerate(st.session_state.generated_mcqs):
        q['question'] = q['question'].replace("**", "")
        st.markdown(f"### {q['question']}")

        option_items = [f"({key}) {val}" for key, val in q["options"].items()]
        selected_display = st.radio(
            label="Select an option",
            options=option_items,
            key=f"q{i}_selected",
            index=None
        )

        if selected_display:
            selected_key = selected_display[1]
            responses[i] = selected_key
        else:
            all_answered = False
            responses[i] = None

        # ✅ Only reveal answers if a full valid submission has happened
        if valid_submission:
            correct = q["correct"]
            explanation = q["explanation"]

            if responses[i] == correct:
                st.markdown(f"<span style='color:green;'>✅ Correct: ({correct}) {q['options'][correct]}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color:red;'>❌ Your Answer: ({responses[i]}) {q['options'].get(responses[i], 'Not selected')}</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:green;'>✅ Correct: ({correct}) {q['options'][correct]}</span>", unsafe_allow_html=True)

            st.markdown(f"**Explanation:** {explanation}")
            st.markdown("---")

    # ✅ Submission Logic
    if st.button("Submit Answers"):
        st.session_state.submit_clicked = True
        if not all_answered:
            st.session_state.valid_submission = False
            st.error("⚠️ Please answer all questions before submitting.")
        else:
            st.session_state.valid_submission = True
            st.rerun()

    if st.button("🔙 Back to Dashboard"):
        st.session_state.page_mode = "dashboard"
        st.session_state.submit_clicked = False
        st.session_state.valid_submission = False
        st.rerun()
