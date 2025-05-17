import streamlit as st
import time
import requests

st.set_page_config(page_title="📄 Doc Chat", layout="centered")
st.title("📄 Document Chat Assistant")

# Section 1: Ingest PDFs
with st.expander("📥 Ingest PDF Documents", expanded=True):
    st.write("Upload one or more PDF files to ingest and embed them.")
    files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)
    if st.button("Ingest"):
        if not files:
            st.warning("Please upload at least one PDF file.")
        else:
            st.write("Uploading...")
            files_data = [("files", (f.name, f.getvalue(), "application/pdf")) for f in files]
            try:
                res = requests.post("http://localhost:8000/ingest", files=files_data)
                if res.status_code == 200:
                    st.markdown(f"**Status:** {res.json().get('message', 'Success')}")
                else:
                    st.error(f"Failed to upload files. Status code: {res.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")

# Section 2: Single Question Answering
with st.expander("❓ Ask a Single Question", expanded=True):
    q = st.text_input("Ask a question:")
    if st.button("Get Answer"):
        if not q:
            st.warning("Please enter a question.")
        else:
            try:
                res = requests.post("http://localhost:8000/chat_answer", json={"question": q})
                if res.status_code == 200:
                    st.markdown(f"**Answer:** {res.json().get('answer', 'No answer returned.')}")
                else:
                    st.error(f"Failed to get answer. Status code: {res.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")

# Section 3: Batch Question Answering
with st.expander("📂 Batch Question Answering (Upload JSON)", expanded=True):
    multi_q_file = st.file_uploader("Upload JSON with multiple questions", type=["json"])

    if st.button("Submit Questions from File") and multi_q_file:
        res = requests.post(
                "http://localhost:8000/batch_answer",
                files={"file": (multi_q_file.name, multi_q_file, "application/json")}
            )
        st.download_button("Download Answers", data=res.content, file_name="answers.json", mime="application/json")