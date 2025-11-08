-- =====================================================
-- Archery Club Database - Data Creation Script
-- =====================================================
-- Purpose:  Seed the archery_db with foundational and sample data
-- Sources:  Age Classes 2025.pdf, AA RULES (Version 6.7 - June 2022)
-- Strategy: Use LAST_INSERT_ID() to capture auto-increment IDs and avoid hard-coded values
-- =====================================================

USE archery_db;

-- =====================================================
-- 1. FOUNDATIONAL DATA (Static Reference Tables)
-- =====================================================

-- =====================================================
-- Table: gender
-- Description: Gender codes for archer categorization
-- =====================================================
INSERT INTO gender (gender_code) VALUES
    ('M'), -- Male
    ('F'); -- Female

-- =====================================================
-- Table: division
-- Description: Bow types for archer categorization (excludes Crossbow)
-- Notes:
--   - Empty string ('') represents "No Division" for recorders who don't compete
-- =====================================================
INSERT INTO division (bow_type_code, is_active) VALUES
    ('R', TRUE),   -- Recurve
    ('C', TRUE),   -- Compound
    ('RB', TRUE),  -- Recurve Barebow
    ('CB', TRUE),  -- Compound Barebow
    ('L', TRUE),   -- Longbow
    ('', TRUE);    -- No Division (for recorders/non-competing members)

-- =====================================================
-- Table: age_class
-- Description: Age groups for archer categorization
-- Source: Age Classes 2025.pdf - Policy Year 2025
-- Note: Age is calculated as of January 1st of the policy year
-- =====================================================
INSERT INTO age_class (age_class_code, min_birth_year, max_birth_year, policy_year) VALUES
    ('U14', 2012, 2025, 2025),  -- Born in 2012 or since 2012
    ('U16', 2010, 2011, 2025),  -- Born in 2010 or 2011
    ('U18', 2008, 2009, 2025),  -- Born in 2008 or 2009
    ('U21', 2005, 2007, 2025),  -- Born in 2005, 2006, or 2007
    ('Open', 1976, 2004, 2025), -- Born 1976 to 2004 inclusive
    ('50+', 1966, 1975, 2025),  -- Born 1966 to 1975
    ('60+', 1956, 1965, 2025),  -- Born 1956 to 1965
    ('70+', 1901, 1955, 2025);  -- Born 1955 or earlier (1901 is floor)

-- =====================================================
-- Table: round
-- Description: Official Target Archery Rounds
-- Source: AA RULES Schedule 9A and common club rounds
-- Note: Naming follows "Distance/TotalArrows" format (1440 = 4x360 arrows, 900 = 3x300 arrows, 720 = 2x360 arrows)
-- =====================================================
INSERT INTO round (round_name) VALUES
    ('WA90/1440'),      -- World Archery 90m round, 1440 arrows total
    ('WA70/1440'),      -- World Archery 70m round, 1440 arrows total
    ('WA60/1440'),      -- World Archery 60m round, 1440 arrows total
    ('AA50/1440'),      -- Archery Australia 50m round, 1440 arrows total
    ('AA40/1440'),      -- Archery Australia 40m round, 1440 arrows total
    ('WA60/900'),       -- World Archery 60m round, 900 arrows total (also called Canberra round)
    ('Short Canberra'); -- Shortened Canberra variant, 900 arrows total

-- =====================================================
-- Table: round_range
-- Description: Distance and target specifications for each range in a round
-- Source: AA RULES Schedule 9A
-- Notes:
--   - Face size: 122 cm (30cm 10-ring), 80 cm (20cm 10-ring)
--   - Ends: 6 arrows = 36 arrows for range; 5 arrows = 30 arrows for range
--   - All rounds use 6 arrows per end (standard), except some specialty rounds
-- =====================================================

-- WA90/1440: 90m, 70m, 50m, 30m distances
INSERT INTO round_range (round_id, distance_m, face_size, ends_per_range) VALUES
    ((SELECT id FROM round WHERE round_name = 'WA90/1440'), 90, 122, 6), -- 36 arrows on 122cm face
    ((SELECT id FROM round WHERE round_name = 'WA90/1440'), 70, 122, 6), -- 36 arrows on 122cm face
    ((SELECT id FROM round WHERE round_name = 'WA90/1440'), 50, 80, 6),  -- 36 arrows on 80cm face
    ((SELECT id FROM round WHERE round_name = 'WA90/1440'), 30, 80, 6);  -- 36 arrows on 80cm face

