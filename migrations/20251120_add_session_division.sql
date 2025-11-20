-- Migration: add division tracking to sessions
-- Date: 2025-11-20

USE archery_db;

-- 1. Add the new column as nullable to avoid failures during backfill
ALTER TABLE session
    ADD COLUMN division_id INT NULL AFTER round_id;

-- 2. Backfill from the member's current division
UPDATE session s
JOIN club_member cm ON cm.id = s.member_id
SET s.division_id = cm.division_id
WHERE s.division_id IS NULL;

-- 3. Enforce NOT NULL and add the foreign key
ALTER TABLE session
    MODIFY COLUMN division_id INT NOT NULL,
    ADD CONSTRAINT fk_session_division
        FOREIGN KEY (division_id)
        REFERENCES division(id)
        ON DELETE RESTRICT;
