import streamlit as st
import os
import tempfile
from google import genai
from google.genai import types

# --- PAGE CONFIGURATION (WIDE & CLEAN) ---
st.set_page_config(
    page_title="पेशी (Peshi) | Legal Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed" # Collapsed to maximize focus on the 3-pane command center
)

# --- THE VISUAL IDENTITY: INJECTED CSS (QUIET AUTHORITY) ---
st.markdown("""
<style>
    /* Global Background and Base Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #FBFBFA !important;
        color: #1A1A1A !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Document & Authoritative Serif Headers */
    h1, h2, h3, .document-title {
        font-family: 'Georgia', serif !important;
        color: #1A1A1A !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    
    /* Sovereign Ink Blue Primary Buttons */
    div.stButton > button:first-child {
        background-color: #1C2E4A !important;
        color: #FBFBFA !important;
        border: 1px solid #1C2E4A !important;
        border-radius: 2px !important;
        padding: 0.5rem 1rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        transition: background-color 80ms ease-in-out !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #0D0D0D !important;
        border-color: #0D0D0D !important;
        color: #FBFBFA !important;
    }

    /* Muted Download/Secondary Buttons */
    div.stDownloadButton > button {
        background-color: transparent !important;
        color: #1C2E4A !important;
        border: 1px solid #1C2E4A !important;
        border-radius: 2px !important;
        font-family: 'Inter', sans-serif !important;
    }
    div.stDownloadButton > button:hover {
        background-color: #F2F1EE !important;
        color: #1A1A1A !important;
    }

    /* Soft Stone Grey Structural Enclosures */
    div[data-testid="stColumn"] {
        background-color: #F2F1EE;
        padding: 1.5rem !important;
        border-radius: 4px;
        border: 1px solid #E5E4E1;
    }
    
    /* Text Input Overrides */
    input[type="text"], input[type="password"] {
        background-color: #FBFBFA !important;
        border: 1px solid #CCB !important;
        color: #1A1A1A !important;
        border-radius: 2px !important;
    }

    /* Clean Up Default Streamlit Padding Elements */
    [data-testid="stBlock"] {
        gap: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SYSTEM INSTRUCTION (UNALTERED CORE LOGIC) ---
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

# --- INITIALIZE MEMORY STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "gemini_files" not in st.session_state:
    st.session_state.gemini_files = []
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None
if "stored_api_key" not in st.session_state:
    st.session_state.stored_api_key = ""

# --- APP HEADER CONTAINER ---
st.markdown("<h1 style='margin-bottom: 0px;'>पेशी <span style='font-family:Inter; font-size:18px; font-weight:400; color:#666;'>| Quiet Authority</span></h1>", unsafe_allow_html=True)
st.markdown("<hr style='margin-top: 5px; margin-bottom: 25px; border-color: #E5E4E1;'>", unsafe_allow_html=True)

# --- THE THREE-PANE COMMAND CENTER ---
pane_left, pane_center, pane_right = st.columns([1.5, 4.0, 3.5], gap="medium")

# =====================================================================
# PANE 1: MATTER NAVIGATION & FILES (LEFT)
# =====================================================================
with pane_left:
    st.markdown("<h3 style='font-size:18px; margin-top:0;'>📂 Matter Records</h3>", unsafe_allow_html=True)
    
    # Secure API Ingestion Node
    api_key = st.text_input(
        "Chamber API Key", 
        type="password", 
        value=st.session_state.stored_api_key,
        placeholder="Enter credential..."
    )
    if api_key != st.session_state.stored_api_key:
        st.session_state.stored_api_key = api_key

    st.markdown("<hr style='border-color: #D5D4D1;'>", unsafe_allow_html=True)
    
    # Document Ingestion Link
    uploaded_files = st.file_uploader("Ingest Case Briefs (PDF)", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
    
    if st.button("Process & Cache Briefs", use_container_width=True):
        if not st.session_state.stored_api_key:
            st.error("API Credential missing.")
        elif not uploaded_files:
            st.warning("No briefs detected.")
        else:
            with st.spinner("Indexing records..."):
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
                    st.success("Briefs locked into active memory.")
                except Exception as e:
                    st.error(f"Ingestion error: {e}")

    # Simulated Archive Index Tree
    st.markdown("<br><p style='font-size:12px; font-weight:600; color:#555; text-transform:uppercase; margin-bottom:5px;'>Active Chamber Index</p>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:13px; line-height: 1.8; color: #444;'>
        <div>📁 Pleadings / Writ Petitions</div>
        <div>📁 Orders & Daily Judgments</div>
        <div>📁 Exhibited Documentary Evidence</div>
    </div>
    """, unsafe_allow_html=True)


