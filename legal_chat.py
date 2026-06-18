import sys
import os
from google import genai
from pdf_reader import extract_text_from_pdf

print("==================================================================")
print("   COURT-GRADE LEGAL AI v6.0: MULTI-FILE INGESTION ENGINE ONLINE  ")
print("==================================================================")

# 1. Insert your API Key here! Keep the quotation marks!
API_KEY = "PASTE_YOUR_API_KEY_HERE"

# 2. Wake up the Cloud LLM Brain
try:
    print("[SYSTEM] Wiring directly to Generative LLM Core...")
    client = genai.Client(api_key=API_KEY)
    print("[SYSTEM] Core engine successfully bound.")
except Exception as e:
    print(f"[SYSTEM] Initialization error: {e}")
    sys.exit()

# 3. The Multi-File Ingestion Pipeline
print("\n[SYSTEM] Booting Multi-File Ingestion Pipeline...")
case_folder = "case_files"
UNIFIED_CASE_MEMORY = ""

# Check if folder exists
if not os.path.exists(case_folder):
    print(f"[ERROR] Could not find the '{case_folder}' directory.")
    print("Please create a folder named 'case_files' and put your PDFs inside.")
    sys.exit()

# Loop through every file in the folder
processed_count = 0
for filename in os.listdir(case_folder):
    file_path = os.path.join(case_folder, filename)
    
    # Process PDFs
    if filename.lower().endswith('.pdf'):
        print(f" -> Extracting: {filename}...")
        extracted_text = extract_text_from_pdf(file_path)
        UNIFIED_CASE_MEMORY += f"\n\n================ DOCUMENT: {filename} ================\n\n"
        UNIFIED_CASE_MEMORY += extracted_text
        processed_count += 1
        
    # Process Text files
    elif filename.lower().endswith('.txt'):
        print(f" -> Extracting: {filename}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            UNIFIED_CASE_MEMORY += f"\n\n================ DOCUMENT: {filename} ================\n\n"
            UNIFIED_CASE_MEMORY += f.read()
        processed_count += 1

if processed_count == 0:
    print("[ERROR] No supported files (PDF, TXT) found in the 'case_files' folder.")
    sys.exit()

print(f"\n[SYSTEM] Successfully stitched {processed_count} file(s) into UNIFIED_CASE_MEMORY.")

def generate_strategic_report():
    print("\n[ROUTER] Executing Full Structural Analysis Flow...")
    print("[SYSTEM] Synthesizing comprehensive legal intelligence across all files. Please wait...\n")
    
    prompt = f"""
    You are a senior legal analyst and elite court-level strategist. Analyze the provided legal text. 
    The text may contain multiple different documents stitched together. Read across all of them to build a unified understanding.
    Ignore any watermark text like 'Rajasthan high court only web copy'.
    
    CRITICAL CONSTRAINT: You must follow the ADAPTIVE REPORTING RULE. Do not force sections to be equally detailed. 
    If information for a specific section is missing or uninferable, explicitly state "Not found in documents". 
    Do not assume, hallucinate, or extrapolate facts outside the provided text. Prioritize accuracy over completeness. Avoid repetition.

    Generate the final output strictly according to this 12-section format:

    1. MATTER SNAPSHOT
    - Brief summary of the case (3–6 lines max).
    - Identify parties involved, nature of dispute (if clearly inferable), and current stage of the case.

    2. CHRONOLOGY (MOST IMPORTANT SECTION ⭐)
    - Strict chronological timeline of all events in sequential order.
    - Extract all dates, actions, filings, and court orders combined into one unified timeline.

    3. LEGAL ISSUES IDENTIFIED ⭐
    - Extract core legal questions involved in the case framed precisely (e.g., 'Whether...').

    4. PARTY CLAIMS & POSITIONS
    - Clearly separate arguments of each party into distinct sub-sections:
      * Petitioner/Plaintiff Stance & Claims
      * Respondent/Defendant Stance & Claims
    - Do not mix statements. Keep structured and comparative.

    5. RELIEF / PRAYER ANALYSIS ⭐
    - Extract exact items sought: Main relief, interim relief (stay/injunction), and alternative relief.

    6. EVIDENCE MAP
    - Map specific facts to supporting document types mentioned (petitions, affidavits, orders, revenue records, deeds, etc.). Show which item supports which claim.

    7. PROCEDURAL HISTORY ⭐
    - Sequential tracking of court process steps: filing, notices, interim orders, hearings, and appeals/revisions.

    8. JURISDICTION & MAINTAINABILITY CHECK ⭐
    - Analyze whether the case is maintainable, court jurisdiction, and if alternative remedies exist. If unclear, state 'Not determinable from documents'.

    9. LIMITATION ANALYSIS ⭐
    - Evaluate if the case appears time-barred. Identify delays, condonation requests, or flag missing limitation data.

    10. RISKS & CONTRADICTIONS ⭐
    - Identify direct contradictions between documents, missing facts, weak claims, or inconsistent statements. If none are found, explicitly state "No major contradictions found".

    11. STATUTORY MAPPING
    - Identify relevant codes or acts explicitly mentioned or clearly applicable.

    12. EVIDENCE STRENGTH & ADMISSIBILITY
    - Evaluate the quality of evidence, primary vs secondary document status, and apparent legal validity.

    Document Text:
    {UNIFIED_CASE_MEMORY}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    print("=========================================================================")
    print("                      STRUCTURED LEGAL INTELLIGENCE REPORT               ")
    print("=========================================================================")
    print(response.text)
    print("=========================================================================\n")

def detect_user_intent(query):
    q = query.lower()
    if any(k in q for k in ['analyze', 'report', 'summarize', 'full analysis', 'generate report']):
        return "GENERATE_ANALYSIS_REPORT"
    return "GROUNDED_PINPOINT_QA"

print("\n[SYSTEM] Continuous Context Layer Online. Unified memory active.")
print("Type 'analyze' for the 12-section blueprint report, or ask any direct question.")

while True:
    try:
        user_input = input("\n(Court-Grade Engine) Enter input: ")
    except (KeyboardInterrupt, EOFError):
        print("\n[SYSTEM] Terminating context session.")
        break
        
    if user_input.lower() == 'exit':
        print("[SYSTEM] Shutting down safely.")
        break
        
    if not user_input.strip():
        continue
        
    intent = detect_user_intent(user_input)
    
    if intent == "GENERATE_ANALYSIS_REPORT":
        generate_strategic_report()
    else:
        print("[ROUTER] Routing to Grounded Q&A Engine...")
        qa_prompt = f"""
        You are a court-grade legal intelligence QA assistant. Answer the user's question using ONLY the provided text.
        
        STRICT RULES:
        - Provide a direct, factual, and grounded answer.
        - Cite or reference specific details from the document text where possible.
        - Do not assume or extrapolate facts.
        - If the answer cannot be found in the text, you must say: "Not found in provided documents."
        
        Document Text:
        {UNIFIED_CASE_MEMORY}
        
        Question: {user_input}
        """
        answer = client.models.generate_content(model='gemini-2.5-flash', contents=qa_prompt)
        print("\n--- GROUNDED EVIDENCE OUTPUT ---")
        print(answer.text.strip())
        print("--------------------------------")