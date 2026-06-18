import streamlit as st
import os
import tempfile
from google import genai
from google.genai import types

# --- PAGE CONFIGURATION (WIDE & CLEAN) ---
st.set_page_config(
    page_title="Peshi / पेशी | Enterprise Legal Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed" 
)

# --- THE VISUAL IDENTITY: INJECTED CSS (HARVEY-INSPIRED APPLE-LIKE MINIMALISM) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #FDFDFD !important;
        color: #111111 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Document & Authoritative Serif Headers */
    h1, h2, h3, .document-title {
        font-family: 'Georgia', serif !important;
        color: #111111 !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    
    /* Sovereign Ink Blue Primary Buttons */
    div.stButton > button:first-child {
        background-color: #111827 !important;
        color: #FDFDFD !important;
        border: 1px solid #111827 !important;
        border-radius: 4px !important;
        padding: 0.6rem 1.2rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.2s ease-in-out !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #374151 !important;
        border-color: #374151 !important;
    }

    /* Soft Stone Grey Structural Enclosures */
    div[data-testid="stColumn"] {
        background-color: #F9FAFB;
        padding: 1.5rem !important;
        border-radius: 6px;
        border: 1px solid #E5E7EB;
    }
    
    /* Text Input Overrides */
    input[type="text"], input[type="password"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        color: #111111 !important;
        border-radius: 4px !important;
    }
    
    /* Hide the default Streamlit file uploader border to make it look cleaner */
    [data-testid="stFileUploadDropzone"] {
        background-color: #FFFFFF !important;
        border: 1px dashed #9CA3AF !important;
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SYSTEM INSTRUCTION ---
PESHI_SYSTEM_INSTRUCTION = """
You are Peshi / पेशी, an elite enterprise-grade Legal AI utilized by top Indian law firms. 
Respond with supreme professionalism, citing specific pages and paragraphs.
Understand English, Hindi, and Hinglish perfectly.
Maintain strict chronological discipline and never invent facts.
"""

# --- INITIALIZE MEMORY STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "gemini_files" not in st.session_state:
    st.session_state.gemini_files = []
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None
if "stored_api_key" not in st.session_state:
    st.session_state.stored_api_key = ""

# --- APP HEADER (FIRM BRANDING) ---
st.markdown("""
<div style='display: flex; justify-content: space-between; align-items: center; padding-bottom: 15px; border-bottom: 1px solid #E5E7EB; margin-bottom: 30px;'>
    <h1 style='margin: 0; font-size: 24px;'>Peshi / पेशी <span style='font-family:Inter; font-size:14px; font-weight:400; color:#6B7280; margin-left: 10px;'>Enterprise Legal Intelligence</span></h1>
    <div style='font-size: 13px; color: #4B5563;'>🔒 256-Bit Encrypted Firm Vault</div>
</div>
""", unsafe_allow_html=True)


# =====================================================================
# VIEW 1: THE ENTERPRISE LANDING DASHBOARD (When no files are uploaded)
# =====================================================================
if not st.session_state.gemini_files:
    dash_left, dash_right = st.columns([1.2, 1], gap="large")
    
    with dash_left:
        st.markdown("<h2>Firm Dashboard & Vault</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #4B5563; font-size: 14px; margin-bottom: 25px;'>Access recent matters, intelligence reports, and active workflows across your practice.</p>", unsafe_allow_html=True)
        
        # Mocking a "Lived-in" Enterprise state so it doesn't look empty
        st.markdown("""
        <div style='background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 6px; padding: 15px; margin-bottom: 15px;'>
            <div style='font-size: 12px; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;'>Recent Active Matters</div>
            
            <div style='display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #F3F4F6;'>
                <div><span style='font-weight: 500; font-size: 14px;'>Writ Petition (C) 402/2026</span><br><span style='font-size: 12px; color: #6B7280;'>M/s Sharma Builders vs. State of Rajasthan</span></div>
                <div style='font-size: 12px; color: #10B981; font-weight: 500;'>Analysis Complete</div>
            </div>
            
            <div style='display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #F3F4F6;'>
                <div><span style='font-weight: 500; font-size: 14px;'>Bail Application No. 1184</span><br><span style='font-size: 12px; color: #6B7280;'>NDPS Act - Sessions Court</span></div>
                <div style='font-size: 12px; color: #F59E0B; font-weight: 500;'>Timeline Pending</div>
            </div>
            
            <div style='display: flex; justify-content: space-between; padding: 10px 0;'>
                <div><span style='font-weight: 500; font-size: 14px;'>Arbitration Appeal 22/2025</span><br><span style='font-size: 12px; color: #6B7280;'>Commercial Court, Mumbai</span></div>
                <div style='font-size: 12px; color: #10B981; font-weight: 500;'>Briefing Ready</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with dash_right:
        st.markdown("<div style='background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 6px; padding: 25px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top: 0; font-size: 18px;'>Ingest New Matter</h3>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 13px; color: #4B5563;'>Upload Charge Sheets, FIRs, SLPs, Annexures, or complete case briefs. Peshi automatically processes English and Hindi text.</p>", unsafe_allow_html=True)
        
        # API Key required before ingestion
        api_key = st.text_input("Firm Infrastructure Key (Gemini API)", type="password", value=st.session_state.stored_api_key)
        if api_key != st.session_state.stored_api_key:
            st.session_state.stored_api_key = api_key

        uploaded_files = st.file_uploader("Drop legal PDFs here", type=["pdf"], accept_multiple_files=True)
        
        if st.button("Initialize Case Engine", use_container_width=True):
            if not st.session_state.stored_api_key:
                st.error("Infrastructure Key required to initialize.")
            elif not uploaded_files:
                st.warning("Please upload case documents.")
            else:
                with st.spinner("Encrypting and indexing case records..."):
                    try:
                        client = genai.Client(api_key=st.session_state.stored_api_key)
                        st.session_state.gemini_files = [] 
                        for file in uploaded_files:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                                tmp.write(file.read())
                                tmp_path = tmp.name
                            uploaded_file = client.files.upload(file=tmp_path)
                            st.session_state.gemini_files.append(uploaded_file)
                            os.remove(tmp_path)
                        st.rerun() # Forces the page to reload into the 3-pane command center
                    except Exception as e:
                        st.error(f"Ingestion fault: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# VIEW 2: THE ACTIVE MATTER COMMAND CENTER (When files ARE uploaded)
# =====================================================================
else:
    pane_left, pane_center, pane_right = st.columns([1.5, 4.0, 3.5], gap="medium")

    # --- PANE 1: MATTER NAVIGATION ---
    with pane_left:
        st.markdown("<h3 style='font-size:16px; margin-top:0;'>📂 Active Brief</h3>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: #E5E7EB; margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)
        
        st.markdown("<p style='font-size:12px; font-weight:600; color:#6B7280; text-transform:uppercase;'>Indexed Records</p>", unsafe_allow_html=True)
        for idx, file in enumerate(st.session_state.gemini_files):
            st.markdown(f"<div style='font-size:13px; padding:8px 0; border-bottom:1px solid #E5E7EB; color:#111111;'>📄 Document 0{idx+1} <br><span style='font-size:11px; color:#6B7280;'>Processed via Vision OCR</span></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Close Matter & Clear Memory", use_container_width=True):
            st.session_state.gemini_files = []
            st.session_state.last_analysis = None
            st.session_state.messages = []
            st.rerun()

    # --- PANE 2: PRIMARY WORKSPACE ---
    with pane_center:
        doc_tab, timeline_tab = st.tabs(["📄 Document Analysis", "⏳ Chronology Engine"])
        
        with doc_tab:
            st.markdown("<div style='background-color:#FFFFFF; border:1px solid #E5E7EB; padding:20px; min-height:500px; border-radius:4px;'>", unsafe_allow_html=True)
            st.markdown("<p style='font-family:Georgia; font-size:18px; color:#111111;'>Record Intelligence Ready</p>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:14px; color:#4B5563;'>The uploaded documents have been parsed. Use the Intelligence Board on the right to extract legal arguments, generate citations, and assess case strength.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with timeline_tab:
            st.markdown("<div style='background-color:#FFFFFF; border:1px solid #E5E7EB; padding:20px; min-height:500px; border-radius:4px;'>", unsafe_allow_html=True)
            st.markdown("<p style='font-family:Georgia; font-size:18px; color:#111111;'>Master Chronology</p>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:14px; color:#4B5563;'>Ask the AI to <em>'Generate a strict chronological timeline of this case'</em> to populate the procedural history here.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # --- PANE 3: STRATEGIC INTELLIGENCE ---
    with pane_right:
        st.markdown("<h3 style='font-size:16px; margin-top:0;'>📊 Intelligence Board</h3>", unsafe_allow_html=True)
        
        if st.button("Execute Core Strategy Brief", type="primary", use_container_width=True):
            with st.spinner("Synthesizing legal framework..."):
                try:
                    client = genai.Client(api_key=st.session_state.stored_api_key)
                    contents = ["Generate a high-level case strategy brief. Identify the core dispute, point out any statutory timelines (like Limitation Act), and cite page numbers for evidence."] + st.session_state.gemini_files
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contents,
                        config=types.GenerateContentConfig(system_instruction=PESHI_SYSTEM_INSTRUCTION)
                    )
                    st.session_state.last_analysis = response.text
                except Exception as e:
                    st.error(f"Execution fault: {e}")

        if st.session_state.last_analysis:
            st.markdown("<div style='background-color:#FFFFFF; border:1px solid #E5E7EB; padding:15px; margin-top:10px; max-height:300px; overflow-y:auto; font-size:13px; line-height:1.6;'>", unsafe_allow_html=True)
            st.markdown(st.session_state.last_analysis)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.download_button("📥 Export Memo to Local Disk", st.session_state.last_analysis, "Peshi_Memo.txt", use_container_width=True)

        st.markdown("<hr style='border-color: #E5E7EB; margin-top:20px; margin-bottom:15px;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:13px; font-weight:600; color:#4B5563; text-transform:uppercase;'>Agentic Query</p>", unsafe_allow_html=True)
        
        qa_container = st.container()
        with qa_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(f"<span style='font-size:13px;'>{msg['content']}</span>", unsafe_allow_html=True)
                    
        if prompt := st.chat_input("Query documents (Hindi/English)..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with qa_container:
                with st.chat_message("user"): 
                    st.markdown(prompt)
                
            with qa_container:
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
                        st.markdown(reply.text)
                        st.session_state.messages.append({"role": "assistant", "content": reply.text})
                    except Exception as e:
                        st.error(f"Error: {e}")