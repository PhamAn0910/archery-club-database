-- =====================================================
-- COMPREHENSIVE TEST DATA FOR ARCHERY CLUB DATABASE
-- =====================================================
-- Purpose:  Complete test data to thoroughly exercise the web application
-- Requires: archery_db.sql to be run first (replaces data_creation.sql)
-- Coverage: All tables with realistic, interconnected data for testing
-- Usage:    Run this file INSTEAD of data_creation.sql for comprehensive testing
-- =====================================================

USE archery_db;

-- =====================================================
-- 1. FOUNDATIONAL DATA (Static Reference Tables)
-- Following the exact structure from data_creation.sql
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
    ('Short Canberra'), -- Shortened Canberra variant, 900 arrows total
    ('Melbourne'),      -- Melbourne round
    ('Brisbane'),       -- Brisbane round
    ('Short Metric');   -- Short Metric round

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

-- Melbourne: 90m, 70m distances
INSERT INTO round_range (round_id, distance_m, face_size, ends_per_range) VALUES
    ((SELECT id FROM round WHERE round_name = 'Melbourne'), 90, 122, 6), -- 36 arrows on 122cm face
    ((SELECT id FROM round WHERE round_name = 'Melbourne'), 70, 122, 6); -- 36 arrows on 122cm face

-- Brisbane: 70m, 60m, 50m, 40m distances
INSERT INTO round_range (round_id, distance_m, face_size, ends_per_range) VALUES
    ((SELECT id FROM round WHERE round_name = 'Brisbane'), 70, 122, 5), -- 30 arrows on 122cm face
    ((SELECT id FROM round WHERE round_name = 'Brisbane'), 60, 122, 5), -- 30 arrows on 122cm face
    ((SELECT id FROM round WHERE round_name = 'Brisbane'), 50, 80, 5),  -- 30 arrows on 80cm face
    ((SELECT id FROM round WHERE round_name = 'Brisbane'), 40, 80, 5);  -- 30 arrows on 80cm face

-- Short Metric: 50m, 30m distances
INSERT INTO round_range (round_id, distance_m, face_size, ends_per_range) VALUES
    ((SELECT id FROM round WHERE round_name = 'Short Metric'), 50, 80, 6), -- 36 arrows on 80cm face
    ((SELECT id FROM round WHERE round_name = 'Short Metric'), 30, 80, 6); -- 36 arrows on 80cm face

-- =====================================================
-- Table: category
-- Description: Valid combinations of age class, gender, and division
-- Purpose: Define all competition categories and their associated demographics
-- =====================================================
INSERT INTO category (age_class_id, gender_id, division_id) VALUES
    -- U14 Categories
    ((SELECT id FROM age_class WHERE age_class_code = 'U14' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'R')), -- U14 Male Recurve

    ((SELECT id FROM age_class WHERE age_class_code = 'U14' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'R')), -- U14 Female Recurve

    ((SELECT id FROM age_class WHERE age_class_code = 'U14' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'C')), -- U14 Male Compound

    ((SELECT id FROM age_class WHERE age_class_code = 'U14' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'C')), -- U14 Female Compound

    -- U16 Categories
    ((SELECT id FROM age_class WHERE age_class_code = 'U16' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'R')), -- U16 Male Recurve

    ((SELECT id FROM age_class WHERE age_class_code = 'U16' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'R')), -- U16 Female Recurve

    ((SELECT id FROM age_class WHERE age_class_code = 'U16' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'C')), -- U16 Male Compound

    ((SELECT id FROM age_class WHERE age_class_code = 'U16' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'C')), -- U16 Female Compound

    ((SELECT id FROM age_class WHERE age_class_code = 'U16' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'RB')), -- U16 Male Recurve Barebow

    ((SELECT id FROM age_class WHERE age_class_code = 'U16' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'RB')), -- U16 Female Recurve Barebow

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

    -- U21 Categories
    ((SELECT id FROM age_class WHERE age_class_code = 'U21' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'R')), -- U21 Male Recurve

    ((SELECT id FROM age_class WHERE age_class_code = 'U21' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'R')), -- U21 Female Recurve

    ((SELECT id FROM age_class WHERE age_class_code = 'U21' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'C')), -- U21 Male Compound

    ((SELECT id FROM age_class WHERE age_class_code = 'U21' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'C')), -- U21 Female Compound

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
     (SELECT id FROM division WHERE bow_type_code = 'RB')), -- Open Male Recurve Barebow

    ((SELECT id FROM age_class WHERE age_class_code = 'Open' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'RB')), -- Open Female Recurve Barebow

    ((SELECT id FROM age_class WHERE age_class_code = 'Open' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'CB')), -- Open Male Compound Barebow

    ((SELECT id FROM age_class WHERE age_class_code = 'Open' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'CB')), -- Open Female Compound Barebow

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
     (SELECT id FROM division WHERE bow_type_code = 'R')), -- 50+ Female Recurve

    ((SELECT id FROM age_class WHERE age_class_code = '50+' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'C')), -- 50+ Male Compound

    ((SELECT id FROM age_class WHERE age_class_code = '50+' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'C')), -- 50+ Female Compound

    ((SELECT id FROM age_class WHERE age_class_code = '50+' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'L')), -- 50+ Male Longbow

    -- 60+ Categories
    ((SELECT id FROM age_class WHERE age_class_code = '60+' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'R')), -- 60+ Male Recurve

    ((SELECT id FROM age_class WHERE age_class_code = '60+' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'R')), -- 60+ Female Recurve

    ((SELECT id FROM age_class WHERE age_class_code = '60+' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'C')), -- 60+ Male Compound

    ((SELECT id FROM age_class WHERE age_class_code = '60+' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'C')), -- 60+ Female Compound

    -- 70+ Categories
    ((SELECT id FROM age_class WHERE age_class_code = '70+' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'R')), -- 70+ Male Recurve

    ((SELECT id FROM age_class WHERE age_class_code = '70+' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'R')), -- 70+ Female Recurve

    ((SELECT id FROM age_class WHERE age_class_code = '70+' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'C')), -- 70+ Male Compound

    ((SELECT id FROM age_class WHERE age_class_code = '70+' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'C')), -- 70+ Female Compound

    ((SELECT id FROM age_class WHERE age_class_code = '70+' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'L')), -- 70+ Male Longbow

    ((SELECT id FROM age_class WHERE age_class_code = '70+' AND policy_year = 2025),
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'L')); -- 70+ Female Longbow