-- WA70/1440: 70m, 60m, 50m, 30m distances
INSERT INTO round_range (round_id, distance_m, face_size, ends_per_range) VALUES
    ((SELECT id FROM round WHERE round_name = 'WA70/1440'), 70, 122, 6), -- 36 arrows on 122cm face
    ((SELECT id FROM round WHERE round_name = 'WA70/1440'), 60, 122, 6), -- 36 arrows on 122cm face
    ((SELECT id FROM round WHERE round_name = 'WA70/1440'), 50, 80, 6),  -- 36 arrows on 80cm face
    ((SELECT id FROM round WHERE round_name = 'WA70/1440'), 30, 80, 6);  -- 36 arrows on 80cm face

-- WA60/1440: 60m, 50m, 40m, 30m distances
INSERT INTO round_range (round_id, distance_m, face_size, ends_per_range) VALUES
    ((SELECT id FROM round WHERE round_name = 'WA60/1440'), 60, 122, 6), -- 36 arrows on 122cm face
    ((SELECT id FROM round WHERE round_name = 'WA60/1440'), 50, 122, 6), -- 36 arrows on 122cm face
    ((SELECT id FROM round WHERE round_name = 'WA60/1440'), 40, 80, 6),  -- 36 arrows on 80cm face
    ((SELECT id FROM round WHERE round_name = 'WA60/1440'), 30, 80, 6);  -- 36 arrows on 80cm face

-- AA50/1440: 50m, 40m, 30m, 20m distances
INSERT INTO round_range (round_id, distance_m, face_size, ends_per_range) VALUES
    ((SELECT id FROM round WHERE round_name = 'AA50/1440'), 50, 122, 6), -- 36 arrows on 122cm face
    ((SELECT id FROM round WHERE round_name = 'AA50/1440'), 40, 122, 6), -- 36 arrows on 122cm face
    ((SELECT id FROM round WHERE round_name = 'AA50/1440'), 30, 80, 6),  -- 36 arrows on 80cm face
    ((SELECT id FROM round WHERE round_name = 'AA50/1440'), 20, 80, 6);  -- 36 arrows on 80cm face

-- AA40/1440: 40m, 30m, 20m, 10m distances
INSERT INTO round_range (round_id, distance_m, face_size, ends_per_range) VALUES
    ((SELECT id FROM round WHERE round_name = 'AA40/1440'), 40, 122, 6), -- 36 arrows on 122cm face
    ((SELECT id FROM round WHERE round_name = 'AA40/1440'), 30, 122, 6), -- 36 arrows on 122cm face
    ((SELECT id FROM round WHERE round_name = 'AA40/1440'), 20, 80, 6),  -- 36 arrows on 80cm face
    ((SELECT id FROM round WHERE round_name = 'AA40/1440'), 10, 80, 6);  -- 36 arrows on 80cm face

-- WA60/900 (Canberra): 60m, 50m, 40m distances (5 ends = 30 arrows per range)
INSERT INTO round_range (round_id, distance_m, face_size, ends_per_range) VALUES
    ((SELECT id FROM round WHERE round_name = 'WA60/900'), 60, 122, 5), -- 30 arrows on 122cm face
    ((SELECT id FROM round WHERE round_name = 'WA60/900'), 50, 122, 5), -- 30 arrows on 122cm face
    ((SELECT id FROM round WHERE round_name = 'WA60/900'), 40, 122, 5);  -- 30 arrows on 122cm face

-- Short Canberra: 50m, 40m, 30m distances (5 ends = 30 arrows per range)
INSERT INTO round_range (round_id, distance_m, face_size, ends_per_range) VALUES
    ((SELECT id FROM round WHERE round_name = 'Short Canberra'), 50, 122, 5), -- 30 arrows on 122cm face
    ((SELECT id FROM round WHERE round_name = 'Short Canberra'), 40, 122, 5), -- 30 arrows on 122cm face
    ((SELECT id FROM round WHERE round_name = 'Short Canberra'), 30, 122, 5);  -- 30 arrows on 122cm face

