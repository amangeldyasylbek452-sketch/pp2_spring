import csv
import json
from connect import connect

DEFAULT_GROUPS = ["Family", "Work", "Friend", "Other"]


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


def format_contact_row(row):
    return (
        f"{row[1]} | email: {row[2] or '-'} | birthday: {row[3] or '-'} | "
        f"group: {row[4] or '-'} | phones: {row[5] or '-'} | added: {row[6]}"
    )


def show_contacts(rows):
    if not rows:
        print("No contacts found")
        return

    for row in rows:
        print(format_contact_row(row))


def query_contacts(limit=100, offset=0, group_name=None, email_search=None, search_pattern=None, sort_by="name"):
    where_clauses = []
    params = []

    if group_name:
        where_clauses.append("g.name = %s")
        params.append(group_name)
    if email_search:
        where_clauses.append("c.email ILIKE %s")
        params.append(f"%{email_search}%")
    if search_pattern:
        where_clauses.append(
            "(c.name ILIKE %s OR c.email ILIKE %s OR p.phone ILIKE %s)"
        )
        params.extend([f"%{search_pattern}%"] * 3)

    where_clause = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    order_clause = "ORDER BY c.name"

    if sort_by == "birthday":
        order_clause = "ORDER BY c.birthday NULLS LAST"
    elif sort_by == "date_added":
        order_clause = "ORDER BY c.created_at"

    sql = f"""
        SELECT c.id,
               c.name,
               c.email,
               c.birthday,
               g.name AS group_name,
               COALESCE(string_agg(p.phone || ' (' || p.type || ')', ', ' ORDER BY p.id), '') AS phones,
               c.created_at
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON p.contact_id = c.id
        {where_clause}
        GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
        {order_clause}
        LIMIT %s OFFSET %s
    """

    params.extend([limit, offset])

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def insert_many_from_csv():
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


