import re

def detect_references(text):
    """Detect Bible references in text."""
    # Bible reference pattern matching the Lua pattern
    pattern = r'\s*([1-3]\s+)?([A-Za-zÀ-ÿ]+\s+\d+:\d+[-]?\d*)'
    
    references = []
    for match in re.finditer(pattern, text):
        book_num = match.group(1) or ''
        reference = book_num + match.group(2)
        reference = ' '.join(reference.split())  # normalize spaces
        
        # Calculate actual reference position without spaces
        ref_start = text.find(reference, match.start(), match.end())
        ref_length = len(reference)
        
        references.append({
            'reference': reference,
            'start': ref_start,
            'end': ref_start + ref_length
        })
    
    return references