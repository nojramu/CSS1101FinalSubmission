# IMPORTS AND SETUP
import json
import os
from datetime import datetime
from colorama import init, Fore

init(autoreset=True)  # for colored outputs

# DATA HANDLING
ARCHIVE_FILE = "barangay_archived.json"

def load_data(file_name):
    """Load data from JSON file or create a new one if it doesn't exist."""
    if not os.path.exists(file_name):
        with open(file_name, "w") as f:
            json.dump({"transactions": []}, f, indent=4)
    with open(file_name, "r") as f:
        return json.load(f)

def save_data(data, file_name):
    """Save updated data to JSON file."""
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)

def get_current_month_file():
    """Return JSON filename for current month."""
    month_str = datetime.now().strftime("%Y-%m")
    return f"barangay_data_{month_str}.json"

def load_archive():
    """Load archived transactions from archive file."""
    if not os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, "w") as f:
            json.dump({"archived": []}, f, indent=4)
    with open(ARCHIVE_FILE, "r") as f:
        return json.load(f)

def save_archive(archive):
    """Save archived transactions."""
    with open(ARCHIVE_FILE, "w") as f:
        json.dump(archive, f, indent=4)

# ARCHIVE PREVIOUS MONTH TRANSACTIONS AUTOMATICALLY
def auto_archive_previous_month():
    archive = load_archive()
    current_month = datetime.now().strftime("%Y-%m")

    for file in os.listdir():
        if file.startswith("barangay_data_") and file.endswith(".json") and current_month not in file:
            data = load_data(file)
            if "transactions" in data and data["transactions"]:
                archive["archived"].extend(data["transactions"])
                save_archive(archive)
                print(Fore.GREEN + f"Archived transactions from {file}.")
            os.remove(file)  # remove old month file after archiving

# TRANSACTION NUMBER
def generate_transaction_number(data):
    """Generate unique transaction number based on today's date MMDDYY and increment."""
    today_str = datetime.now().strftime("%m%d%y")
    existing_numbers = [t['transaction_number'] for t in data['transactions'] if t['transaction_number'].startswith(today_str)]
    for i in range(1, 100):
        num = f"{today_str}{i:02d}"
        if num not in existing_numbers:
            return num
    raise ValueError("Maximum number of transactions for today reached.")

# CALCULATE FEE
def calculate_fee(document_type):
    fees = {
        "Certificate of Indigency": 0,
        "Cedula": 50,
        "Barangay Clearance": 40,
        "Certificate of Good Conduct": 0
    }
    return fees.get(document_type, 0)

# DASHBOARD
def show_dashboard():
    data = load_data(get_current_month_file())
    total = len(data["transactions"])
    pending = sum(1 for t in data["transactions"] if t["status"] == "Pending")
    completed = sum(1 for t in data["transactions"] if t["status"] == "Completed")
    print(Fore.BLUE + "\n===================================================")
    print("Welcome to Barangay San Pascual Document Request Dashboard.")
    print("===================================================")
    print(f"Total Requests Submitted: {total}")
    print(f"Pending Requests: {pending}")
    print(f"Completed Requests: {completed}")
    print("===================================================\n")

