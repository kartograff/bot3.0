def format_phone(phone: str) -> str:
    """
    Format phone number to a readable form (optional).
    """
    # Simple: just return as is, or could add formatting
    return phone

def format_car_info(brand: str, model: str, year: int = None) -> str:
    """
    Format car information for display.
    """
    if year:
        return f"{brand} {model} ({year})"
    return f"{brand} {model}"

def format_tire_size(width: int, profile: int, diameter: float) -> str:
    """
    Format tire size as e.g., "205/55 R16".
    """
    return f"{width}/{profile} R{int(diameter) if diameter.is_integer() else diameter}"

def format_price(price: float, currency: str = "₽") -> str:
    """
    Format price with currency.
    """
    return f"{price:,.0f} {currency}".replace(",", " ")

def format_datetime(date, time) -> str:
    """
    Format date and time for display.
    """
    return f"{date} {time}"