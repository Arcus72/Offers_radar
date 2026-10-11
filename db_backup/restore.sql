-- Restores offers.csv into the offers table, skipping offers already present.
-- Run: docker compose exec db psql -U postgres -d accdata -f /db_backup/restore.sql
BEGIN;

CREATE TEMP TABLE stg (LIKE offers) ON COMMIT DROP;

-- HEADER MATCH: fails if the CSV columns differ from the table's (names or order)
COPY stg FROM '/db_backup/offers.csv' WITH (FORMAT csv, DELIMITER ';', HEADER MATCH);

INSERT INTO offers SELECT * FROM stg ON CONFLICT (offer_id) DO NOTHING;

COMMIT;
