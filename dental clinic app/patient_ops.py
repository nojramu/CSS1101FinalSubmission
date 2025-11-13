# patient_ops.py
from datetime import date, datetime
from data_handler import load_data, save_data, ARCHIVE_FILE
from validation import validate_contact, validate_date_str



# Note: load_data/save_data come from data_handler and use default ACTIVE_FILE

def find_patient(patients, name):
    """Find patient(s) by partial name (case insensitive)."""
    matches = [
        p for p in patients
        if name.lower() in p.get("firstName", "").lower() or name.lower() in p.get("lastName", "").lower()
    ]

    if not matches:
        print("❌ No patient found with that name.")
        return None

    # Always show list to choose from (even if 1 match)
    print("\nMatching patients:")
    for i, p in enumerate(matches, 1):
        print(f"{i}. {p.get('firstName','')} {p.get('lastName','')}")
    while True:
        try:
            choice = int(input("Select patient number: "))
            if 1 <= choice <= len(matches):
                return matches[choice - 1]
            else:
                print("❌ Invalid selection. Try again.")
        except ValueError:
            print("❌ Please enter a valid number.")


def create_patient(patients):
    print("\n--- Create New Patient ---")
    first_name = input("Enter first name: ").strip()
    last_name = input("Enter last name: ").strip()
    bday = input("Enter birthday (YYYY-MM-DD): ").strip()
    if bday and not validate_date_str(bday):
        print("❌ Invalid birthday format. Use YYYY-MM-DD.")
        return
    contact = validate_contact()

    new_patient = {
        "firstName": first_name,
        "lastName": last_name,
        "bday": bday,
        "contact": contact,
        "balance": 0.0,
        "schedule": "",
        "scheduleStatus": False,  # means appointment pending
        "procedure": [],            # store history as list of dicts
        "status": "paid",
        "isActive": True,
        "lastUpdated": date.today().isoformat()
    }

    patients.append(new_patient)
    save_data(patients)
    print(f"\n✅ Patient '{first_name} {last_name}' added successfully!\n")


