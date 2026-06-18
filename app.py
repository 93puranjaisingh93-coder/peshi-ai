import streamlit as st
import os
import json
import tempfile
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Peshi / पेशी | Enterprise Legal Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# "QUIET AUTHORITY" DESIGN SYSTEM
# Courtroom Cream backgrounds / Chamber Charcoal UI / Sovereign Ink accents
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600&display=swap');

:root {
    --paper: #FAF8F4;
    --paper-raised: #FFFFFF;
    --ink: #1C1B19;
    --ink-soft: #4A4640;
    --ink-faint: #8A8478;
    --rule: #E4DFD6;
    --rule-strong: #D3CCBE;
    --charcoal: #1F2226;
    --charcoal-hover: #2D3138;
    --sovereign: #1E3A5F;
    --sovereign-soft: #EBF0F5;
    --gold-line: #9C8552;
    --success: #3D7A5C;
    --pending: #A6692B;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {
    background-color: var(--paper) !important;
    color: var(--ink) !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stHeader"] { background-color: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
.block-container { padding-top: 2.2rem !important; max-width: 1500px !important; }

h1, h2, h3, h4, .chamber-serif {
    font-family: 'Source Serif 4', Georgia, serif !important;
    color: var(--ink) !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em;
}
p, span, div, label { font-family: 'Inter', sans-serif; }

/* Buttons */
div.stButton > button, div.stDownloadButton > button {
    background-color: var(--charcoal) !important;
    color: var(--paper) !important;
    border: 1px solid var(--charcoal) !important;
    border-radius: 3px !important;
    padding: 0.55rem 1.1rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 13.5px !important;
    letter-spacing: 0.01em;
    transition: all 0.15s ease-in-out !important;
    box-shadow: none !important;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    background-color: var(--charcoal-hover) !important;
    border-color: var(--charcoal-hover) !important;
}
div.stButton > button[kind="primary"] {
    background-color: var(--sovereign) !important;
    border-color: var(--sovereign) !important;
}
div.stButton > button[kind="primary"]:hover {
    background-color: #2A4A73 !important;
}

/* Containers / columns used as panels */
div[data-testid="stColumn"] > div > div[data-testid="stVerticalBlock"] {
    gap: 0.6rem;
}

/* Inputs */
input[type="text"], input[type="password"], textarea {
    background-color: var(--paper-raised) !important;
    border: 1px solid var(--rule-strong) !important;
    color: var(--ink) !important;
    border-radius: 3px !important;
    font-family: 'Inter', sans-serif !important;
}
input[type="text"]:focus, input[type="password"]:focus, textarea:focus {
    border-color: var(--sovereign) !important;
    box-shadow: 0 0 0 1px var(--sovereign) !important;
}
[data-testid="stFileUploadDropzone"] {
    background-color: var(--paper-raised) !important;
    border: 1px dashed var(--rule-strong) !important;
    border-radius: 4px !important;
}

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid var(--rule);
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif;
    font-size: 13.5px;
    font-weight: 500;
    color: var(--ink-soft);
    background-color: transparent;
    padding: 10px 16px;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--sovereign) !important;
    border-bottom: 2px solid var(--sovereign) !important;
}

/* Chat */
[data-testid="stChatMessage"] {
    background-color: var(--paper-raised);
    border: 1px solid var(--rule);
    border-radius: 4px;
}
[data-testid="stChatInput"] textarea {
    background-color: var(--paper-raised) !important;
}

/* Scrollbars for chamber feel */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-thumb { background: var(--rule-strong); border-radius: 3px; }
::-webkit-scrollbar-track { background: transparent; }

/* Custom utility classes used in markdown blocks below */
.panel {
    background: var(--paper-raised);
    border: 1px solid var(--rule);
    border-radius: 5px;
}
.panel-header {
    font-size: 11px;
    color: var(--ink-faint);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}