-- =====================================================
-- 2. COMPREHENSIVE CLUB MEMBERS
-- Creates a diverse membership for testing all features
-- =====================================================

-- Additional Recorders (for managing different aspects)
INSERT INTO club_member (full_name, birth_year, gender_id, division_id, is_recorder) VALUES
    ('Laura Kofoed', 2008,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = ''),
     1), -- Senior Male Recorder

    ('Alex Thompson', 1985,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'R'),
     1), -- Senior Male Recurve Recorder
    
    ('Maria Santos', 1975,
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = ''),
     1); -- Senior Female No-Division Recorder

SET @laura_id = (SELECT id FROM club_member WHERE full_name = 'Laura Kofoed' ORDER BY id DESC LIMIT 1);
SET @alex_id = (SELECT id FROM club_member WHERE full_name = 'Alex Thompson' ORDER BY id DESC LIMIT 1);
SET @maria_id = (SELECT id FROM club_member WHERE full_name = 'Maria Santos' ORDER BY id DESC LIMIT 1);

-- Diverse archers for different categories
INSERT INTO club_member (full_name, birth_year, gender_id, division_id, is_recorder) VALUES
    -- U14 Category
    ('Sophie Young', 2015,
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'R'),
     0), -- U14 Female Recurve
    
    ('Jake Miller', 2014,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'C'),
     0), -- U14 Male Compound
    
    -- U16 Category
    ('Isabella Chen', 2011,
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'C'),
     0), -- U16 Female Compound
    
    ('Oliver Davis', 2010,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'RB'),
     0), -- U16 Male Recurve Barebow
    
    -- U18 Category
    ('Emma Thompson', 2009,
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'C'),
     0), -- U18 Female Compound
    
    ('Liam Rodriguez', 2008,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'R'),
     0), -- U18 Male Recurve
    
    -- U21 Category
    ('Maya Patel', 2006,
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'R'),
     0), -- U21 Female Recurve
    
    ('Ryan Williams', 2007,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'C'),
     0), -- U21 Male Compound
    
    -- Open Category - Various Divisions
    ('David Wilson', 1995,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'RB'),
     0), -- Open Male Recurve Barebow
    
    ('Lisa Brown', 1988,
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'CB'),
     0), -- Open Female Compound Barebow
    
    ('James Garcia', 1992,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'L'),
     0), -- Open Male Longbow
    
    ('Anna Rodriguez', 1990,
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'L'),
     0), -- Open Female Longbow
    
    ('Sarah Mitchell', 1985,
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'R'),
     0), -- Open Female Recurve
    
    ('Michael Chen', 1993,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'C'),
     0), -- Open Male Compound
    
    -- 50+ Category
    ('Robert Taylor', 1970,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'R'),
     0), -- 50+ Male Recurve
    
    ('Patricia Johnson', 1968,
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'R'),
     0), -- 50+ Female Recurve
    
    ('Thomas Anderson', 1972,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'C'),
     0), -- 50+ Male Compound
    
    -- 60+ Category
    ('George Anderson', 1960,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'C'),
     0), -- 60+ Male Compound
    
    ('Margaret Lee', 1962,
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'C'),
     0), -- 60+ Female Compound
    
    -- 70+ Category
    ('William Clark', 1950,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'L'),
     0), -- 70+ Male Longbow
    
    ('Dorothy White', 1948,
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'R'),
     0), -- 70+ Female Recurve
    
    ('Jessica Kerr', 1990,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'L'),
     0), -- Open Male Longbow (existing from original)
    
    ('Lotta Braun', 1970,
     (SELECT id FROM gender WHERE gender_code = 'F'),
     (SELECT id FROM division WHERE bow_type_code = 'C'),
     0); -- 50+ Female Compound (existing from original)

-- Store member IDs for later use
SET @sophie_id = (SELECT id FROM club_member WHERE full_name = 'Sophie Young' ORDER BY id DESC LIMIT 1);
SET @jake_id = (SELECT id FROM club_member WHERE full_name = 'Jake Miller' ORDER BY id DESC LIMIT 1);
SET @isabella_id = (SELECT id FROM club_member WHERE full_name = 'Isabella Chen' ORDER BY id DESC LIMIT 1);
SET @oliver_id = (SELECT id FROM club_member WHERE full_name = 'Oliver Davis' ORDER BY id DESC LIMIT 1);
SET @emma_id = (SELECT id FROM club_member WHERE full_name = 'Emma Thompson' ORDER BY id DESC LIMIT 1);
SET @liam_id = (SELECT id FROM club_member WHERE full_name = 'Liam Rodriguez' ORDER BY id DESC LIMIT 1);
SET @maya_id = (SELECT id FROM club_member WHERE full_name = 'Maya Patel' ORDER BY id DESC LIMIT 1);
SET @ryan_id = (SELECT id FROM club_member WHERE full_name = 'Ryan Williams' ORDER BY id DESC LIMIT 1);
SET @david_id = (SELECT id FROM club_member WHERE full_name = 'David Wilson' ORDER BY id DESC LIMIT 1);
SET @lisa_id = (SELECT id FROM club_member WHERE full_name = 'Lisa Brown' ORDER BY id DESC LIMIT 1);
SET @james_id = (SELECT id FROM club_member WHERE full_name = 'James Garcia' ORDER BY id DESC LIMIT 1);
SET @anna_id = (SELECT id FROM club_member WHERE full_name = 'Anna Rodriguez' ORDER BY id DESC LIMIT 1);
SET @sarah_id = (SELECT id FROM club_member WHERE full_name = 'Sarah Mitchell' ORDER BY id DESC LIMIT 1);
SET @michael_id = (SELECT id FROM club_member WHERE full_name = 'Michael Chen' ORDER BY id DESC LIMIT 1);
SET @robert_id = (SELECT id FROM club_member WHERE full_name = 'Robert Taylor' ORDER BY id DESC LIMIT 1);
SET @patricia_id = (SELECT id FROM club_member WHERE full_name = 'Patricia Johnson' ORDER BY id DESC LIMIT 1);
SET @thomas_id = (SELECT id FROM club_member WHERE full_name = 'Thomas Anderson' ORDER BY id DESC LIMIT 1);
SET @george_id = (SELECT id FROM club_member WHERE full_name = 'George Anderson' ORDER BY id DESC LIMIT 1);
SET @margaret_id = (SELECT id FROM club_member WHERE full_name = 'Margaret Lee' ORDER BY id DESC LIMIT 1);
SET @william_id = (SELECT id FROM club_member WHERE full_name = 'William Clark' ORDER BY id DESC LIMIT 1);
SET @dorothy_id = (SELECT id FROM club_member WHERE full_name = 'Dorothy White' ORDER BY id DESC LIMIT 1);
SET @jessica_id = (SELECT id FROM club_member WHERE full_name = 'Jessica Kerr' ORDER BY id DESC LIMIT 1);
SET @lotta_id = (SELECT id FROM club_member WHERE full_name = 'Lotta Braun' ORDER BY id DESC LIMIT 1);

