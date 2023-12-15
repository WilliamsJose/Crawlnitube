import unicodedata

def normalize_string(input_str):
    normalized_str = unicodedata.normalize('NFD', input_str)
    cleaned_str = ''.join(ch for ch in normalized_str if not unicodedata.combining(ch))
    return cleaned_str.lower().replace(" ", "_")