def export_to_json():
    filename = input("Enter export filename (e.g. contacts.json): ").strip() or "contacts_export.json"
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT c.id, c.name, c.email, c.birthday, g.name AS group_name, p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON p.contact_id = c.id
        ORDER BY c.name, p.id
        """
    )
    rows = cur.fetchall()

    contacts = []
    contact_map = {}
    for contact_id, name, email, birthday, group_name, phone, phone_type in rows:
        if contact_id not in contact_map:
            contact_map[contact_id] = {
                "name": name,
                "email": email,
                "birthday": birthday.isoformat() if birthday else None,
                "group": group_name,
                "phones": [],
            }
        if phone:
            contact_map[contact_id]["phones"].append({"phone": phone, "type": phone_type})

    contacts = list(contact_map.values())
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(contacts, file, indent=2, default=str)

    cur.close()
    conn.close()
    print(f"Exported {len(contacts)} contacts to {filename}")


def import_from_json():
    filename = input("Enter import filename (e.g. contacts.json): ").strip() or "contacts_import.json"
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    conn = connect()
    cur = conn.cursor()
    imported = 0
    skipped = 0

    for item in data:
        name = item.get("name")
        if not name:
            skipped += 1
            continue

        email = item.get("email")
        birthday = item.get("birthday")
        if birthday == "":
            birthday = None
        group_name = item.get("group")
        phone_items = item.get("phones") or []

        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        existing = cur.fetchone()
        if existing:
            choice = None
            while choice not in ("skip", "overwrite"):
                choice = input(f"Contact '{name}' already exists. skip or overwrite? ").strip().lower()
            if choice == "skip":
                skipped += 1
                continue
            cur.execute(
                "UPDATE contacts SET email = %s, birthday = %s, group_id = %s WHERE name = %s",
                (email, birthday, get_group_id(cur, group_name), name),
            )
            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            contact_id = cur.fetchone()[0]
            cur.execute("DELETE FROM phones WHERE contact_id = %s", (contact_id,))
        else:
            contact_id = upsert_contact(cur, name, email, birthday, group_name)

        for phone_item in phone_items:
            if isinstance(phone_item, dict):
                phone = phone_item.get("phone")
                phone_type = phone_item.get("type", "mobile")
            else:
                phone = str(phone_item)
                phone_type = "mobile"
            insert_phone(cur, contact_id, phone, phone_type)

        imported += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"Imported {imported} contacts from JSON")
    if skipped:
        print(f"Skipped {skipped} contacts")


def search_by_pattern():
    pattern = input("Enter search pattern: ").strip()
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    show_contacts(rows)


def search_by_email():
    email = input("Enter email partial: ").strip()
    rows = query_contacts(email_search=email)
    show_contacts(rows)


def filter_by_group():
    group_name = input("Enter group name (Family, Work, Friend, Other): ").strip()
    rows = query_contacts(group_name=group_name)
    show_contacts(rows)


def paginate_contacts():
    try:
        limit = int(input("Enter page size [5]: ").strip() or 5)
    except ValueError:
        limit = 5
    group_name = input("Filter by group (leave blank for all): ").strip() or None
    email_search = input("Search by email partial (leave blank for all): ").strip() or None
    sort_by = input("Sort by name, birthday, or date_added [name]: ").strip().lower() or "name"
    if sort_by not in ("name", "birthday", "date_added"):
        sort_by = "name"

    offset = 0
    while True:
        rows = query_contacts(limit=limit, offset=offset, group_name=group_name, email_search=email_search, sort_by=sort_by)
        if not rows and offset == 0:
            print("No results found")
            break
        if not rows:
            print("No more pages")
            offset = max(0, offset - limit)
            break

        print(f"\nShowing page {offset // limit + 1}")
        show_contacts(rows)

        action = input("Enter [n]ext, [p]rev, [q]uit: ").strip().lower()
        if action == "n":
            offset += limit
        elif action == "p":
            offset = max(0, offset - limit)
        elif action == "q":
            break
        else:
            print("Invalid choice")


def add_phone_to_contact():
    name = input("Enter contact name: ").strip()
    phone = input("Enter phone number: ").strip()
    phone_type = input("Enter phone type (home/work/mobile): ").strip().lower()

    conn = connect()
    cur = conn.cursor()
    cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
    conn.commit()
    cur.close()
    conn.close()
    print("Phone added successfully")


def move_contact_to_group():
    name = input("Enter contact name: ").strip()
    group_name = input("Enter target group: ").strip()

    conn = connect()
    cur = conn.cursor()
    cur.execute("CALL move_to_group(%s, %s)", (name, group_name))
    conn.commit()
    cur.close()
    conn.close()
    print("Contact moved successfully")


def show_all():
    rows = query_contacts(limit=1000, offset=0)
    show_contacts(rows)


def menu():
    while True:
        print("\n--- EXTENDED CONTACT MENU ---")
        print("1 - Create schema")
        print("2 - Run functions.sql")
        print("3 - Run procedures.sql")
        print("4 - Import contacts from CSV")
        print("5 - Import contacts from JSON")
        print("6 - Export contacts to JSON")
        print("7 - Show all contacts")
        print("8 - Filter by group")
        print("9 - Search by email")
        print("10 - Search by pattern")
        print("11 - Paginate contacts")
        print("12 - Add phone to contact")
        print("13 - Move contact to group")
        print("0 - Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            create_schema()
        elif choice == "2":
            execute_sql_file("functions.sql")
        elif choice == "3":
            execute_sql_file("procedures.sql")
        elif choice == "4":
            insert_many_from_csv()
        elif choice == "5":
            import_from_json()
        elif choice == "6":
            export_to_json()
        elif choice == "7":
            show_all()
        elif choice == "8":
            filter_by_group()
        elif choice == "9":
            search_by_email()
        elif choice == "10":
            search_by_pattern()
        elif choice == "11":
            paginate_contacts()
        elif choice == "12":
            add_phone_to_contact()
        elif choice == "13":
            move_contact_to_group()
        elif choice == "0":
            print("Goodbye")
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    menu()
