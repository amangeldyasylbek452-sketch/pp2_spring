 --Amangeldi Assylbek lab2
 --1.1
CREATE DATABASE hotel_main
    WITH OWNER = CURRENT_USER
         TEMPLATE = template0
         ENCODING = 'UTF8';
 --1.2
CREATE DATABASE hotel_archive
    WITH TEMPLATE = template0
         ENCODING = 'UTF8'
         CONNECTION LIMIT = 40;
 --1.3
CREATE DATABASE hotel_test
    WITH TEMPLATE = template0
         ENCODING = 'UTF8'
         CONNECTION LIMIT = 8;
 
ALTER DATABASE hotel_test IS_TEMPLATE = true;
 --2.1
CREATE TABLE guests (
    guest_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone CHAR(15),
    date_of_birth DATE,
    registration_date DATE,
    loyalty_balance NUMERIC(10,2),
    is_active BOOLEAN,
    loyalty_points BIGINT
);
 
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    job_title VARCHAR(40),
    hire_date DATE,
    salary NUMERIC(12,2),
    is_full_time BOOLEAN,
    years_experience INTEGER
);
 
CREATE TABLE rooms (
    room_id SERIAL PRIMARY KEY,
    room_code CHAR(6),
    room_name VARCHAR(60),
    description TEXT,
    floor_number SMALLINT,
    capacity INTEGER,
    nightly_rate NUMERIC(10,2),
    is_available BOOLEAN,
    floor_area REAL,
    created_at TIMESTAMP WITHOUT TIME ZONE
);
 --2.2
CREATE TABLE housekeeping_schedule (
    schedule_id SERIAL PRIMARY KEY,
    room_id INTEGER,
    employee_id INTEGER,
    service_date DATE,
    start_time TIME WITHOUT TIME ZONE,
    end_time TIME WITHOUT TIME ZONE,
    duration INTERVAL,
    service_notes VARCHAR(100)
);
 
CREATE TABLE reservations (
    reservation_id SERIAL PRIMARY KEY,
    guest_id INTEGER,
    room_id INTEGER,
    check_in_date DATE,
    check_out_date DATE,
    number_of_guests SMALLINT,
    status_code CHAR(2),
    total_amount NUMERIC(12,2),
    discount_percentage NUMERIC(4,1),
    booking_timestamp TIMESTAMP WITH TIME ZONE,
    last_updated TIMESTAMP WITH TIME ZONE
);
 --3.1
ALTER TABLE guests
    ADD COLUMN middle_name VARCHAR(30),
    ADD COLUMN guest_status VARCHAR(20);
 
ALTER TABLE guests
    ALTER COLUMN phone TYPE VARCHAR(25);
 
ALTER TABLE guests
    ALTER COLUMN guest_status SET DEFAULT 'ACTIVE',
    ALTER COLUMN loyalty_balance SET DEFAULT 0.00;
 
ALTER TABLE guests
    RENAME COLUMN registration_date TO registered_on;
 
ALTER TABLE employees
    ADD COLUMN department_code CHAR(5),
    ADD COLUMN specialization TEXT;
ALTER TABLE employees
    ALTER COLUMN years_experience TYPE SMALLINT;
ALTER TABLE employees
    ALTER COLUMN is_full_time SET DEFAULT TRUE;
ALTER TABLE employees
    ADD COLUMN last_training_date DATE;
ALTER TABLE rooms
    ADD COLUMN room_category_id SMALLINT,
    ADD COLUMN comfort_level SMALLINT;
ALTER TABLE rooms
    ALTER COLUMN room_code TYPE VARCHAR(10);
ALTER TABLE rooms
    ALTER COLUMN capacity SET DEFAULT 2;
ALTER TABLE rooms
    ADD COLUMN has_balcony BOOLEAN DEFAULT FALSE;
 --3.2

ALTER TABLE housekeeping_schedule
    ADD COLUMN priority_level SMALLINT;
 
ALTER TABLE housekeeping_schedule
    DROP COLUMN duration;
 
ALTER TABLE housekeeping_schedule
    ADD COLUMN service_type VARCHAR(20);
 
ALTER TABLE housekeeping_schedule
    ALTER COLUMN service_notes TYPE VARCHAR(200);
 
ALTER TABLE housekeeping_schedule
    ADD COLUMN equipment_needed TEXT;
 
ALTER TABLE reservations
    ADD COLUMN extra_charges NUMERIC(10,2) DEFAULT 0.00;
 
ALTER TABLE reservations
    ALTER COLUMN status_code TYPE VARCHAR(20);
 
ALTER TABLE reservations
    RENAME COLUMN status_code TO reservation_status;
 
ALTER TABLE reservations
    ALTER COLUMN reservation_status SET DEFAULT 'PENDING';
 
ALTER TABLE reservations
    ADD COLUMN actual_check_in TIMESTAMP WITH TIME ZONE;
 
ALTER TABLE reservations
    DROP COLUMN last_updated;
 --4.1
CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(100),
    department_code CHAR(5),
    office_location VARCHAR(50),
    phone VARCHAR(20),
    annual_budget NUMERIC(14,2),
    established_year INTEGER
);
 
CREATE TABLE hotel_services (
    service_id SERIAL PRIMARY KEY,
    service_code CHAR(8),
    service_name VARCHAR(100),
    description TEXT,
    unit_price NUMERIC(10,2),
    average_duration INTERVAL,
    is_available BOOLEAN,
    customer_rating DOUBLE PRECISION,
    created_at TIMESTAMP WITHOUT TIME ZONE
) TABLESPACE service_data;
 
CREATE TABLE reservation_services (
    reservation_service_id SERIAL PRIMARY KEY,
    reservation_id INTEGER,
    service_id INTEGER,
    service_date DATE,
    quantity SMALLINT,
    unit_price NUMERIC(10,2),
    total_price NUMERIC(12,2),
    service_status VARCHAR(20)
);
 --4.2

ALTER TABLE employees
    ADD COLUMN department_id INTEGER;
 
ALTER TABLE reservations
    ADD COLUMN assigned_employee_id INTEGER;
 
ALTER TABLE employees
    ADD COLUMN supervisor_id INTEGER;
 
CREATE TABLE room_categories (
    category_id SMALLSERIAL PRIMARY KEY,
    category_name VARCHAR(40),
    category_code CHAR(3),
    base_rate NUMERIC(10,2),
    max_occupancy SMALLINT
);
 
CREATE TABLE season_calendar (
    season_id SMALLSERIAL PRIMARY KEY,
    season_name VARCHAR(30),
    calendar_year INTEGER,
    start_date DATE,
    end_date DATE,
    booking_deadline TIMESTAMP WITH TIME ZONE,
    price_multiplier NUMERIC(4,2),
    is_current BOOLEAN
);
 --5.1
DROP TABLE IF EXISTS reservation_services;
DROP TABLE IF EXISTS hotel_services;
 
DROP TABLE IF EXISTS room_categories;
 
CREATE TABLE room_categories (
    category_id SMALLSERIAL PRIMARY KEY,
    category_name VARCHAR(40),
    category_code CHAR(3),
    base_rate NUMERIC(10,2),
    max_occupancy SMALLINT,
    description TEXT
);
 
DROP TABLE IF EXISTS season_calendar CASCADE;
 
CREATE TABLE season_calendar (
    season_id SMALLSERIAL PRIMARY KEY,
    season_name VARCHAR(30),
    calendar_year INTEGER,
    start_date DATE,
    end_date DATE,
    booking_deadline TIMESTAMP WITH TIME ZONE,
    price_multiplier NUMERIC(4,2),
    is_current BOOLEAN
);
 
