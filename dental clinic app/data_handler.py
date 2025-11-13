import json
import os
import sys
from datetime import date, datetime, timedelta

def resource_path(relative_path):
    """
    Get absolute path to resource, works for both development and PyInstaller .exe
    """
    try:
        base_path = sys._MEIPASS  # Temporary folder used by PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# File paths (safe for PyInstaller)
ACTIVE_FILE = resource_path("active_patients.json")
ARCHIVE_FILE = resource_path("archived_patients.json")

def load_data(file=ACTIVE_FILE):
    """Load patient data from JSON file."""
    if not os.path.exists(file):
        return []
    with open(file, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_data(patients, file=ACTIVE_FILE):
    """Save patient data to JSON file."""
    with open(file, "w", encoding="utf-8") as f:
        json.dump(patients, f, indent=4, ensure_ascii=False)

def auto_archive_inactive(patients):
    """
    Move patients not updated for 3 months to archive.
    Returns the active list after moving old records to archive file.
    """
    active = []
    archived = load_data(ARCHIVE_FILE)
    today = date.today()

    for p in patients:
        # If lastUpdated missing, treat as today to avoid accidental archiving
        last_str = p.get("lastUpdated", date.today().isoformat())
        try:
            last_updated = datetime.strptime(last_str, "%Y-%m-%d").date()
        except Exception:
            # try fallback format with time, else use today
            try:
                last_updated = datetime.strptime(last_str, "%Y-%m-%d %H:%M:%S").date()
            except Exception:
                last_updated = today

        if today - last_updated > timedelta(days=90) or not p.get("isActive", True):
            p["isActive"] = False
            archived.append(p)
        else:
            active.append(p)

    save_data(active, ACTIVE_FILE)
    save_data(archived, ARCHIVE_FILE)
    return active
