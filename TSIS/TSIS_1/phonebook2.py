import csv
from connect import connect

DEFAULT_GROUPS = ["Family", "Work", "Friend", "Other"]


def create_schema():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            email VARCHAR(100),
            birthday DATE,
            group_id INTEGER REFERENCES groups(id),
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS phones (
            id SERIAL PRIMARY KEY,
            contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
            phone VARCHAR(20) NOT NULL,
            type VARCHAR(10) NOT NULL CHECK (type IN ('home', 'work', 'mobile'))
        )
    """)

    for group in DEFAULT_GROUPS:
        cur.execute(
            "INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
            (group,),
        )

    conn.commit()
    cur.close()
    conn.close()
    print("Schema created successfully")


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


def get_group_id(cur, group_name):
    if not group_name:
        return None

    cur.execute(
        "INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
        (group_name,),
    )
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    row = cur.fetchone()
    return row[0] if row else None


def upsert_contact(cur, name, email=None, birthday=None, group_name=None):
    group_id = get_group_id(cur, group_name) if group_name else None
    cur.execute(
        """
            INSERT INTO contacts (name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE
            SET email = COALESCE(EXCLUDED.email, contacts.email),
                birthday = COALESCE(EXCLUDED.birthday, contacts.birthday),
                group_id = COALESCE(EXCLUDED.group_id, contacts.group_id)
            RETURNING id
        """,
        (name, email, birthday, group_id),
    )
    return cur.fetchone()[0]


def insert_phone(cur, contact_id, phone, phone_type="mobile"):
    if not phone:
        return
    if phone_type not in ("home", "work", "mobile"):
        phone_type = "mobile"

    cur.execute(
        "SELECT 1 FROM phones WHERE contact_id = %s AND phone = %s",
        (contact_id, phone),
    )
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
            (contact_id, phone, phone_type),
        )


def show_all_contacts():
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        """
            SELECT c.name,
                   c.email,
                   c.birthday,
                   g.name AS group_name,
                   COALESCE(string_agg(p.phone || ' (' || p.type || ')', ', ' ORDER BY p.id), '') AS phones
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            LEFT JOIN phones p ON p.contact_id = c.id
            GROUP BY c.id, g.name
            ORDER BY c.name
        """
    )
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if rows:
        for row in rows:
            print(
                f"{row[0]} | email: {row[1] or '-'} | birthday: {row[2] or '-'} | "
                f"group: {row[3] or '-'} | phones: {row[4] or '-'}"
            )
    else:
        print("Contact list is empty")


def insert_from_csv():
    conn = connect()
    cur = conn.cursor()

    imported = 0
    skipped = 0

    with open("contacts.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if not row:
                continue
            values = [item.strip() for item in row]
            if not values or values[0].lower() == "name":
                continue

            if len(values) >= 6:
                name, email, birthday, group_name, phone, phone_type = (
                    values[0], values[1] or None, values[2] or None,
                    values[3] or None, values[4] or None, values[5].lower() or "mobile"
                )
            elif len(values) == 5:
                name, email, birthday, group_name, phone = (
                    values[0], values[1] or None, values[2] or None,
                    values[3] or None, values[4] or None
                )
                phone_type = "mobile"
            elif len(values) == 2:
                name, phone = values[0], values[1]
                email = birthday = group_name = None
                phone_type = "mobile"
            else:
                skipped += 1
                continue

            if not name:
                skipped += 1
                continue

            contact_id = upsert_contact(cur, name, email, birthday, group_name)
            insert_phone(cur, contact_id, phone, phone_type)
            imported += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"Imported {imported} contacts from CSV")
    if skipped:
        print(f"Skipped {skipped} invalid rows")


def insert_from_console():
    name = input("Enter name: ").strip()
    email = input("Enter email (optional): ").strip() or None
    birthday = input("Enter birthday (YYYY-MM-DD, optional): ").strip() or None
    group_name = input("Enter group (Family, Work, Friend, Other): ").strip() or None
    phone = input("Enter phone: ").strip()
    phone_type = input("Enter phone type (home/work/mobile): ").strip().lower() or "mobile"

    conn = connect()
    cur = conn.cursor()
    contact_id = upsert_contact(cur, name, email, birthday, group_name)
    insert_phone(cur, contact_id, phone, phone_type)

    conn.commit()
    cur.close()
    conn.close()
    print("Contact added successfully")


def search_by_name():
    pattern = input("Enter name or part of name: ").strip()

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        """
            SELECT c.name, c.email, c.birthday, g.name AS group_name,
                   COALESCE(string_agg(p.phone || ' (' || p.type || ')', ', ' ORDER BY p.id), '') AS phones
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            LEFT JOIN phones p ON p.contact_id = c.id
            WHERE c.name ILIKE %s
            GROUP BY c.id, g.name
            ORDER BY c.name
        """,
        (f"%{pattern}%",),
    )
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if rows:
        for row in rows:
            print(
                f"{row[0]} | email: {row[1] or '-'} | birthday: {row[2] or '-'} | "
                f"group: {row[3] or '-'} | phones: {row[4] or '-'}"
            )
    else:
        print("No contacts found")


def search_by_phone_prefix():
    prefix = input("Enter phone prefix: ").strip()

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        """
            SELECT c.name, c.email, c.birthday, g.name AS group_name,
                   COALESCE(string_agg(p.phone || ' (' || p.type || ')', ', ' ORDER BY p.id), '') AS phones
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            JOIN phones p ON p.contact_id = c.id
            WHERE p.phone LIKE %s
            GROUP BY c.id, g.name
            ORDER BY c.name
        """,
        (f"{prefix}%",),
    )
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if rows:
        for row in rows:
            print(
                f"{row[0]} | email: {row[1] or '-'} | birthday: {row[2] or '-'} | "
                f"group: {row[3] or '-'} | phones: {row[4] or '-'}"
            )
    else:
        print("No contacts found")


def update_contact():
    name = input("Enter current name of contact: ").strip()
    print("1 - Update name")
    print("2 - Update phone")

    choice = input("Choose option: ").strip()

    conn = connect()
    cur = conn.cursor()

    if choice == "1":
        new_name = input("Enter new name: ").strip()
        cur.execute(
            "UPDATE contacts SET name = %s WHERE name = %s",
            (new_name, name),
        )
        print("Name updated successfully")
    elif choice == "2":
        new_phone = input("Enter new phone: ").strip()
        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        row = cur.fetchone()
        if row:
            contact_id = row[0]
            insert_phone(cur, contact_id, new_phone)
            print("Phone added successfully")
        else:
            print("Contact not found")
    else:
        print("Invalid choice")

    conn.commit()
    cur.close()
    conn.close()


def delete_by_name():
    name = input("Enter name to delete: ").strip()

    conn = connect()
    cur = conn.cursor()

    cur.execute("DELETE FROM contacts WHERE name = %s", (name,))

    conn.commit()
    cur.close()
    conn.close()
    print("Contact deleted by name")


def delete_by_phone():
    phone = input("Enter phone to delete: ").strip()

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM contacts WHERE id IN (SELECT contact_id FROM phones WHERE phone = %s)",
        (phone,),
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Contact deleted by phone")


def menu():
    while True:
        print("\n--- PHONEBOOK MENU ---")
        print("1. Create schema")
        print("2. Import contacts from CSV")
        print("3. Add contact from console")
        print("4. Show all contacts")
        print("5. Search by name")
        print("6. Search by phone prefix")
        print("7. Update contact")
        print("8. Delete by name")
        print("9. Delete by phone")
        print("0. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            create_schema()
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