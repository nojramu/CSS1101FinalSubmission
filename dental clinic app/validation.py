# validation.py
from datetime import datetime

def validate_contact():
    """Validate contact number format. Loops until valid."""
    while True:
        contact = input("Enter contact number (11 digits, starts with 09): ").strip()
        if not contact:
            print("❌ Contact cannot be empty.")
            continue
        if not contact.isdigit():
            print("❌ Contact number must contain only digits.")
        elif len(contact) != 11:
            print("❌ Contact number must be exactly 11 digits.")
        elif not contact.startswith("09"):
            print("❌ Contact number must start with '09'.")
        else:
            return contact

def validate_date_str(d):
    """Return True if d is YYYY-MM-DD, False otherwise."""
    if not d:
        return False
    try:
        datetime.strptime(d, "%Y-%m-%d")
        return True
    except ValueError:
        return False
