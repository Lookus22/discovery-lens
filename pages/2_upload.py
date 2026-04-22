"""Page 2 — File Upload"""
import streamlit as st

st.set_page_config(page_title="Upload — Discovery Lens", page_icon="📂", layout="wide")
st.title("📂 Upload your discovery files")

if not st.session_state.get("goal"):
    st.warning("Please set your product goal first.")
    st.stop()

st.markdown(f"**Product:** {st.session_state['product_name']}  \n**Goal:** {st.session_state['goal']}")
st.divider()

SOURCE_TYPES = ["interview", "review", "ticket", "usability"]
uploaded_files = st.file_uploader("Upload discovery files (PDF, DOCX, CSV, TXT)", type=["pdf", "docx", "csv", "txt"], accept_multiple_files=True)
source_type = st.selectbox("Source type for these files", options=SOURCE_TYPES)

if uploaded_files:
    st.info(f"{len(uploaded_files)} file(s) ready — tagged as **{source_type}**")
    if st.button("▶ Run pipeline", type="primary"):
        st.warning("Pipeline not yet implemented. Wire up pipeline/ modules here.")
