-- -----------------------------------------------------
-- Archery Score Recording Database - Seed Data Script
-- Populated using:
-- 1. age classes 2025.pdf
-- 2. AA RULES (Version 6.7 - June 2022).pdf (Outdoor Target Archery)
-- -----------------------------------------------------

USE archery_db;

-- -----------------------------------------------------
-- 1. Table: gender
-- Source: (Mentions Male, Female)
-- -----------------------------------------------------
INSERT INTO gender (gender_code) VALUES
('M'),
('F');

-- -----------------------------------------------------
-- 2. Table: division
-- Source: (Rule 7.9.3 lists outdoor divisions)
-- Note: Crossbow is omitted as per project-specific sources
-- -----------------------------------------------------
INSERT INTO division (bow_type_code, is_active) VALUES
('R', TRUE),  -- Recurve
('C', TRUE),  -- Compound
('RB', TRUE), -- Recurve Barebow (mapped from Barebow Recurve)
('CB', TRUE), -- Compound Barebow (mapped from Barebow Compound)
('L', TRUE);  -- Longbow

-- -----------------------------------------------------
-- 3. Table: age_class
-- Source: (All data from age classes 2025.pdf for policy_year 2025)
-- -----------------------------------------------------
INSERT INTO age_class (age_class_code, min_birth_year, max_birth_year, policy_year) VALUES
('U14', 2012, 2025, 2025), -- 'born in the year 2012 or since 2012'
('U16', 2010, 2011, 2025), -- 'born in the years 2010 or 2011'
('U18', 2008, 2009, 2025), -- 'born in the years 2008 or 2009'
('U21', 2005, 2007, 2025), -- 'born in the years 2005, 2006 or 2007'
('Open', 1976, 2004, 2025), -- 'born in 1976 to 2004 inclusive'
('50+', 1966, 1975, 2025), -- 'born in the years 1966 to 1975'
('60+', 1956, 1965, 2025), -- 'born in the years 1956 to 1965'
('70+', 1901, 1955, 2025); -- 'born in or prior to 1955' (1901 is assumed floor)

-- -----------------------------------------------------
-- 4. Table: round
-- Source: (Schedule 9A Official Target Archery Rounds)
-- -----------------------------------------------------
INSERT INTO round (round_name) VALUES
('WA90/1440'),      --
('WA70/1440'),      --
('WA60/1440'),      --
('AA50/1440'),      --
('AA40/1440'),      --
('WA60/900'),       -- (Also known as Canberra)
('Short Canberra'); --

-- -----------------------------------------------------
-- 5. Table: competition
-- Source: User-defined data based on project context
-- -----------------------------------------------------
INSERT INTO competition (name, start_date, end_date, rules_note) VALUES
('Club Championship 2025', '2025-01-01', '2025-12-31', 'Yearly club championship.'),
('October WA 60/900', '2025-10-10', '2025-10-10', 'Club competition, WA60/900 round.');

-- -----------------------------------------------------
-- 6. Table: category
-- Creates valid combinations of age, gender, and division.
-- -----------------------------------------------------
INSERT INTO category (age_class_id, gender_id, division_id) VALUES
-- U18 Male Recurve
((SELECT id FROM age_class WHERE age_class_code = 'U18' AND policy_year = 2025),
 (SELECT id FROM gender WHERE gender_code = 'M'),
 (SELECT id FROM division WHERE bow_type_code = 'R')),

-- 50+ Female Compound
((SELECT id FROM age_class WHERE age_class_code = '50+' AND policy_year = 2025),
 (SELECT id FROM gender WHERE gender_code = 'F'),
 (SELECT id FROM division WHERE bow_type_code = 'C')),

-- Open Male Longbow
((SELECT id FROM age_class WHERE age_class_code = 'Open' AND policy_year = 2025),
 (SELECT id FROM gender WHERE gender_code = 'M'),
 (SELECT id FROM division WHERE bow_type_code = 'L'));

-- -----------------------------------------------------
-- 7. Table: club_member
-- Creating sample archers that fit some of the categories
-- -----------------------------------------------------
INSERT INTO club_member (full_name, birth_year, gender_id, division_id, is_recorder) VALUES
-- Archer 1: U18 Male Recurve
('Laura Kofoed', 2008, (SELECT id FROM gender WHERE gender_code = 'M'), (SELECT id FROM division WHERE bow_type_code = 'R'), 1),
-- Archer 2: 50+ Female Compound
('Lotta Braun', 1970, (SELECT id FROM gender WHERE gender_code = 'F'), (SELECT id FROM division WHERE bow_type_code = 'C'), 0),
-- Archer 3: Open Male Longbow
('Jessica Kerr', 1990, (SELECT id FROM gender WHERE gender_code = 'M'), (SELECT id FROM division WHERE bow_type_code = 'L'), 0);

-- -----------------------------------------------------
-- 8. Table: round_range
-- Source: (Schedule 9A).
-- Face size: + = 122cm, * = 80cm
-- Ends: 36 arrows = 6 ends, 30 arrows = 5 ends.
-- -----------------------------------------------------

-- Ranges for WA90/1440
INSERT INTO round_range (round_id, distance_m, face_size, ends_per_range) VALUES
((SELECT id FROM round WHERE round_name = 'WA90/1440'), 90, 122, 6), -- 36+
((SELECT id FROM round WHERE round_name = 'WA90/1440'), 70, 122, 6), -- 36+
((SELECT id FROM round WHERE round_name = 'WA90/1440'), 50, 80, 6),  -- 36*
((SELECT id FROM round WHERE round_name = 'WA90/1440'), 30, 80, 6);  -- 36*

