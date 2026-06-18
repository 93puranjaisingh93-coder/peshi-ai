import os
from pypdf import PdfReader
from font_bridge import kruti_to_unicode  # <--- NEW BRIDGE IMPORT

print("====================================================")
print("   LEGAL DOCUMENT INGESTION ENGINE IS ONLINE        ")
print("====================================================")

def extract_text_from_pdf(pdf_path):
    """
    Rips text from a PDF page by page to handle massive files.
    """
    if not os.path.exists(pdf_path):
        return f"[ERROR] Could not find the file: {pdf_path}"
        
    print(f"[SYSTEM] Opening case file: {pdf_path}...")
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    print(f"[SYSTEM] Detected {total_pages} pages. Initiating extraction...\n")
    
    extracted_text = ""
    
    # Loop through every single page
    for page_num in range(total_pages):
        page = reader.pages[page_num]
        text = page.extract_text()
        
        if text:
            extracted_text += text + "\n"
            print(f" -> Extracted Page {page_num + 1}/{total_pages}")
            
    return extracted_text

# Let's test it on a file named 'sample_case.pdf'
test_file = "sample_case.pdf"

# Run the extraction
case_data = extract_text_from_pdf(test_file)

if "[ERROR]" not in case_data:
    # Push the raw extracted text through our linguistic bridge
    case_data = kruti_to_unicode(case_data)  # <--- NEW BRIDGE TRIGGER

    print("\n--- EXTRACTION COMPLETE ---")
    print(f"Total Characters Extracted: {len(case_data)}")
    print("Preview of first 250 characters:")
    print("----------------------------------")
    print(case_data[:250])
    print("----------------------------------")
else:
    print(case_data)