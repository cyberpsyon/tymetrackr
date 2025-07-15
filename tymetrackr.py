import sqlite3
import argparse
from datetime import datetime

def init_db():
    conn = sqlite3.connect('tymetrackr.db')
    c = conn.cursor()
    c.execute('''
              CREATE TABLE IF NOT EXISTS entries (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT NOT NULL,
                  start_time TEXT NOT NULL,
                  end_time TEXT NOT NULL, 
                  role TEXT NOT NULL, 
                  task TEXT NOT NULL,
                  notes TEXT,
                  total_hours REAL NOT NULL                
              )
              ''')
    conn.commit()
    conn.close()
 
def calculate_total_hours(start, end):
    time_format = "%H:%M"
    start_dt = datetime.strptime(start, time_format)
    end_dt = datetime.strptime(end, time_format)
    duration = end_dt - start_dt
    return round(duration.total_seconds() / 3600, 2)

def add_entry(date, start, end, role, task, notes):
    total_hours = calculate_total_hours(start, end)
    conn = sqlite3.connect('tymetrackr.db')
    c = conn.cursor()
    c.execute('''
            INSERT INTO entries (date, start_time, end_time, role, task, notes, total_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (date, start, end, role, task, notes, total_hours))
    conn.commit()
    conn.close()
    print(f"Added entry: {date} | {role} | {total_hours} hrs")
    
def view_entries():
    conn = sqlite3.connect('tymetrackr.db')
    c = conn.cursor()
    c.execute("SELECT id, date, start_time, end_time, role, task, notes, total_hours FROM entries ORDER BY date DESC")
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("No entries found.")
        return

    print("\n Logged Time Entries:")
    print("-" * 80)
    for row in rows:
        entry_id, date, start, end, role, task, notes, hours = row
        print(f"[{entry_id}] {date} | {start}-{end} | {role:<6} | {hours} hrs | {task}")
        if notes:
            print(f"   Notes: {notes}")
        print("-" * 80)

def delete_entry(entry_id):
    conn = sqlite3.connect('tymetrackr.db')
    c = conn.cursor()
    c.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
    row = c.fetchone()
    if not row:
        print(f"Entry with ID {entry_id} not found.")
        conn.close()
        return

    c.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    
def add_interactive():
    print("\n📝 Add a Time Entry\n" + "-"*30)
    date = input("Date (YYYY-MM-DD): ")
    start = input("Start Time (HH:MM): ")
    end = input("End Time (HH:MM): ")
    role = input("Role (e.g. TA, AppSec): ")
    task = input("Task Description: ")
    notes = input("Optional Notes: ")

    add_entry(date, start, end, role, task, notes)
    
def main_menu():
    while True:
        print("\n==============================")
        print("      ⏱️  TymeTrackr Menu")
        print("==============================")
        print("1. Add time entry")
        print("2. View entries")
        print("3. Delete an entry")
        print("4. Quit")
        print("------------------------------")
        choice = input("Choose an option (1-4): ")

        if choice == "1":
            add_interactive()
        elif choice == "2":
            view_entries()
        elif choice == "3":
            entry_id = input("Enter the entry ID to delete: ")
            if entry_id.isdigit():
                delete_entry(int(entry_id))
            else:
                print("❌ Invalid ID.")
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter a number 1–4.")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Time Tracking CLI Tool")
    subparsers = parser.add_subparsers(dest="command")
    parser_view = subparsers.add_parser("view", help="View all time entries")
    parser_init = subparsers.add_parser("init", help="Initialize the database")
    parser_delete = subparsers.add_parser("delete", help="Delete an entry by ID")
    parser_delete.add_argument("--id", type=int, required=True, help="Entry ID to delete")
    parser_prompt = subparsers.add_parser("prompt", help="Add entry with interactive prompts")


    
    parser_add = subparsers.add_parser("add", help="Add a time entry")
    parser_add.add_argument("--date", required=True, help="Date (YYYY-MM-DD)")
    parser_add.add_argument("--start", required=True, help="Start time (HH:MM)")
    parser_add.add_argument("--end", required=True, help="End time (HH:MM)")
    parser_add.add_argument("--role", required=True, help="Role (e.g. TA, AppSec)")
    parser_add.add_argument("--task", required=True, help="Short task description")
    parser_add.add_argument("--notes", default="", help="Optional notes")
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_db()
    elif args.command == "add":
        add_entry(args.date, args.start, args.end, args.role, args.task, args.notes)
    elif args.command == "view":
        view_entries()
    elif args.command == "delete":
        delete_entry(args.id)
    elif args.command == "prompt":
        add_interactive()
    else:
        main_menu()