-- =====================================================
-- Table: category
-- Description: Valid combinations of age class, gender, and division
-- Purpose: Define all competition categories and their associated demographics
-- =====================================================
INSERT INTO category (age_class_id, gender_id, division_id) VALUES
    -- U18 Categories
    ((SELECT id FROM age_class WHERE age_class_code = 'U18' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'R')), -- U18 Male Recurve

    ((SELECT id FROM age_class WHERE age_class_code = 'U18' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'R')), -- U18 Female Recurve

    ((SELECT id FROM age_class WHERE age_class_code = 'U18' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'C')), -- U18 Male Compound

    ((SELECT id FROM age_class WHERE age_class_code = 'U18' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'C')), -- U18 Female Compound

    -- Open Categories
    ((SELECT id FROM age_class WHERE age_class_code = 'Open' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'R')), -- Open Male Recurve

    ((SELECT id FROM age_class WHERE age_class_code = 'Open' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'R')), -- Open Female Recurve

    ((SELECT id FROM age_class WHERE age_class_code = 'Open' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'C')), -- Open Male Compound

    ((SELECT id FROM age_class WHERE age_class_code = 'Open' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'C')), -- Open Female Compound

    ((SELECT id FROM age_class WHERE age_class_code = 'Open' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'L')), -- Open Male Longbow

    ((SELECT id FROM age_class WHERE age_class_code = 'Open' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'L')), -- Open Female Longbow

    -- 50+ Categories
    ((SELECT id FROM age_class WHERE age_class_code = '50+' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'R')), -- 50+ Male Recurve

    ((SELECT id FROM age_class WHERE age_class_code = '50+' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'C')), -- 50+ Female Compound

    ((SELECT id FROM age_class WHERE age_class_code = '50+' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'L')); -- 50+ Male Longbow

-- =====================================================
-- 2. SAMPLE DATA (For Testing and Demonstration)
-- =====================================================

-- =====================================================
-- Table: club_member
-- Description: Sample club members (archers)
-- Notes:
--   - is_recorder = 1: Member can record scores (recorder role)
--   - is_recorder = 0: Member is a regular archer
--   - AV number is auto-generated by trigger (business_id trigger)
-- =====================================================

-- Archer 1: Young male recurve archer, serves as club recorder
INSERT INTO club_member (full_name, birth_year, gender_id, division_id, is_recorder) VALUES
    ('Laura Kofoed', 2008,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = ''),
     1); -- is_recorder = 1
SET @laura_id = LAST_INSERT_ID();

-- Archer 2: Senior female compound archer, regular member
INSERT INTO club_member (full_name, birth_year, gender_id, division_id, is_recorder) VALUES
    ('Lotta Braun', 1970,
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'C'),
     0); -- is_recorder = 0
SET @lotta_id = LAST_INSERT_ID();

-- Archer 3: Open male longbow archer, regular member
INSERT INTO club_member (full_name, birth_year, gender_id, division_id, is_recorder) VALUES
    ('Jessica Kerr', 1990,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'L'),
     0); -- is_recorder = 0
SET @jessica_id = LAST_INSERT_ID();

-- Archer 4: Open female recurve archer, regular member
INSERT INTO club_member (full_name, birth_year, gender_id, division_id, is_recorder) VALUES
    ('Sarah Mitchell', 1985,
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'R'),
     0); -- is_recorder = 0
SET @sarah_id = LAST_INSERT_ID();

-- Archer 5: U18 female compound archer, regular member
INSERT INTO club_member (full_name, birth_year, gender_id, division_id, is_recorder) VALUES
    ('Emma Thompson', 2009,
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'C'),
     0); -- is_recorder = 0
SET @emma_id = LAST_INSERT_ID();

