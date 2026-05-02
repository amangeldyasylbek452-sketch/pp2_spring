# phonebook.py - Phone Book app TSIS1

import csv
import json
import psycopg2
import psycopg2.extras
from datetime import datetime
from connect import get_conn

# connect to database
conn = get_conn()

# print one contact nicely
def print_contact(c):
    print(f"  Name: {c['first_name']} {c['last_name']}")
    print(f"  Email: {c['email']}")
    print(f"  Birthday: {c['birthday']}")
    print(f"  Group: {c['group_name']}")
    print(f"  Phones: {c['phones_csv']}")
    print()

# find group by name, create if not exists
def get_group_id(name):
    cur = conn.cursor()
    cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    # group not found, create new one
    cur.execute("INSERT INTO groups(name) VALUES(%s) RETURNING id", (name,))
    gid = cur.fetchone()[0]
    conn.commit()
    return gid

# add new contact
def add_contact():
    print("\n-- Add Contact --")
    first = input("First name: ")
    last  = input("Last name: ")
    email = input("Email: ") or None
    bday  = input("Birthday (YYYY-MM-DD): ") or None
    group = input("Group name: ")

    gid = get_group_id(group) if group else None

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO contacts(first_name, last_name, email, birthday, group_id)"
        " VALUES(%s,%s,%s,%s,%s) RETURNING id",
        (first, last, email, bday, gid)
    )
    cid = cur.fetchone()[0]
    conn.commit()

    # add phone numbers one by one
    while True:
        phone = input("Phone (press Enter to stop): ")
        if not phone:
            break
        ptype = input("Type (home/work/mobile): ") or "mobile"
        cur.execute(
            "INSERT INTO phones(contact_id, phone, type) VALUES(%s,%s,%s)",
            (cid, phone, ptype)
        )
        conn.commit()
    print(f"Contact {first} {last} added!")

# delete contact by name or phone
def delete_contact():
    print("\n-- Delete Contact --")
    term = input("Enter name or phone: ")
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM contacts WHERE first_name ILIKE %s OR last_name ILIKE %s"
        " OR id IN (SELECT contact_id FROM phones WHERE phone ILIKE %s)",
        (term, term, term)
    )
    print(f"Deleted {cur.rowcount} contact(s).")
    conn.commit()

# search contacts by name, email or phone
def search_contacts():
    print("\n-- Search --")
    term = input("Search: ")
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    # calls our search_contacts function from procedures.sql
    cur.execute("SELECT * FROM search_contacts(%s)", (term,))
    rows = cur.fetchall()
    if not rows:
        print("Nothing found.")
        return
    for r in rows:
        print_contact(dict(r))

# browse contacts page by page
def browse_contacts():
    print("\n-- Browse --")
    sc  = input("Sort by: 1=name  2=birthday  3=date added: ")
    col = {"2": "c.birthday", "3": "c.created_at"}.get(sc, "c.first_name")
    gf  = input("Filter by group id (blank = all): ")
    where = f"WHERE c.group_id = {int(gf)}" if gf.isdigit() else ""

    offset = 0
    while True:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(f"""
            SELECT c.first_name, c.last_name, c.email, c.birthday,
                   g.name AS group_name,
                   STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones_csv
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            LEFT JOIN phones p ON p.contact_id = c.id
            {where}
            GROUP BY c.id, g.name, c.created_at
            ORDER BY {col}
            LIMIT 5 OFFSET %s
        """, (offset,))
        rows = cur.fetchall()

        if not rows:
            print("No more contacts.")
            break

        for r in rows:
            print_contact(dict(r))

        nav = input("[n]ext  [p]rev  [q]uit: ").strip().lower()
        if nav == "n":
            offset += 5
        elif nav == "p":
            offset = max(0, offset - 5)
        else:
            break

