import math
from datetime import datetime
import streamlit as st
from src.mcqgen.mcq_generator import generate_mcq
from src.mcqgen.utils import download_as_word
from src.mcqgen.logger import logging

# Custom CSS for button color
st.markdown("""
    <style>
    div.stDownloadButton > button:first-child {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 16px;
    }
    div.stDownloadButton > button:first-child:hover {
        background-color: #45a049;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for num_rows, page, and results
if "num_rows" not in st.session_state:
    st.session_state.num_rows = 1
if "page" not in st.session_state:
    st.session_state.page = 1
if "results" not in st.session_state:
    st.session_state.results = {}

st.title("MCQ Generator App")
st.write(""*2)

# Add Row button (above form)
if st.button("➕ Add Row"):
    st.session_state.num_rows += 1

with st.form("user_inputs", clear_on_submit=False):
    # First row layout
    
    col1, col2, col3, col4 = st.columns([6, 6, 4, 3])
    with col1:
        subject = st.text_input("Topic", placeholder="Enter topic for MCQs", label_visibility="visible")
    with col2:
        quiz_tone = st.pills("Tone", ["easy", "medium", "hard"], selection_mode="multi")
    with col3:
        mcq_count = st.number_input("Count", min_value=1, max_value=50)
    with col4:
        st.write("")
        recent_data = st.toggle("Recent", value=False)

    # Additional rows
    for i in range(1, st.session_state.num_rows):
        col1, col2, col3, col4 = st.columns([6, 6, 4, 3])
        with col1:
            st.text_input("Topic", placeholder="Enter topic for MCQs", key=f"topic_{i}")
        with col2:
            st.pills("Tone", ["easy", "medium", "hard"], selection_mode="multi", key=f"tone_{i}")
        with col3:
            st.number_input("Count", min_value=1, max_value=50, key=f"count_{i}")
        with col4:
            st.write("")
            st.toggle("Recent", value=False, key=f"recent_{i}")

    # Final generate button
    generate = st.form_submit_button("🚀 Generate MCQs")

if generate:
    try:
        # Reset pagination
        st.session_state.page = 1

        with st.spinner("Processing..."):
            # Collect all inputs into topics_list
            topics_list = [{
                "topic": subject,
                "difficulty": ", ".join([t.capitalize() for t in quiz_tone]) if quiz_tone else "",
                "count": mcq_count,
                "recent": recent_data
            }]
            
            for i in range(st.session_state.num_rows):
                topic = st.session_state.get(f"topic_{i}", "").strip()
                tone = st.session_state.get(f"tone_{i}", [])
                count = st.session_state.get(f"count_{i}", 0)
                recent = st.session_state.get(f"recent_{i}", False)
                if topic:
                    topics_list.append({
                        "topic": topic,
                        "difficulty": ", ".join([t.capitalize() for t in tone]) if tone else "",
                        "count": count,
                        "recent": recent
                    })

            # Save results in session state
            st.session_state.results = generate_mcq(topics_list)
    except Exception as e:
        logging.error(f"Error: {e}")

# ---------------- Pagination + Display ---------------- #
# After pagination block
if st.session_state.results:
    try:
        result = st.session_state.results
        per_page = 5
        total_questions = len(result)
        logging.info(f"Total questions generated: {total_questions}")
        total_pages = math.ceil(total_questions / per_page)

        # Clamp page number within range
        st.session_state.page = max(1, min(st.session_state.page, total_pages))

        start_idx = (st.session_state.page - 1) * per_page
        end_idx = start_idx + per_page
        current_items = list(result.items())[start_idx:end_idx]

        st.subheader(f"📘 Showing {start_idx+1} - {min(end_idx, total_questions)} of {total_questions} Questions")

        # Display MCQs
        for qid, data in current_items:
            with st.container():
                st.markdown(
                    """
                    <div style="padding:15px; margin-bottom:20px; border-radius:12px; 
                                background-color:#f9f9f9; box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(f"### Q{qid}. {data['mcq']}")
                st.markdown(
                    f"<p style='color:#555;'><b>Topic:</b> {data['Topic']} &nbsp; | &nbsp; "
                    f"<b>Difficulty:</b> {data['Difficulty']}</p>",
                    unsafe_allow_html=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)

                for opt, text in data['options'].items():
                    st.markdown(f"- **{opt})** {text}")

                with st.expander("✅ Show Answer & Explanation"):
                    answer_key = data['Answer'].lower().strip()
                    answer_text = data['options'].get(answer_key, "Not found")
                    st.markdown(f"**Answer:** {answer_key}) {answer_text}")
                    st.markdown(f"**Explanation:** {data['Explanation']}")

                st.markdown("---")

        # Pagination controls
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("⬅️ Previous") and st.session_state.page > 1:
                st.session_state.page -= 1
                st.rerun()

        with col3:
            if st.button("Next ➡️") and st.session_state.page < total_pages:
                st.session_state.page += 1
                st.rerun()

        with col2:
            st.markdown(
                f"<p style='text-align:center;'>Page {st.session_state.page} of {total_pages}</p>",
                unsafe_allow_html=True,
            )

        # ---------------- Download Button ---------------- #
        # Generate datetime-based filename
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"MCQ_Questions_{current_time}.docx"

        # Download button
        st.markdown("### 📥 Download")
        doc_file = download_as_word(result)
        st.download_button(
            label="⬇️ Download as Word Document",
            data=doc_file,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        st.error(f"Error displaying results: {e}")
        logging.error(f"Error displaying results: {e}")
