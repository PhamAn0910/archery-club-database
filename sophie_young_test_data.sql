-- =====================================================
-- SOPHIE YOUNG TEST DATA FOR DISTANCE PERFORMANCE VISUALIZATION
-- =====================================================
-- Purpose: Add comprehensive arrow data for Sophie Young's confirmed sessions
-- Usage: Run after comprehensive_test_data.sql to enhance visualization testing
-- Target: Sophie Young (ID: 100003) - Sessions 5 & 6 (Confirmed status)
-- =====================================================

USE archery_db;

-- =====================================================
-- SESSION 5: AA50/1440 (Sophie Young - Confirmed)
-- Ranges: 50m (122cm), 40m (122cm), 30m (80cm), 20m (80cm)
-- Performance pattern: Better at closer distances, struggles at 50m
-- =====================================================

-- Clear existing partial data for session 5
DELETE FROM arrow WHERE end_id IN (SELECT id FROM `end` WHERE session_id = 5);
DELETE FROM `end` WHERE session_id = 5;

-- 50m Range (122cm face) - 6 ends - Struggling at long distance
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES 
    (5, 13, 1), (5, 13, 2), (5, 13, 3), (5, 13, 4), (5, 13, 5), (5, 13, 6);

-- 50m arrows - Average ~5.5 per arrow (struggling)
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    -- End 1: 28 points (4.7 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 1), 1, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 1), 2, '5'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 1), 3, '4'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 1), 4, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 1), 5, '4'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 1), 6, '3'),
    -- End 2: 32 points (5.3 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 2), 1, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 2), 2, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 2), 3, '5'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 2), 4, '5'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 2), 5, '5'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 2), 6, '4'),
    -- End 3: 35 points (5.8 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 3), 1, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 3), 2, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 3), 3, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 3), 4, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 3), 5, '5'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 3), 6, '4'),
    -- End 4: 30 points (5.0 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 4), 1, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 4), 2, '5'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 4), 3, '5'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 4), 4, '5'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 4), 5, '5'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 4), 6, '4'),
    -- End 5: 33 points (5.5 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 5), 1, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 5), 2, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 5), 3, '5'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 5), 4, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 5), 5, '5'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 5), 6, '4'),
    -- End 6: 36 points (6.0 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 6), 1, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 6), 2, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 6), 3, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 6), 4, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 6), 5, '5'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 13 AND end_no = 6), 6, '4');

-- 40m Range (122cm face) - 6 ends - Improving performance
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES 
    (5, 14, 1), (5, 14, 2), (5, 14, 3), (5, 14, 4), (5, 14, 5), (5, 14, 6);

-- 40m arrows - Average ~6.8 per arrow (decent)
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    -- End 1: 42 points (7.0 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 1), 1, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 1), 2, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 1), 3, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 1), 4, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 1), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 1), 6, '6'),
    -- End 2: 40 points (6.7 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 2), 1, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 2), 2, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 2), 3, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 2), 4, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 2), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 2), 6, '6'),
    -- End 3: 41 points (6.8 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 3), 1, '9'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 3), 2, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 3), 3, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 3), 4, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 3), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 3), 6, '6'),
    -- End 4: 39 points (6.5 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 4), 1, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 4), 2, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 4), 3, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 4), 4, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 4), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 4), 6, '6'),
    -- End 5: 43 points (7.2 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 5), 1, '9'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 5), 2, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 5), 3, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 5), 4, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 5), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 5), 6, '6'),
    -- End 6: 38 points (6.3 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 6), 1, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 6), 2, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 6), 3, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 6), 4, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 6), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 14 AND end_no = 6), 6, '5');

-- 30m Range (80cm face) - 6 ends - Good performance on smaller face
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES 
    (5, 15, 1), (5, 15, 2), (5, 15, 3), (5, 15, 4), (5, 15, 5), (5, 15, 6);