.hairline { border: none; border-top: 1px solid var(--rule); margin: 14px 0; }
.status-dot { display:inline-block; width:6px; height:6px; border-radius:50%; margin-right:6px; }
</style>
""", unsafe_allow_html=True)

PESHI_SYSTEM_INSTRUCTION = """
You are Peshi / पेशी, an elite enterprise-grade Legal AI utilized by top Indian law firms.
Respond with supreme professionalism, citing specific pages and paragraphs.
Understand English, Hindi, and Hinglish perfectly.
Maintain strict chronological discipline and never invent facts.
"""

CHRONOLOGY_SYSTEM_INSTRUCTION = """
You are a meticulous Indian legal chronology analyst. Extract every dated event from the
supplied case documents (FIRs, charge sheets, orders, petitions, annexures, correspondence).
Rules:
- Only extract events with an identifiable date (exact date, or month/year if exact day is absent).
- Never invent or estimate a date that is not stated or directly inferable from the document.
- For each event, identify which source document it came from and the page number if visible.
- Classify each event's legal significance (e.g. "Procedural", "Evidentiary", "Statutory Deadline", "Order/Judgment", "Filing").
- Order events strictly chronologically, oldest first.
- Write descriptions in formal Indian legal drafting style, concise, third person.
Return ONLY valid JSON matching the provided schema. No prose, no markdown fences.
"""

CHRONOLOGY_SCHEMA = {
    "type": "object",
    "properties": {
        "events": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "ISO date YYYY-MM-DD, or YYYY-MM if day unknown"},
                    "display_date": {"type": "string", "description": "Human-readable date as it should appear, e.g. '14 March 2024'"},
                    "title": {"type": "string", "description": "Short event headline, max 10 words"},
                    "description": {"type": "string", "description": "1-3 sentence formal description"},
                    "source_document": {"type": "string", "description": "Which uploaded document this came from"},
                    "page_reference": {"type": "string", "description": "Page or paragraph number if available, else empty string"},
                    "category": {
                        "type": "string",
                        "enum": ["Procedural", "Evidentiary", "Statutory Deadline", "Order/Judgment", "Filing", "Other"]
                    }
                },
                "required": ["date", "display_date", "title", "description", "source_document", "category"]
            }
        }
    },
    "required": ["events"]
}

# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    "messages": [],
    "gemini_files": [],
    "gemini_file_names": [],
    "last_analysis": None,
    "stored_api_key": "",
    "chronology": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div style='display: flex; justify-content: space-between; align-items: center; padding-bottom: 18px; border-bottom: 1px solid var(--rule); margin-bottom: 32px;'>
<h1 style='margin: 0; font-size: 25px;'>Peshi / पेशी <span style='font-family:Inter; font-size:13px; font-weight:400; color:var(--ink-faint); margin-left: 12px; letter-spacing:0.02em;'>ENTERPRISE LEGAL INTELLIGENCE</span></h1>
<div style='font-size: 12.5px; color: var(--ink-soft); display:flex; align-items:center;'><span class='status-dot' style='background:var(--success);'></span>256-Bit Encrypted Firm Vault</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# DASHBOARD (no files yet)
# ============================================================
if not st.session_state.gemini_files:
    dash_left, dash_right = st.columns([1.2, 1], gap="large")

    with dash_left:
        st.markdown("<h2>Firm Dashboard &amp; Vault</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: var(--ink-soft); font-size: 14px; margin-bottom: 25px;'>Access recent matters, intelligence reports, and active workflows across your practice.</p>", unsafe_allow_html=True)

        st.markdown("""
<div class='panel' style='padding: 18px;'>
<div class='panel-header' style='margin-bottom: 12px;'>Recent Active Matters</div>
<div style='display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--rule);'>
<div><span style='font-weight: 500; font-size: 14px;'>Writ Petition (C) 402/2026</span><br><span style='font-size: 12px; color: var(--ink-faint);'>M/s Sharma Builders vs. State of Rajasthan</span></div>
<div style='font-size: 12px; color: var(--success); font-weight: 500;'>Analysis Complete</div>
</div>
<div style='display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--rule);'>
<div><span style='font-weight: 500; font-size: 14px;'>Bail Application No. 1184</span><br><span style='font-size: 12px; color: var(--ink-faint);'>NDPS Act &mdash; Sessions Court</span></div>
<div style='font-size: 12px; color: var(--pending); font-weight: 500;'>Timeline Pending</div>
</div>
<div style='display: flex; justify-content: space-between; padding: 12px 0;'>
<div><span style='font-weight: 500; font-size: 14px;'>Arbitration Appeal 22/2025</span><br><span style='font-size: 12px; color: var(--ink-faint);'>Commercial Court, Mumbai</span></div>
<div style='font-size: 12px; color: var(--success); font-weight: 500;'>Briefing Ready</div>
</div>
</div>
        """, unsafe_allow_html=True)

    with dash_right:
        st.markdown("""
