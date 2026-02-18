import re
from datetime import datetime

def validate_phone(phone: str) -> bool:
    """
    Validate a phone number.
    Removes common separators and checks if the result is digits (10-15 chars).
    """
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    return cleaned.isdigit() and 10 <= len(cleaned) <= 15

def validate_year(year: int) -> bool:
    """
    Validate a year: between 1900 and next year.
    """
    current_year = datetime.now().year
    return 1900 <= year <= current_year + 1

def validate_tire_diameter(diameter: float) -> bool:
    """
    Validate tire diameter (R) – typical range 10–30 inches.
    """
    return 10.0 <= diameter <= 30.0

def validate_tire_width(width: int) -> bool:
    """
    Validate tire width in mm – typical range 100–400.
    """
    return 100 <= width <= 400

def validate_tire_profile(profile: int) -> bool:
    """
    Validate tire profile (aspect ratio) – typical range 20–90 %.
    """
    return 20 <= profile <= 90

def validate_email(email: str) -> bool:
    """
    Basic email format validation.
    """
    pattern = r'^[^@]+@[^@]+\.[^@]+$'
    return re.match(pattern, email) is not None