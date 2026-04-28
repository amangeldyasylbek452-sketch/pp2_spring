-- 1. Procedure: insert or update a contact with a phone
CREATE OR REPLACE PROCEDURE insert_or_update_user(p_name TEXT, p_phone TEXT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INT;
BEGIN
    SELECT id INTO v_contact_id FROM contacts WHERE name = p_name;

    IF v_contact_id IS NULL THEN
        INSERT INTO contacts(name) VALUES (p_name)
        RETURNING id INTO v_contact_id;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM phones WHERE contact_id = v_contact_id AND phone = p_phone
    ) THEN
        INSERT INTO phones(contact_id, phone, type)
        VALUES (v_contact_id, p_phone, 'mobile');
    END IF;
END;
$$;


-- 2. Procedure: insert many contacts with validation
CREATE OR REPLACE PROCEDURE insert_many_users(p_names TEXT[], p_phones TEXT[])
LANGUAGE plpgsql
AS $$
DECLARE
    i INTEGER;
    v_contact_id INT;
BEGIN
    IF array_length(p_names, 1) IS DISTINCT FROM array_length(p_phones, 1) THEN
        RAISE EXCEPTION 'Arrays must have same length';
    END IF;

    CREATE TEMP TABLE IF NOT EXISTS invalid_data (
        name TEXT,
        phone TEXT
    ) ON COMMIT DROP;

    DELETE FROM invalid_data;

    FOR i IN 1..array_length(p_names, 1) LOOP
        IF p_phones[i] ~ '^\+?[0-9]{7,15}$' THEN
            SELECT id INTO v_contact_id FROM contacts WHERE name = p_names[i];

            IF v_contact_id IS NULL THEN
                INSERT INTO contacts(name) VALUES (p_names[i])
                RETURNING id INTO v_contact_id;
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM phones WHERE contact_id = v_contact_id AND phone = p_phones[i]
            ) THEN
                INSERT INTO phones(contact_id, phone, type)
                VALUES (v_contact_id, p_phones[i], 'mobile');
            END IF;
        ELSE
            INSERT INTO invalid_data(name, phone)
            VALUES (p_names[i], p_phones[i]);
        END IF;
    END LOOP;
END;
$$;


-- 3. Procedure: delete by contact name or phone number
CREATE OR REPLACE PROCEDURE delete_user(p_value TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM contacts
    WHERE name = p_value
       OR id IN (
           SELECT contact_id FROM phones WHERE phone = p_value
       );
END;
$$;


-- 4. Procedure: add a new phone number to an existing contact
CREATE OR REPLACE PROCEDURE add_phone(p_contact_name VARCHAR, p_phone VARCHAR, p_type VARCHAR)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INT;
BEGIN
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type: %', p_type;
    END IF;

    SELECT id INTO v_contact_id FROM contacts WHERE name = p_contact_name;
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact % does not exist', p_contact_name;
    END IF;

    INSERT INTO phones(contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);
END;
$$;


-- 5. Procedure: move a contact into a group, creating the group if needed
CREATE OR REPLACE PROCEDURE move_to_group(p_contact_name VARCHAR, p_group_name VARCHAR)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INT;
    v_group_id INT;
BEGIN
    SELECT id INTO v_contact_id FROM contacts WHERE name = p_contact_name;
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact % does not exist', p_contact_name;
    END IF;

    INSERT INTO groups(name) VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
END;
$$;