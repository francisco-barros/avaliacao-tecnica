import re

def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

def validate_password(password, min_length=6):
    return len(password) >= min_length

def validate_required(value):
    return value is not None and str(value).strip() != ""