# move contact to another group using stored procedure
def move_to_group():
    print("\n-- Move to Group --")
    name  = input("Contact name (first last): ")
    group = input("New group name: ")
    cur = conn.cursor()
    try:
        cur.execute("CALL move_to_group(%s::VARCHAR, %s::VARCHAR)", (name, group))
        conn.commit()
        print("Done!")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")

# export all contacts to json file
def export_json():
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT c.id, c.first_name, c.last_name, c.email,
               c.birthday::TEXT, g.name AS group_name
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
    """)
    contacts = cur.fetchall()
    data = []
    for c in contacts:
        d = dict(c)
        cid = d.pop("id")
        # get phones for this contact
        cur.execute("SELECT phone, type FROM phones WHERE contact_id = %s", (cid,))
        d["phones"] = [dict(p) for p in cur.fetchall()]
        data.append(d)

    filename = f"contacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    json.dump(data, open(filename, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"Exported to {filename}")

# import contacts from json file
def import_json():
    path = input("JSON filename: ")
    records = json.load(open(path, encoding="utf-8"))
    for r in records:
        fn, ln = r.get("first_name", ""), r.get("last_name", "")
        cur = conn.cursor()
        # check if contact already exists
        cur.execute("SELECT id FROM contacts WHERE first_name ILIKE %s AND last_name ILIKE %s", (fn, ln))
        existing = cur.fetchone()
        if existing:
            ans = input(f"{fn} {ln} already exists. Overwrite? y/n: ")
            if ans != "y":
                continue
            cur.execute("DELETE FROM contacts WHERE id = %s", (existing[0],))
            conn.commit()

        gid = get_group_id(r["group_name"]) if r.get("group_name") else None
        cur.execute(
            "INSERT INTO contacts(first_name, last_name, email, birthday, group_id)"
            " VALUES(%s,%s,%s,%s,%s) RETURNING id",
            (fn, ln, r.get("email"), r.get("birthday"), gid)
        )
        cid = cur.fetchone()[0]
        conn.commit()

        for p in r.get("phones", []):
            cur.execute(
                "INSERT INTO phones(contact_id, phone, type) VALUES(%s,%s,%s)",
                (cid, p["phone"], p.get("type", "mobile"))
            )
        conn.commit()
    print("Import done!")

# import contacts from csv file
def import_csv():
    path = input("CSV filename: ")
    reader = csv.DictReader(open(path, encoding="utf-8"))
    for row in reader:
        try:
            fn  = row["first_name"].strip()
            ln  = row.get("last_name", "").strip()
            gid = get_group_id(row["group"].strip()) if row.get("group") else None
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO contacts(first_name, last_name, email, birthday, group_id)"
                " VALUES(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING id",
                (fn, ln, row.get("email") or None, row.get("birthday") or None, gid)
            )
            result = cur.fetchone()
            conn.commit()
            # add phone if provided
            if result and row.get("phone", "").strip():
                cur.execute(
                    "INSERT INTO phones(contact_id, phone, type) VALUES(%s,%s,%s)",
                    (result[0], row["phone"].strip(), row.get("phone_type", "mobile"))
                )
                conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Skipped row: {e}")
    print("CSV import done!")

# main menu
def main():
    while True:
        print("\n=== PhoneBook ===")
        print("1. Add contact")
        print("2. Delete contact")
        print("3. Search contacts")
        print("4. Browse contacts")
        print("5. Move to group")
        print("6. Export to JSON")
        print("7. Import from JSON")
        print("8. Import from CSV")
        print("0. Exit")

        choice = input("Choice: ")

        if choice == "1":
            add_contact()
        elif choice == "2":
            delete_contact()
        elif choice == "3":
            search_contacts()
        elif choice == "4":
            browse_contacts()
        elif choice == "5":
            move_to_group()
        elif choice == "6":
            export_json()
        elif choice == "7":
            import_json()
        elif choice == "8":
            import_csv()
        elif choice == "0":
            print("Bye!")
            conn.close()
            break
        else:
            print("Wrong choice.")

main()