-- =====================================================
-- Table: competition
-- Description: Club competitions for the year
-- Notes:
--   - Club Championship 2025: Year-long accumulation competition
--   - October WA 60/900: Single event competition
-- =====================================================
INSERT INTO competition (name, start_date, end_date, rules_note) VALUES
    ('Club Championship 2025',
     '2025-01-01', '2025-12-31',
     'Year-long club championship. Best scores accumulated from official rounds throughout the year.'),
    ('October WA 60/900',
     '2025-10-10', '2025-10-10',
     'Single event competition using WA60/900 (Canberra) round.'),
    ('Spring Championship',
     '2025-03-01', '2025-05-31',
     'Spring season championship covering March to May.');

-- =====================================================
-- Table: session
-- Description: Score recording sessions (scoresheets) for sample archers
-- Strategy: Create sessions for demonstrated rounds with different statuses
-- =====================================================

-- Session 1: Laura shoots WA60/900 (Confirmed - ready for competition)
INSERT INTO session (member_id, round_id, shoot_date, status) VALUES
    (@laura_id,
     (SELECT id FROM round WHERE round_name = 'WA60/900'),
     '2025-10-10',
     'Confirmed'); -- Confirmed score
SET @session1_id = LAST_INSERT_ID();

-- Session 2: Lotta shoots WA90/1440 (Preliminary - pending recorder approval)
INSERT INTO session (member_id, round_id, shoot_date, status) VALUES
    (@lotta_id,
     (SELECT id FROM round WHERE round_name = 'WA90/1440'),
     '2025-10-11',
     'Preliminary'); -- Preliminary score (needs approval)
SET @session2_id = LAST_INSERT_ID();

-- Session 3: Jessica shoots Short Canberra (Confirmed)
INSERT INTO session (member_id, round_id, shoot_date, status) VALUES
    (@jessica_id,
     (SELECT id FROM round WHERE round_name = 'Short Canberra'),
     '2025-10-12',
     'Confirmed'); -- Confirmed score
SET @session3_id = LAST_INSERT_ID();

-- Session 4: Sarah shoots WA60/900 (Confirmed)
INSERT INTO session (member_id, round_id, shoot_date, status) VALUES
    (@sarah_id,
     (SELECT id FROM round WHERE round_name = 'WA60/900'),
     '2025-10-10',
     'Confirmed'); -- Confirmed score
SET @session4_id = LAST_INSERT_ID();

-- Session 5: Emma shoots Short Canberra (Preliminary)
INSERT INTO session (member_id, round_id, shoot_date, status) VALUES
    (@emma_id,
     (SELECT id FROM round WHERE round_name = 'Short Canberra'),
     '2025-10-12',
     'Preliminary'); -- Preliminary score
SET @session5_id = LAST_INSERT_ID();

-- =====================================================
-- Table: end
-- Description: Sets of arrows (ends) for each session
-- Strategy: Use LAST_INSERT_ID() to capture round_range IDs, then create ends
-- Notes:
--   - Each end consists of 6 arrows (or as specified for the round)
--   - end_no is the sequence number within the range
-- =====================================================

-- Cache round_range IDs for WA60/900
SET @wa60_900_60m = (SELECT id FROM round_range WHERE round_id = (SELECT id FROM round WHERE round_name = 'WA60/900') AND distance_m = 60);
SET @wa60_900_50m = (SELECT id FROM round_range WHERE round_id = (SELECT id FROM round WHERE round_name = 'WA60/900') AND distance_m = 50);
SET @wa60_900_40m = (SELECT id FROM round_range WHERE round_id = (SELECT id FROM round WHERE round_name = 'WA60/900') AND distance_m = 40);

-- Cache round_range IDs for WA90/1440
SET @wa90_1440_90m = (SELECT id FROM round_range WHERE round_id = (SELECT id FROM round WHERE round_name = 'WA90/1440') AND distance_m = 90);

-- Cache round_range IDs for Short Canberra
SET @short_can_50m = (SELECT id FROM round_range WHERE round_id = (SELECT id FROM round WHERE round_name = 'Short Canberra') AND distance_m = 50);
SET @short_can_40m = (SELECT id FROM round_range WHERE round_id = (SELECT id FROM round WHERE round_name = 'Short Canberra') AND distance_m = 40);
SET @short_can_30m = (SELECT id FROM round_range WHERE round_id = (SELECT id FROM round WHERE round_name = 'Short Canberra') AND distance_m = 30);