-- Ranges for WA60/900
INSERT INTO round_range (round_id, distance_m, face_size, ends_per_range) VALUES
((SELECT id FROM round WHERE round_name = 'WA60/900'), 60, 122, 5), -- 30+
((SELECT id FROM round WHERE round_name = 'WA60/900'), 50, 122, 5), -- 30+
((SELECT id FROM round WHERE round_name = 'WA60/900'), 40, 122, 5); -- 30+

-- Ranges for Short Canberra
INSERT INTO round_range (round_id, distance_m, face_size, ends_per_range) VALUES
((SELECT id FROM round WHERE round_name = 'Short Canberra'), 50, 122, 5), -- 30+
((SELECT id FROM round WHERE round_name = 'Short Canberra'), 40, 122, 5), -- 30+
((SELECT id FROM round WHERE round_name = 'Short Canberra'), 30, 122, 5); -- 30+


-- -----------------------------------------------------
-- 9. Table: session
-- Simulating scoresheets for our archers
-- -----------------------------------------------------
INSERT INTO session (member_id, round_id, shoot_date, status) VALUES
-- Archer 1 shoots the 'October WA 60/900' competition
(1, (SELECT id FROM round WHERE round_name = 'WA60/900'), '2025-10-10', 'Confirmed'),

-- Archer 2 shoots a practice 'WA90/1440'
(2, (SELECT id FROM round WHERE round_name = 'WA90/1440'), '2025-10-11', 'Preliminary'),

-- Archer 1 shoots a practice 'Short Canberra'
(1, (SELECT id FROM round WHERE round_name = 'Short Canberra'), '2025-10-12', 'Confirmed');

-- -----------------------------------------------------
-- 10. Table: end
-- Populating ends for Session 1 (Archer 1, WA60/900)
-- This round has 3 ranges, 5 ends each.
-- We will get the round_range_id dynamically.
-- -----------------------------------------------------
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES
-- Session 1, 60m Range (5 ends)
(1, (SELECT id FROM round_range WHERE round_id = (SELECT id FROM round WHERE round_name = 'WA60/900') AND distance_m = 60), 1), -- End 1 at 60m
(1, (SELECT id FROM round_range WHERE round_id = (SELECT id FROM round WHERE round_name = 'WA60/900') AND distance_m = 60), 2), -- End 2 at 60m
(1, (SELECT id FROM round_range WHERE round_id = (SELECT id FROM round WHERE round_name = 'WA60/900') AND distance_m = 60), 3), -- End 3 at 60m
(1, (SELECT id FROM round_range WHERE round_id = (SELECT id FROM round WHERE round_name = 'WA60/900') AND distance_m = 60), 4), -- End 4 at 60m
(1, (SELECT id FROM round_range WHERE round_id = (SELECT id FROM round WHERE round_name = 'WA60/900') AND distance_m = 60), 5), -- End 5 at 60m
-- Session 1, 50m Range (5 ends)
(1, (SELECT id FROM round_range WHERE round_id = (SELECT id FROM round WHERE round_name = 'WA60/900') AND distance_m = 50), 1), -- End 1 at 50m
(1, (SELECT id FROM round_range WHERE round_id = (SELECT id FROM round WHERE round_name = 'WA60/900') AND distance_m = 50), 2); -- End 2 at 50m (partial data)

-- -----------------------------------------------------
-- 11. Table: arrow
-- Populating arrows for the first two ends and one end from the second range of Session 1
-- Note: The `end_id`s (1, 2, 6) are assumed based on the insertion order above.
-- -----------------------------------------------------
-- Arrows for End 1 (end_id = 1)
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
(1, 1, 'X'),  --
(1, 2, '10'),
(1, 3, '9'),
(1, 4, '9'),
(1, 5, '8'),
(1, 6, 'M'); --

-- Arrows for End 2 (end_id = 2)
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
(2, 1, '10'),
(2, 2, '9'),
(2, 3, '8'),
(2, 4, '7'),
(2, 5, '7'),
(2, 6, '6');

-- Arrows for End 6 (end_id = 6)
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
(6, 1, 'X'),
(6, 2, 'X'),
(6, 3, '10'),
(6, 4, '9'),
(6, 5, '9'),
(6, 6, '8');


-- -----------------------------------------------------
-- 12. Table: competition_entry
-- Linking Session 1 to the 'October WA 60/900' competition
-- -----------------------------------------------------
INSERT INTO competition_entry (session_id, competition_id, category_id, final_total, rank_in_category) VALUES
(
    1, -- Session 1
    (SELECT id FROM competition WHERE name = 'October WA 60/900'), -- Competition ID
    (SELECT id FROM category WHERE -- Category ID for U18 Male Recurve
        age_class_id = (SELECT id FROM age_class WHERE age_class_code = 'U18' AND policy_year = 2025) AND
        gender_id = (SELECT id FROM gender WHERE gender_code = 'M') AND
        division_id = (SELECT id FROM division WHERE bow_type_code = 'R')),
    720, -- A plausible 'frozen' total score for this round
    1    -- Assuming 1st place for this entry
);

-- -----------------------------------------------------
-- 13. Table: competition_entry (for Championship)
-- We can also link the *same* session to the Club Championship
-- -----------------------------------------------------
INSERT INTO competition_entry (session_id, competition_id, category_id, final_total) VALUES
(
    1, -- Session 1
    (SELECT id FROM competition WHERE name = 'Club Championship 2025'), -- Competition ID
    (SELECT id FROM category WHERE -- Category ID for U18 Male Recurve
        age_class_id = (SELECT id FROM age_class WHERE age_class_code = 'U18' AND policy_year = 2025) AND
        gender_id = (SELECT id FROM gender WHERE gender_code = 'M') AND
        division_id = (SELECT id FROM division WHERE bow_type_code = 'R')),
    720 -- The same frozen total
    -- Rank is left NULL as it would be calculated at the end of the year
);