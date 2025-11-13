import json
import os
import random
import re
from datetime import datetime, timedelta

DATA_FILE = "data.json"

# Simple color helpers (works on most terminals, no external deps)
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"
    WHITE = "\033[37m"

# Transaction display widths
ID_WIDTH = 6
DATE_WIDTH = 12
TYPE_WIDTH = 8
AMOUNT_WIDTH = 12
CATEGORY_WIDTH = 20
DESC_WIDTH = 25


def color(text, *styles):
    if not styles:
        return text
    return "".join(styles) + str(text) + C.RESET

def strip_ansi(s):
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', s)

def truncate_to_display_width(text, width):
    plain = strip_ansi(text)
    if len(plain) <= width:
        return text
    # Truncate plain to width, then find corresponding index in text
    truncated_plain = plain[:width]
    idx = 0
    plain_idx = 0
    while plain_idx < len(truncated_plain) and idx < len(text):
        if text[idx] == '\x1B':
            # Skip ANSI sequence
            idx += 1
            while idx < len(text) and text[idx] != 'm':
                idx += 1
            if idx < len(text):
                idx += 1
        else:
            plain_idx += 1
            idx += 1
    return text[:idx]

def pad_to_display_width(text, width):
    plain = strip_ansi(text)
    if len(plain) >= width:
        return truncate_to_display_width(text, width)
    padding = width - len(plain)
    return text + ' ' * padding

# --- Helper Functions ---
def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")
    # On Windows cmd, enable ANSI if possible (best-effort)
    try:
        if os.name == "nt":
            os.system("")
    except Exception:
        pass

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "transactions": {}}
    with open(DATA_FILE, "r") as file:
        data = json.load(file)
    if "users" not in data:
        data["users"] = {}
    if "transactions" not in data:
        data["transactions"] = {}
    return data

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def is_valid_email(email):
    return bool(re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email))