def update_patient(patients):
    print("\n--- Update Patient Info ---")
    name = input("Enter patient name to update: ")
    patient = find_patient(patients, name)
    if not patient:
        return

    while True:
        print(f"\nEditing patient: {patient['firstName']} {patient['lastName']}")
        print(f"Birthday: {patient.get('bday','')}")
        print(f"Contact: {patient.get('contact','')}")
        print(f"Balance: ₱{patient.get('balance',0.0)}")
        print(f"Next Schedule: {patient.get('schedule','')}")
        print("Procedure History:")

        # Show procedure history properly
        if isinstance(patient.get("procedure"), list) and patient["procedure"]:
            for i, proc in enumerate(patient["procedure"], 1):
                print(f"  {i}. {proc.get('name','')} - ₱{proc.get('amount',0)} ({proc.get('date','')})")
        else:
            print("  No procedure history yet.")

        print(f"Status: {patient.get('status','')}")
        print(f"Active: {patient.get('isActive', True)}")
        print("\nChoose what to edit:")
        print("1. First Name")
        print("2. Last Name")
        print("3. Contact")
        # print("4. Balance (not editable)")
        print("4. Schedule")
        print("5. Edit All")
        print("6. Schedule Status")
        print("7. Update Procedure")
        print("8. Settle Balance")
        print("9. Exit Update Mode")
       
        choice = input("Enter your choice (1-9): ").strip()

        if choice == "1":
            patient["firstName"] = input("Enter new first name: ").strip()
            print("✅ First name updated!")
        elif choice == "2":
            patient["lastName"] = input("Enter new last name: ").strip()
            print("✅ Last name updated!")
        elif choice == "3":
            patient["contact"] = validate_contact()
            print("✅ Contact updated successfully!")
        # elif choice == "4":
        #     print("❌ You cannot directly edit balance. Please use 'Update Procedure / Add Payment' instead.")
        elif choice == "4":
            sched = input("Enter new appointment (YYYY-MM-DD): ").strip()
            if sched:
                try:
                    # Try parsing to a valid date
                    parsed_date = datetime.strptime(sched, "%Y-%m-%d")
                    # Always save as zero-padded format (YYYY-MM-DD)
                    sched = parsed_date.strftime("%Y-%m-%d")
                    patient["schedule"] = sched
                    patient["scheduleStatus"] = False
                    print(f"✅ Schedule updated to {sched}!")
                except ValueError:
                    print("❌ Invalid date format. Please use YYYY-MM-DD.")
            else:
                print("ℹ️ Schedule not changed.")

        elif choice == "5":
            print("\nLeave blank if you don’t want to change a field.")
            fn = input(f"New first name ({patient['firstName']}): ").strip() or patient["firstName"]
            ln = input(f"New last name ({patient['lastName']}): ").strip() or patient["lastName"]
            while True:
                contact_input = input(f"New contact ({patient['contact']}): ").strip()
                if not contact_input:
                    # leave old contact unchanged
                    contact_input = patient["contact"]
                    break
                elif not contact_input.isdigit():
                    print("❌ Contact number must contain only digits.")
                elif len(contact_input) != 11:
                    print("❌ Contact number must be exactly 11 digits.")
                elif not contact_input.startswith("09"):
                    print("❌ Contact number must start with '09'.")
                else:
                    break  # ✅ valid input
                   
            # sched = input(f"New schedule ({patient.get('schedule','')}): ").strip() or patient.get('schedule','')
            # patient["firstName"], patient["lastName"] = fn, ln
            # patient["schedule"] = sched
            # print("✅ All editable fields updated successfully!")

        elif choice == "6":
            print("\n--- Mark Patient Visit as Done ---")

            # Check if the patient has a schedule
            if not patient.get("schedule"):
                print("❌ No schedule found for this patient.")
            else:
                today = date.today().isoformat()
                print(f"🗓️ Current schedule: {patient['schedule']}")

                # Always ask first before marking as done
                confirm = input("Do you want to mark this visit as done? (y/n): ").strip().lower()
                if confirm != "y":
                    print("ℹ️ Visit not marked.")
                    continue  # back to update menu

                # Warn if scheduled date is not today
                if patient["schedule"] != today:
                    confirm2 = input("⚠️ The scheduled date is not today. Still mark as done? (y/n): ").strip().lower()
                    if confirm2 != "y":
                        print("ℹ️ Visit not marked.")
                        continue  # back to update menu

                # Mark as visited
                patient["scheduleStatus"] = True
                print("✅ Visit marked as completed and removed from upcoming appointments.")



        elif choice == "7":
            print("\n--- Update Procedure / Add Payment ---")
            procedure_name = input("Enter procedure name: ").strip()
            if not procedure_name:
                print("❌ Procedure name cannot be empty.")
                continue

            # amount input validation
            while True:
                payment_input = input("Enter payment amount: ₱").strip()
                if not payment_input:
                    print("❌ Amount cannot be empty.")
                    continue
                try:
                    amount = float(payment_input)
                    if amount < 0:
                        print("❌ Amount cannot be negative.")
                        continue
                    break
                except ValueError:
                    print("❌ Invalid amount. Please enter a number.")

            # initialize procedure list if missing
            if not isinstance(patient.get("procedure"), list):
                patient["procedure"] = []

            # append procedure dict
            proc_entry = {
                "name": procedure_name,
                "amount": amount,
                "date": date.today().isoformat()
            }
            patient["procedure"].append(proc_entry)

            # update balance & status
            patient["balance"] = float(patient.get("balance", 0.0)) + amount
            patient["status"] = "unpaid" if patient["balance"] > 0 else "paid"

            print("✅ Procedure added and recorded to history!")

        elif choice == "8":
            print("\n--- Settle Balance ---")

            # ✅ Show detailed procedure history with partial payments
            if "procedure" in patient and patient["procedure"]:
                print("\n🦷 Procedure History:")
                for i, p in enumerate(patient["procedure"], 1):
                    paid = p.get("paid", 0.0)
                    remaining = p["amount"] - paid
                    print(f"  {i}. {p['name']} - ₱{p['amount']} | Paid: ₱{paid} | Remaining: ₱{remaining} ({p['date']})")
            else:
                print("No recorded procedures yet.")

            # ✅ Show total balance
            total_balance = patient.get("balance", 0)
            if total_balance <= 0:
                print("\n✅ No balance to settle.")
            else:
                print(f"\nCurrent total balance: ₱{total_balance}")

                while True:
                    payment_input = input("Enter payment amount: ₱").strip()
                    if not payment_input:
                        print("❌ Payment cannot be empty. Please enter a valid number.")
                        continue
                    try:
                        payment = float(payment_input)
                        if payment < 0:
                            print("❌ Payment cannot be negative.")
                            continue
                        if payment > total_balance:
                            print(f"❌ Payment cannot exceed the total balance of ₱{total_balance}.")
                            continue
                        break
                    except ValueError:
                        print("❌ Invalid input. Please enter a number.")

                remaining_payment = payment

                # ✅ Apply payment to procedures in order
                for p in patient["procedure"]:
                    unpaid = p["amount"] - p.get("paid", 0.0)
                    if unpaid <= 0:
                        continue  # already fully paid
                    if remaining_payment >= unpaid:
                        p["paid"] = p.get("paid", 0.0) + unpaid
                        remaining_payment -= unpaid
                    else:
                        p["paid"] = p.get("paid", 0.0) + remaining_payment
                        remaining_payment = 0
                        break

                # ✅ Recalculate balance
                total_paid = sum(p.get("paid", 0.0) for p in patient["procedure"])
                total_due = sum(p["amount"] for p in patient["procedure"])
                patient["balance"] = total_due - total_paid

                # ✅ Update status
                if patient["balance"] <= 0:
                    patient["balance"] = 0
                    patient["status"] = "paid"
                    print("\n✅ Balance fully settled!")
                else:
                    patient["status"] = "unpaid"
                    print(f"\nPartial payment accepted. Remaining balance: ₱{patient['balance']}")

            # ✅ Save updates
            patient["lastUpdated"] = date.today().isoformat()
            save_data(patients)




        elif choice == "9":
            print("💾 Changes saved. Exiting update mode...\n")
            break
        else:
            print("❌ Invalid choice. Try again.")

        # update timestamp and save
        patient["lastUpdated"] = date.today().isoformat()
        save_data(patients)
        