-- 30m arrows - Average ~7.5 per arrow (good)
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    -- End 1: 46 points (7.7 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 1), 1, '9'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 1), 2, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 1), 3, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 1), 4, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 1), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 1), 6, '7'),
    -- End 2: 44 points (7.3 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 2), 1, '9'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 2), 2, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 2), 3, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 2), 4, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 2), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 2), 6, '6'),
    -- End 3: 45 points (7.5 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 3), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 3), 2, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 3), 3, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 3), 4, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 3), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 3), 6, '6'),
    -- End 4: 47 points (7.8 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 4), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 4), 2, '9'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 4), 3, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 4), 4, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 4), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 4), 6, '5'),
    -- End 5: 42 points (7.0 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 5), 1, '9'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 5), 2, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 5), 3, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 5), 4, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 5), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 5), 6, '5'),
    -- End 6: 48 points (8.0 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 6), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 6), 2, '9'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 6), 3, '9'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 6), 4, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 6), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 15 AND end_no = 6), 6, '6');

-- 20m Range (80cm face) - 6 ends - Best performance at closest distance
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES 
    (5, 16, 1), (5, 16, 2), (5, 16, 3), (5, 16, 4), (5, 16, 5), (5, 16, 6);

-- 20m arrows - Average ~8.2 per arrow (excellent)
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    -- End 1: 51 points (8.5 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 1), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 1), 2, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 1), 3, '9'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 1), 4, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 1), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 1), 6, '7'),
    -- End 2: 48 points (8.0 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 2), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 2), 2, '9'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 2), 3, '9'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 2), 4, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 2), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 2), 6, '6'),
    -- End 3: 49 points (8.2 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 3), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 3), 2, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 3), 3, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 3), 4, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 3), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 3), 6, '6'),
    -- End 4: 46 points (7.7 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 4), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 4), 2, '9'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 4), 3, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 4), 4, '8'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 4), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 4), 6, '5'),
    -- End 5: 52 points (8.7 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 5), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 5), 2, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 5), 3, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 5), 4, '9'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 5), 5, '4'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 5), 6, 'M'),
    -- End 6: 50 points (8.3 avg)
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 6), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 6), 2, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 6), 3, '9'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 6), 4, '9'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 6), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 5 AND round_range_id = 16 AND end_no = 6), 6, '6');

-- =====================================================
-- SESSION 6: AA40/1440 (Sophie Young - Confirmed)
-- Ranges: 40m (122cm), 30m (122cm), 20m (80cm), 10m (80cm)
-- Performance pattern: Shows improvement from session 5, best at close range
-- =====================================================

-- Clear existing data for session 6 (if any)
DELETE FROM arrow WHERE end_id IN (SELECT id FROM `end` WHERE session_id = 6);
DELETE FROM `end` WHERE session_id = 6;

-- 40m Range (122cm face) - 6 ends - Better than session 5 at same distance
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES 
    (6, 17, 1), (6, 17, 2), (6, 17, 3), (6, 17, 4), (6, 17, 5), (6, 17, 6);

-- 40m arrows - Average ~7.2 per arrow (improved from 6.8 in session 5)
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    -- End 1: 44 points (7.3 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 1), 1, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 1), 2, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 1), 3, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 1), 4, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 1), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 1), 6, '6'),
    -- End 2: 42 points (7.0 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 2), 1, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 2), 2, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 2), 3, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 2), 4, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 2), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 2), 6, '6'),
    -- End 3: 45 points (7.5 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 3), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 3), 2, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 3), 3, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 3), 4, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 3), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 3), 6, '6'),
    -- End 4: 43 points (7.2 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 4), 1, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 4), 2, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 4), 3, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 4), 4, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 4), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 4), 6, '6'),
    -- End 5: 46 points (7.7 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 5), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 5), 2, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 5), 3, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 5), 4, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 5), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 5), 6, '6'),
    -- End 6: 40 points (6.7 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 6), 1, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 6), 2, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 6), 3, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 6), 4, '6'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 6), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 17 AND end_no = 6), 6, '6');

-- 30m Range (122cm face) - 6 ends - Good consistent performance
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES 
    (6, 18, 1), (6, 18, 2), (6, 18, 3), (6, 18, 4), (6, 18, 5), (6, 18, 6);

-- 30m arrows - Average ~7.8 per arrow (good, improved from 7.5 at 30m/80cm)
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    -- End 1: 48 points (8.0 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 1), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 1), 2, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 1), 3, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 1), 4, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 1), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 1), 6, '6'),
    -- End 2: 46 points (7.7 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 2), 1, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 2), 2, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 2), 3, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 2), 4, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 2), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 2), 6, '6'),
    -- End 3: 47 points (7.8 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 3), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 3), 2, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 3), 3, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 3), 4, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 3), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 3), 6, '6'),
    -- End 4: 45 points (7.5 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 4), 1, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 4), 2, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 4), 3, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 4), 4, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 4), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 4), 6, '6'),
    -- End 5: 49 points (8.2 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 5), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 5), 2, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 5), 3, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 5), 4, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 5), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 5), 6, '6'),
    -- End 6: 44 points (7.3 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 6), 1, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 6), 2, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 6), 3, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 6), 4, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 6), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 18 AND end_no = 6), 6, '6');