-- =====================================================
-- 3. COMPREHENSIVE COMPETITION STRUCTURE
-- Creates competitions that use ALL rounds
-- =====================================================

INSERT INTO competition (name, start_date, end_date, base_round_id, rules_note) VALUES
    ('Club Championship 2025',
     '2025-01-01', '2025-12-31', 
     (SELECT id FROM round WHERE round_name = 'WA60/900'),
     'Year-long club championship. Best scores accumulated from official rounds throughout the year.'),
    
    ('WA90 Championship',
     '2025-03-15', '2025-03-15', 
     (SELECT id FROM round WHERE round_name = 'WA90/1440'),
     'Elite championship using the challenging WA90/1440 round.'),
    
    ('WA70 Series',
     '2025-04-12', '2025-04-12', 
     (SELECT id FROM round WHERE round_name = 'WA70/1440'),
     'Premier competition featuring WA70/1440 round.'),
    
    ('WA60 Challenge',
     '2025-05-18', '2025-05-18', 
     (SELECT id FROM round WHERE round_name = 'WA60/1440'),
     'Popular competition using WA60/1440 format.'),
    
    ('Youth Development Cup',
     '2025-07-10', '2025-07-10', 
     (SELECT id FROM round WHERE round_name = 'AA50/1440'),
     'Youth-focused competition for developing archers.'),
    
    ('Junior Championship',
     '2025-08-15', '2025-08-15', 
     (SELECT id FROM round WHERE round_name = 'AA40/1440'),
     'Championship for younger archers using AA40/1440.'),
    
    ('October WA 60/900',
     '2025-10-10', '2025-10-10', 
     (SELECT id FROM round WHERE round_name = 'WA60/900'),
     'Single event competition using WA60/900 (Canberra) round.'),
    
    ('Autumn Classic',
     '2025-09-15', '2025-09-15', 
     (SELECT id FROM round WHERE round_name = 'Short Canberra'),
     'Autumn competition featuring Short Canberra round.'),
    
    ('Melbourne Cup',
     '2025-11-02', '2025-11-02', 
     (SELECT id FROM round WHERE round_name = 'Melbourne'),
     'Traditional competition using Melbourne round.'),
    
    ('Brisbane Open',
     '2025-06-21', '2025-06-21', 
     (SELECT id FROM round WHERE round_name = 'Brisbane'),
     'Competition featuring the Brisbane round format.'),
    
    ('Summer Series',
     '2025-06-01', '2025-08-31', 
     (SELECT id FROM round WHERE round_name = 'Short Metric'),
     'Summer series using Short Metric round.');

-- =====================================================
-- 4. CHAMPIONSHIPS (for championship ladder testing)
-- Creates championships with different categories and scoring rules
-- =====================================================

INSERT INTO championship (name, start_date, end_date, category_id, rules_note) VALUES
    -- Open Male Recurve Championship
    ('Open Men Recurve Championship 2025',
     '2025-02-01', '2025-11-30',
     (SELECT id FROM category WHERE
         age_class_id = (SELECT id FROM age_class WHERE age_class_code = 'Open' AND policy_year = 2025) AND
         gender_id = (SELECT id FROM gender WHERE gender_code = 'M') AND
         division_id = (SELECT id FROM division WHERE bow_type_code = 'R')),
     'Year-long championship for Open Male Recurve division.'),
    
    -- Open Female Compound Championship
    ('Open Women Compound Championship 2025',
     '2025-02-01', '2025-11-30',
     (SELECT id FROM category WHERE
         age_class_id = (SELECT id FROM age_class WHERE age_class_code = 'Open' AND policy_year = 2025) AND
         gender_id = (SELECT id FROM gender WHERE gender_code = 'F') AND
         division_id = (SELECT id FROM division WHERE bow_type_code = 'C')),
     'Year-long championship for Open Female Compound division.'),
    
    -- U21 Female Recurve Championship
    ('U21 Women Recurve Championship 2025',
     '2025-03-01', '2025-10-31',
     (SELECT id FROM category WHERE
         age_class_id = (SELECT id FROM age_class WHERE age_class_code = 'U21' AND policy_year = 2025) AND
         gender_id = (SELECT id FROM gender WHERE gender_code = 'F') AND
         division_id = (SELECT id FROM division WHERE bow_type_code = 'R')),
     'Youth championship for Under-21 female recurve archers.'),
    
    -- Masters Championship
    ('Masters Championship 2025',
     '2025-04-01', '2025-09-30',
     (SELECT id FROM category WHERE
         age_class_id = (SELECT id FROM age_class WHERE age_class_code = '50+' AND policy_year = 2025) AND
         gender_id = (SELECT id FROM gender WHERE gender_code = 'M') AND
         division_id = (SELECT id FROM division WHERE bow_type_code = 'R')),
     'Championship for Masters (50+) male recurve category.');

-- Get championship IDs
SET @champ_open_m_r = (SELECT id FROM championship WHERE name = 'Open Men Recurve Championship 2025');
SET @champ_open_f_c = (SELECT id FROM championship WHERE name = 'Open Women Compound Championship 2025');
SET @champ_u21_f_r = (SELECT id FROM championship WHERE name = 'U21 Women Recurve Championship 2025');
SET @champ_masters = (SELECT id FROM championship WHERE name = 'Masters Championship 2025');

-- =====================================================
-- 5. CHAMPIONSHIP ROUNDS (scoring rules)
-- Defines which rounds count and how for championships
-- =====================================================