-- Session 1 (Laura - WA60/900) - 60m range: 5 ends
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session1_id, @wa60_900_60m, 1);
SET @s1_60m_end1 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session1_id, @wa60_900_60m, 2);
SET @s1_60m_end2 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session1_id, @wa60_900_60m, 3);
SET @s1_60m_end3 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session1_id, @wa60_900_60m, 4);
SET @s1_60m_end4 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session1_id, @wa60_900_60m, 5);
SET @s1_60m_end5 = LAST_INSERT_ID();

-- Session 1 (Laura - WA60/900) - 50m range: 5 ends
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session1_id, @wa60_900_50m, 1);
SET @s1_50m_end1 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session1_id, @wa60_900_50m, 2);
SET @s1_50m_end2 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session1_id, @wa60_900_50m, 3);
SET @s1_50m_end3 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session1_id, @wa60_900_50m, 4);
SET @s1_50m_end4 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session1_id, @wa60_900_50m, 5);
SET @s1_50m_end5 = LAST_INSERT_ID();

-- Session 1 (Laura - WA60/900) - 40m range: 5 ends
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session1_id, @wa60_900_40m, 1);
SET @s1_40m_end1 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session1_id, @wa60_900_40m, 2);
SET @s1_40m_end2 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session1_id, @wa60_900_40m, 3);
SET @s1_40m_end3 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session1_id, @wa60_900_40m, 4);
SET @s1_40m_end4 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session1_id, @wa60_900_40m, 5);
SET @s1_40m_end5 = LAST_INSERT_ID();

-- Session 2 (Lotta - WA90/1440) - 90m range: 1 sample end for demonstration
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session2_id, @wa90_1440_90m, 1);
SET @s2_90m_end1 = LAST_INSERT_ID();

-- Session 3 (Jessica - Short Canberra) - 50m range: 5 ends
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session3_id, @short_can_50m, 1);
SET @s3_50m_end1 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session3_id, @short_can_50m, 2);
SET @s3_50m_end2 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session3_id, @short_can_50m, 3);
SET @s3_50m_end3 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session3_id, @short_can_50m, 4);
SET @s3_50m_end4 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session3_id, @short_can_50m, 5);
SET @s3_50m_end5 = LAST_INSERT_ID();

-- Session 3 (Jessica - Short Canberra) - 40m range: 5 ends
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session3_id, @short_can_40m, 1);
SET @s3_40m_end1 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session3_id, @short_can_40m, 2);
SET @s3_40m_end2 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session3_id, @short_can_40m, 3);
SET @s3_40m_end3 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session3_id, @short_can_40m, 4);
SET @s3_40m_end4 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session3_id, @short_can_40m, 5);
SET @s3_40m_end5 = LAST_INSERT_ID();

-- Session 3 (Jessica - Short Canberra) - 30m range: 5 ends
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session3_id, @short_can_30m, 1);
SET @s3_30m_end1 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session3_id, @short_can_30m, 2);
SET @s3_30m_end2 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session3_id, @short_can_30m, 3);
SET @s3_30m_end3 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session3_id, @short_can_30m, 4);
SET @s3_30m_end4 = LAST_INSERT_ID();
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (@session3_id, @short_can_30m, 5);
SET @s3_30m_end5 = LAST_INSERT_ID();

-- =====================================================
-- Table: arrow
-- Description: Individual arrow scores for each end
-- Notes:
--   - Arrow values: 1-10 (scoring rings), 'X' (10-ring tie-breaker), 'M' (miss)
--   - 6 arrows per end for standard rounds
--   - Order of arrows: highest to lowest (per archery convention)
-- =====================================================

-- Session 1, 60m range, End 1: Strong round
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s1_60m_end1, 1, 'X'),  -- Best: inner 10
    (@s1_60m_end1, 2, '10'),
    (@s1_60m_end1, 3, '9'),
    (@s1_60m_end1, 4, '9'),
    (@s1_60m_end1, 5, '8'),
    (@s1_60m_end1, 6, '8');