def view_patients(patients, show_active=True):
    print("\n--- Patient List ---")
    filtered = [p for p in patients if p["isActive"] == show_active]
    if not filtered:
        print("No patients found.\n")
        return
    for p in filtered:
        print(f"\nName: {p['firstName']} {p['lastName']}")
        print(f"Birthday: {p['bday']}")
        print(f"Contact: {p['contact']}")
        print(f"Balance: ₱{p['balance']}")
        print(f"Next Schedule: {p['schedule']}")
        #print(f"Procedure: {p['procedure']}")
        if isinstance(p["procedure"], list):
            print("Procedure History:")
            for pr in p["procedure"]:
                print(f"  - {pr['name']} (₱{pr['amount']}) on {pr['date']}")
        else:
            print(f"Procedure: {p['procedure']}")

        print(f"Status: {p['status']}")
        print(f"Active: {p['isActive']}")
    print()

# def archive_patient(patients):
#     print("\n--- Archive Patient ---")
#     name = input("Enter patient name to archive: ")
#     patient = find_patient(patients, name)
#     if not patient:
#         return

#     archived = load_data(ARCHIVE_FILE)
#     patient["isActive"] = False
#     archived.append(patient)
#     patients.remove(patient)

#     save_data(patients)
#     save_data(archived, ARCHIVE_FILE)
#     print(f"📦 Patient '{patient['firstName']} {patient['lastName']}' archived.\n")

#     def view_balance_stats(patients):
#         print("\n--- Floating Balance Stats ---")
#         found = False  # flag to track if any unpaid balance was shown

#         for p in patients:
#             if p.get("isActive", True) and p.get("status") == "unpaid" and p.get("balance", 0) > 0:
#                 print(f"{p['firstName']} {p['lastName']}: ₱{p['balance']}")
#                 found = True

#         if not found:
#             print("✅ No outstanding balances. All patients are fully paid!")
#         print()

def archive_patient(patients):
    print("\n--- Archive Patient ---")
    name = input("Enter patient name to archive: ")
    patient = find_patient(patients, name)
    if not patient:
        return

    archived = load_data(ARCHIVE_FILE)
    patient["isActive"] = False
    archived.append(patient)
    patients.remove(patient)

    save_data(patients)
    save_data(archived, ARCHIVE_FILE)
    print(f"📦 Patient '{patient['firstName']} {patient['lastName']}' archived.\n")


def view_balance_stats(patients):
    print("\n--- Floating Balance Stats ---")
    found = False  # flag to track if any unpaid balance was shown

    for p in patients:
        if p.get("isActive", True) and p.get("status") == "unpaid" and p.get("balance", 0) > 0:
            print(f"{p['firstName']} {p['lastName']}: ₱{p['balance']}")
            found = True

    if not found:
        print("✅ No outstanding balances. All patients are fully paid!")
    print()





def view_schedule(patients):
    print("\n--- Upcoming Appointments ---")
    found = False
    today = date.today()

    for p in patients:
        schedule_str = p.get("schedule", "").strip()
        if not schedule_str:
            continue  # skip if no schedule at all

        # parse schedule safely
        try:
            sched_date = datetime.strptime(schedule_str, "%Y-%m-%d").date()
        except ValueError:
            # skip invalid date formats
            continue

        # Only show active patients with schedule today or future.
        # If schedule is today and scheduleStatus is True (visited), skip it.
        if not p.get("isActive", True):
            continue

        if sched_date < today:
            # optional: you might want to show past schedules somewhere else
            continue

        if sched_date == today and p.get("scheduleStatus", False):
            # visited already today -> do not show
            continue

        # show upcoming (today or future) appointments that are not visited today
        print(f"{p['firstName']} {p['lastName']} - Next Appointment: {p['schedule']}")
        found = True

    if not found:
        print("✅ No upcoming appointments. All schedules are completed!")
    print()



# ----------------- Dashboard -----------------

def dashboard(patients):
    today = date.today().isoformat()

    # Show only patients scheduled today, still active, and not yet visited
    todays_patients = [
        f"{p['firstName']} {p['lastName']}"
        for p in patients
        if p.get("schedule") == today and p.get("isActive", True) and not p.get("scheduleStatus", False)
    ]

    unpaid_count = sum(1 for p in patients if p.get("status") == "unpaid" and p.get("isActive", True))

    print("\n===============================================")
    print(f"🦷  Today’s Date: {today}")
    print(f"📅  Appointments Today: {len(todays_patients)} | Names: {', '.join(todays_patients) or 'None'}")
    print(f"💰  Unpaid Patients: {unpaid_count}")
    print("===============================================\n")