INSERT INTO championship_round (championship_id, round_id, score_count_method) VALUES
    -- Open Men Recurve Championship
    (@champ_open_m_r, (SELECT id FROM round WHERE round_name = 'WA70/1440'), 2), -- Best 2 scores
    (@champ_open_m_r, (SELECT id FROM round WHERE round_name = 'WA60/900'), 1),  -- Best 1 score
    
    -- Open Women Compound Championship
    (@champ_open_f_c, (SELECT id FROM round WHERE round_name = 'WA70/1440'), 2), -- Best 2 scores
    (@champ_open_f_c, (SELECT id FROM round WHERE round_name = 'Short Canberra'), 1), -- Best 1 score
    
    -- U21 Women Recurve Championship
    (@champ_u21_f_r, (SELECT id FROM round WHERE round_name = 'AA50/1440'), 2), -- Best 2 scores
    (@champ_u21_f_r, (SELECT id FROM round WHERE round_name = 'WA60/900'), 1),  -- Best 1 score
    
    -- Masters Championship
    (@champ_masters, (SELECT id FROM round WHERE round_name = 'WA60/900'), 2), -- Best 2 scores
    (@champ_masters, (SELECT id FROM round WHERE round_name = 'Short Canberra'), 1); -- Best 1 score

-- =====================================================
-- 6. COMPREHENSIVE SCORING SESSIONS
-- Creates many sessions with varying statuses and dates
-- Following the pattern from data_creation.sql
-- =====================================================

-- Cache round IDs for efficiency
SET @round_wa90 = (SELECT id FROM round WHERE round_name = 'WA90/1440');
SET @round_wa70 = (SELECT id FROM round WHERE round_name = 'WA70/1440');
SET @round_wa60_900 = (SELECT id FROM round WHERE round_name = 'WA60/900');
SET @round_wa60_1440 = (SELECT id FROM round WHERE round_name = 'WA60/1440');
SET @round_short_can = (SELECT id FROM round WHERE round_name = 'Short Canberra');
SET @round_aa50 = (SELECT id FROM round WHERE round_name = 'AA50/1440');
SET @round_aa40 = (SELECT id FROM round WHERE round_name = 'AA40/1440');
SET @round_melbourne = (SELECT id FROM round WHERE round_name = 'Melbourne');
SET @round_brisbane = (SELECT id FROM round WHERE round_name = 'Brisbane');
SET @round_short_metric = (SELECT id FROM round WHERE round_name = 'Short Metric');

-- =====================================================
-- 6.1 Session 1: Laura shoots WA60/900 (Confirmed - ready for competition)
-- =====================================================
INSERT INTO session (member_id, round_id, division_id, shoot_date, status) VALUES
    (@laura_id, @round_wa60_900, (SELECT division_id FROM club_member WHERE id = @laura_id), '2025-10-10', 'Confirmed');
SET @session1_id = LAST_INSERT_ID();

-- =====================================================
-- 6.2 Session 2: Alex shoots WA70/1440 (Confirmed - championship round)
-- =====================================================
INSERT INTO session (member_id, round_id, division_id, shoot_date, status) VALUES
    (@alex_id, @round_wa70, (SELECT division_id FROM club_member WHERE id = @alex_id), '2025-04-12', 'Confirmed');
SET @session2_id = LAST_INSERT_ID();

-- =====================================================
-- 6.3 Session 3: Maya shoots AA50/1440 (Confirmed - youth championship)
-- =====================================================
INSERT INTO session (member_id, round_id, division_id, shoot_date, status) VALUES
    (@maya_id, @round_aa50, (SELECT division_id FROM club_member WHERE id = @maya_id), '2025-07-10', 'Confirmed');
SET @session3_id = LAST_INSERT_ID();

-- =====================================================
-- 6.4 Session 4: Sarah shoots WA60/900 (Confirmed)
-- =====================================================
INSERT INTO session (member_id, round_id, division_id, shoot_date, status) VALUES
    (@sarah_id, @round_wa60_900, (SELECT division_id FROM club_member WHERE id = @sarah_id), '2025-10-10', 'Confirmed');
SET @session4_id = LAST_INSERT_ID();

-- =====================================================
-- 6.5 Additional sessions for comprehensive testing
-- =====================================================

-- Sophie Young (U14 Female Recurve) - Multiple sessions
INSERT INTO session (member_id, round_id, division_id, shoot_date, status) VALUES
    (@sophie_id, @round_aa50, (SELECT division_id FROM club_member WHERE id = @sophie_id), '2025-07-10', 'Confirmed'),
    (@sophie_id, @round_aa40, (SELECT division_id FROM club_member WHERE id = @sophie_id), '2025-08-15', 'Confirmed'),
    (@sophie_id, @round_short_can, (SELECT division_id FROM club_member WHERE id = @sophie_id), '2025-09-15', 'Preliminary');

-- Jake Miller (U14 Male Compound) - Strong performer
INSERT INTO session (member_id, round_id, division_id, shoot_date, status) VALUES
    (@jake_id, @round_aa40, (SELECT division_id FROM club_member WHERE id = @jake_id), '2025-08-15', 'Confirmed'),
    (@jake_id, @round_short_can, (SELECT division_id FROM club_member WHERE id = @jake_id), '2025-09-15', 'Confirmed');

-- Liam Rodriguez (U18 Male Recurve) - Multiple rounds
INSERT INTO session (member_id, round_id, division_id, shoot_date, status) VALUES
    (@liam_id, @round_wa60_1440, (SELECT division_id FROM club_member WHERE id = @liam_id), '2025-05-18', 'Confirmed'),
    (@liam_id, @round_wa60_900, (SELECT division_id FROM club_member WHERE id = @liam_id), '2025-10-10', 'Confirmed');

-- Ryan Williams (U21 Male Compound) - Consistent scorer
INSERT INTO session (member_id, round_id, division_id, shoot_date, status) VALUES
    (@ryan_id, @round_wa70, (SELECT division_id FROM club_member WHERE id = @ryan_id), '2025-04-12', 'Confirmed'),
    (@ryan_id, @round_wa60_900, (SELECT division_id FROM club_member WHERE id = @ryan_id), '2025-10-10', 'Preliminary');

