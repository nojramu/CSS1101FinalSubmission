# main.py
from data_handler import load_data, auto_archive_inactive, save_data, ARCHIVE_FILE
from patient_ops import (
    create_patient, update_patient, view_patients, view_balance_stats, view_schedule, dashboard
)
from data_handler import load_data as load_from_file

import os
import sys
import time
import shutil

def type_effect(text, delay=0.03):
    """Simulate typing effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def progress_bar(task="Loading", duration=2.5):
    """Simulate a loading progress bar."""
    width = shutil.get_terminal_size().columns - 30
    steps = 30
    type_effect(f"{task}...")
    for i in range(steps + 1):
        bar = "█" * i + "-" * (steps - i)
        sys.stdout.write(f"\r[{bar}] {int(i/steps*100)}%")
        sys.stdout.flush()
        time.sleep(duration / steps)
    print("\n")

def show_ascii_logo():
    """Display ASCII logo of the clinic app."""
    logo = r"""
██████╗ ███████╗███╗   ██╗████████╗ █████╗ ██╗     
██╔══██╗██╔════╝████╗  ██║╚══██╔══╝██╔══██╗██║     
██║  ██║█████╗  ██╔██╗ ██║   ██║   ███████║██║     
██║  ██║██╔══╝  ██║╚██╗██║   ██║   ██╔══██║██║     
██████╔╝███████╗██║ ╚████║   ██║   ██║  ██║███████╗
╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚══════╝
              🦷 Dental Clinic Management System 🦷
    """
    print(logo)

def cinematic_intro():
    """Run a cinematic 'hackerman' style intro."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("===============================================")
    type_effect("Initializing secure system connection...")
    progress_bar("Loading patient database", 2)
    progress_bar("Verifying records integrity", 2)
    progress_bar("Activating user interface", 1.5)
    time.sleep(0.5)
    type_effect("🧠 AI Module: Online")
    type_effect("💾 Data Module: Ready")
    type_effect("🦷 System Diagnostics: OK")
    print("===============================================")
    time.sleep(0.8)
    os.system('cls' if os.name == 'nt' else 'clear')
    show_ascii_logo()
    type_effect("\nWelcome, Doctor! Your digital assistant is now online. 🖥️")
    time.sleep(1)
    print("===============================================\n")



def main():

    #cinematic_intro()

    patients = load_data()
    patients = auto_archive_inactive(patients)

    while True:
        dashboard(patients)
        print("""
======== DENTAL CLINIC CRUD APP ========
1. Create New Patient
2. Update Patient Info
3. View Active Patients
4. View Archived Patients
5. View Floating Balance Stats
6. View Incoming Schedules
7. Exit
""")
        choice = input("Enter choice (1-7): ").strip()

        if choice == "1":
            create_patient(patients)
        elif choice == "2":
            update_patient(patients)
        elif choice == "3":
            view_patients(patients, show_active=True)
        elif choice == "4":
            archived = load_from_file(ARCHIVE_FILE)
            view_patients(archived, show_active=False)
        # elif choice == "5":
        #     archive_patient(patients)
        elif choice == "5":
            view_balance_stats(patients)
        elif choice == "6":
            view_schedule(patients)
        elif choice == "7":
            print("👋 Exiting program... Goodbye!")
            save_data(patients)  # ensure final save
            break
        else:
            print("❌ Invalid choice. Try again.\n")

        # refresh and auto-archive on loop
        patients = load_data()
        patients = auto_archive_inactive(patients)

if __name__ == "__main__":
    main()
