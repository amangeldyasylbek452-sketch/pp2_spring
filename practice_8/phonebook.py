import csv
from connect import connect


def create_table():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Table is ready")


def execute_sql_file(filename):
    conn = connect()
    cur = conn.cursor()

    with open(filename, "r", encoding="utf-8") as file:
        sql = file.read()
        cur.execute(sql)

    conn.commit()
    cur.close()
    conn.close()
    print(f"{filename} executed successfully")


def insert_or_update_user():
    name = input("Enter name: ")
    phone = input("Enter phone: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("CALL insert_or_update_user(%s, %s)", (name, phone))

    conn.commit()
    cur.close()
    conn.close()
    print("User inserted or updated")


def search_by_pattern():
    pattern = input("Enter pattern: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if rows:
        for row in rows:
            print(row)
    else:
        print("No matching records found")


def insert_many_from_csv():
    names = []
    phones = []

    with open("contacts.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            names.append(row[0])
            phones.append(row[1])

    conn = connect()
    cur = conn.cursor()

    cur.execute("CALL insert_many_users(%s, %s)", (names, phones))

    cur.execute("SELECT * FROM invalid_data")
    invalid_rows = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()

    print("Bulk insert completed")

    if invalid_rows:
        print("Invalid data:")
        for row in invalid_rows:
            print(row)
    else:
        print("No invalid data")


def show_paginated():
    limit = int(input("Enter limit: "))
    offset = int(input("Enter offset: "))

    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if rows:
        for row in rows:
            print(row)
    else:
        print("No records found")


def delete_user():
    value = input("Enter username or phone to delete: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("CALL delete_user(%s)", (value,))

    conn.commit()
    cur.close()
    conn.close()
    print("Delete completed")


def show_all():
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM phonebook ORDER BY id")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if rows:
        for row in rows:
            print(row)
    else:
        print("Phonebook is empty")


def menu():
    while True:
        print("\n--- PHONEBOOK MENU ---")
        print("1 - Create table")
        print("2 - Run functions.sql")
        print("3 - Run procedures.sql")
        print("4 - Insert or update one user")
        print("5 - Search by pattern")
        print("6 - Insert many users from CSV")
        print("7 - Show paginated data")
        print("8 - Delete user by name or phone")
        print("9 - Show all contacts")
        print("0 - Exit")

        choice = input("Choose: ")

        if choice == "1":
            create_table()
        elif choice == "2":
            execute_sql_file("functions.sql")
        elif choice == "3":
            execute_sql_file("procedures.sql")
        elif choice == "4":
            insert_or_update_user()
        elif choice == "5":
            search_by_pattern()
        elif choice == "6":
            insert_many_from_csv()
        elif choice == "7":
            show_paginated()
        elif choice == "8":
            delete_user()
        elif choice == "9":
            show_all()
        elif choice == "0":
            print("Goodbye")
            break
        else:
            print("Invalid choice")


menu()