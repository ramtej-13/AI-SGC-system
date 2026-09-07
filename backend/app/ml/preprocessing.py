import re
import string

def clean_text(text: str) -> str:
    """
    Cleans input text by:
    1. Converting None or non-string to empty string
    2. Lowercasing
    3. Normalizing whitespace (tabs, newlines, multi-spaces)
    4. Removing URLs and emails
    5. Stripping punctuation while preserving alphanumeric characters and intra-word hyphens
    6. Trimming leading/trailing whitespace
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
        
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    
    # Remove email addresses
    text = re.sub(r"\S+@\S+\.\S+", " ", text)
    
    # Replace punctuation with space, but keep letters and numbers
    # We replace characters in string.punctuation with space
    punct_pattern = re.compile(f"[{re.escape(string.punctuation)}]")
    text = punct_pattern.sub(" ", text)
    
    # Normalize whitespaces
    text = re.sub(r"\s+", " ", text).strip()
    
    return text
