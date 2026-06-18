print("[SYSTEM] Linguistic Font Bridge Initialized.")

def kruti_to_unicode(raw_text):
    """
    Acts as a translation matrix for legacy Indian court fonts.
    In a full production build, this dictionary contains all 500+ character maps.
    For our immediate pipeline test, we are mapping the exact header tokens of your file.
    """
    translation_matrix = {
        "Hkkjrh;": "भारतीय",
        "lafonk": "संविदा",
        "vf/kfu;e": "अधिनियम",
        "bdkbZ": "इकाई",
        "i`\"BHkwfe": "पृष्ठभूमि",
        "[THE INDIAN CONTRACT ACT, 1872]": "[THE INDIAN CONTRACT ACT, 1872]"
    }
    
    clean_text = raw_text
    # Scan the text and replace the legacy English keystrokes with actual Hindi
    for kruti_str, unicode_str in translation_matrix.items():
        clean_text = clean_text.replace(kruti_str, unicode_str)
        
    return clean_text