<div class='panel' style='padding: 26px;'>
<h3 style='margin-top: 0; font-size: 18px;'>Ingest New Matter</h3>
<p style='font-size: 13px; color: var(--ink-soft);'>Upload Charge Sheets, FIRs, SLPs, Annexures, or complete case briefs. Peshi automatically processes English and Hindi text.</p>
</div>
        """, unsafe_allow_html=True)

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
                        st.session_state.gemini_file_names = []
                        for file in uploaded_files:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                                tmp.write(file.read())
                                tmp_path = tmp.name
                            uploaded_file = client.files.upload(file=tmp_path)
                            st.session_state.gemini_files.append(uploaded_file)
                            st.session_state.gemini_file_names.append(file.name)
                            os.remove(tmp_path)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ingestion fault: {e}")

# ============================================================
# 3-PANE COMMAND CENTER
# ============================================================
else:
    pane_left, pane_center, pane_right = st.columns([1.5, 4.0, 3.5], gap="medium")

    # ---------------- LEFT: Matter records ----------------
    with pane_left:
        st.markdown("<h3 style='font-size:16px; margin-top:0;'>📂 Active Brief</h3>", unsafe_allow_html=True)
        st.markdown("<hr class='hairline' style='margin-top: 5px;'>", unsafe_allow_html=True)

        st.markdown("<p class='panel-header'>Indexed Records</p>", unsafe_allow_html=True)
        names = st.session_state.gemini_file_names or [f"Document 0{i+1}" for i in range(len(st.session_state.gemini_files))]
        for idx, name in enumerate(names):
            st.markdown(f"<div style='font-size:13px; padding:9px 0; border-bottom:1px solid var(--rule); color:var(--ink);'>📄 {name}<br><span style='font-size:11px; color:var(--ink-faint);'>Processed via Vision OCR</span></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Close Matter &amp; Clear Memory", use_container_width=True):
            st.session_state.gemini_files = []
            st.session_state.gemini_file_names = []
            st.session_state.last_analysis = None
            st.session_state.chronology = None
            st.session_state.messages = []
            st.rerun()

    # ---------------- CENTER: Document / Chronology tabs ----------------
    with pane_center:
        doc_tab, timeline_tab = st.tabs(["📄 Document Analysis", "⏳ Chronology Engine"])

        with doc_tab:
            st.markdown("""