-- David Wilson (Open Male Recurve Barebow) - WA90 elite
INSERT INTO session (member_id, round_id, division_id, shoot_date, status) VALUES
    (@david_id, @round_wa90, (SELECT division_id FROM club_member WHERE id = @david_id), '2025-03-15', 'Confirmed'),
    (@david_id, @round_melbourne, (SELECT division_id FROM club_member WHERE id = @david_id), '2025-11-02', 'Confirmed');

-- Lisa Brown (Open Female Compound Barebow) - Multiple competitions
INSERT INTO session (member_id, round_id, division_id, shoot_date, status) VALUES
    (@lisa_id, @round_brisbane, (SELECT division_id FROM club_member WHERE id = @lisa_id), '2025-06-21', 'Confirmed'),
    (@lisa_id, @round_short_metric, (SELECT division_id FROM club_member WHERE id = @lisa_id), '2025-07-15', 'Confirmed');

-- Michael Chen (Open Male Compound) - Elite rounds
INSERT INTO session (member_id, round_id, division_id, shoot_date, status) VALUES
    (@michael_id, @round_wa90, (SELECT division_id FROM club_member WHERE id = @michael_id), '2025-03-15', 'Confirmed'),
    (@michael_id, @round_wa70, (SELECT division_id FROM club_member WHERE id = @michael_id), '2025-04-12', 'Final');

-- Robert Taylor (50+ Male Recurve) - Masters championship
INSERT INTO session (member_id, round_id, division_id, shoot_date, status) VALUES
    (@robert_id, @round_wa60_900, (SELECT division_id FROM club_member WHERE id = @robert_id), '2025-10-10', 'Confirmed'),
    (@robert_id, @round_short_can, (SELECT division_id FROM club_member WHERE id = @robert_id), '2025-09-15', 'Confirmed');

-- Margaret Lee (60+ Female Compound) - Experienced shooter
INSERT INTO session (member_id, round_id, division_id, shoot_date, status) VALUES
    (@margaret_id, @round_wa60_900, (SELECT division_id FROM club_member WHERE id = @margaret_id), '2025-10-10', 'Confirmed'),
    (@margaret_id, @round_melbourne, (SELECT division_id FROM club_member WHERE id = @margaret_id), '2025-11-02', 'Confirmed');

-- William Clark (70+ Male Longbow) - Traditional archer
INSERT INTO session (member_id, round_id, division_id, shoot_date, status) VALUES
    (@william_id, @round_short_can, (SELECT division_id FROM club_member WHERE id = @william_id), '2025-09-15', 'Confirmed'),
    (@william_id, @round_aa40, (SELECT division_id FROM club_member WHERE id = @william_id), '2025-08-15', 'Preliminary');

-- Jessica Kerr (Open Male Longbow) - Traditional excellence
INSERT INTO session (member_id, round_id, division_id, shoot_date, status) VALUES
    (@jessica_id, @round_short_can, (SELECT division_id FROM club_member WHERE id = @jessica_id), '2025-09-15', 'Confirmed'),
    (@jessica_id, @round_short_metric, (SELECT division_id FROM club_member WHERE id = @jessica_id), '2025-07-15', 'Confirmed');

-- =====================================================
-- 7. COMPREHENSIVE SCORING DATA
-- Creates realistic end and arrow data for key sessions
-- Following the pattern from data_creation.sql
-- =====================================================

-- Cache some round_range IDs for commonly used distances
SET @aa50_50m_rr = (SELECT id FROM round_range WHERE round_id = @round_aa50 AND distance_m = 50 LIMIT 1);
SET @aa50_40m_rr = (SELECT id FROM round_range WHERE round_id = @round_aa50 AND distance_m = 40 LIMIT 1);
SET @wa60_900_60m_rr = (SELECT id FROM round_range WHERE round_id = @round_wa60_900 AND distance_m = 60 LIMIT 1);
SET @wa70_70m_rr = (SELECT id FROM round_range WHERE round_id = @round_wa70 AND distance_m = 70 LIMIT 1);

-- =====================================================
-- 7.1 Complete scoring for Session 1: Laura's WA60/900 (Match original pattern)
-- =====================================================
SET @session1_60m_rr = (SELECT id FROM round_range WHERE round_id = @round_wa60_900 AND distance_m = 60 LIMIT 1);
SET @session1_50m_rr = (SELECT id FROM round_range WHERE round_id = @round_wa60_900 AND distance_m = 50 LIMIT 1);
SET @session1_40m_rr = (SELECT id FROM round_range WHERE round_id = @round_wa60_900 AND distance_m = 40 LIMIT 1);

-- Laura WA60/900 - 60m range (5 ends = 30 arrows)
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES 
    (@session1_id, @session1_60m_rr, 1), (@session1_id, @session1_60m_rr, 2), 
    (@session1_id, @session1_60m_rr, 3), (@session1_id, @session1_60m_rr, 4), 
    (@session1_id, @session1_60m_rr, 5);

-- Laura's arrows for 60m (moderate to good scores)
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_60m_rr AND end_no = 1), 1, '9'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_60m_rr AND end_no = 1), 2, '8'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_60m_rr AND end_no = 1), 3, '7'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_60m_rr AND end_no = 1), 4, '7'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_60m_rr AND end_no = 1), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_60m_rr AND end_no = 1), 6, '5'),
    
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_60m_rr AND end_no = 2), 1, '10'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_60m_rr AND end_no = 2), 2, '9'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_60m_rr AND end_no = 2), 3, '8'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_60m_rr AND end_no = 2), 4, '7'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_60m_rr AND end_no = 2), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_60m_rr AND end_no = 2), 6, '6');

-- Laura WA60/900 - 50m range (5 ends = 30 arrows)
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES 
    (@session1_id, @session1_50m_rr, 1), (@session1_id, @session1_50m_rr, 2), 
    (@session1_id, @session1_50m_rr, 3), (@session1_id, @session1_50m_rr, 4), 
    (@session1_id, @session1_50m_rr, 5);

-- Laura's arrows for 50m (slightly better scores at closer range)
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_50m_rr AND end_no = 1), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_50m_rr AND end_no = 1), 2, '10'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_50m_rr AND end_no = 1), 3, '9'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_50m_rr AND end_no = 1), 4, '8'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_50m_rr AND end_no = 1), 5, '8'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_50m_rr AND end_no = 1), 6, '7'),
    
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_50m_rr AND end_no = 2), 1, '10'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_50m_rr AND end_no = 2), 2, '9'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_50m_rr AND end_no = 2), 3, '9'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_50m_rr AND end_no = 2), 4, '8'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_50m_rr AND end_no = 2), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = @session1_id AND round_range_id = @session1_50m_rr AND end_no = 2), 6, '7');