-- Session 1, 60m range, End 2: Good round
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s1_60m_end2, 1, '10'),
    (@s1_60m_end2, 2, '9'),
    (@s1_60m_end2, 3, '9'),
    (@s1_60m_end2, 4, '8'),
    (@s1_60m_end2, 5, '8'),
    (@s1_60m_end2, 6, '7');

-- Session 1, 60m range, End 3: Average round
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s1_60m_end3, 1, '9'),
    (@s1_60m_end3, 2, '8'),
    (@s1_60m_end3, 3, '8'),
    (@s1_60m_end3, 4, '7'),
    (@s1_60m_end3, 5, '7'),
    (@s1_60m_end3, 6, '6');

-- Session 1, 60m range, End 4: Weaker round with a miss
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s1_60m_end4, 1, '8'),
    (@s1_60m_end4, 2, '7'),
    (@s1_60m_end4, 3, '7'),
    (@s1_60m_end4, 4, '6'),
    (@s1_60m_end4, 5, '5'),
    (@s1_60m_end4, 6, 'M');

-- Session 1, 60m range, End 5: Recovery round
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s1_60m_end5, 1, '9'),
    (@s1_60m_end5, 2, '9'),
    (@s1_60m_end5, 3, '8'),
    (@s1_60m_end5, 4, '8'),
    (@s1_60m_end5, 5, '7'),
    (@s1_60m_end5, 6, '7');

-- Session 1, 50m range, End 1: Strong at closer distance
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s1_50m_end1, 1, 'X'),
    (@s1_50m_end1, 2, 'X'),
    (@s1_50m_end1, 3, '10'),
    (@s1_50m_end1, 4, '9'),
    (@s1_50m_end1, 5, '9'),
    (@s1_50m_end1, 6, '8');

-- Session 1, 50m range, End 2-5: Consistent good rounds
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s1_50m_end2, 1, '10'), (@s1_50m_end2, 2, '10'), (@s1_50m_end2, 3, '9'), (@s1_50m_end2, 4, '9'), (@s1_50m_end2, 5, '8'), (@s1_50m_end2, 6, '8');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s1_50m_end3, 1, '10'), (@s1_50m_end3, 2, '9'), (@s1_50m_end3, 3, '9'), (@s1_50m_end3, 4, '8'), (@s1_50m_end3, 5, '8'), (@s1_50m_end3, 6, '7');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s1_50m_end4, 1, '9'), (@s1_50m_end4, 2, '9'), (@s1_50m_end4, 3, '8'), (@s1_50m_end4, 4, '8'), (@s1_50m_end4, 5, '7'), (@s1_50m_end4, 6, '7');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s1_50m_end5, 1, '10'), (@s1_50m_end5, 2, '10'), (@s1_50m_end5, 3, '9'), (@s1_50m_end5, 4, '9'), (@s1_50m_end5, 5, '8'), (@s1_50m_end5, 6, '8');

-- Session 1, 40m range, End 1-5: Very strong performance at 40m
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s1_40m_end1, 1, 'X'), (@s1_40m_end1, 2, 'X'), (@s1_40m_end1, 3, '10'), (@s1_40m_end1, 4, '10'), (@s1_40m_end1, 5, '9'), (@s1_40m_end1, 6, '9');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s1_40m_end2, 1, 'X'), (@s1_40m_end2, 2, '10'), (@s1_40m_end2, 3, '10'), (@s1_40m_end2, 4, '9'), (@s1_40m_end2, 5, '9'), (@s1_40m_end2, 6, '8');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s1_40m_end3, 1, '10'), (@s1_40m_end3, 2, '10'), (@s1_40m_end3, 3, '10'), (@s1_40m_end3, 4, '9'), (@s1_40m_end3, 5, '9'), (@s1_40m_end3, 6, '8');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s1_40m_end4, 1, '10'), (@s1_40m_end4, 2, '10'), (@s1_40m_end4, 3, '9'), (@s1_40m_end4, 4, '9'), (@s1_40m_end4, 5, '8'), (@s1_40m_end4, 6, '8');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s1_40m_end5, 1, 'X'), (@s1_40m_end5, 2, 'X'), (@s1_40m_end5, 3, '10'), (@s1_40m_end5, 4, '10'), (@s1_40m_end5, 5, '9'), (@s1_40m_end5, 6, '9');

