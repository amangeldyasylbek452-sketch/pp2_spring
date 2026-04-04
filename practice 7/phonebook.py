import csv
from connect import connect


def create_table():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL
        )
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Table created successfully")


def insert_from_csv():
    conn = connect()
    cur = conn.cursor()

    with open("contacts.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            name = row[0]
            phone = row[1]

            cur.execute(
                "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
                (name, phone)
            )

    conn.commit()
    cur.close()
    conn.close()
    print("Data imported from CSV successfully")


def insert_from_console():
    name = input("Enter name: ")
    phone = input("Enter phone: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
        (name, phone)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Contact added successfully")


def show_all_contacts():
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM phonebook ORDER BY id")
    rows = cur.fetchall()

    if rows:
        for row in rows:
            print(row)
    else:
        print("PhoneBook is empty")

    cur.close()
    conn.close()


def search_by_name():
    pattern = input("Enter name or part of name: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM phonebook WHERE name ILIKE %s",
        (f"%{pattern}%",)
    )
    rows = cur.fetchall()

    if rows:
        for row in rows:
            print(row)
    else:
        print("No contacts found")

    cur.close()
    conn.close()


def search_by_phone_prefix():
    prefix = input("Enter phone prefix: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM phonebook WHERE phone LIKE %s",
        (f"{prefix}%",)
    )
    rows = cur.fetchall()

    if rows:
        for row in rows:
            print(row)
    else:
        print("No contacts found")

    cur.close()
    conn.close()


def update_contact():
    name = input("Enter current name of contact: ")
    print("1 - Update name")
    print("2 - Update phone")

    choice = input("Choose option: ")

    conn = connect()
    cur = conn.cursor()

    if choice == "1":
        new_name = input("Enter new name: ")
        cur.execute(
            "UPDATE phonebook SET name = %s WHERE name = %s",
            (new_name, name)
        )
        print("Name updated successfully")

    elif choice == "2":
        new_phone = input("Enter new phone: ")
        cur.execute(
            "UPDATE phonebook SET phone = %s WHERE name = %s",
            (new_phone, name)
        )
        print("Phone updated successfully")

    else:
        print("Invalid choice")

    conn.commit()
    cur.close()
    conn.close()


def delete_by_name():
    name = input("Enter name to delete: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM phonebook WHERE name = %s",
        (name,)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Contact deleted by name")


def delete_by_phone():
    phone = input("Enter phone to delete: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM phonebook WHERE phone = %s",
        (phone,)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Contact deleted by phone")


def menu():
    while True:
        print("\n--- PHONEBOOK MENU ---")
        print("1. Create table")
        print("2. Import contacts from CSV")
        print("3. Add contact from console")
        print("4. Show all contacts")
        print("5. Search by name")
        print("6. Search by phone prefix")
        print("7. Update contact")
        print("8. Delete by name")
        print("9. Delete by phone")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            create_table()
        elif choice == "2":
            insert_from_csv()
        elif choice == "3":
            insert_from_console()
        elif choice == "4":
            show_all_contacts()
        elif choice == "5":
            search_by_name()
        elif choice == "6":
            search_by_phone_prefix()
        elif choice == "7":
            update_contact()
        elif choice == "8":
            delete_by_name()
        elif choice == "9":
            delete_by_phone()
        elif choice == "0":
            print("Goodbye")
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    menu()