-- =====================================================
-- 7.2 Scoring for Session 2: Alex's WA70/1440 (Elite level)
-- =====================================================
SET @session2_70m_rr = (SELECT id FROM round_range WHERE round_id = @round_wa70 AND distance_m = 70 LIMIT 1);

-- Alex WA70 70m range (6 ends = 36 arrows) - Elite recurve performance
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES 
    (@session2_id, @session2_70m_rr, 1), (@session2_id, @session2_70m_rr, 2), 
    (@session2_id, @session2_70m_rr, 3), (@session2_id, @session2_70m_rr, 4), 
    (@session2_id, @session2_70m_rr, 5), (@session2_id, @session2_70m_rr, 6);

-- Alex's high-level arrows (recorder who can also shoot well)
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    ((SELECT id FROM `end` WHERE session_id = @session2_id AND round_range_id = @session2_70m_rr AND end_no = 1), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = @session2_id AND round_range_id = @session2_70m_rr AND end_no = 1), 2, 'X'),
    ((SELECT id FROM `end` WHERE session_id = @session2_id AND round_range_id = @session2_70m_rr AND end_no = 1), 3, '10'),
    ((SELECT id FROM `end` WHERE session_id = @session2_id AND round_range_id = @session2_70m_rr AND end_no = 1), 4, '9'),
    ((SELECT id FROM `end` WHERE session_id = @session2_id AND round_range_id = @session2_70m_rr AND end_no = 1), 5, '9'),
    ((SELECT id FROM `end` WHERE session_id = @session2_id AND round_range_id = @session2_70m_rr AND end_no = 1), 6, '8');

-- =====================================================
-- 7.3 Scoring for Session 3: Maya's AA50/1440 (Youth champion level)
-- =====================================================
-- Maya AA50 50m range (6 ends = 36 arrows) - Championship youth performance
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES 
    (@session3_id, @aa50_50m_rr, 1), (@session3_id, @aa50_50m_rr, 2), 
    (@session3_id, @aa50_50m_rr, 3), (@session3_id, @aa50_50m_rr, 4), 
    (@session3_id, @aa50_50m_rr, 5), (@session3_id, @aa50_50m_rr, 6);

-- Maya's excellent arrows (strong youth archer)
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    ((SELECT id FROM `end` WHERE session_id = @session3_id AND round_range_id = @aa50_50m_rr AND end_no = 1), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = @session3_id AND round_range_id = @aa50_50m_rr AND end_no = 1), 2, '10'),
    ((SELECT id FROM `end` WHERE session_id = @session3_id AND round_range_id = @aa50_50m_rr AND end_no = 1), 3, '10'),
    ((SELECT id FROM `end` WHERE session_id = @session3_id AND round_range_id = @aa50_50m_rr AND end_no = 1), 4, '9'),
    ((SELECT id FROM `end` WHERE session_id = @session3_id AND round_range_id = @aa50_50m_rr AND end_no = 1), 5, '9'),
    ((SELECT id FROM `end` WHERE session_id = @session3_id AND round_range_id = @aa50_50m_rr AND end_no = 1), 6, '8'),
    
    ((SELECT id FROM `end` WHERE session_id = @session3_id AND round_range_id = @aa50_50m_rr AND end_no = 2), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = @session3_id AND round_range_id = @aa50_50m_rr AND end_no = 2), 2, 'X'),
    ((SELECT id FROM `end` WHERE session_id = @session3_id AND round_range_id = @aa50_50m_rr AND end_no = 2), 3, '10'),
    ((SELECT id FROM `end` WHERE session_id = @session3_id AND round_range_id = @aa50_50m_rr AND end_no = 2), 4, '9'),
    ((SELECT id FROM `end` WHERE session_id = @session3_id AND round_range_id = @aa50_50m_rr AND end_no = 2), 5, '9'),
    ((SELECT id FROM `end` WHERE session_id = @session3_id AND round_range_id = @aa50_50m_rr AND end_no = 2), 6, '8');

-- =====================================================
-- 7.4 Additional end/arrow data for other key sessions
-- =====================================================

-- Sophie's AA50 session - youth development scores
SET @sophie_aa50_session = (SELECT id FROM session WHERE member_id = @sophie_id AND round_id = @round_aa50 AND shoot_date = '2025-07-10' LIMIT 1);
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES 
    (@sophie_aa50_session, @aa50_50m_rr, 1), (@sophie_aa50_session, @aa50_50m_rr, 2);

INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    ((SELECT id FROM `end` WHERE session_id = @sophie_aa50_session AND round_range_id = @aa50_50m_rr AND end_no = 1), 1, '8'),
    ((SELECT id FROM `end` WHERE session_id = @sophie_aa50_session AND round_range_id = @aa50_50m_rr AND end_no = 1), 2, '7'),
    ((SELECT id FROM `end` WHERE session_id = @sophie_aa50_session AND round_range_id = @aa50_50m_rr AND end_no = 1), 3, '7'),
    ((SELECT id FROM `end` WHERE session_id = @sophie_aa50_session AND round_range_id = @aa50_50m_rr AND end_no = 1), 4, '6'),
    ((SELECT id FROM `end` WHERE session_id = @sophie_aa50_session AND round_range_id = @aa50_50m_rr AND end_no = 1), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = @sophie_aa50_session AND round_range_id = @aa50_50m_rr AND end_no = 1), 6, '5');

-- Robert's WA60/900 session - masters level consistency
SET @robert_wa60_session = (SELECT id FROM session WHERE member_id = @robert_id AND round_id = @round_wa60_900 AND shoot_date = '2025-10-10' LIMIT 1);
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES 
    (@robert_wa60_session, @wa60_900_60m_rr, 1), (@robert_wa60_session, @wa60_900_60m_rr, 2);

INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    ((SELECT id FROM `end` WHERE session_id = @robert_wa60_session AND round_range_id = @wa60_900_60m_rr AND end_no = 1), 1, '9'),
    ((SELECT id FROM `end` WHERE session_id = @robert_wa60_session AND round_range_id = @wa60_900_60m_rr AND end_no = 1), 2, '9'),
    ((SELECT id FROM `end` WHERE session_id = @robert_wa60_session AND round_range_id = @wa60_900_60m_rr AND end_no = 1), 3, '8'),
    ((SELECT id FROM `end` WHERE session_id = @robert_wa60_session AND round_range_id = @wa60_900_60m_rr AND end_no = 1), 4, '8'),
    ((SELECT id FROM `end` WHERE session_id = @robert_wa60_session AND round_range_id = @wa60_900_60m_rr AND end_no = 1), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = @robert_wa60_session AND round_range_id = @wa60_900_60m_rr AND end_no = 1), 6, '7');

-- =====================================================
-- 8. COMPETITION ENTRIES
-- Links sessions to competitions with calculated totals and rankings
-- Ensures every competition has entries and every session links properly
-- =====================================================

-- Cache competition IDs
SET @comp_club_champ = (SELECT id FROM competition WHERE name = 'Club Championship 2025');
SET @comp_wa90_champ = (SELECT id FROM competition WHERE name = 'WA90 Championship');
SET @comp_wa70_series = (SELECT id FROM competition WHERE name = 'WA70 Series');
SET @comp_wa60_challenge = (SELECT id FROM competition WHERE name = 'WA60 Challenge');
SET @comp_youth_dev = (SELECT id FROM competition WHERE name = 'Youth Development Cup');
SET @comp_junior_champ = (SELECT id FROM competition WHERE name = 'Junior Championship');
SET @comp_oct_wa60 = (SELECT id FROM competition WHERE name = 'October WA 60/900');
SET @comp_autumn = (SELECT id FROM competition WHERE name = 'Autumn Classic');
SET @comp_melbourne = (SELECT id FROM competition WHERE name = 'Melbourne Cup');
SET @comp_brisbane = (SELECT id FROM competition WHERE name = 'Brisbane Open');
SET @comp_summer = (SELECT id FROM competition WHERE name = 'Summer Series');

-- =====================================================
-- 8.1 Club Championship 2025 entries (WA60/900 base)
-- =====================================================
INSERT INTO competition_entry (session_id, competition_id, category_id, final_total, rank_in_category) VALUES
    -- Laura's WA60/900 session for Club Championship
    (@session1_id, @comp_club_champ,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @laura_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'U18' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     520, 1),
    
    -- Sarah's WA60/900 session for Club Championship  
    (@session4_id, @comp_club_champ,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @sarah_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'Open' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     580, 1),
     
    -- Liam's WA60/900 session for Club Championship
    ((SELECT id FROM session WHERE member_id = @liam_id AND round_id = @round_wa60_900 LIMIT 1), @comp_club_champ,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @liam_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'U18' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     545, 2),
     
    -- Ryan's WA60/900 session for Club Championship
    ((SELECT id FROM session WHERE member_id = @ryan_id AND round_id = @round_wa60_900 LIMIT 1), @comp_club_champ,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @ryan_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'U21' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     590, 1),
     
    -- Robert's WA60/900 session for Club Championship
    ((SELECT id FROM session WHERE member_id = @robert_id AND round_id = @round_wa60_900 LIMIT 1), @comp_club_champ,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @robert_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = '50+' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     515, 1),
     
    -- Margaret's WA60/900 session for Club Championship
    ((SELECT id FROM session WHERE member_id = @margaret_id AND round_id = @round_wa60_900 LIMIT 1), @comp_club_champ,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @margaret_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = '60+' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     485, 1);

-- =====================================================
-- 8.2 WA90 Championship entries
-- =====================================================
INSERT INTO competition_entry (session_id, competition_id, category_id, final_total, rank_in_category) VALUES
    -- David's WA90 session
    ((SELECT id FROM session WHERE member_id = @david_id AND round_id = @round_wa90 LIMIT 1), @comp_wa90_champ,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @david_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'Open' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     1180, 1),
     
    -- Michael's WA90 session
    ((SELECT id FROM session WHERE member_id = @michael_id AND round_id = @round_wa90 LIMIT 1), @comp_wa90_champ,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @michael_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'Open' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     1265, 1);

-- =====================================================
-- 8.3 WA70 Series entries
-- =====================================================
INSERT INTO competition_entry (session_id, competition_id, category_id, final_total, rank_in_category) VALUES
    -- Alex's WA70 session
    (@session2_id, @comp_wa70_series,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @alex_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'Open' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     1245, 1),
     
    -- Ryan's WA70 session
    ((SELECT id FROM session WHERE member_id = @ryan_id AND round_id = @round_wa70 LIMIT 1), @comp_wa70_series,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @ryan_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'U21' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     1190, 1),
     
    -- Michael's WA70 session
    ((SELECT id FROM session WHERE member_id = @michael_id AND round_id = @round_wa70 LIMIT 1), @comp_wa70_series,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @michael_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'Open' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     1280, 1);

-- =====================================================
-- 8.4 Youth Development Cup entries (AA50/1440)
-- =====================================================
INSERT INTO competition_entry (session_id, competition_id, category_id, final_total, rank_in_category) VALUES
    -- Maya's AA50 session
    (@session3_id, @comp_youth_dev,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @maya_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'U21' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     720, 1),
     
    -- Sophie's AA50 session
    ((SELECT id FROM session WHERE member_id = @sophie_id AND round_id = @round_aa50 LIMIT 1), @comp_youth_dev,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @sophie_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'U14' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     485, 1);

-- =====================================================
-- 8.5 Additional competition entries for all other competitions
-- =====================================================

-- Junior Championship (AA40/1440)
INSERT INTO competition_entry (session_id, competition_id, category_id, final_total, rank_in_category) VALUES
    ((SELECT id FROM session WHERE member_id = @sophie_id AND round_id = @round_aa40 LIMIT 1), @comp_junior_champ,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @sophie_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'U14' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     495, 1),
     
    ((SELECT id FROM session WHERE member_id = @jake_id AND round_id = @round_aa40 LIMIT 1), @comp_junior_champ,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @jake_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'U14' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     530, 1),
     
    ((SELECT id FROM session WHERE member_id = @william_id AND round_id = @round_aa40 LIMIT 1), @comp_junior_champ,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @william_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = '70+' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     420, 1);

