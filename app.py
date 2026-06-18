import streamlit as st
import os
import tempfile
import base64
from google import genai
from google.genai import types

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Peshi / पेशी | Enterprise Legal Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed" 
)

# --- CLEAN CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Georgia&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #FDFDFD !important;
        color: #111111 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    h1, h2, h3 {
        font-family: 'Georgia', serif !important;
        color: #111111 !important;
        font-weight: 600 !important;
    }
    
    div.stButton > button:first-child {
        background-color: #111827 !important;
        color: #FDFDFD !important;
        border-radius: 4px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease-in-out !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #374151 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SYSTEM INSTRUCTION ---
PESHI_SYSTEM_INSTRUCTION = """
You are Peshi / पेशी, an elite enterprise-grade Legal AI utilized by top Indian law firms. 
Respond with supreme professionalism, citing specific pages and paragraphs.
Maintain strict chronological discipline and never invent facts.
"""

# --- INITIALIZE MEMORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "gemini_files" not in st.session_state:
    st.session_state.gemini_files = []
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = []
if "pdf_names" not in st.session_state:
    st.session_state.pdf_names = []
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None
if "last_timeline" not in st.session_state:
    st.session_state.last_timeline = None
if "stored_api_key" not in st.session_state:
    st.session_state.stored_api_key = ""

# --- HEADER ---
st.markdown("<h1>Peshi / पेशी <span style='font-family:Inter; font-size:16px; font-weight:400; color:#6B7280;'>| Enterprise Legal Intelligence</span></h1>", unsafe_allow_html=True)
st.divider()

# =====================================================================
# VIEW 1: ENTERPRISE DASHBOARD
# =====================================================================
if not st.session_state.gemini_files:
    dash_left, dash_right = st.columns([1.2, 1], gap="large")
    
    with dash_left:
        st.subheader("Firm Dashboard & Vault")
        st.write("Access recent matters, intelligence reports, and active workflows across your practice.")
        
        with st.container(border=True):
            st.caption("RECENT ACTIVE MATTERS")
            st.markdown("**Writ Petition (C) 402/2026** - M/s Sharma Builders vs. State of Rajasthan 🟢 *Analysis Complete*")
            st.divider()
            st.markdown("**Bail Application No. 1184** - NDPS Act - Sessions Court 🟠 *Timeline Pending*")
            st.divider()
            st.markdown("**Arbitration Appeal 22/2025** - Commercial Court, Mumbai 🟢 *Briefing Ready*")
            
    with dash_right:
        with st.container(border=True):
            st.subheader("Ingest New Matter")
            st.write("Upload Charge Sheets, FIRs, SLPs, Annexures, or complete case briefs.")
            
            api_key = st.text_input("Firm Infrastructure Key (Gemini API)", type="password", value=st.session_state.stored_api_key)
            if api_key != st.session_state.stored_api_key:
                st.session_state.stored_api_key = api_key

            uploaded_files = st.file_uploader("Drop legal PDFs here", type=["pdf"], accept_multiple_files=True)
            
            if st.button("Initialize Case Engine", use_container_width=True):
                if not st.session_state.stored_api_key:
                    st.error("Infrastructure Key required.")
                elif not uploaded_files:
                    st.warning("Please upload case documents.")
                else:
                    with st.spinner("Encrypting and indexing case records..."):
                        try:
                            client = genai.Client(api_key=st.session_state.stored_api_key)
                            st.session_state.gemini_files = [] 
                            st.session_state.pdf_bytes = []
                            st.session_state.pdf_names = []
                            
                            for file in uploaded_files:
                                file_data = file.read()
                                st.session_state.pdf_bytes.append(file_data)
                                st.session_state.pdf_names.append(file.name)
                                
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                                    tmp.write(file_data)
                                    tmp_path = tmp.name
                                uploaded_file = client.files.upload(file=tmp_path)
                                st.session_state.gemini_files.append(uploaded_file)
                                os.remove(tmp_path)
                            st.rerun() 
                        except Exception as e:
                            st.error(f"Ingestion fault: {e}")

# =====================================================================
# VIEW 2: ACTIVE MATTER COMMAND CENTER
# =====================================================================
else:
    pane_left, pane_center, pane_right = st.columns([1.5, 4.0, 3.5], gap="medium")

    # --- PANE 1: MATTER NAV ---
    with pane_left:
        with st.container(border=True):
            st.subheader("📂 Active Brief")
            st.caption("INDEXED RECORDS")
            for name in st.session_state.pdf_names:
                st.write(f"📄 {name}")
            
            st.divider()
            if st.button("Close Matter & Clear Memory", use_container_width=True):
                st.session_state.gemini_files = []
                st.session_state.pdf_bytes = []
                st.session_state.pdf_names = []
                st.session_state.last_analysis = None
                st.session_state.last_timeline = None
                st.session_state.messages = []
                st.rerun()

    # --- PANE 2: CENTER WORKSPACE ---
    with pane_center:
        doc_tab, timeline_tab = st.tabs(["📄 Document Viewer", "⏳ Chronology Engine"])
        
        with doc_tab:
            with st.container(border=True):
                st.subheader("Record Viewer")
                selected_doc_idx = st.selectbox("Select Document to Read:", range(len(st.session_state.pdf_names)), format_func=lambda x: st.session_state.pdf_names[x])
                
                if st.session_state.pdf_bytes:
                    base64_pdf = base64.b64encode(st.session_state.pdf_bytes[selected_doc_idx]).decode('utf-8')
                    pdf_display = f'<object data="data:application/pdf;base64,{base64_pdf}" type="application/pdf" width="100%" height="650px"><embed src="data:application/pdf;base64,{base64_pdf}" type="application/pdf" width="100%" height="650px" /></object>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
            
        with timeline_tab:
            with st.container(border=True):
                st.subheader("Master Chronology")
                if st.button("Extract Chronological Timeline", use_container_width=True):
                    with st.spinner("Crawling documents for dates and events..."):
                        try:
                            client = genai.Client(api_key=st.session_state.stored_api_key)
                            prompt = "Read the uploaded documents. Extract every single date mentioned and create a strict chronological timeline table. Format it as a Markdown table with columns: Date | Event | Page/Paragraph Citation."
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=[prompt] + st.session_state.gemini_files,
                                config=types.GenerateContentConfig(system_instruction=PESHI_SYSTEM_INSTRUCTION)
                            )
                            st.session_state.last_timeline = response.text
                        except Exception as e:
                            st.error(f"Error: {e}")
                
                if st.session_state.last_timeline:
                    st.markdown(st.session_state.last_timeline)

    # --- PANE 3: INTELLIGENCE BOARD ---
    with pane_right:
        with st.container(border=True):
            st.subheader("📊 Intelligence Board")
            
            if st.button("Execute Core Strategy Brief", use_container_width=True):
                with st.spinner("Synthesizing formal Briefing Memorandum..."):
                    try:
                        client = genai.Client(api_key=st.session_state.stored_api_key)
                        prompt = """
                        Generate a formal 'Case Briefing Memorandum' in the following format:
                        # Case Briefing Memorandum
                        ## 1. Executive Summary
                        [Concise overview of the dispute]
                        ## 2. Core Legal Issues
                        [Bulleted list of issues]
                        ## 3. Evidence Chronology Highlights
                        [Key events linked to page citations]
                        ## 4. Precedents & Strategic Risks
                        [Legal risks and recommended stance]
                        ## 5. Recommended Hearing Preparation Notes
                        [Actionable points for the counsel]
                        
                        Cite all claims with [Page X, Para Y]. Keep tone authoritative.
                        """
                        contents = [prompt] + st.session_state.gemini_files
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=contents,
                            config=types.GenerateContentConfig(system_instruction=PESHI_SYSTEM_INSTRUCTION)
                        )
                        st.session_state.last_analysis = response.text
                    except Exception as e:
                        st.error(f"Analysis fault: {e}")

            if st.session_state.last_analysis:
                st.divider()
                st.markdown(st.session_state.last_analysis)
                st.download_button(
                    label="📥 Download Briefing Memo (.txt)",
                    data=st.session_state.last_analysis,
                    file_name="Briefing_Memorandum.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            st.divider()
            st.caption("AGENTIC QUERY (English/Hinglish)")
            
            qa_container = st.container()
            with qa_container:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.write(msg['content'])
                        
            if prompt := st.chat_input("Query documents..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with qa_container:
                    with st.chat_message("user"): 
                        st.write(prompt)
                    with st.chat_message("assistant"):
                        try:
                            client = genai.Client(api_key=st.session_state.stored_api_key)
                            chat_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:]])
                            full_query = f"Context:\n{chat_context}\n\nQuestion: {prompt}"
                            reply = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=[full_query] + st.session_state.gemini_files,
                                config=types.GenerateContentConfig(system_instruction=PESHI_SYSTEM_INSTRUCTION)
                            )
                            st.write(reply.text)
                            st.session_state.messages.append({"role": "assistant", "content": reply.text})
                        except Exception as e:
                            st.error(f"Error: {e}")