# ADDRESS INPUT
def input_address():
    house_number = input("Enter House Number: ").strip()
    streets = ["San Bartolome St.", "Sta. Cruz", "Nazareno", "San Juan", "Sto. Nino", "Delarosa"]
    print("\nChoose your Street:")
    for idx, street in enumerate(streets, 1):
        print(f"{idx}. {street}")
    while True:
        choice = input("Enter choice (1-6): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= 6:
            street_selected = streets[int(choice)-1]
            break
        else:
            print(Fore.RED + "Invalid choice. Try again.")
    full_address = f"{house_number}, {street_selected}, San Pascual Obando Bulacan"
    return full_address

# NEW TRANSACTION
def new_transaction():
    data_file = get_current_month_file()
    data = load_data(data_file)
    transaction_number = generate_transaction_number(data)
    documents = []

    while True:
        print("\nSelect document to request:")
        print("1. Certificate of Indigency (FREE)")
        print("2. Cedula (₱50)")
        print("3. Barangay Clearance (₱40)")
        print("4. Certificate of Good Conduct (FREE)")

        doc_types = {"1": "Certificate of Indigency", "2": "Cedula",
                     "3": "Barangay Clearance", "4": "Certificate of Good Conduct"}
        choice = input("Choice (1-4): ").strip()
        document_type = doc_types.get(choice)
        if not document_type:
            print(Fore.RED + "Invalid selection.")
            continue

        print(Fore.YELLOW + f"\n--- Enter details for {document_type} ---")
        first_name = input("First Name: ").strip()
        last_name = input("Last Name: ").strip()
        doc = {
            "type": document_type,
            "First Name": first_name,
            "Last Name": last_name,
            "Home Address": input_address(),
            "Age": input("Age: ").strip(),
            "Purpose": input("Purpose: ").strip()
        }

        if document_type in ["Certificate of Indigency", "Cedula"]:
            while True:
                try:
                    income = float(input("Monthly Income: "))
                    if document_type == "Certificate of Indigency" and income > 20000:
                        print(Fore.RED + "Income exceeds ₱20,000. Cannot request Certificate of Indigency.\n")
                        return
                    doc["Monthly Income"] = income
                    break
                except ValueError:
                    print(Fore.RED + "Invalid input. Enter numeric value.")

        doc["Fee"] = calculate_fee(document_type)
        documents.append(doc)

        another = input("Request another document under same transaction? (y/n): ").lower()
        if another != 'y':
            break

    total_fee = sum(d["Fee"] for d in documents)
    transaction = {
        "transaction_number": transaction_number,
        "documents": documents,
        "total_fee": total_fee,
        "status": "Pending",
        "date_created": datetime.now().strftime("%Y-%m-%d")
    }

    data["transactions"].append(transaction)
    save_data(data, data_file)
    print(Fore.GREEN + f"\nTransaction #{transaction_number} recorded! Total Fee: ₱{total_fee}")

# VIEW TRANSACTIONS
def view_transactions():
    data_file = get_current_month_file()
    data = load_data(data_file)
    if not data["transactions"]:
        print(Fore.YELLOW + "No transactions available.")
        return
    choice = input("View Daily or Monthly transactions? (D/M): ").upper()
    today = datetime.now().strftime("%Y-%m-%d")
    month = datetime.now().strftime("%Y-%m")
    filtered = []
    if choice == "D":
        filtered = [t for t in data["transactions"] if t["date_created"] == today]
        print(Fore.CYAN + f"\n--- Transactions Today ({today}) ---")
    else:
        filtered = [t for t in data["transactions"] if t["date_created"].startswith(month)]
        print(Fore.CYAN + f"\n--- Transactions This Month ({month}) ---")
    for t in filtered:
        print(Fore.MAGENTA + f"\nTransaction #: {t['transaction_number']} | Status: {t['status']} | Total Fee: ₱{t['total_fee']}")
        for i, doc in enumerate(t["documents"], 1):
            print(f"  Document {i}: {doc['type']}")
            for k, v in doc.items():
                if k != "type":
                    print(f"    {k}: {v}")

# SEARCH / UPDATE / MARK COMPLETE
def manage_transaction():
    data_file = get_current_month_file()
    data = load_data(data_file)
    while True:
        print("\nSearch Transaction by:")
        print("1. Transaction Number")
        print("2. Status")
        print("3. Date Created")
        print("4. Go Back")
        choice = input("Choice (1-4): ").strip()

        if choice == "4":
            return
        elif choice == "1":
            txn_num = input("Enter Transaction Number: ").strip()
            filtered = [t for t in data["transactions"] if t["transaction_number"] == txn_num]
        elif choice == "2":
            print("Statuses: Pending, Completed")
            status = input("Enter Status: ").capitalize()
            filtered = [t for t in data["transactions"] if t["status"] == status]
        elif choice == "3":
            date_str = input("Enter Date (YYYY-MM-DD): ").strip()
            filtered = [t for t in data["transactions"] if t["date_created"] == date_str]
        else:
            print(Fore.RED + "Invalid choice.")
            continue

        if not filtered:
            print(Fore.YELLOW + "No matching transactions found.")
            continue

        for t in filtered:
            print(Fore.CYAN + f"\nTransaction #: {t['transaction_number']} | Status: {t['status']} | Total Fee: ₱{t['total_fee']}")
            for i, doc in enumerate(t["documents"], 1):
                print(f"  Document {i}: {doc['type']}")
                for k, v in doc.items():
                    if k != "type":
                        print(f"    {k}: {v}")

        if len(filtered) == 1:
            transaction = filtered[0]
        else:
            txn_num = input("Enter Transaction Number to manage (or 'B' to go back): ").strip()
            if txn_num.upper() == 'B':
                return
            transaction = next((t for t in data["transactions"] if t["transaction_number"] == txn_num), None)
            if not transaction:
                print(Fore.RED + "Transaction not found.")
                continue

        print("\n1. Update Transaction")
        print("2. Mark as Complete")
        print("3. Go Back")
        action = input("Choose action (1-3): ").strip()

        if action == "3":
            return
        elif action == "1":
            print("\nWhich document to update?")
            for i, doc in enumerate(transaction["documents"], 1):
                print(f"{i}. {doc['type']}")
            doc_choice = input("Document number (or 'B' to go back): ")
            if doc_choice.upper() == 'B':
                continue
            if not doc_choice.isdigit() or int(doc_choice) not in range(1, len(transaction["documents"]) + 1):
                print(Fore.RED + "Invalid selection.")
                continue
            doc = transaction["documents"][int(doc_choice) - 1]
            # Change document type
            print("Select new document type:")
            doc_types = ["Certificate of Indigency", "Cedula", "Barangay Clearance", "Certificate of Good Conduct"]
            for i, d in enumerate(doc_types, 1):
                print(f"{i}. {d}")
            new_type_choice = input("Choice (or 'B' to go back): ")
            if new_type_choice.upper() == 'B':
                continue
            if new_type_choice.isdigit() and 1 <= int(new_type_choice) <= 4:
                doc["type"] = doc_types[int(new_type_choice) - 1]
                doc["Fee"] = calculate_fee(doc["type"])
            for field in doc.keys():
                if field not in ["type", "Fee"]:
                    new_val = input(f"Enter new {field} (leave blank to keep '{doc[field]}'): ")
                    if new_val.strip():
                        doc[field] = new_val
            transaction["total_fee"] = sum(d["Fee"] for d in transaction["documents"])
            save_data(data, data_file)
            print(Fore.GREEN + "Transaction updated successfully.")
        elif action == "2":
            transaction["status"] = "Completed"
            save_data(data, data_file)
            print(Fore.GREEN + "Transaction marked as completed successfully.")
        else:
            print(Fore.RED + "Invalid action.")

# MAIN MENU
def main():
    auto_archive_previous_month()  # Automatically archive old transactions at program start
    while True:
        show_dashboard()
        print("Menu Options:")
        print("1. New Transaction")
        print("2. View Transactions (Daily/Monthly)")
        print("3. Search / Manage Transaction")
        print("4. Exit")

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            new_transaction()
        elif choice == "2":
            view_transactions()
        elif choice == "3":
            manage_transaction()
        elif choice == "4":
            print(Fore.BLUE + "\nThank you for using Barangay San Pascual Document Request System.")
            break
        else:
            print(Fore.RED + "Invalid choice.")

        input("\nPress Enter to return to dashboard...")

# ENTRY POINT
if __name__ == "__main__":
    main()