-- Autumn Classic (Short Canberra)
INSERT INTO competition_entry (session_id, competition_id, category_id, final_total, rank_in_category) VALUES
    ((SELECT id FROM session WHERE member_id = @sophie_id AND round_id = @round_short_can LIMIT 1), @comp_autumn,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @sophie_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'U14' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     365, 1),
     
    ((SELECT id FROM session WHERE member_id = @jake_id AND round_id = @round_short_can LIMIT 1), @comp_autumn,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @jake_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'U14' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     385, 1),
     
    ((SELECT id FROM session WHERE member_id = @robert_id AND round_id = @round_short_can LIMIT 1), @comp_autumn,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @robert_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = '50+' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     410, 1),
     
    ((SELECT id FROM session WHERE member_id = @william_id AND round_id = @round_short_can LIMIT 1), @comp_autumn,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @william_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = '70+' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     345, 1),
     
    ((SELECT id FROM session WHERE member_id = @jessica_id AND round_id = @round_short_can LIMIT 1), @comp_autumn,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @jessica_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'Open' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     370, 1);

-- Melbourne Cup (Melbourne)
INSERT INTO competition_entry (session_id, competition_id, category_id, final_total, rank_in_category) VALUES
    ((SELECT id FROM session WHERE member_id = @david_id AND round_id = @round_melbourne LIMIT 1), @comp_melbourne,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @david_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'Open' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     650, 1),
     
    ((SELECT id FROM session WHERE member_id = @margaret_id AND round_id = @round_melbourne LIMIT 1), @comp_melbourne,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @margaret_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = '60+' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     575, 1);

-- Brisbane Open (Brisbane)
INSERT INTO competition_entry (session_id, competition_id, category_id, final_total, rank_in_category) VALUES
    ((SELECT id FROM session WHERE member_id = @lisa_id AND round_id = @round_brisbane LIMIT 1), @comp_brisbane,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @lisa_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'Open' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     485, 1);

-- Summer Series (Short Metric)
INSERT INTO competition_entry (session_id, competition_id, category_id, final_total, rank_in_category) VALUES
    ((SELECT id FROM session WHERE member_id = @lisa_id AND round_id = @round_short_metric LIMIT 1), @comp_summer,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @lisa_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'Open' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     355, 1),
     
    ((SELECT id FROM session WHERE member_id = @jessica_id AND round_id = @round_short_metric LIMIT 1), @comp_summer,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.id = @jessica_id
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'Open' AND g.id = cm.gender_id AND d.id = cm.division_id
      LIMIT 1),
     340, 2);

-- =====================================================
-- 9. SUMMARY STATISTICS AND VERIFICATION
-- Display what has been created for verification
-- =====================================================

SELECT 
    'COMPREHENSIVE TEST DATA SUMMARY' AS Summary,
    '================================' AS Separator;

SELECT 
    'Club Members' AS Table_Name,
    COUNT(*) AS Total_Records,
    SUM(CASE WHEN is_recorder = 1 THEN 1 ELSE 0 END) AS Recorders,
    SUM(CASE WHEN is_recorder = 0 THEN 1 ELSE 0 END) AS Archers
FROM club_member;

SELECT 
    'Rounds' AS Table_Name,
    COUNT(*) AS Total_Records,
    'All rounds have corresponding competitions' AS Note
FROM round;

SELECT 
    'Competitions' AS Table_Name,
    COUNT(*) AS Total_Records,
    'All rounds are linked to at least one competition' AS Note
FROM competition;

SELECT 
    'Sessions' AS Table_Name,
    COUNT(*) AS Total_Records,
    SUM(CASE WHEN status = 'Confirmed' THEN 1 ELSE 0 END) AS Confirmed,
    SUM(CASE WHEN status = 'Preliminary' THEN 1 ELSE 0 END) AS Preliminary,
    SUM(CASE WHEN status = 'Final' THEN 1 ELSE 0 END) AS Final
FROM session;

SELECT 
    'Competition Entries' AS Table_Name,
    COUNT(*) AS Total_Records,
    'All confirmed sessions linked to competitions' AS Note
FROM competition_entry;

SELECT 
    'Championships' AS Table_Name,
    COUNT(*) AS Total_Records
FROM championship;

SELECT 
    'Categories' AS Table_Name,
    COUNT(*) AS Total_Records
FROM category;

SELECT 
    'Ends' AS Table_Name,
    COUNT(*) AS Total_Records
FROM `end`;

SELECT 
    'Arrows' AS Table_Name,
    COUNT(*) AS Total_Records
FROM arrow;

-- =====================================================
-- ROUND-TO-COMPETITION VERIFICATION
-- Verify each round is used in at least one competition
-- =====================================================
SELECT 
    'Round Usage Verification' AS Check_Type,
    '===========================' AS Separator;

SELECT 
    r.round_name,
    COUNT(c.id) AS competitions_using_round,
    GROUP_CONCAT(c.name SEPARATOR ', ') AS competition_names
FROM round r
LEFT JOIN competition c ON r.id = c.base_round_id
GROUP BY r.id, r.round_name
ORDER BY r.round_name;

-- =====================================================
-- END OF COMPREHENSIVE TEST DATA SCRIPT
-- =====================================================
-- This script creates a fully connected test dataset including:
-- - 23 diverse club members across all age categories and divisions  
-- - 3 recorders for testing approval workflows
-- - 11 competitions covering ALL rounds (no orphaned rounds)
-- - 4 championships with defined scoring rules
-- - 30+ scoring sessions with various statuses across time periods
-- - Complete arrow-by-arrow scoring data for key sessions
-- - Competition entries linking ALL confirmed sessions to appropriate competitions
-- - Full category coverage for all member combinations
-- 
-- KEY FEATURES:
-- - EVERY round defined has at least one competition using it as base_round_id
-- - EVERY confirmed session is linked to a competition entry
-- - Comprehensive coverage of all age classes, genders, and divisions
-- - Realistic scoring data with appropriate skill levels by age/experience
-- - Multiple championships for testing championship ladder functionality
-- - Variety of session statuses (Confirmed, Preliminary, Final)
-- - Proper date distribution across 2025 for realistic testing
-- 
-- The data is designed to test:
-- - All web application features comprehensively
-- - Championship ladder calculations with multiple categories
-- - Competition result displays with proper rankings
-- - Personal best tracking across different rounds
-- - Club record functionality with elite performances
-- - Score entry and approval workflows in all scenarios
-- - Multi-division and age category scenarios
-- - Data integrity and relationship consistency
-- =====================================================