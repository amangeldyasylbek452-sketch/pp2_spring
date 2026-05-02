-- add phone to existing contact by full name
CREATE OR REPLACE PROCEDURE add_phone(p_name VARCHAR, p_phone VARCHAR, p_type VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE
    v_id INTEGER;
BEGIN
    -- find contact by first and last name
    SELECT id INTO v_id FROM contacts
    WHERE first_name ILIKE split_part(p_name, ' ', 1)
    AND last_name ILIKE split_part(p_name, ' ', 2)
    LIMIT 1;

    IF v_id IS NULL THEN
        RAISE EXCEPTION 'Contact not found';
    END IF;

    INSERT INTO phones(contact_id, phone, type) VALUES(v_id, p_phone, p_type);
END;
$$;

-- move contact to another group, create group if not exists
CREATE OR REPLACE PROCEDURE move_to_group(p_name VARCHAR, p_group VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE
    v_cid INTEGER;
    v_gid INTEGER;
BEGIN
    -- find contact
    SELECT id INTO v_cid FROM contacts
    WHERE first_name ILIKE split_part(p_name, ' ', 1)
    AND last_name ILIKE split_part(p_name, ' ', 2)
    LIMIT 1;

    IF v_cid IS NULL THEN
        RAISE EXCEPTION 'Contact not found';
    END IF;

    -- find or create group
    SELECT id INTO v_gid FROM groups WHERE name ILIKE p_group;
    IF v_gid IS NULL THEN
        INSERT INTO groups(name) VALUES(p_group) RETURNING id INTO v_gid;
    END IF;

    UPDATE contacts SET group_id = v_gid WHERE id = v_cid;
END;
$$;

-- search contacts by name, email or phone
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(id INT, first_name VARCHAR, last_name VARCHAR,
              email VARCHAR, birthday DATE, group_name VARCHAR, phones_csv TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        c.id, c.first_name, c.last_name, c.email, c.birthday,
        g.name,
        STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ')
            OVER (PARTITION BY c.id)
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE c.first_name ILIKE '%' || p_query || '%'
       OR c.last_name  ILIKE '%' || p_query || '%'
       OR c.email      ILIKE '%' || p_query || '%'
       OR p.phone      ILIKE '%' || p_query || '%'
    ORDER BY c.last_name, c.first_name;
END;
$$;