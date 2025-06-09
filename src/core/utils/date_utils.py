from datetime import datetime, date

def calculate_age(birth_date_str: str) -> int:
    """
    Calculate age from birth date string in format 'YYYY-MM-DD'.
    
    Args:
        birth_date_str (str): Birth date in format 'YYYY-MM-DD'
        
    Returns:
        int: Age in years
    """
    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
    today = date.today()
    
    age = today.year - birth_date.year
    
    # Check if birthday has occurred this year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
        
    return age

def parse_birth_date(birth_date_str: str) -> date:
    """
    Parse birth date string in format 'YYYY-MM-DD' to date object.
    
    Args:
        birth_date_str (str): Birth date in format 'YYYY-MM-DD'
        
    Returns:
        date: Date object representing the birth date
    """
    return datetime.strptime(birth_date_str, "%Y-%m-%d").date()