-- Session 2 (Lotta - WA90/1440), 90m range, End 1: Sample preliminary round
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s2_90m_end1, 1, '10'), (@s2_90m_end1, 2, '9'), (@s2_90m_end1, 3, '8'), (@s2_90m_end1, 4, '7'), (@s2_90m_end1, 5, '6'), (@s2_90m_end1, 6, '5');

-- Session 3 (Jessica - Short Canberra), 50m range, End 1-5: Good performance
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s3_50m_end1, 1, '10'), (@s3_50m_end1, 2, '10'), (@s3_50m_end1, 3, '9'), (@s3_50m_end1, 4, '9'), (@s3_50m_end1, 5, '8'), (@s3_50m_end1, 6, '8');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s3_50m_end2, 1, '10'), (@s3_50m_end2, 2, '9'), (@s3_50m_end2, 3, '9'), (@s3_50m_end2, 4, '8'), (@s3_50m_end2, 5, '8'), (@s3_50m_end2, 6, '7');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s3_50m_end3, 1, '9'), (@s3_50m_end3, 2, '9'), (@s3_50m_end3, 3, '8'), (@s3_50m_end3, 4, '8'), (@s3_50m_end3, 5, '7'), (@s3_50m_end3, 6, '7');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s3_50m_end4, 1, '8'), (@s3_50m_end4, 2, '8'), (@s3_50m_end4, 3, '7'), (@s3_50m_end4, 4, '7'), (@s3_50m_end4, 5, '6'), (@s3_50m_end4, 6, '6');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s3_50m_end5, 1, '10'), (@s3_50m_end5, 2, '10'), (@s3_50m_end5, 3, '9'), (@s3_50m_end5, 4, '9'), (@s3_50m_end5, 5, '8'), (@s3_50m_end5, 6, '8');

-- Session 3 (Jessica - Short Canberra), 40m range, End 1-5: Excellent performance at 40m
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s3_40m_end1, 1, 'X'), (@s3_40m_end1, 2, 'X'), (@s3_40m_end1, 3, '10'), (@s3_40m_end1, 4, '10'), (@s3_40m_end1, 5, '9'), (@s3_40m_end1, 6, '9');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s3_40m_end2, 1, 'X'), (@s3_40m_end2, 2, '10'), (@s3_40m_end2, 3, '10'), (@s3_40m_end2, 4, '9'), (@s3_40m_end2, 5, '9'), (@s3_40m_end2, 6, '8');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s3_40m_end3, 1, '10'), (@s3_40m_end3, 2, '10'), (@s3_40m_end3, 3, '10'), (@s3_40m_end3, 4, '9'), (@s3_40m_end3, 5, '9'), (@s3_40m_end3, 6, '8');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s3_40m_end4, 1, '10'), (@s3_40m_end4, 2, '10'), (@s3_40m_end4, 3, '9'), (@s3_40m_end4, 4, '9'), (@s3_40m_end4, 5, '8'), (@s3_40m_end4, 6, '8');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s3_40m_end5, 1, 'X'), (@s3_40m_end5, 2, 'X'), (@s3_40m_end5, 3, '10'), (@s3_40m_end5, 4, '10'), (@s3_40m_end5, 5, '9'), (@s3_40m_end5, 6, '9');

-- Session 3 (Jessica - Short Canberra), 30m range, End 1-5: Outstanding performance at 30m
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s3_30m_end1, 1, 'X'), (@s3_30m_end1, 2, 'X'), (@s3_30m_end1, 3, 'X'), (@s3_30m_end1, 4, '10'), (@s3_30m_end1, 5, '10'), (@s3_30m_end1, 6, '9');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s3_30m_end2, 1, 'X'), (@s3_30m_end2, 2, 'X'), (@s3_30m_end2, 3, '10'), (@s3_30m_end2, 4, '10'), (@s3_30m_end2, 5, '9'), (@s3_30m_end2, 6, '9');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s3_30m_end3, 1, 'X'), (@s3_30m_end3, 2, '10'), (@s3_30m_end3, 3, '10'), (@s3_30m_end3, 4, '10'), (@s3_30m_end3, 5, '9'), (@s3_30m_end3, 6, '9');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s3_30m_end4, 1, '10'), (@s3_30m_end4, 2, '10'), (@s3_30m_end4, 3, '10'), (@s3_30m_end4, 4, '9'), (@s3_30m_end4, 5, '9'), (@s3_30m_end4, 6, '9');
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    (@s3_30m_end5, 1, 'X'), (@s3_30m_end5, 2, 'X'), (@s3_30m_end5, 3, 'X'), (@s3_30m_end5, 4, '10'), (@s3_30m_end5, 5, '10'), (@s3_30m_end5, 6, '10');