<div class='panel' style='padding:22px; min-height:500px;'>
<p class='chamber-serif' style='font-size:18px;'>Record Intelligence Ready</p>
<p style='font-size:14px; color:var(--ink-soft);'>The uploaded documents have been parsed. Use the Intelligence Board on the right to extract legal arguments, generate citations, and assess case strength.</p>
</div>
            """, unsafe_allow_html=True)

        with timeline_tab:
            top_l, top_r = st.columns([3, 1])
            with top_l:
                st.markdown("<p class='chamber-serif' style='font-size:18px; margin-bottom:2px;'>Master Chronology</p>", unsafe_allow_html=True)
                st.markdown("<p style='font-size:13px; color:var(--ink-soft); margin-top:0;'>Strict date-order extraction across all indexed records.</p>", unsafe_allow_html=True)
            with top_r:
                build_clicked = st.button("Build Chronology", use_container_width=True)

            if build_clicked:
                with st.spinner("Reconstructing case timeline..."):
                    try:
                        client = genai.Client(api_key=st.session_state.stored_api_key)
                        doc_list_note = "Source documents in order: " + ", ".join(names) + "."
                        contents = [
                            doc_list_note,
                            "Extract the full chronology of events from these case documents as instructed."
                        ] + st.session_state.gemini_files

                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=contents,
                            config=types.GenerateContentConfig(
                                system_instruction=CHRONOLOGY_SYSTEM_INSTRUCTION,
                                response_mime_type="application/json",
                                response_schema=CHRONOLOGY_SCHEMA,
                            )
                        )
                        parsed = json.loads(response.text)
                        st.session_state.chronology = parsed.get("events", [])
                    except Exception as e:
                        st.error(f"Chronology extraction fault: {e}")

            if st.session_state.chronology:
                events = st.session_state.chronology
                category_colors = {
                    "Procedural": "#6B7280",
                    "Evidentiary": "#1E3A5F",
                    "Statutory Deadline": "#A6692B",
                    "Order/Judgment": "#3D7A5C",
                    "Filing": "#9C8552",
                    "Other": "#8A8478",
                }
                rows_html = "<div style='position:relative; padding-left:18px;'>"
                rows_html += "<div style='position:absolute; left:5px; top:6px; bottom:6px; width:1px; background:var(--rule-strong);'></div>"
                for ev in events:
                    color = category_colors.get(ev.get("category", "Other"), "#8A8478")
                    page_ref = ev.get("page_reference", "")
                    page_html = f" &middot; p.{page_ref}" if page_ref else ""
                    rows_html += f"""
<div style='position:relative; margin-bottom:20px;'>
<div style='position:absolute; left:-18px; top:5px; width:9px; height:9px; border-radius:50%; background:{color}; border:2px solid var(--paper-raised);'></div>
<div style='font-size:11.5px; color:var(--ink-faint); text-transform:uppercase; letter-spacing:0.04em; margin-bottom:3px;'>{ev.get("display_date","")} &nbsp;&bull;&nbsp; <span style='color:{color};'>{ev.get("category","")}</span></div>
<div style='font-weight:600; font-size:14.5px; color:var(--ink); margin-bottom:3px;'>{ev.get("title","")}</div>
<div style='font-size:13px; color:var(--ink-soft); line-height:1.55;'>{ev.get("description","")}</div>
<div style='font-size:11.5px; color:var(--ink-faint); margin-top:4px; font-style:italic;'>Source: {ev.get("source_document","")}{page_html}</div>
</div>
"""
                rows_html += "</div>"

                st.markdown(f"""
<div class='panel' style='padding:22px; max-height:560px; overflow-y:auto;'>
{rows_html}
</div>
                """, unsafe_allow_html=True)

                chron_text = "\n\n".join(
                    f"{ev.get('display_date','')} — {ev.get('title','')}\n{ev.get('description','')}\n(Source: {ev.get('source_document','')}{' p.' + ev.get('page_reference') if ev.get('page_reference') else ''})"
                    for ev in events
                )
                st.download_button("📥 Export Chronology", chron_text, "Peshi_Chronology.txt", use_container_width=True)
            elif not build_clicked:
                st.markdown("""
<div class='panel' style='padding:22px; min-height:420px; display:flex; align-items:center; justify-content:center;'>
<p style='font-size:14px; color:var(--ink-faint); text-align:center;'>No chronology built yet.<br>Click <strong>Build Chronology</strong> to extract a dated timeline from the indexed records.</p>
</div>
                """, unsafe_allow_html=True)

    # ---------------- RIGHT: Intelligence Board & Chat ----------------
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
            st.markdown(f"""
<div class='panel' style='padding:16px; margin-top:10px; max-height:300px; overflow-y:auto; font-size:13px; line-height:1.6;'>
{st.session_state.last_analysis}
</div>
            """, unsafe_allow_html=True)

            st.download_button("📥 Export Memo to Local Disk", st.session_state.last_analysis, "Peshi_Memo.txt", use_container_width=True)

        st.markdown("<hr class='hairline'>", unsafe_allow_html=True)
        st.markdown("<p class='panel-header'>Agentic Query</p>", unsafe_allow_html=True)

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