def is_valid_password(password):
    # Must contain at least one lowercase, one uppercase, and one number, no special characters
    return bool(re.fullmatch(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z0-9]+", password))

# --- Core Features ---
def sign_up(data):
    clear_terminal()
    print(color("Sign Up", C.BOLD))
    print(color("----------------", C.BOLD))
    print(color("Create a new user account.", C.DIM))
    print()



    confirm = input("Do you really want to sign up? (y/n): ").lower()
    if confirm != "y":
        print("Returning to main menu...")
        input("Press Enter to continue...")
        clear_terminal()
        return

    email = input("Enter your email: ").strip()
    if not is_valid_email(email):
        print(color("❌ Invalid email format!", C.RED, C.BOLD))
        input("Press Enter to continue...")
        return

    username = input("Enter username: ").strip()
    if username in data["users"]:
        print(color("❌ Username already exists.", C.RED, C.BOLD))
        input("Press Enter to continue...")
        return

    while True:
        password = input("Enter password (must include A–Z, a–z, and 0–9 only): ").strip()
        if not is_valid_password(password):
            print(color("❌ Password must have at least one uppercase, one lowercase, one digit, and no special characters.", C.YELLOW))
            continue
        confirm_pass = input("Confirm password: ").strip()
        if password != confirm_pass:
            print(color("❌ Passwords do not match!", C.RED))
            continue
        break

    data["users"][username] = {"email": email, "password": password}
    data["transactions"][username] = []  # This should now work with the fixed load_data()
    save_data(data)
    print(color("✅ Account created successfully!", C.GREEN, C.BOLD))
    input("Press Enter to return to main menu...")

def login(data):
    clear_terminal()
    print(color("Login", C.BOLD))
    print(color("----------------", C.BOLD))
    print(color("Log in to your existing account.", C.DIM))
    print()



    confirm = input("Do you really want to log in? (y/n): ").lower()
    if confirm != "y":
        print("Returning to main menu...")
        input("Press Enter to continue...")
        clear_terminal()
        return

    print(color("\nCredentials", C.BOLD))
    user_input = input("Enter username or email: ").strip()
    username = None
    if is_valid_email(user_input):
        # Find username by email
        for u, info in data["users"].items():
            if info["email"] == user_input:
                username = u
                break
        if not username:
            print("❌ Email not found.")
            input("Press Enter to continue...")
            return None
    else:
        username = user_input
        if username not in data["users"]:
            print("❌ Username not found.")
            input("Press Enter to continue...")
            return None

    password = input("Enter password: ").strip()
    if password != data["users"][username]["password"]:
        print(color("❌ Incorrect password.", C.RED))
        input("Press Enter to continue...")
        return None

    print(color("✅ Login successful!", C.GREEN, C.BOLD))
    input("Press Enter to continue...")
    return username

def add_record(data, username):
    while True:
        clear_terminal()
        print(color("Add Record", C.BOLD))
        print(color("----------------", C.BOLD))
        print(color("Add a new expense or income record.", C.DIM))
        print()



        confirm = input("Do you really want to add a record? (y/n): ").lower()
        if confirm != "y":
            print("Returning to main menu...")
            input("Press Enter to continue...")
            clear_terminal()
            return
        clear_terminal()

        # Validate date with option for today
        while True:
            print(color("Date:", C.BOLD))
            use_today = input("Use today's date? (y/n): ").lower().strip()
            if use_today == "y":
                date = datetime.now().strftime("%Y-%m-%d")
                break
            elif use_today == "n":
                date = input("Enter date (YYYY-MM-DD): ").strip()
                if not date:
                    print("❌ Date cannot be empty.")
                    continue
                try:
                    datetime.strptime(date, "%Y-%m-%d")  # Check format
                    break
                except ValueError:
                    print("❌ Invalid date format. Use YYYY-MM-DD (e.g., 2023-10-15).")
            else:
                print(color("❌ Please enter 'y' or 'n'.", C.YELLOW))

        # Validate type with menu for ease
        while True:
            print(color("\nSelect type:", C.BOLD))
            print("1. Expense")
            print("2. Income")
            type_choice = input("Choose (1 or 2): ").strip()
            if type_choice == "1":
                type_ = "Expense"
                break
            elif type_choice == "2":
                type_ = "Income"
                break
            else:
                print(color("❌ Invalid choice. Enter 1 for Expense or 2 for Income.", C.RED))

        # Validate category based on type
        if type_ == "Expense":
            expense_categories = ["Food & Groceries", "Transportation", "Entertainment", "Personal Needs", "Personal Wants", "Health & Fitness", "Bills", "School/Work"]
            print(color("\nSelect expense category:", C.BOLD))
            for i, cat in enumerate(expense_categories, 1):
                print(f"{i}. {cat}")
            while True:
                cat_choice = input("Choose (1-8): ").strip()
                if cat_choice.isdigit() and 1 <= int(cat_choice) <= 8:
                    category = expense_categories[int(cat_choice) - 1]
                    break
                else:
                    print("❌ Invalid choice. Enter 1-8.")
        else:  # Income
            income_categories = ["Allowance", "Work", "Reward", "Gift"]
            print(color("\nSelect income category:", C.BOLD))
            for i, cat in enumerate(income_categories, 1):
                print(f"{i}. {cat}")
            while True:
                cat_choice = input("Choose (1-4): ").strip()
                if cat_choice.isdigit() and 1 <= int(cat_choice) <= 4:
                    category = income_categories[int(cat_choice) - 1]
                    break
                else:
                    print("❌ Invalid choice. Enter 1-4.")

        # Validate amount
        while True:
            amount_input = input("\nEnter amount: ").strip()
            if not amount_input:
                print("❌ Amount cannot be empty. Please enter a valid number.")
                continue
            try:
                amount = float(amount_input)
                if amount <= 0:
                    print("❌ Amount must be a positive number greater than 0.")
                    continue
                break  # Valid input, exit loop
            except ValueError:
                print("❌ Invalid amount. Please enter a valid number (e.g., 100.50).")

        desc = input("Add description? (y/n): ").lower().strip()
        description = input("Enter description: ").strip() if desc == "y" else "N/A"

        transaction = {
            "id": len(data["transactions"][username]) + 1,
            "date": date,
            "type": type_,
            "amount": amount,
            "category": category,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }

        data["transactions"][username].append(transaction)
        save_data(data)
        print(color("✅ Record added successfully!", C.GREEN, C.BOLD))

        print()
        add_another = input("Add another record? (y/n) or press Enter to exit: ").lower().strip()
        if add_another == "y":
            clear_terminal()
        else:
            break
    input("Press Enter to return to main menu...")

def view_history(data, username):
    clear_terminal()
    print(color("View History", C.BOLD))
    print(color("----------------", C.BOLD))
    print(color("View your transaction history.", C.DIM))
    print()



    transactions = data["transactions"][username]
    if not transactions:
        print("No transactions found.")
        input("Press Enter to return to main menu...")
        return

    print(color("Filter options:", C.BOLD))
    print("1. All transactions")
    print("2. By category")
    print("3. By date")
    print("4. By type (Expense/Income)")
    print("5. Recent transactions")
    print("6. By specific date")
    filter_choice = input("Choose filter (1-6): ").strip()

    filtered = transactions

    if filter_choice == "2":
        clear_terminal()
        print(color("Select type:", C.BOLD))
        print(color("1. Expense", C.WHITE))
        print(color("2. Income", C.WHITE))
        type_choice = input("Choose (1 or 2): ").strip()
        if type_choice == "1":
            type_ = "Expense"
            categories = ["Food & Groceries", "Transportation", "Entertainment", "Personal Needs", "Personal Wants", "Health & Fitness", "Bills", "School/Work"]
        elif type_choice == "2":
            type_ = "Income"
            categories = ["Allowance", "Work", "Reward", "Gift"]
        else:
            print(color("❌ Invalid choice.", C.RED))
            input("Press Enter to continue...")
            return
        # Calculate percentages for categories
        overall_total = sum(t["amount"] for t in transactions if t["type"] == type_)
        category_totals = {}
        for cat in categories:
            category_totals[cat] = sum(t["amount"] for t in transactions if t["category"] == cat and t["type"] == type_)
        print(color(f"\nSelect category for {type_}:", C.BOLD))
        for i, cat in enumerate(categories, 1):
            pct = (category_totals[cat] / overall_total * 100) if overall_total > 0 else 0
            print(color(f"{i}. {cat} ({pct:.1f}%)", C.WHITE))
        cat_choice = input(f"Choose (1-{len(categories)}): ").strip()
        if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
            category = categories[int(cat_choice) - 1]
            filtered = [t for t in transactions if t["category"] == category and t["type"] == type_]
            category_total = category_totals[category]
            pct = (category_total / overall_total * 100) if overall_total > 0 else 0
            clear_terminal()
            print(color(f"---------------- {category} ({pct:.1f}%) ----------------", C.WHITE, C.BOLD))
            # Summary total in white at the top
            print(color(f"Total for {category}: ₱{category_total:.2f}", C.WHITE))
            # Display transactions
            for t in filtered:
                print(color(f"[{t['id']}] {t['date']} | {t['type']} | ₱{t['amount']:.2f} | {t['category']} | {t['description']}", C.DIM))
            # Calculate and display summary
            total_income = sum(t["amount"] for t in filtered if t["type"] == "Income")
            total_expense = sum(t["amount"] for t in filtered if t["type"] == "Expense")
            balance = total_income - total_expense
            print()
            print(color("---------------- Summary ----------------", C.BOLD))
            print(color(f"Total Income: ₱{total_income:.2f}", C.GREEN))
            print(color(f"Total Expenses: ₱{total_expense:.2f}", C.RED))
            bal_color = C.GREEN if balance >= 0 else C.RED
            print(color(f"Total Balance: ₱{balance:.2f}", bal_color, C.BOLD))
            print()
            input("Press Enter to return to main menu...")
            return
        else:
            print(color("❌ Invalid choice.", C.RED))
            input("Press Enter to continue...")
            return
    elif filter_choice == "3":
        clear_terminal()
        print(color("Choose date filter:", C.BOLD))
        print(color("1. Today's transactions", C.WHITE))
        print(color("2. Yesterday's transactions", C.WHITE))
        print(color("3. By Day (how many days?)", C.WHITE))
        print(color("4. By Week (how many weeks?)", C.WHITE))
        print(color("5. By Month (how many months?)", C.WHITE))
        print(color("6. By Year (how many years?)", C.WHITE))
        group_choice = input("Choose (1-6): ").strip()

        def ymd_keys(d):
        # Returns (year, month, day)
            try:
                dt = datetime.strptime(d, "%Y-%m-%d")
                return dt.year, dt.month, dt.day
            except Exception:
                # Fallback if date is malformed
                parts = d.split("-")
                y = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 0
                m = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
                dd = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
                return y, m, dd

        order = input("Ascending or Descending by date (a/d): ").lower().strip()
        filtered = sorted(filtered, key=lambda x: x["date"], reverse=(order == "d"))

        # Calculate overall totals for percentages
        total_income = sum(t["amount"] for t in filtered if t["type"] == "Income")
        total_expense = sum(t["amount"] for t in filtered if t["type"] == "Expense")

        prev_income = None
        prev_expense = None

        if group_choice == "1":
            # Today's transactions
            clear_terminal()
            today = datetime.now().strftime("%Y-%m-%d")
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            filtered = [t for t in transactions if t["date"] == today]
            print(color(f"\n---------------- {today} ----------------", C.BOLD))
            if filtered:
                today_income = sum(t["amount"] for t in filtered if t["type"] == "Income")
                today_expense = sum(t["amount"] for t in filtered if t["type"] == "Expense")
                yesterday_income = sum(t["amount"] for t in transactions if t["date"] == yesterday and t["type"] == "Income")
                yesterday_expense = sum(t["amount"] for t in transactions if t["date"] == yesterday and t["type"] == "Expense")
                income_pct = (today_income / total_income * 100) if total_income > 0 else 0
                expense_pct = (today_expense / total_expense * 100) if total_expense > 0 else 0
                income_change = f" ({(today_income - yesterday_income) / yesterday_income * 100:.1f}% change)" if yesterday_income > 0 else ""
                expense_change = f" ({(today_expense - yesterday_expense) / yesterday_expense * 100:.1f}% change)" if yesterday_expense > 0 else ""
                print(f"Total Income: ₱{today_income:.2f} ({color('{:.1f}'.format(income_pct), C.GREEN)}%){income_change} | Total Expense: ₱{today_expense:.2f} ({color('{:.1f}'.format(expense_pct), C.RED)}%){expense_change} | Savings: ₱{today_income - today_expense:.2f}")
            for t in filtered:
                print(color(f"  [{t['id']}] {t['date']} | {t['type']} | ₱{t['amount']:.2f} | {t['category']} | {t['description']}", C.DIM))
        elif group_choice == "2":
            # Yesterday's transactions
            clear_terminal()
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            day_before = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
            filtered = [t for t in transactions if t["date"] == yesterday]
            print(color(f"\n---------------- {yesterday} ----------------", C.BOLD))
            if filtered:
                yesterday_income = sum(t["amount"] for t in filtered if t["type"] == "Income")
                yesterday_expense = sum(t["amount"] for t in filtered if t["type"] == "Expense")
                day_before_income = sum(t["amount"] for t in transactions if t["date"] == day_before and t["type"] == "Income")
                day_before_expense = sum(t["amount"] for t in transactions if t["date"] == day_before and t["type"] == "Expense")
                income_pct = (yesterday_income / total_income * 100) if total_income > 0 else 0
                expense_pct = (yesterday_expense / total_expense * 100) if total_expense > 0 else 0
                income_change = f" ({(yesterday_income - day_before_income) / day_before_income * 100:.1f}% change)" if day_before_income > 0 else ""
                expense_change = f" ({(yesterday_expense - day_before_expense) / day_before_expense * 100:.1f}% change)" if day_before_expense > 0 else ""
                print(f"Total Income: ₱{yesterday_income:.2f} ({color('{:.1f}'.format(income_pct), C.GREEN)}%){income_change} | Total Expense: ₱{yesterday_expense:.2f} ({color('{:.1f}'.format(expense_pct), C.RED)}%){expense_change} | Savings: ₱{yesterday_income - yesterday_expense:.2f}")
            for t in filtered:
                print(color(f"  [{t['id']}] {t['date']} | {t['type']} | ₱{t['amount']:.2f} | {t['category']} | {t['description']}", C.DIM))
        elif group_choice == "3":
            # Group by day (YYYY-MM-DD)
            while True:
                num_input = input("How many days? (enter number or 'all'): ").strip().lower()
                if not num_input:
                    print("❌ Input cannot be empty.")
                    continue
                if num_input == 'all':
                    num = None  # Will handle all
                    break
                try:
                    num = int(num_input)
                    if num <= 0:
                        print("❌ Number must be a positive integer.")
                        continue
                    break
                except ValueError:
                    print("❌ Invalid input. Enter a positive integer or 'all'.")
            groups = {}
            if num is None:
                # All days
                for t in filtered:
                    groups.setdefault(t["date"], []).append(t)
            else:
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=num)
                for t in transactions:
                    dt = datetime.strptime(t["date"], "%Y-%m-%d").date()
                    if start_date <= dt <= end_date:
                        groups.setdefault(t["date"], []).append(t)
            sorted_keys = sorted(groups.keys(), reverse=(order == "d"))
            prev_income = None
            prev_expense = None
            for key in sorted_keys:
                print(color(f"\n---------------- {key} ----------------", C.BOLD))
                income_total = sum(x["amount"] for x in groups[key] if x["type"] == "Income")
                expense_total = sum(x["amount"] for x in groups[key] if x["type"] == "Expense")
                income_pct = (income_total / total_income * 100) if total_income > 0 else 0
                expense_pct = (expense_total / total_expense * 100) if total_expense > 0 else 0
                income_change = f" ({(income_total - prev_income) / prev_income * 100:.1f}% change)" if prev_income and prev_income > 0 else ""
                expense_change = f" ({(expense_total - prev_expense) / prev_expense * 100:.1f}% change)" if prev_expense and prev_expense > 0 else ""
                print(f"Total Income: ₱{income_total:.2f} ({color('{:.1f}'.format(income_pct), C.GREEN)}%){income_change} | Total Expense: ₱{expense_total:.2f} ({color('{:.1f}'.format(expense_pct), C.RED)}%){expense_change} | Savings: ₱{income_total - expense_total:.2f}")
                for t in groups[key]:
                    print(color(f"  [{t['id']}] {t['date']} | {t['type']} | ₱{t['amount']:.2f} | {t['category']} | {t['description']}", C.DIM))
                prev_income = income_total
                prev_expense = expense_total
        elif group_choice == "4":
            # Group by week (YYYY-WW)
            while True:
                num_input = input("How many weeks? (enter number or 'all'): ").strip().lower()
                if not num_input:
                    print("❌ Input cannot be empty.")
                    continue
                if num_input == 'all':
                    num = None  # Will handle all
                    break
                try:
                    num = int(num_input)
                    if num <= 0:
                        print("❌ Number must be a positive integer.")
                        continue
                    break
                except ValueError:
                    print("❌ Invalid input. Enter a positive integer or 'all'.")
            groups = {}
            if num is None:
                # All weeks
                for t in filtered:
                    try:
                        dt = datetime.strptime(t["date"], "%Y-%m-%d")
                        y, w, _ = dt.isocalendar()
                        key = f"{y:04d}-W{w:02d}"
                        groups.setdefault(key, []).append(t)
                    except:
                        continue  # Skip malformed dates
            else:
                end_date = datetime.now().date()
                start_date = end_date - timedelta(weeks=num)
                for t in transactions:
                    dt = datetime.strptime(t["date"], "%Y-%m-%d").date()
                    if start_date <= dt <= end_date:
                        y, w, _ = dt.isocalendar()
                        key = f"{dt.year:04d}-W{w:02d}"
                        groups.setdefault(key, []).append(t)
            sorted_keys = sorted(groups.keys(), reverse=(order == "d"))
            prev_income = None
            prev_expense = None
            for key in sorted_keys:
                print(color(f"\n---------------- {key} ----------------", C.BOLD))
                income_total = sum(x["amount"] for x in groups[key] if x["type"] == "Income")
                expense_total = sum(x["amount"] for x in groups[key] if x["type"] == "Expense")
                income_pct = (income_total / total_income * 100) if total_income > 0 else 0
                expense_pct = (expense_total / total_expense * 100) if total_expense > 0 else 0
                income_change = f" ({(income_total - prev_income) / prev_income * 100:.1f}% change)" if prev_income and prev_income > 0 else ""
                expense_change = f" ({(expense_total - prev_expense) / prev_expense * 100:.1f}% change)" if prev_expense and prev_expense > 0 else ""
                print(f"Total Income: ₱{income_total:.2f} ({color('{:.1f}'.format(income_pct), C.GREEN)}%){income_change} | Total Expense: ₱{expense_total:.2f} ({color('{:.1f}'.format(expense_pct), C.RED)}%){expense_change} | Savings: ₱{income_total - expense_total:.2f}")
                for t in groups[key]:
                    print(color(f"  [{t['id']}] {t['date']} | {t['type']} | ₱{t['amount']:.2f} | {t['category']} | {t['description']}", C.DIM))
                prev_income = income_total
                prev_expense = expense_total
        elif group_choice == "5":
            # Group by month (YYYY-MM)
            while True:
                num_input = input("How many months? (enter number or 'all'): ").strip().lower()
                if not num_input:
                    print("❌ Input cannot be empty.")
                    continue
                if num_input == 'all':
                    num = None  # Will handle all
                    break
                try:
                    num = int(num_input)
                    if num <= 0:
                        print("❌ Number must be a positive integer.")
                        continue
                    break
                except ValueError:
                    print("❌ Invalid input. Enter a positive integer or 'all'.")
            groups = {}
            if num is None:
                # All months
                for t in filtered:
                    y, m, _ = ymd_keys(t["date"])
                    key = f"{y:04d}-{m:02d}"
                    groups.setdefault(key, []).append(t)
            else:
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=num*30)  # Approximate months
                for t in transactions:
                    dt = datetime.strptime(t["date"], "%Y-%m-%d").date()
                    if start_date <= dt <= end_date:
                        key = f"{dt.year:04d}-{dt.month:02d}"
                        groups.setdefault(key, []).append(t)
            sorted_keys = sorted(groups.keys(), reverse=(order == "d"))
            prev_income = None
            prev_expense = None
            for key in sorted_keys:
                print(color(f"\n---------------- {key} ----------------", C.BOLD))
                income_total = sum(x["amount"] for x in groups[key] if x["type"] == "Income")
                expense_total = sum(x["amount"] for x in groups[key] if x["type"] == "Expense")
                income_pct = (income_total / total_income * 100) if total_income > 0 else 0
                expense_pct = (expense_total / total_expense * 100) if total_expense > 0 else 0
                income_change = f" ({(income_total - prev_income) / prev_income * 100:.1f}% change)" if prev_income and prev_income > 0 else ""
                expense_change = f" ({(expense_total - prev_expense) / prev_expense * 100:.1f}% change)" if prev_expense and prev_expense > 0 else ""
                print(f"Total Income: ₱{income_total:.2f} ({color('{:.1f}'.format(income_pct), C.GREEN)}%){income_change} | Total Expense: ₱{expense_total:.2f} ({color('{:.1f}'.format(expense_pct), C.RED)}%){expense_change} | Savings: ₱{income_total - expense_total:.2f}")
                for t in groups[key]:
                    print(color(f"  [{t['id']}] {t['date']} | {t['type']} | ₱{t['amount']:.2f} | {t['category']} | {t['description']}", C.DIM))
                prev_income = income_total
                prev_expense = expense_total
        elif group_choice == "6":
            # Group by year
            while True:
                num_input = input("How many years? (enter number or 'all'): ").strip().lower()
                if not num_input:
                    print("❌ Input cannot be empty.")
                    continue
                if num_input == 'all':
                    num = None  # Will handle all
                    break
                try:
                    num = int(num_input)
                    if num <= 0:
                        print("❌ Number must be a positive integer.")
                        continue
                    break
                except ValueError:
                    print("❌ Invalid input. Enter a positive integer or 'all'.")
            groups = {}
            if num is None:
                # All years
                for t in filtered:
                    y, _, _ = ymd_keys(t["date"])
                    groups.setdefault(y, []).append(t)
            else:
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=num*365)  # Approximate years
                for t in transactions:
                    dt = datetime.strptime(t["date"], "%Y-%m-%d").date()
                    if start_date <= dt <= end_date:
                        groups.setdefault(dt.year, []).append(t)
            sorted_keys = sorted(groups.keys(), reverse=(order == "d"))
            prev_income = None
            prev_expense = None
            for y in sorted_keys:
                print(color(f"\n---------------- {y} ----------------", C.BOLD))
                income_total = sum(x["amount"] for x in groups[y] if x["type"] == "Income")
                expense_total = sum(x["amount"] for x in groups[y] if x["type"] == "Expense")
                income_pct = (income_total / total_income * 100) if total_income > 0 else 0
                expense_pct = (expense_total / total_expense * 100) if total_expense > 0 else 0
                income_change = f" ({(income_total - prev_income) / prev_income * 100:.1f}% change)" if prev_income and prev_income > 0 else ""
                expense_change = f" ({(expense_total - prev_expense) / prev_expense * 100:.1f}% change)" if prev_expense and prev_expense > 0 else ""
                print(f"Total Income: ₱{income_total:.2f} ({color('{:.1f}'.format(income_pct), C.GREEN)}%){income_change} | Total Expense: ₱{expense_total:.2f} ({color('{:.1f}'.format(expense_pct), C.RED)}%){expense_change} | Savings: ₱{income_total - expense_total:.2f}")
                for t in groups[y]:
                    print(color(f"  [{t['id']}] {t['date']} | {t['type']} | ₱{t['amount']:.2f} | {t['category']} | {t['description']}", C.DIM))
                prev_income = income_total
                prev_expense = expense_total
        else:
            # No grouping
            for t in filtered:
                print(color(f"[{t['id']}] {t['date']} | {t['type']} | ₱{t['amount']:.2f} | {t['category']} | {t['description']}", C.DIM))

    elif filter_choice == "4":
        clear_terminal()
        print(color("Select type:", C.BOLD))
        print(color("1. Expense", C.WHITE))
        print(color("2. Income", C.WHITE))
        type_choice = input("Choose (1 or 2): ").strip()
        if type_choice == "1":
            type_ = "Expense"
        elif type_choice == "2":
            type_ = "Income"
        else:
            print(color("❌ Invalid choice.", C.RED))
            input("Press Enter to continue...")
            return
        filtered = [t for t in transactions if t["type"] == type_]
        # Calculate overall totals for percentage
        overall_total = sum(t["amount"] for t in transactions if t["type"] == type_)
        type_total = sum(t["amount"] for t in filtered)
        pct = (type_total / overall_total * 100) if overall_total > 0 else 0
        clear_terminal()
        print(color(f"---------------- {type_} ({pct:.1f}%) ----------------", C.WHITE, C.BOLD))
        # Summary total in white at the top
        print(color(f"Total for {type_}: ₱{type_total:.2f}", C.WHITE))
        # Display transactions
        for t in filtered:
            print(color(f"[{t['id']}] {t['date']} | {t['type']} | ₱{t['amount']:.2f} | {t['category']} | {t['description']}", C.DIM))
        # Calculate and display summary
        total_income = sum(t["amount"] for t in filtered if t["type"] == "Income")
        total_expense = sum(t["amount"] for t in filtered if t["type"] == "Expense")
        balance = total_income - total_expense
        print()
        print(color("---------------- Summary ----------------", C.BOLD))
        print(color(f"Total Income: ₱{total_income:.2f}", C.GREEN))
        print(color(f"Total Expenses: ₱{total_expense:.2f}", C.RED))
        bal_color = C.GREEN if balance >= 0 else C.RED
        print(color(f"Total Balance: ₱{balance:.2f}", bal_color, C.BOLD))
        print()
        input("Press Enter to return to main menu...")
        return
    elif filter_choice == "5":
        while True:
            clear_terminal()
            num_input = input("How many recent transactions? ").strip()
            if not num_input:
                print(color("❌ Number cannot be empty.", C.RED))
                continue
            try:
                num = int(num_input)
                if num <= 0:
                    print(color("❌ Number must be a positive integer.", C.RED))
                    continue
                break
            except ValueError:
                print(color("❌ Invalid number. Please enter a positive integer.", C.RED))
        filtered = transactions[-num:] if num < len(transactions) else transactions
        clear_terminal()
        print(color(f"---------------- Recent {num} Transactions ----------------", C.WHITE, C.BOLD))
        # Summary total in white at the top
        recent_total_income = sum(t["amount"] for t in filtered if t["type"] == "Income")
        recent_total_expense = sum(t["amount"] for t in filtered if t["type"] == "Expense")
        recent_balance = recent_total_income - recent_total_expense
        print(color(f"Total Income: ₱{recent_total_income:.2f} | Total Expenses: ₱{recent_total_expense:.2f} | Savings: ₱{recent_balance:.2f}", C.WHITE))
        # Display transactions
        for t in filtered:
            print(color(f"[{t['id']}] {t['date']} | {t['type']} | ₱{t['amount']:.2f} | {t['category']} | {t['description']}", C.DIM))
        # Calculate and display summary
        total_income = sum(t["amount"] for t in filtered if t["type"] == "Income")
        total_expense = sum(t["amount"] for t in filtered if t["type"] == "Expense")
        balance = total_income - total_expense
        print()
        print(color("---------------- Summary ----------------", C.BOLD))
        print(color(f"Total Income: ₱{total_income:.2f}", C.GREEN))
        print(color(f"Total Expenses: ₱{total_expense:.2f}", C.RED))
        bal_color = C.GREEN if balance >= 0 else C.RED
        print(color(f"Total Balance: ₱{balance:.2f}", bal_color, C.BOLD))
        print()
        input("Press Enter to return to main menu...")
        return
    elif filter_choice == "6":
        clear_terminal()
        date = input("Enter date (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(date, "%Y-%m-%d")
            filtered = [t for t in transactions if t["date"] == date]
            clear_terminal()
            print(color(f"---------------- Transactions for {date} ----------------", C.WHITE, C.BOLD))
            # Summary total in white at the top
            date_total_income = sum(t["amount"] for t in filtered if t["type"] == "Income")
            date_total_expense = sum(t["amount"] for t in filtered if t["type"] == "Expense")
            date_balance = date_total_income - date_total_expense
            print(color(f"Total Income: ₱{date_total_income:.2f} | Total Expenses: ₱{date_total_expense:.2f} | Savings: ₱{date_balance:.2f}", C.WHITE))
            # Display transactions
            for t in filtered:
                print(color(f"[{t['id']}] {t['date']} | {t['type']} | ₱{t['amount']:.2f} | {t['category']} | {t['description']}", C.DIM))
            # Calculate and display summary
            total_income = sum(t["amount"] for t in filtered if t["type"] == "Income")
            total_expense = sum(t["amount"] for t in filtered if t["type"] == "Expense")
            balance = total_income - total_expense
            print()
            print(color("---------------- Summary ----------------", C.BOLD))
            print(color(f"Total Income: ₱{total_income:.2f}", C.GREEN))
            print(color(f"Total Expenses: ₱{total_expense:.2f}", C.RED))
            bal_color = C.GREEN if balance >= 0 else C.RED
            print(color(f"Total Savings: ₱{balance:.2f}", C.YELLOW))
            print()
            input("Press Enter to return to main menu...")
            return
        except ValueError:
            print(color("❌ Invalid date format. Use YYYY-MM-DD.", C.RED))
            input("Press Enter to continue...")
            return


    elif filter_choice != "1":
        print("❌ Invalid choice.")
        input("Press Enter to continue...")
        return

    if not filtered:
        print("No transactions match the filter.")
        input("Press Enter to return to main menu...")
        return

    # Calculate summary
    total_income = sum(t["amount"] for t in filtered if t["type"] == "Income")
    total_expense = sum(t["amount"] for t in filtered if t["type"] == "Expense")
    balance = total_income - total_expense
    # Display summary
    print(color("\n---------------- Summary ----------------", C.BOLD))
    print(color(f"Total Income: ₱{total_income:.2f}", C.GREEN))
    print(color(f"Total Expenses: ₱{total_expense:.2f}", C.RED))
    bal_color = C.GREEN if balance >= 0 else C.RED
    print(color(f"Total Balance: ₱{balance:.2f}", bal_color, C.BOLD))
    print()

    if filter_choice == "3":
        # For date filter, display grouped as before, but summary is overall
        pass  # Already handled above
    elif filter_choice in ["1", "2"]:
        # Display transactions for all and category filters
        for t in filtered:
            print(color(f"[{t['id']}] {t['date']} | {t['type']} | ₱{t['amount']:.2f} | {t['category']} | {t['description']}", C.DIM))

    input("\nPress Enter to return to main menu...")

def delete_record(data, username):
    while True:
        clear_terminal()
        print(color("Delete Record", C.BOLD))
        print(color("----------------", C.BOLD))
        print(color("Delete an existing transaction record.", C.DIM))
        print()



        confirm = input("Do you really want to delete a record? (y/n): ").lower()
        if confirm != "y":
            print("Returning to main menu...")
            input("Press Enter to continue...")
            return
        clear_terminal()

        clear_terminal()
        transactions = data["transactions"][username]
        if not transactions:
            print("No transactions found.")
            input("Press Enter to continue...")
            return

        print(color("Delete options:", C.BOLD))
        print("1. Delete by date")
        print("2. Delete by transaction ID")
        print("3. Delete all records")
        delete_choice = input("Choose (1-3): ").strip()

        if delete_choice == "1":
            clear_terminal()
            print(color("Delete by Date", C.BOLD))
            print(color("Enter the date to delete all records for that date.", C.DIM))
            print()
            use_today = input("Use today's date? (y/n): ").lower().strip()
            if use_today == "y":
                date = datetime.now().strftime("%Y-%m-%d")
            elif use_today == "n":
                date = input("Enter date (YYYY-MM-DD): ").strip()
                if not date:
                    print("❌ Date cannot be empty.")
                    input("Press Enter to continue...")
                    continue
                try:
                    datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    print("❌ Invalid date format. Use YYYY-MM-DD.")
                    input("Press Enter to continue...")
                    continue
            else:
                print("❌ Please enter 'y' or 'n'.")
                input("Press Enter to continue...")
                continue

            filtered = [t for t in transactions if t["date"] == date]
            if not filtered:
                print(f"No transactions found for {date}.")
                input("Press Enter to continue...")
                continue

            print(color(f"\nTransactions for {date}:", C.BOLD))
            for t in filtered:
                print(color(f"[{t['id']}] {t['date']} | {t['type']} | ₱{t['amount']:.2f} | {t['category']} | {t['description']}", C.GRAY))

            confirm = input(f"\nDelete all {len(filtered)} record(s) for {date}? (y/n): ").lower().strip()
            if confirm == "y":
                confirm2 = input("Are you sure? This action cannot be undone. (type 'YES' to confirm): ").strip()
                if confirm2 == "YES":
                    data["transactions"][username] = [t for t in transactions if t["date"] != date]
                    save_data(data)
                    print(color("✅ Records deleted successfully!", C.GREEN, C.BOLD))
                else:
                    print("Deletion cancelled.")
            else:
                print("Deletion cancelled.")
        elif delete_choice == "2":
            clear_terminal()
            print(color("Delete by ID", C.BOLD))
            print(color("Enter the transaction ID to delete.", C.DIM))
            print()
            tid_input = input("Enter transaction ID: ").strip()
            if not tid_input:
                print("❌ ID cannot be empty.")
                input("Press Enter to continue...")
                continue
            try:
                tid = int(tid_input)
            except ValueError:
                print("❌ Invalid ID. Must be a number.")
                input("Press Enter to continue...")
                continue

            transaction = next((t for t in transactions if t["id"] == tid), None)
            if not transaction:
                print("Transaction not found.")
                input("Press Enter to continue...")
                continue

            print(color("Transaction to delete:", C.BOLD))
            print(color(f"[{transaction['id']}] {transaction['date']} | {transaction['type']} | ₱{transaction['amount']:.2f} | {transaction['category']} | {transaction['description']}", C.GRAY))

            confirm = input("Delete this record? (y/n): ").lower().strip()
            if confirm == "y":
                confirm2 = input("Are you sure? This action cannot be undone. (type 'YES' to confirm): ").strip()
                if confirm2 == "YES":
                    data["transactions"][username] = [t for t in transactions if t["id"] != tid]
                    save_data(data)
                    print(color("✅ Record deleted successfully!", C.GREEN, C.BOLD))
                else:
                    print("Deletion cancelled.")
            else:
                print("Deletion cancelled.")
        elif delete_choice == "3":
            clear_terminal()
            print(color("Delete All Records", C.BOLD))
            print(color("⚠️  WARNING: This will permanently delete ALL your transaction records!", C.RED, C.BOLD))
            print(color("This action cannot be undone.", C.RED))
            print()
            total_records = len(transactions)
            if total_records == 0:
                print("No records to delete.")
                input("Press Enter to continue...")
                continue
            print(color(f"You have {total_records} transaction(s) that will be deleted.", C.YELLOW))
            print()
            confirm1 = input("Are you absolutely sure you want to delete ALL records? (type 'YES' to confirm): ").strip()
            if confirm1 == "YES":
                confirm2 = input("This is your final confirmation. Type 'DELETE ALL' to proceed: ").strip()
                if confirm2 == "DELETE ALL":
                    confirm3 = input("Last chance! Type 'CONFIRM DELETE ALL' to permanently delete everything: ").strip()
                    if confirm3 == "CONFIRM DELETE ALL":
                        data["transactions"][username] = []
                        save_data(data)
                        print(color("✅ All records deleted successfully!", C.GREEN, C.BOLD))
                    else:
                        print("Deletion cancelled.")
                else:
                    print("Deletion cancelled.")
            else:
                print("Deletion cancelled.")
        else:
            print(color("❌ Invalid choice.", C.RED))
            input("Press Enter to continue...")
            continue

        print()
        delete_another = input("Delete another record? (y/n) or press Enter to exit: ").lower().strip()
        if delete_another == "y":
            clear_terminal()
        else:
            break
    input("Press Enter to return to main menu...")

def edit_record(data, username):
    while True:
        clear_terminal()
        print(color("Edit Record", C.BOLD))
        print(color("----------------", C.BOLD))
        print(color("Edit an existing transaction record.", C.DIM))
        print()



        confirm = input("Do you really want to edit a record? (y/n): ").lower()
        if confirm != "y":
            print("Returning to main menu...")
            input("Press Enter to continue...")
            return
        clear_terminal()

        clear_terminal()
        transactions = data["transactions"][username]
        if not transactions:
            print("No transactions found.")
            input("Press Enter to continue...")
            return

        use_today = input("Use today's date? (y/n): ").lower().strip()
        if use_today == "y":
            today = datetime.now().strftime("%Y-%m-%d")
            year, month, day = today.split("-")
        elif use_today == "n":
            print(color("Date format: YYYY-MM-DD", C.BOLD))
            date_input = input("Enter date (YYYY-MM-DD): ").strip()
            if not date_input:
                print("❌ Date cannot be empty.")
                input("Press Enter to continue...")
                continue
            try:
                datetime.strptime(date_input, "%Y-%m-%d")
                year, month, day = date_input.split("-")
            except ValueError:
                print("❌ Invalid date format. Use YYYY-MM-DD.")
                input("Press Enter to continue...")
                continue
        else:
            print("❌ Please enter 'y' or 'n'.")
            input("Press Enter to continue...")
            continue

        filtered = [t for t in transactions if t["date"].startswith(f"{year}-{month}-{day}")]
        if not filtered:
            print("No transactions found for that date.")
            input("Press Enter to continue...")
            continue

        print(color(f"\n--------------- {year}-{month}-{day} ---------------", C.BOLD))
        for t in filtered:
            print(color(f"[{t['id']}] {t['date']} | {t['type']} | ₱{t['amount']:.2f} | {t['category']} | {t['description']}", C.GRAY))

        tid_input = input("\nEnter transaction ID to edit: ").strip()
        if not tid_input:
            print("❌ ID cannot be empty.")
            input("Press Enter to continue...")
            continue
        try:
            tid = int(tid_input)
        except ValueError:
            print("❌ Invalid ID. Must be a number.")
            input("Press Enter to continue...")
            continue

        transaction = next((t for t in transactions if t["id"] == tid), None)
        if not transaction:
            print("Transaction not found.")
            input("Press Enter to continue...")
            continue

        print(color("\nWhat do you want to edit?", C.BOLD))
        print("1. Type\n2. Amount\n3. Category\n4. Description\n5. Date")
        choice = input("Choose between the options: ").strip()

        if choice == "1":
            while True:
                clear_terminal()
                print(color("\nSelect new type:", C.BOLD))
                print("1. Expense")
                print("2. Income")
                new_choice = input("Choose (1 or 2): ").strip()
                if new_choice == "1":
                    transaction["type"] = "Expense"
                    break
                elif new_choice == "2":
                    transaction["type"] = "Income"
                    break
                else:
                    print("❌ Invalid choice. Enter 1 or 2.")
        elif choice == "2":
            while True:
                clear_terminal()
                amount_input = input(color("New amount: ", C.BOLD)).strip()
                if not amount_input:
                    print("❌ Amount cannot be empty.")
                    continue
                try:
                    new_amount = float(amount_input)
                    if new_amount <= 0:
                        print("❌ Amount must be positive.")
                        continue
                    transaction["amount"] = new_amount
                    break
                except ValueError:
                    print("❌ Invalid amount. Enter a number.")

        elif choice == "3":
            # Edit category based on current type
            clear_terminal()
            if transaction["type"] == "Expense":
                expense_categories = ["Food & Groceries", "Transportation", "Entertainment", "Personal Needs", "Personal Wants", "Health & Fitness", "Bills", "School/Work"]
                print(color("Select new expense category:", C.BOLD))
                for i, cat in enumerate(expense_categories, 1):
                    print(f"{i}. {cat}")
                while True:
                    cat_choice = input("Choose (1-8): ").strip()
                    if cat_choice.isdigit() and 1 <= int(cat_choice) <= 8:
                        transaction["category"] = expense_categories[int(cat_choice) - 1]
                        break
                    else:
                        print("❌ Invalid choice. Enter 1-8.")
            else:  # Income
                income_categories = ["Allowance", "Work", "Reward", "Gift"]
                print(color("Select new income category:", C.BOLD))
                for i, cat in enumerate(income_categories, 1):
                    print(f"{i}. {cat}")
                while True:
                    cat_choice = input("Choose (1-4): ").strip()
                    if cat_choice.isdigit() and 1 <= int(cat_choice) <= 4:
                        transaction["category"] = income_categories[int(cat_choice) - 1]
                        break
                    else:
                        print("❌ Invalid choice. Enter 1-4.")
        elif choice == "4":
            clear_terminal()
            transaction["description"] = input(color("New description: ", C.BOLD)).strip()
        elif choice == "5":
            clear_terminal()
            print(color("New Date format: YYYY-MM-DD", C.BOLD))
            use_today = input("Use today's date? (y/n): ").lower().strip()
            if use_today == "y":
                new_date = datetime.now().strftime("%Y-%m-%d")
            elif use_today == "n":
                new_date = input("Enter date (YYYY-MM-DD): ").strip()
                if not new_date:
                    print("❌ Date cannot be empty.")
                    continue
                try:
                    datetime.strptime(new_date, "%Y-%m-%d")
                except ValueError:
                    print("❌ Invalid date format. Use YYYY-MM-DD.")
                    continue
            else:
                print("❌ Please enter 'y' or 'n'.")
                continue
            transaction["date"] = new_date
        else:
            print("Invalid choice.")
            input("Press Enter to continue...")
            continue

        print(color("\nUpdated record preview:", C.BOLD))
        print(color(f"[{transaction['id']}] {transaction['date']} | {transaction['type']} | ₱{transaction['amount']:.2f} | {transaction['category']} | {transaction['description']}", C.CYAN))

        confirm = input("Save changes? (y/n): ").lower().strip()
        if confirm == "y":
            save_data(data)
            print(color("✅ Record updated successfully!", C.GREEN, C.BOLD))
        else:
            print("Changes discarded.")

        print()
        edit_another = input("Edit another record? (y/n) or press Enter to exit: ").lower().strip()
        if edit_another == "y":
            clear_terminal()
        else:
            break
    input("Press Enter to return to main menu...")

def dashboard(data, username):
    while True:
        clear_terminal()
        transactions = data["transactions"][username]
        total_income = sum(t["amount"] for t in transactions if t["type"] == "Income")
        total_expense = sum(t["amount"] for t in transactions if t["type"] == "Expense")
        balance = total_income - total_expense
        total_savings = balance

        # Define today_str early
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")

        # Calculate summaries by category
        income_summary = {}
        expense_summary = {}
        for t in transactions:
            if t["type"] == "Income":
                income_summary[t["category"]] = income_summary.get(t["category"], 0) + t["amount"]
            elif t["type"] == "Expense":
                expense_summary[t["category"]] = expense_summary.get(t["category"], 0) + t["amount"]

        today_income_summary = {}
        today_expense_summary = {}
        for t in transactions:
            if t["date"] == today_str:
                if t["type"] == "Income":
                    today_income_summary[t["category"]] = today_income_summary.get(t["category"], 0) + t["amount"]
                elif t["type"] == "Expense":
                    today_expense_summary[t["category"]] = today_expense_summary.get(t["category"], 0) + t["amount"]

        print(color("Dashboard", C.BOLD))
        print(color("----------------", C.BOLD))
        print(color(f"Hello, {username}! Welcome!", C.DIM))
        print(color("Your financial dashboard.\nSummarizes your Money flow!", C.DIM))
        print()



        # Calculate data for analytics and tips
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        today_str = today.strftime("%Y-%m-%d")
        yesterday_str = yesterday.strftime("%Y-%m-%d")
        today_expense = sum(t["amount"] for t in transactions if t["type"] == "Expense" and t["date"] == today_str)
        yesterday_expense = sum(t["amount"] for t in transactions if t["type"] == "Expense" and t["date"] == yesterday_str)
        today_income = sum(t["amount"] for t in transactions if t["type"] == "Income" and t["date"] == today_str)
        yesterday_income = sum(t["amount"] for t in transactions if t["type"] == "Income" and t["date"] == yesterday_str)
        today_savings = today_income - today_expense
        yesterday_savings = yesterday_income - yesterday_expense
        has_today_data = today_expense > 0 or today_income > 0
        has_yesterday_data = yesterday_expense > 0 or yesterday_income > 0

        # Financial Summary and Analytics Sections (side by side)
        bal_color = C.GREEN if balance >= 0 else C.RED
        today_balance = today_income - today_expense
        today_bal_color = C.GREEN if today_balance >= 0 else C.RED
        fs_lines = [
            color("-" * 15 + " Financial Summary " + "-" * 15, C.BOLD),
            color(f"Total Income: ₱{total_income:.2f}", C.GREEN),
            color(f"Total Expenses: ₱{total_expense:.2f}", C.RED),
            color(f"Total Balance: ₱{balance:.2f}", bal_color, C.BOLD),
            "",
            color(f"Today's Income: ₱{today_income:.2f}", C.GREEN),
            color(f"Today's Expenses: ₱{today_expense:.2f}", C.RED),
            color(f"Today's Balance: ₱{today_balance:.2f}", today_bal_color, C.BOLD),
            ""
        ]
        # Analytics
        an_lines = [color("-" * 15 + " Analytics " + "-" * 15, C.BOLD)]
        unique_dates = set(t["date"] for t in transactions)
        num_days = len(unique_dates) if unique_dates else 1
        avg_expense_per_day = total_expense / num_days if num_days > 0 else 0
        avg_income_per_day = total_income / num_days if num_days > 0 else 0
        avg_savings_per_day = total_savings / num_days if num_days > 0 else 0
        an_lines.append(color(f"Average Expense per Day: ₱{avg_expense_per_day:.2f}", C.RED))
        an_lines.append(color(f"Average Income per Day: ₱{avg_income_per_day:.2f}", C.GREEN))
        an_lines.append(color(f"Average Savings per Day: ₱{avg_savings_per_day:.2f}", C.YELLOW))
        an_lines.append(color(f"Total Days Tracked: {num_days}", C.WHITE))
        if has_today_data and has_yesterday_data:
            if yesterday_expense > 0:
                expense_change_val = ((today_expense - yesterday_expense) / yesterday_expense) * 100
                if expense_change_val > 0:
                    expense_msg = color(f"Expenses increased by {expense_change_val:.1f}% (₱{yesterday_expense:.2f} to ₱{today_expense:.2f}).", C.RED)
                elif expense_change_val < 0:
                    expense_msg = color(f"Expenses decreased by {abs(expense_change_val):.1f}% (₱{yesterday_expense:.2f} to ₱{today_expense:.2f}).", C.GREEN)
                else:
                    expense_msg = color("Expenses same as yesterday.", C.YELLOW)
            else:
                expense_msg = color(f"No expenses yesterday, today ₱{today_expense:.2f}.", C.BLUE)
            if yesterday_savings != 0:
                savings_change_val = ((today_savings - yesterday_savings) / abs(yesterday_savings)) * 100
                if savings_change_val > 0:
                    savings_msg = color(f"Savings increased by {savings_change_val:.1f}% (₱{yesterday_savings:.2f} to ₱{today_savings:.2f}).", C.YELLOW)
                elif savings_change_val < 0:
                    savings_msg = color(f"Savings decreased by {abs(savings_change_val):.1f}% (₱{yesterday_savings:.2f} to ₱{today_savings:.2f}).", C.RED)
                else:
                    savings_msg = color("Savings same as yesterday.", C.YELLOW)
            else:
                savings_msg = color(f"No savings yesterday for percentage calculation.", C.BLUE)
            an_lines.append(expense_msg)
            an_lines.append(savings_msg)
        elif has_yesterday_data:
            an_lines.append(color(f"No records for today. Yesterday's expenses: ₱{yesterday_expense:.2f}, Income: ₱{yesterday_income:.2f}, Savings: ₱{yesterday_savings:.2f}.", C.MAGENTA))
        elif has_today_data:
            an_lines.append(color(f"No records for yesterday. Today's expenses: ₱{today_expense:.2f}, Income: ₱{today_income:.2f}, Savings: ₱{today_savings:.2f}.", C.MAGENTA))
        else:
            an_lines.append(color("No recent data for daily change calculations.", C.MAGENTA))
        an_lines.append("")
        # Print side by side with fixed widths for better alignment
        analytics_width = 60
        financial_width = 60
        max_len = max(len(fs_lines), len(an_lines))
        for i in range(max_len):
            fs = fs_lines[i] if i < len(fs_lines) else ""
            an = an_lines[i] if i < len(an_lines) else ""
            an_padded = pad_to_display_width(an, analytics_width)
            fs_padded = pad_to_display_width(fs, financial_width)
            line = f"{an_padded}  |  {fs_padded}"
            print(line)
        print()
        # Income and Expense Breakdown Sections (side by side)
        ib_lines = []
        if income_summary:
            ib_lines.append(color("-" * 15 + " Income Breakdown " + "-" * 15, C.BOLD))
            for cat in sorted(income_summary.keys()):
                pct = (income_summary[cat] / total_income * 100) if total_income > 0 else 0
                ib_lines.append(f"  - {cat}: ₱{income_summary[cat]:.2f} ({pct:.1f}%)")
            ib_lines.append("")
            # Today's Income Breakdown subsection
            if today_income_summary:
                ib_lines.append(color("-" * 15 + " Today's Income Breakdown " + "-" * 15, C.BOLD))
                for cat in sorted(today_income_summary.keys()):
                    pct = (today_income_summary[cat] / today_income * 100) if today_income > 0 else 0
                    ib_lines.append(f"  - {cat}: ₱{today_income_summary[cat]:.2f} ({pct:.1f}%)")
                ib_lines.append("")
        eb_lines = []
        if expense_summary:
            eb_lines.append(color("-" * 15 + " Expense Breakdown " + "-" * 15, C.BOLD))
            for cat in sorted(expense_summary.keys()):
                pct = (expense_summary[cat] / total_expense * 100) if total_expense > 0 else 0
                eb_lines.append(f"  - {cat}: ₱{expense_summary[cat]:.2f} ({pct:.1f}%)")
            eb_lines.append("")
            # Today's Expense Breakdown subsection
            if today_expense_summary:
                eb_lines.append(color("-" * 15 + " Today's Expense Breakdown " + "-" * 15, C.BOLD))
                for cat in sorted(today_expense_summary.keys()):
                    pct = (today_expense_summary[cat] / today_expense * 100) if today_expense > 0 else 0
                    eb_lines.append(f"  - {cat}: ₱{today_expense_summary[cat]:.2f} ({pct:.1f}%)")
                eb_lines.append("")
        # Print side by side
        max_len = max(len(ib_lines), len(eb_lines))
        for i in range(max_len):
            ib = ib_lines[i] if i < len(ib_lines) else ""
            eb = eb_lines[i] if i < len(eb_lines) else ""
            eb_padded = pad_to_display_width(eb, 60)
            ib_padded = pad_to_display_width(ib, 60)
            print(f"{eb_padded}  |  {ib_padded}")

        # Suggestion Section - Provides personalized financial tips based on user's spending patterns
        print()
        print(color("-" * 15 + " Suggestion " + "-" * 15, C.BOLD))

        # Calculate expense trend over last 7 days for cases with no today data
        # This helps provide tips when daily data is missing
        last_7_days = [today - timedelta(days=i) for i in range(1, 8)]
        last_7_expenses = [sum(t["amount"] for t in transactions if t["type"] == "Expense" and t["date"] == d.strftime("%Y-%m-%d")) for d in last_7_days]
        avg_expense_last_7 = sum(last_7_expenses) / len(last_7_expenses) if last_7_expenses else 0
        expense_trend = yesterday_expense - avg_expense_last_7 if avg_expense_last_7 > 0 else 0

        # Find top expense categories for saving tips, prioritizing essentials
        # Essentials are prioritized for better financial guidance
        expense_categories = {}
        for t in transactions:
            if t["type"] == "Expense":
                expense_categories[t["category"]] = expense_categories.get(t["category"], 0) + t["amount"]

        essentials = ["Food & Groceries", "Transportation", "School/Work", "Personal Needs", "Bills", "Health & Fitness"]
        desires = ["Entertainment", "Personal Wants"]

        top_essentials = sorted([(cat, amt) for cat, amt in expense_categories.items() if cat in essentials], key=lambda x: essentials.index(x[0]))
        top_desires = sorted([(cat, amt) for cat, amt in expense_categories.items() if cat in desires], key=lambda x: x[1], reverse=True)

        # Define focus areas for tips - uses top essentials and desires for personalized advice
        focus_areas = ", ".join([cat[0] for cat in top_essentials[:2]]) if top_essentials else "essentials"
        focus_desires = ", ".join([cat[0] for cat in top_desires[:2]]) if top_desires else "wants"

        # Secondary tips arrays - provide additional guidance based on financial scenarios
        # These are categorized by situation: spending too much, saving too much, or expense trends
        secondary_tips_spend_too_much = [
            f"Focus on cutting back on {focus_desires} for efficient savings by planning purchases ahead.",
            f"Prioritize essentials by reducing spending on {focus_desires} to stabilize your savings and avoid unnecessary debt.",
            f"Optimize your budget by limiting {focus_desires} to reduce overall expenses and build a stronger financial foundation.",
            f"Lessen spends on {focus_desires} to free up more for essentials.",
            f"Cut back on non-essential {focus_desires} to prioritize needs over wants.",
            f"Redirect funds from {focus_desires} towards essentials for long-term benefits.",
            f"Review and reduce {focus_desires} expenses to prioritize essentials.",
            f"Avoid impulse buys on {focus_desires} to ensure essentials are covered.",
            f"Track daily expenses on {focus_desires} to identify areas for cost reduction and better budgeting.",
            f"Set weekly limits for {focus_desires} to prevent overspending and encourage mindful purchasing.",
            f"Compare prices for {focus_desires} items to find better deals and save money.",
            f"Delay gratification by waiting before buying {focus_desires} to see if you really need them.",
            f"Substitute cheaper alternatives for {focus_desires} to maintain satisfaction without high costs.",
            f"Use cash instead of cards for {focus_desires} to make spending feel more real and reduce impulse buys.",
            f"Create a 'no spend' day each week to break the habit of unnecessary {focus_desires} purchases."
        ]

        secondary_tips_saved_too_much = [
            f"Great job on saving! Treat yourself to something from {focus_desires} after hitting savings goals, but don't spend everything.",
            f"Excellent savings progress! Enjoy a small indulgence from {focus_desires} once essentials are covered, keeping savings intact.",
            f"Fantastic work saving! Reward yourself with a modest treat from {focus_desires} without depleting your balance.",
            f"Keep up the great savings habit! Consider investing a portion of your savings for future growth while enjoying occasional {focus_desires}.",
            f"Outstanding savings achievement! Use some savings for a small treat from {focus_desires} while maintaining your emergency fund.",
            f"Well done on your savings! Balance rewards from {focus_desires} with continued saving to build wealth over time.",
            f"Impressive savings rate! Reward your discipline with a small indulgence from {focus_desires}, then resume saving.",
            f"Congratulations on saving! Allocate a small portion for fun from {focus_desires} while preserving the rest for security.",
            f"With strong savings, explore low-risk investments to grow your funds while treating yourself to {focus_desires}.",
            f"Maintain your savings momentum by setting aside rewards from {focus_desires} after achieving financial milestones."
        ]

        secondary_tips_trend_increase = [
            f"Expenses increased recently; focus on reducing costs in {focus_desires} to get back on track.",
            f"With rising expenses, review {focus_desires} for opportunities to cut back and stabilize spending.",
            f"Your spending has been increasing; prioritize budgeting for {focus_desires} to prevent further rises.",
            f"Expense uptick noted; optimize {focus_desires} by finding cheaper alternatives or reducing frequency.",
            f"Rising expenses over the past week; concentrate on essentials like {focus_areas} to curb the increase.",
            f"Your recent spending is higher; implement strict limits on {focus_desires} to reverse the increase.",
            f"Expenses climbing; audit {focus_desires} for unnecessary costs and eliminate them promptly.",
            f"Increased weekly spending; redirect focus to {focus_areas} for better financial control.",
            f"Expense rise observed; plan ahead for {focus_desires} to avoid impulsive purchases driving costs up.",
            f"With expenses up, emphasize cost-saving measures in {focus_desires} to flatten the increase."
        ]
        secondary_tips_trend_decrease = [
            f"Great job lowering expenses! Keep optimizing {focus_areas} to maintain this positive decrease.",
            f"Expenses decreased; continue focusing on {focus_areas} for sustained savings growth.",
            f"Positive expense reduction; reward yourself with a small treat from {focus_desires} while keeping {focus_areas} in check.",
            f"Your spending is lower; invest the savings from {focus_areas} into building an emergency fund.",
            f"Excellent expense control; use the freed-up funds from {focus_areas} to pay off debts or save more.",
            f"Decreased spending noted; maintain discipline in {focus_areas} and consider increasing savings contributions.",
            f"Expenses down; celebrate by planning a budget-friendly activity from {focus_desires} without overspending.",
            f"Your expenses are decreasing; analyze what worked in {focus_areas} and apply it consistently.",
            f"Lower expenses achieved; allocate extra savings from {focus_areas} towards long-term financial goals.",
            f"Expense reduction success; balance rewards from {focus_desires} with continued focus on {focus_areas}."
        ]
        secondary_tips_trend_stable = [
            f"Stable expenses; keep monitoring {focus_areas} to ensure they remain within budget.",
            f"Expenses steady; use this period to review {focus_desires} and plan for occasional indulgences.",
            f"Your spending is consistent; focus on automating savings while keeping {focus_areas} optimized.",
            f"Stable expenses maintained; consider setting new goals for {focus_areas} to further reduce costs.",
            f"Expense stability achieved; reward consistency with a small allowance for {focus_desires}.",
            f"Steady spending; audit {focus_areas} for potential efficiencies without disrupting balance.",
            f"Expenses stable; use the predictability to build a buffer in savings from {focus_areas}.",
            f"Your spending is consistent; plan for future expenses in {focus_areas} to avoid unexpected spikes.",
            f"Stable expenses; explore ways to enhance savings by fine-tuning {focus_desires} spending.",
            f"Expense stability; maintain focus on {focus_areas} and gradually increase savings contributions."
        ]

        # Calculate percentage changes for expense and savings from yesterday to today
        expense_change = 0
        savings_change = 0
        if has_yesterday_data:
            if yesterday_expense > 0:
                expense_change = ((today_expense - yesterday_expense) / yesterday_expense) * 100
            if yesterday_savings != 0:
                savings_change = ((today_savings - yesterday_savings) / abs(yesterday_savings)) * 100

        # Define scenario-based primary tips for suggestion section based on data availability and changes
        # These tips are general advice tailored to the user's current financial situation
        if not has_today_data and not has_yesterday_data:
            suggestion_tips = [
                "💡 Tip: Start by tracking your daily coffee runs or lunch expenses. Small purchases add up quickly and seeing them can motivate better choices.",
                "💡 Tip: Begin with essentials like groceries and transportation. Most people spend the most here, so tracking these first gives immediate insights.",
                "💡 Tip: Don't worry about recording every tiny expense at first. Focus on the bigger ones like rent, utilities, and major purchases to build the habit.",
                "💡 Tip: Think of tracking like a diet - you don't need to be perfect, just consistent. Even logging 3-4 transactions a day helps you see patterns.",
                "💡 Tip: Start with your phone's note app if you don't have fancy tools. The key is getting comfortable with seeing where your money goes regularly."
            ]
        elif not has_today_data:
            if expense_trend > 0:
                suggestion_tips = [
                    "💡 Tip: When expenses rise, most people find cutting dining out helps. Try cooking simple meals at home a few nights a week to save.",
                    "💡 Tip: Review your subscriptions - many people forget about unused streaming services or gym memberships that cost $10-20 monthly.",
                    "💡 Tip: Plan your grocery shopping with a list. People often buy impulsively in stores, leading to wasted food and higher bills.",
                    "💡 Tip: If driving everywhere, try walking or biking for short trips. Gas and parking add up faster than most realize.",
                    "💡 Tip: Wait 24 hours before non-essential purchases. That 'want' often fades, saving you money that could go toward real needs."
                ]
            elif expense_trend < 0:
                suggestion_tips = [
                    "💡 Tip: Great job saving! Many people put extra money into a high-interest savings account to earn a little interest while keeping it safe.",
                    "💡 Tip: Build an emergency fund with your savings. Aim for 3 months of expenses - most people wish they had this during unexpected bills.",
                    "💡 Tip: Keep the momentum by setting small savings goals. Like 'save $50 this week' - it feels achievable and builds good habits.",
                    "💡 Tip: Treat yourself with a want after hitting savings goals - maybe a home movie night or a small affordable treat. Non-monetary rewards keep you motivated without spending everything.",
                    "💡 Tip: Reflect on what worked. Did meal prepping help? Or skipping online shopping? Most people find repeating successful strategies leads to more savings."
                ]
            else:
                suggestion_tips = [
                    "💡 Tip: With stable spending, set up automatic transfers to savings. Many people forget to save consistently, so automation helps.",
                    "💡 Tip: Review your budget categories. You might be overspending on entertainment while undersaving - adjust to match your priorities.",
                    "💡 Tip: Track your spending triggers. For many, stress or boredom leads to unnecessary purchases - awareness helps control them.",
                    "💡 Tip: Look for side gigs during stable times. Delivery apps, freelance work, or selling unused items can boost your income noticeably.",
                    "💡 Tip: Use this calm period to learn about investing. Many people start with simple index funds through apps like Robinhood or Vanguard."
                ]
        elif not has_yesterday_data:
            suggestion_tips = [
                "💡 Tip: Add yesterday's transactions to see trends. Most people are surprised how much they spend on small essentials when they look back.",
                "💡 Tip: Make it a habit to record expenses right after they happen. Waiting means forgetting smaller essential purchases like coffee or snacks.",
                "💡 Tip: Start with big essentials first. Rent, groceries, and bills are usually the easiest to remember and most impactful.",
                "💡 Tip: Complete data gives better comparisons. Without yesterday's info, you miss seeing if today was better or worse for essentials.",
                "💡 Tip: Think of it like exercise tracking - consistency matters more than perfection. Even partial data helps you improve essential spending."
            ]
        else:
            if yesterday_expense > 0 and expense_change > 10:
                suggestion_tips = [
                    "💡 Tip: Focus on essentials: When expenses jump, prioritize Food & Groceries first. Meal planning and store brands save money for other essentials.",
                    "💡 Tip: Cut transportation essentials immediately. Try carpooling or public transit - it saves money and reduces stress for other needs.",
                    "💡 Tip: Skip non-essentials for a week. That daily coffee habit adds up, freeing money for essentials like Bills and Transportation.",
                    "💡 Tip: Implement the 24-hour rule for wants. Most impulse buys seem less important after thinking, saving for essentials.",
                    "💡 Tip: Prioritize needs over wants. Ask 'Is this essential?' - most people find they can delay purchases to focus on Food & Groceries and Bills."
                ]
            elif yesterday_expense > 0 and expense_change < -10:
                suggestion_tips = [
                    "💡 Tip: With lower expenses, invest the difference in essentials. Many people start with retirement accounts for long-term security like future Bills.",
                    "💡 Tip: Reward yourself with a want after essentials are covered. A small treat from savings feels good without spending everything on non-essentials.",
                    "💡 Tip: Set goals to maintain low expenses on essentials. Like 'keep groceries under $100 this week' - specific targets help most people stay on track.",
                    "💡 Tip: Note what reduced your spending on essentials. Was it cooking at home? Walking instead of driving? Most people benefit from repeating what works.",
                    "💡 Tip: Increase savings rate now for essentials. When expenses are down, save more - many people aim to cover 20% of income for future needs."
                ]
            elif savings_change > 20:
                suggestion_tips = [
                    "💡 Tip: With growing savings, diversify into investments for essentials. Many people spread money across accounts for safety and future Bills.",
                    "💡 Tip: Build emergency fund for essentials. Most advisors recommend 6-12 months of expenses for security during unexpected Food or Transport costs.",
                    "💡 Tip: Automate contributions for essentials. Set up transfers automatically - most people find this ensures money for needs without temptation.",
                    "💡 Tip: Look into tax-advantaged accounts for essentials. 401(k)s or IRAs grow money for retirement needs without immediate taxes.",
                    "💡 Tip: Pay off high-interest debt first for essentials. Credit cards charge 15-25% interest, so using savings here frees money for Food & Groceries."
                ]
            elif savings_change < -20:
                suggestion_tips = [
                    "💡 Tip: Focus on essentials: When savings drop, optimize Food & Groceries and Transportation first. Small changes here help most people recover.",
                    "💡 Tip: Audit recurring bills for essentials. Many people find duplicate services costing monthly that can be cut to save for needs.",
                    "💡 Tip: Freeze non-essential spending temporarily. A 'no spend' week on entertainment frees money for essentials like Bills and Food.",
                    "💡 Tip: Track every expense closely for essentials. Most people are shocked by how small purchases add up when monitoring carefully.",
                    "💡 Tip: Rebalance budget focusing on essentials. Cut back on wants to prioritize needs and savings - many people find this restores stability."
                ]
            else:
                suggestion_tips = [
                    "💡 Tip: Create a budget focusing on essentials. Many people use 50/30/20: 50% needs (Food, Transport, Bills), 30% wants, 20% savings.",
                    "💡 Tip: Track daily spending to catch leaks in essentials. Most people don't realize how $5 snacks prevent reaching goals for Bills or Food.",
                    "💡 Tip: Always buy needs before wants for essentials. Ask 'Is this essential?' - this mindset helps most people make better decisions.",
                    "💡 Tip: Set specific goals for essentials. Like 'Save $500 for emergency fund' - clear targets motivate more than vague 'save money' plans.",
                    "💡 Tip: Do weekly check-ins focusing on essentials. Most people find reviewing progress helps stay on track and adjust for Food & Transport needs."
                ]

        # Select a random primary tip from the scenario-based list
        selected_suggestion_tip = random.choice(suggestion_tips)

        # Display tips based on data availability and financial changes
        # Primary tip is always shown, secondary tip is shown for specific scenarios to provide extra guidance
        if not has_today_data and not has_yesterday_data:
            print(color("No expenses or income recorded for today or yesterday. Start tracking your transactions to get personalized tips!", C.YELLOW))
            print(color(selected_suggestion_tip, C.CYAN, C.BOLD))
        elif not has_today_data:
            # Base tip on expense/savings increase or decrease from last 7 days
            print(color(selected_suggestion_tip, C.CYAN, C.BOLD))
            if expense_trend > 0:
                secondary_tip = random.choice(secondary_tips_trend_increase)
                print(color(secondary_tip, C.BLUE))
            elif expense_trend < 0:
                secondary_tip = random.choice(secondary_tips_trend_decrease)
                print(color(secondary_tip, C.BLUE))
            else:
                secondary_tip = random.choice(secondary_tips_trend_stable)
                print(color(secondary_tip, C.BLUE))
        elif not has_yesterday_data:
            print(color(selected_suggestion_tip, C.CYAN, C.BOLD))
        else:
            # Base analysis on yesterday's data to advise today's spending
            if yesterday_expense > 0:
                if expense_change > 10:
                    print(color(selected_suggestion_tip, C.CYAN, C.BOLD))
                    if top_essentials:
                        secondary_tip = random.choice(secondary_tips_spend_too_much)
                        print(color(secondary_tip, C.BLUE))
                elif expense_change < -10:
                    print(color(selected_suggestion_tip, C.CYAN, C.BOLD))
                    secondary_tip = random.choice(secondary_tips_trend_decrease)
                    print(color(secondary_tip, C.BLUE))
                elif savings_change > 20:
                    print(color(selected_suggestion_tip, C.CYAN, C.BOLD))
                    secondary_tip = random.choice(secondary_tips_saved_too_much)
                    print(color(secondary_tip, C.BLUE))
                elif savings_change < -20:
                    print(color(selected_suggestion_tip, C.CYAN, C.BOLD))
                    if top_essentials:
                        secondary_tip = random.choice(secondary_tips_spend_too_much)
                        print(color(secondary_tip, C.BLUE))
                else:
                    print(color(selected_suggestion_tip, C.CYAN, C.BOLD))
                    secondary_tip = random.choice(secondary_tips_trend_stable)
                    print(color(secondary_tip, C.BLUE))
            else:
                print(color(selected_suggestion_tip, C.CYAN, C.BOLD))

        print()

        # Options Section
        print(color("-" * 15 + " Options " + "-" * 15, C.BOLD))
        print(color("1. Add Record", C.WHITE))
        print(color("2. View History", C.WHITE))
        print(color("3. Edit Record", C.WHITE))
        print(color("4. Delete Record", C.WHITE))
        print(color("5. Logout", C.WHITE))

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_record(data, username)
        elif choice == "2":
            view_history(data, username)
        elif choice == "3":
            edit_record(data, username)
        elif choice == "4":
            delete_record(data, username)
        elif choice == "5":
            break
        else:
            print("Invalid choice.")
            input("Press Enter to continue...")

def main():
    data = load_data()
    while True:
        clear_terminal()
        print(color("Expense & Savings Tracker", C.BOLD))
        print(color("----------------", C.BOLD))
        print(color("Track expenses and income.\nNo more disappearing Money!", C.DIM))
        print()



        print(color("Please choose a function:", C.BOLD))
        print(color("1. Sign Up", C.WHITE))
        print(color("2. Login", C.WHITE))
        print(color("3. Exit", C.WHITE))

        choice = input("Choose an option: ").strip()

        if choice == "1":
            sign_up(data)
        elif choice == "2":
            user = login(data)
            if user:
                dashboard(data, user)
        elif choice == "3":
            print(color("👋 Goodbye! See you next time.", C.GRAY))
            break
        else:
            print("Invalid choice.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
