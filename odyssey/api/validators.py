import re
from datetime import datetime

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, phone))

def validate_dimensions(dimensions):
    pattern = r'^\d+x\d+x\d+in$'
    return bool(re.match(pattern, dimensions))

def validate_temp_range(temp_range):
    pattern = r'^\d+(-\d+)?°[CF]$'
    return bool(re.match(pattern, temp_range))

def validate_postal_code(postal_code, country='US'):
    patterns = {
        'US': r'^\d{5}(-\d{4})?$',
        'CA': r'^[A-Z]\d[A-Z]\s?\d[A-Z]\d$'
    }
    return bool(re.match(patterns.get(country, r'.+'), postal_code)) 