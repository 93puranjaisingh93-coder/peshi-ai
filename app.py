import streamlit as st
import os
import tempfile
from google import genai
from google.genai import types

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Peshi AI | Court-Grade Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SYSTEM INSTRUCTION (HARDENED) ---
PESHI_SYSTEM_INSTRUCTION = """
You are Peshi, an elite Court-Grade Legal Document Intelligence System. You are not a chatbot; you are a Senior Legal Analyst.

--- HARD NEGATIVE CONSTRAINTS ---
1. NO RIGID CLASSIFICATION: Do not force documents into specific case types. Handle all domains fluidly.
2. NO HALLUCINATION: If a fact, date, or outcome is not explicitly found in the provided documents, you MUST state "Not found in documents." Do not speculate.
3. NO BLIND REPETITION: Every case is unique. Do not blindly copy-paste report formats.
4. NO TIMELINE NEGLECT: Chronology is the core of legal intelligence. Always maintain a strict, precise, and sequential timeline.

--- MANDATORY BEHAVIORS ---
1. EXPLICIT UNCERTAINTY: If documents are ambiguous, be explicit about the uncertainty.
2. MULTI-LINGUAL: Understand English, Hindi, and Hinglish. Reply in the same language/tone as the user.
3. CITATION: Every factual claim must be backed by a reference (e.g., [Page X, Para Y]).
4. STRENGTH ASSESSMENT: NEVER predict the "final outcome" or state who "will win." Instead, frame your analysis as a "Case Strength Assessment" based on evidence, precedents, and procedural validity. Use objective language like "High probability of relief" or "Significant procedural hurdles."
"""

# --- SESSION MEMORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "gemini_files" not in st.session_state:
    st.session_state.gemini_files = []
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None

# --- UI: SIDEBAR ---
with st.sidebar:
    st.header("📂 Peshi Data Ingestion")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.markdown("---")
    uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)
    
    if st.button("Process & Cache Files"):
        if not api_key:
            st.error("API Key required.")
        elif not uploaded_files:
            st.warning("Upload PDFs first.")
        else:
            with st.spinner("Caching files for Peshi..."):
                try:
                    client = genai.Client(api_key=api_key)
                    st.session_state.gemini_files = [] 
                    for file in uploaded_files:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            tmp.write(file.read())
                            tmp_path = tmp.name
                        uploaded_file = client.files.upload(file=tmp_path)
                        st.session_state.gemini_files.append(uploaded_file)
                        os.remove(tmp_path)
                    st.success("Documents ready.")
                except Exception as e:
                    st.error(f"Upload error: {e}")

# --- UI: MAIN ---
st.title("⚖️ Peshi: Court-Grade Legal Intelligence")
col1, col2 = st.columns([1.2, 1])

# Column 1: Analysis
with col1:
    st.subheader("📊 Strategic Blueprint")
    if st.button("Generate Full 12-Section Analysis", type="primary"):
        if not st.session_state.gemini_files:
            st.error("Upload files first.")
        else:
            with st.spinner("Peshi is analyzing..."):
                try:
                    client = genai.Client(api_key=api_key)
                    contents = ["Generate the full legal blueprint report, citing [Page X, Para Y] for every point."] + st.session_state.gemini_files
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contents,
                        config=types.GenerateContentConfig(system_instruction=PESHI_SYSTEM_INSTRUCTION)
                    )
                    st.session_state.last_analysis = response.text
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Analysis error: {e}")

    if st.session_state.last_analysis:
        st.download_button(
            label="📄 Download Analysis as Text/Report",
            data=st.session_state.last_analysis,
            file_name="Peshi_Legal_Report.txt",
            mime="text/plain"
        )

# Column 2: Chat
with col2:
    st.subheader("💬 Continuous Q&A")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Ask anything (Hinglish/Hindi/English)..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
            
        if not st.session_state.gemini_files:
            st.warning("Upload files first.")
        else:
            with st.chat_message("assistant"):
                try:
                    client = genai.Client(api_key=api_key)
                    chat_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:]])
                    full_query = f"Context:\n{chat_context}\n\nQuestion: {prompt}"
                    
                    reply = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[full_query] + st.session_state.gemini_files,
                        config=types.GenerateContentConfig(system_instruction=PESHI_SYSTEM_INSTRUCTION)
                    )
                    st.markdown(reply.text)
                    st.session_state.messages.append({"role": "assistant", "content": reply.text})
                except Exception as e:
                    st.error(f"Error: {e}")