# =====================================================================
# PANE 2: PRIMARY WORKING AREA & CHRONOLOGY (CENTER)
# =====================================================================
with pane_center:
    # Check if a matter exists to show operational state
    if not st.session_state.gemini_files:
        st.markdown("<h2 style='font-size:36px; margin-top:20px; text-align:center;'>Every Matter. Understood.</h2>", unsafe_allow_html=True)
        st.markdown("""
        <p style='color: #444; font-size: 15px; text-align: center; max-width: 500px; margin: 0 auto; line-height: 1.6;'>
            Upload petitions, pleadings, orders, evidence, judgments, and legal records. 
            Peshi analyzes the entire matter, identifies issues, surfaces relevant precedents, 
            and helps lawyers prepare with clarity before every hearing.
        </p>
        """, unsafe_allow_html=True)
    else:
        # Document/Timeline Toggles
        doc_tab, timeline_tab = st.tabs(["📄 Primary Brief Workspace", "⏳ Master Chronology"])
        
        with doc_tab:
            st.markdown("<div style='background-color:#FBFBFA; border:1px solid #D5D4D1; padding:20px; min-height:400px; border-radius:2px;'>", unsafe_allow_html=True)
            st.markdown("<p style='font-family:Georgia; font-size:18px; font-style:italic; color:#444;'>Active Record Viewer</p>", unsafe_allow_html=True)
            st.markdown("<hr style='border-color: #E5E4E1;'>", unsafe_allow_html=True)
            for idx, file in enumerate(uploaded_files):
                st.markdown(f"**Record [{idx+1}]:** `{file.name}` — *Successfully indexed into cloud pipeline.*")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with timeline_tab:
            st.markdown("<div style='background-color:#FBFBFA; border:1px solid #D5D4D1; padding:20px; min-height:400px; border-radius:2px;'>", unsafe_allow_html=True)
            st.markdown("<p style='font-family:Georgia; font-size:18px; font-style:italic; color:#444;'>Procedural Event History Matrix</p>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:13px; color:#666;'>To populate the definitive chronological table matrix, prompt the Analysis Engine panel to the right.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


# =====================================================================
# PANE 3: ANALYSIS & INTELLIGENCE BOARD (RIGHT)
# =====================================================================
with pane_right:
    st.markdown("<h3 style='font-size:18px; margin-top:0;'>📊 Strategic Intelligence</h3>", unsafe_allow_html=True)
    
    if st.button("Generate Case Structural Blueprint", type="primary", use_container_width=True):
        if not st.session_state.stored_api_key:
            st.error("Set Chamber API Key.")
        elif not st.session_state.gemini_files:
            st.error("Ingest records in the left panel first.")
        else:
            with st.spinner("Analyzing arguments..."):
                try:
                    client = genai.Client(api_key=st.session_state.stored_api_key)
                    contents = ["Generate the full legal blueprint report, identifying core legal issues, relevant precedents, and precise hearing preparation notes. Cite [Page X, Para Y] explicitly."] + st.session_state.gemini_files
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contents,
                        config=types.GenerateContentConfig(system_instruction=PESHI_SYSTEM_INSTRUCTION)
                    )
                    st.session_state.last_analysis = response.text
                except Exception as e:
                    st.error(f"Analysis fault: {e}")

    # Persistent Display Layout Block
    if st.session_state.last_analysis:
        st.markdown("<div style='background-color:#FBFBFA; border:1px solid #D5D4D1; padding:15px; margin-top:10px; max-height:350px; overflow-y:auto; font-size:14px; font-family:Georgia; line-height:1.6;'>", unsafe_allow_html=True)
        st.markdown(st.session_state.last_analysis)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.download_button(
            label="📄 Extract Briefing Memo to Disk",
            data=st.session_state.last_analysis,
            file_name="Peshi_Briefing_Memo.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.markdown("<hr style='border-color: #D5D4D1; margin-top:20px; margin-bottom:15px;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:14px; font-weight:600; margin-bottom:5px;'>💡 Targeted Submissions Q&A</p>", unsafe_allow_html=True)
    
    # Isolated Q&A Block Layout
    qa_container = st.container()
    with qa_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(f"<span style='font-size:13.5px;'>{msg['content']}</span>", unsafe_allow_html=True)
                
    if prompt := st.chat_input("Examine specific claim (Hinglish/English)..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with qa_container:
            with st.chat_message("user"): 
                st.markdown(prompt)
            
        if not st.session_state.stored_api_key:
            st.error("API Key missing.")
        elif not st.session_state.gemini_files:
            st.warning("Load case briefs first.")
        else:
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