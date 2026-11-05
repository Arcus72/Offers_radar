-- Restores offers.csv into the offers table, skipping offers already present.
-- Run: docker compose exec db psql -U postgres -d accdata -f /db_backup/restore.sql
BEGIN;

CREATE TABLE IF NOT EXISTS offers (
    added_date DATE,
    type VARCHAR(100),
    city VARCHAR(100),
    district VARCHAR(100),
    street VARCHAR(255),
    area NUMERIC,
    rooms INTEGER,
    bed_rooms INTEGER,
    bathrooms INTEGER,
    floor INTEGER,
    building_floors INTEGER,
    building_type VARCHAR(100),
    building_material VARCHAR(100),
    build_year INTEGER,
    interior_description TEXT,
    lift BOOLEAN,
    kitchen_type VARCHAR(100),
    condition VARCHAR(100),
    has_balcony BOOLEAN,
    balcony_area NUMERIC,
    storage_room BOOLEAN,
    parking VARCHAR(255),
    heating VARCHAR(100),
    accessible BOOLEAN,
    fenced BOOLEAN,
    monitoring BOOLEAN,
    rent_fee NUMERIC,
    school BOOLEAN,
    school_dist NUMERIC,
    kindergarten BOOLEAN,
    kindergarten_dist NUMERIC,
    university BOOLEAN,
    university_dist NUMERIC,
    shop BOOLEAN,
    shop_dist NUMERIC,
    public_transport BOOLEAN,
    public_transport_dist NUMERIC,
    park BOOLEAN,
    park_dist NUMERIC,
    medical BOOLEAN,
    medical_dist NUMERIC,
    pharmacy BOOLEAN,
    pharmacy_dist NUMERIC,
    city_center BOOLEAN,
    city_center_dist NUMERIC,
    title TEXT,
    price NUMERIC,
    offer_id BIGINT PRIMARY KEY,
    main_img_url TEXT,
    market_price NUMERIC
);

CREATE TEMP TABLE stg (LIKE offers) ON COMMIT DROP;

COPY stg FROM '/db_backup/offers.csv' WITH (FORMAT csv, DELIMITER ';', HEADER MATCH);

INSERT INTO offers
SELECT *
FROM stg
ON CONFLICT (offer_id) DO NOTHING;

COMMIT;
