# # components/dashboard.py
# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns

# from utils.supabase_utils import get_document_record, download_pdf_from_supabase
# from components.mcq_generator import fetch_chapter_content, generate_mcqs, parse_mcq_output


# def student_dashboard_page():
#     df = pd.read_excel("D:\\Downloads\\Adjusted_Single_Student_Marksheet.xlsx")
#     df.columns = df.columns.str.strip()

#     chapter_columns = [col for col in df.columns if col not in ["Student", "Mock_Test", "Total Marks"]]

#     st.title("📊 Student Performance Dashboard for 10th Class Science Subject")
#     st.markdown("### 🧑 Student: Shubham")

#     col1, col2 = st.columns(2)
#     col3, col4 = st.columns(2)

#     with col1:
#         st.subheader("📈 Total Marks Over Tests")
#         fig1, ax1 = plt.subplots()
#         ax1.plot(df["Mock_Test"], df["Total Marks"], marker='o', linestyle='-', color='green')
#         ax1.set_xlabel("Test")
#         ax1.set_ylabel("Total Marks")
#         ax1.set_title("Performance Over Time")
#         ax1.grid(True)
#         st.pyplot(fig1)

#     with col2:
#         st.subheader("📊 Avg. Chapter Performance")
#         avg_scores = df[chapter_columns].mean().sort_values(ascending=False)
#         fig2, ax2 = plt.subplots(figsize=(6, 5))
#         sns.barplot(x=avg_scores.values, y=avg_scores.index, palette="coolwarm", ax=ax2)
#         ax2.set_title("Average Scores by Chapter")
#         ax2.set_xlabel("Avg Marks")
#         st.pyplot(fig2)

#     with col3:
#         st.subheader("🥧 Strong vs Weak")
#         thresh = avg_scores.mean()
#         strong = (avg_scores >= thresh).sum()
#         weak = (avg_scores < thresh).sum()
#         fig3, ax3 = plt.subplots()
#         ax3.pie([strong, weak], labels=["Strong", "Weak"], autopct="%1.1f%%", startangle=90, colors=["#4CAF50", "#FF5722"])
#         ax3.axis("equal")
#         st.pyplot(fig3)

#     selected_chapter = st.sidebar.selectbox("Select a Chapter", chapter_columns)

#     with col4:
#         st.subheader(f"🔍 {selected_chapter} Over Tests")
#         fig4, ax4 = plt.subplots()
#         ax4.plot(df["Mock_Test"], df[selected_chapter], marker='o', color='blue')
#         ax4.set_title(f"Scores in {selected_chapter}")
#         ax4.set_xlabel("Test")
#         ax4.set_ylabel("Marks")
#         ax4.grid(True)
#         st.pyplot(fig4)

#     st.markdown("---")
#     st.subheader("📄 Chapter Content & Practice")

#     # Get full record from Supabase
#     doc_info = get_document_record(selected_chapter)
#     print(f"\n\nDoc Info - {doc_info}")

#     if doc_info:
#         document_url = doc_info["document_url"]
#         file_name = doc_info["file_name"]
#         bucket_name = "letslearntogether"  # 🔁 use your bucket name here

#         st.markdown(f"#### [📄 Open PDF for {selected_chapter}]({document_url})")

#         if st.button("⬇️ Download PDF to Generate MCQs"):
#             local_path = f"downloads/{file_name}"
#             success = download_pdf_from_supabase(bucket_name, file_name, local_path)
#             if success:
#                 st.success(f"✅ PDF downloaded to: `{local_path}`")
#                 st.session_state.downloaded_pdf_path = local_path
#             else:
#                 st.error("❌ Failed to download PDF from Supabase.")

#         if "downloaded_pdf_path" in st.session_state:
#             st.info("PDF is ready for MCQ generation in the next step.")

#         if st.button("🧠 Generate Practice Questions"):
#             _, content = fetch_chapter_content(selected_chapter)
#             print(f"\n\nContent fetched from database ->{content}")
#             if content:
#                 raw = generate_mcqs(content, temperature=0.7)
#                 mcqs = parse_mcq_output(raw)
#                 st.session_state.generated_mcqs = mcqs
#                 st.session_state.selected_chapter_title = selected_chapter
#                 st.session_state.page_mode = "mcq_practice"
#                 st.rerun()
#     else:
#         st.warning("❌ No document mapping found for this chapter.")
        
# def practice_questions_page():
#     st.title(f"🧠 Practice Questions - {st.session_state.get('selected_chapter_title', '')}")
    
#     if "generated_mcqs" not in st.session_state:
#         st.warning("No questions available.")
#         return