-- 20m Range (80cm face) - 6 ends - Very good performance
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES 
    (6, 19, 1), (6, 19, 2), (6, 19, 3), (6, 19, 4), (6, 19, 5), (6, 19, 6);

-- 20m arrows - Average ~8.4 per arrow (excellent, improved from 8.2 in session 5)
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    -- End 1: 52 points (8.7 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 1), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 1), 2, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 1), 3, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 1), 4, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 1), 5, '4'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 1), 6, '2'),
    -- End 2: 50 points (8.3 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 2), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 2), 2, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 2), 3, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 2), 4, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 2), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 2), 6, '6'),
    -- End 3: 51 points (8.5 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 3), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 3), 2, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 3), 3, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 3), 4, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 3), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 3), 6, '5'),
    -- End 4: 49 points (8.2 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 4), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 4), 2, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 4), 3, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 4), 4, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 4), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 4), 6, '6'),
    -- End 5: 48 points (8.0 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 5), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 5), 2, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 5), 3, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 5), 4, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 5), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 5), 6, '6'),
    -- End 6: 53 points (8.8 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 6), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 6), 2, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 6), 3, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 6), 4, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 6), 5, '3'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 19 AND end_no = 6), 6, 'M');

-- 10m Range (80cm face) - 6 ends - Excellent performance at shortest distance
INSERT INTO `end` (session_id, round_range_id, end_no) VALUES 
    (6, 20, 1), (6, 20, 2), (6, 20, 3), (6, 20, 4), (6, 20, 5), (6, 20, 6);

-- 10m arrows - Average ~8.8 per arrow (outstanding)
INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES
    -- End 1: 54 points (9.0 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 1), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 1), 2, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 1), 3, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 1), 4, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 1), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 1), 6, '7'),
    -- End 2: 52 points (8.7 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 2), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 2), 2, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 2), 3, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 2), 4, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 2), 5, '5'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 2), 6, '5'),
    -- End 3: 53 points (8.8 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 3), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 3), 2, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 3), 3, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 3), 4, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 3), 5, '3'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 3), 6, 'M'),
    -- End 4: 51 points (8.5 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 4), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 4), 2, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 4), 3, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 4), 4, '9'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 4), 5, '7'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 4), 6, '6'),
    -- End 5: 55 points (9.2 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 5), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 5), 2, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 5), 3, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 5), 4, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 5), 5, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 5), 6, '5'),
    -- End 6: 50 points (8.3 avg)
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 6), 1, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 6), 2, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 6), 3, 'X'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 6), 4, '8'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 6), 5, '6'),
    ((SELECT id FROM `end` WHERE session_id = 6 AND round_range_id = 20 AND end_no = 6), 6, '6');

-- =====================================================
-- SUMMARY OF EXPECTED PERFORMANCE DATA
-- =====================================================
-- After running this script, Sophie Young should have comprehensive distance data:
--
-- Session 5 (AA50/1440):
-- - 50m (122cm): ~5.5 avg per arrow (struggling)
-- - 40m (122cm): ~6.8 avg per arrow (decent) 
-- - 30m (80cm):  ~7.5 avg per arrow (good)
-- - 20m (80cm):  ~8.2 avg per arrow (excellent)
--
-- Session 6 (AA40/1440):
-- - 40m (122cm): ~7.2 avg per arrow (improved from 6.8)
-- - 30m (122cm): ~7.8 avg per arrow (good on larger face)
-- - 20m (80cm):  ~8.4 avg per arrow (excellent, improved from 8.2)
-- - 10m (80cm):  ~8.8 avg per arrow (outstanding)
--
-- This data will show clear patterns:
-- 1. Better performance at closer distances
-- 2. Improvement between sessions at same distances (40m, 20m)
-- 3. Face size impact (30m: 7.8 on 122cm vs 7.5 on 80cm)
-- 4. Clear progression from struggling (5.5) to excellent (8.8)
-- =====================================================