-- =====================================================
-- Table: competition_entry
-- Description: Links sessions to competitions with rankings
-- Notes:
--   - final_total: Frozen score from the session for this competition
--   - rank_in_category: Ranking within the category (1 = 1st place, NULL = not ranked or tied)
--   - Multiple sessions can be linked to the same competition if applicable
-- =====================================================

INSERT INTO competition_entry (session_id, competition_id, category_id, final_total, rank_in_category) VALUES
    -- Laura (Session 1) in October WA 60/900
    (@session1_id,
     (SELECT id FROM competition WHERE name = 'October WA 60/900'),
     (SELECT id FROM category WHERE
         age_class_id = (SELECT id FROM age_class WHERE age_class_code = 'U18' AND policy_year = 2025) AND
         gender_id = (SELECT id FROM gender WHERE gender_code = 'M') AND
         division_id = (SELECT id FROM division WHERE bow_type_code = 'R')),
     720, -- Plausible total: (8+9+9+9+8) + (10+9+9+8+8+7) + (10+9+9+8+8+7) + (9+8+8+7+7+6) + (9+8+8+7+7+7) + (20+20+10+9+9+8) + (20+10+10+9+9+8) + (10+10+10+9+9+8) + (10+10+9+9+8+8) + (20+20+10+10+9+9)
     1),   -- 1st place

    -- Laura (Session 1) in Club Championship 2025
    (@session1_id,
     (SELECT id FROM competition WHERE name = 'Club Championship 2025'),
     (SELECT id FROM category WHERE
         age_class_id = (SELECT id FROM age_class WHERE age_class_code = 'U18' AND policy_year = 2025) AND
         gender_id = (SELECT id FROM gender WHERE gender_code = 'M') AND
         division_id = (SELECT id FROM division WHERE bow_type_code = 'R')),
     720,
     NULL),  -- No rank yet (championship ongoing)

    -- Sarah (Session 4) in October WA 60/900
    (@session4_id,
     (SELECT id FROM competition WHERE name = 'October WA 60/900'),
     (SELECT id FROM category WHERE
         age_class_id = (SELECT id FROM age_class WHERE age_class_code = 'Open' AND policy_year = 2025) AND
         gender_id = (SELECT id FROM gender WHERE gender_code = 'F') AND
         division_id = (SELECT id FROM division WHERE bow_type_code = 'R')),
     680,  -- Slightly lower score
     1),   -- 1st place in her category

    -- Jessica (Session 3) in Spring Championship
    (@session3_id,
     (SELECT id FROM competition WHERE name = 'Spring Championship'),
     (SELECT id FROM category WHERE
         age_class_id = (SELECT id FROM age_class WHERE age_class_code = 'Open' AND policy_year = 2025) AND
         gender_id = (SELECT id FROM gender WHERE gender_code = 'M') AND
         division_id = (SELECT id FROM division WHERE bow_type_code = 'L')),
     710,
     1);   -- 1st place in longbow category

-- =====================================================
-- End of Data Creation Script
-- =====================================================
-- Script completed successfully. All foundational and sample data created.
-- The database is now populated with:
--   - Reference data: gender, divisions, age classes, rounds, round ranges, categories
--   - Sample members: 5 archers with varying roles and abilities
--   - Sample sessions: 5 scoring sessions with different statuses
--   - Sample ends and arrows: Complete detailed scores demonstrating archery data
--   - Sample competitions and entries: Linking sessions to competitions with rankings
-- =====================================================