#     responses = {}
#     submitted = st.button("Submit Answers")
#     print(st.session_state.generated_mcqs)
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
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from utils.supabase_utils import get_document_record, download_pdf_from_supabase
from components.mcq_generator import fetch_chapter_content, generate_mcqs, parse_mcq_output


def student_dashboard_page():
    st.title("📊 Student Performance Dashboard - Science 10th")
    st.markdown("### 🧑 Student: Shubham")

    csv_url = "https://raw.githubusercontent.com/shubhamjangid510/letslearn_v2/main/Updated_Chapter-Wise_Performance_Data.csv"

    df = pd.read_csv(csv_url)


    # Extract columns
    total_cols = [col for col in df.columns if col.startswith("Total_")]
    wrong_cols = [col for col in df.columns if col.startswith("Wrong_")]
    chapter_names = [col.replace("Wrong_", "") for col in wrong_cols]

    # Build performance summary
    chapter_summary = pd.DataFrame({
        "Chapter": chapter_names,
        "Total_Attempts": [df[f"Total_{ch}"].sum() for ch in chapter_names],
        "Total_Wrong": [df[f"Wrong_{ch}"].sum() for ch in chapter_names],
        "Total_Correct": [df[ch].sum() for ch in chapter_names],
    })
    chapter_summary["Accuracy (%)"] = (chapter_summary["Total_Correct"] / chapter_summary["Total_Attempts"] * 100).round(2)
    weak_df = chapter_summary[chapter_summary["Accuracy (%)"] < 60].sort_values(by="Accuracy (%)")
    strong_df = chapter_summary[chapter_summary["Accuracy (%)"] >= 60]

    # === Visual Area ===
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Chapter-wise Accuracy (%)")
        fig1, ax1 = plt.subplots(figsize=(6, 5))
        sns.barplot(data=chapter_summary.sort_values("Accuracy (%)"), x="Accuracy (%)", y="Chapter", palette="Blues", ax=ax1)
        ax1.set_xlim(0, 100)
        st.pyplot(fig1)

    with col2:
        st.subheader("🥧 Overall Correct vs Wrong")
        total_correct = chapter_summary["Total_Correct"].sum()
        total_wrong = chapter_summary["Total_Wrong"].sum()
        fig2, ax2 = plt.subplots()
        ax2.pie([total_correct, total_wrong], labels=["Correct", "Wrong"], colors=["#4CAF50", "#FF5252"],
                autopct="%1.1f%%", startangle=90)
        ax2.axis("equal")
        st.pyplot(fig2)

    # === Strong vs Weak Pie ===
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("💪 Strong vs Weak Chapters")
        fig3, ax3 = plt.subplots()
        ax3.pie([len(strong_df), len(weak_df)], labels=["Strong", "Weak"], colors=["#8BC34A", "#E91E63"],
                autopct="%1.0f%%", startangle=140)
        ax3.axis("equal")
        st.pyplot(fig3)

    with col4:
        st.subheader("📌 Weak Chapters Summary")
        for _, row in weak_df.iterrows():
            st.markdown(f"- **{row['Chapter']}** (Accuracy: {row['Accuracy (%)']}%)")

    st.markdown("---")
    st.markdown("### 🧠 Practice MCQs for Weak Chapters")

    # Dropdown limited to weak chapters
    weak_chapters = weak_df["Chapter"].tolist()
    if weak_chapters:
        selected_chapter = st.selectbox("Select a Weak Chapter", weak_chapters)

        doc_info = get_document_record(selected_chapter)
        if doc_info:
            file_name = doc_info["file_name"]
            document_url = doc_info["document_url"]
            bucket_name = "letslearntogether"

            st.markdown(f"[📄 Open Chapter PDF]({document_url})")

            if st.button("⬇️ Download PDF for Practice"):
                local_path = f"downloads/{file_name}"
                success = download_pdf_from_supabase(bucket_name, file_name, local_path)
                if success:
                    st.success("✅ PDF downloaded!")
                    st.session_state.downloaded_pdf_path = local_path

            if st.button("🧠 Generate Practice MCQs"):
                with st.spinner("Generating the MCQs and redirecting to you to the Practice Page as soon as the generation is complete."):
                    _, content = fetch_chapter_content(selected_chapter)
                    if content:
                        raw = generate_mcqs(content, temperature=0.7)
                        mcqs = parse_mcq_output(raw)
                        st.session_state.generated_mcqs = mcqs
                        st.session_state.selected_chapter_title = selected_chapter
                        st.session_state.page_mode = "mcq_practice"
                        st.rerun()
        else:
            st.warning("❌ No document mapping found for this chapter.")
    else:
        st.success("🎉 No weak chapters! Great performance.")
