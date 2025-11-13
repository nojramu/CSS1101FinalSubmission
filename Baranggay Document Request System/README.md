# 🏛️ Barangay San Pascual Document Request System

A **Python-based console application** that allows residents to conveniently request official barangay documents, view their transactions, update or complete them, and automatically manage monthly records and archives.

---

## 📘 Features

### 🧾 Transaction Management
- Create new transactions with **auto-generated unique transaction numbers**  
  Format: `MMDDYYXX` (e.g., `11022501`)
- Supports multiple document requests under one transaction.
- Automatically calculates fees based on document type.

### 📅 Date-Based Viewing
- View only the transactions made **today**.
- View all **transactions for the current month**.
- New JSON file is created **every month** for easy record separation.

### 🔍 Search, Update, and Complete Transactions
- Unified interface for:
  - Searching by **Transaction Number**, **Date**, or **Status**.
  - Updating transaction details:
    - Change document type (fee auto-recalculates)
    - Edit first name, last name, purpose, and address
  - Marking a transaction as **Completed**

### 📦 Automatic Archiving
- Transactions are automatically archived when a new month starts.
- Archived transactions are stored in a separate file:  
  `archived_transactions.json`

### 🏠 Simplified Address Input
Users can easily enter their address using guided input:
- Enter House Number  
- Choose from predefined streets:
  - San Bartolome St.
  - Sta. Cruz
  - Nazareno
  - San Juan
  - Sto. Niño
  - Delarosa  
→ Automatically appends *San Pascual, Obando, Bulacan*.

### 🎨 Color-Coded Interface
- Uses the `colorama` library for a vibrant terminal display:
  - 🟩 Green: Success messages  
  - 🟨 Yellow: Warnings  
  - 🟥 Red: Errors  
  - 🟦 Cyan: Headers and prompts  

---

## 🗂️ Document Fees

| Document Type | Fee  |
|---------------|------|
| Certificate of Indigency | ₱0 |
| Cedula | ₱50 |
| Barangay Clearance | ₱40 |
| Certificate of Good Conduct | ₱0 |

> ⚠️ For the **Certificate of Indigency**, applicants with a monthly income **above ₱20,000** are **not qualified**.

---

## 📁 File Structure
BarangaySanPascual/
│
├── main.py # Main program file
├── archived_transactions.json # Archived transactions (auto-managed)
├── barangay_data_2025_11.json # Monthly data file (auto-generated)
└── README.md # Documentation

🧠 How It Works
Dashboard
- Displays statistics:
- Total requests
- Pending requests
- Completed requests

Main Menu
Option	Description
1	Create a new transaction
2	View today's transactions
3	View monthly transactions
4	Search / Update / Complete transactions
5	Exit the system

New Transaction Flow
- Choose document type(s)
- Enter first & last name
- Provide home address (house number + street)
- Specify age and purpose
- (If required) Enter monthly income
- Confirm and view total fee

Search / Update / Complete
After finding a transaction:
- Update details (including changing document type)
- Mark as completed
- Or cancel the operation

🧾 Archiving Rules
When a new month starts, the system:
- Creates a new JSON file for the new month.
- Moves previous transactions to archived_transactions.json.
- Deletes outdated monthly files.

🧑‍💻 Example Run
===================================================
Barangay San Pascual Document Request Dashboard
===================================================
Total Requests: 5
Pending Requests: 2
Completed Requests: 3
===================================================
Menu Options:
1. New Transaction
2. View Today's Transactions
3. View Monthly Transactions
4. Search / Update / Complete Transaction
5. Exit
Enter your choice: 1

🧰 Dependencies
- Library	Purpose
- json	Storing and managing data
- os	File handling
- datetime	Date-based features
- colorama	Colored terminal output

Comments and Suggestions
- Data Management is good.
- The system allows easy access to transactions and updates its details and status.
- Compilation of transactions each day is really helpful for bookkeeping.
- Hoping that this could run in a more user-friendly interface.
- Would consider using in the future once fully developed.
- Would prefer if the users can use the system in their own houses.

📜 License
This project is open-source and free to use for educational or community management purposes.
Developed for Barangay San Pascual, Obando, Bulacan.
----------------------------------

Each monthly JSON file (e.g., `barangay_data_2025_11.json`) stores:
```json
{
    "transactions": [
        {
            "transaction_number": "110225-01",
            "documents": [...],
            "total_fee": 90,
            "status": "Pending",
            "date_created": "2025-11-02"
        }
    ],
    "archived": []
}

-----------------------------------
