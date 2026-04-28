-- 1. Extended schema for richer contacts
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100),
    birthday DATE,
    group_id INTEGER REFERENCES groups(id),
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS phones (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    phone VARCHAR(20) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('home', 'work', 'mobile'))
);

CREATE OR REPLACE FUNCTION search_contacts(pattern TEXT)
RETURNS TABLE(
    id INT,
    name TEXT,
    email TEXT,
    birthday DATE,
    group_name TEXT,
    phones TEXT,
    created_at TIMESTAMP
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
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
    WHERE c.name ILIKE '%' || pattern || '%'
       OR c.email ILIKE '%' || pattern || '%'
       OR p.phone ILIKE '%' || pattern || '%'
    GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
    ORDER BY c.name;
END;
$$;


CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(
    id INT,
    name TEXT,
    email TEXT,
    birthday DATE,
    group_name TEXT,
    phones TEXT,
    created_at TIMESTAMP
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
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
    GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
    ORDER BY c.created_at
    LIMIT p_limit OFFSET p_offset;
END;
$$;