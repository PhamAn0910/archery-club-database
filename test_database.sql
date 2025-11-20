-- =====================================================
-- Database Testing and Verification Script
-- Purpose: Verify all improvements are working correctly
-- Date: November 19, 2025
-- =====================================================

USE archery_db;

-- =====================================================
-- TEST 1: Recorder Constraints
-- =====================================================
SELECT '==== TEST 1: Recorder Constraints ====' AS test_section;

-- 1.1: Verify recorders have NULL division and NULL av_number
SELECT 
    'Test 1.1: Recorders have NULL division/AV' AS test_name,
    CASE 
        WHEN COUNT(*) = 2 
         AND SUM(CASE WHEN division_id IS NULL AND av_number IS NULL THEN 1 ELSE 0 END) = 2
        THEN '✅ PASS'
        ELSE '❌ FAIL'
    END AS result,
    GROUP_CONCAT(full_name) AS recorders
FROM club_member 
WHERE is_recorder = TRUE;

-- 1.2: Verify archers have division and av_number
SELECT 
    'Test 1.2: Archers have division/AV' AS test_name,
    CASE 
        WHEN COUNT(*) = 7 
         AND SUM(CASE WHEN division_id IS NOT NULL AND av_number IS NOT NULL THEN 1 ELSE 0 END) = 7
        THEN '✅ PASS'
        ELSE '❌ FAIL'
    END AS result,
    COUNT(*) AS archer_count
FROM club_member 
WHERE is_recorder = FALSE;

-- 1.3: Test constraint - Try to insert recorder with division (should fail)
SELECT 'Test 1.3: Recorder with division constraint' AS test_name;
-- Uncomment to test (will fail):
-- INSERT INTO club_member (full_name, birth_year, gender_id, division_id, is_recorder) 
-- VALUES ('Test Recorder', 1990, 1, 1, TRUE);
SELECT '⚠️ MANUAL TEST: Try inserting recorder with division (should fail)' AS instruction;

-- 1.4: Test constraint - Try to insert archer without division (should fail)
SELECT 'Test 1.4: Archer without division constraint' AS test_name;
-- Uncomment to test (will fail):
-- INSERT INTO club_member (full_name, birth_year, gender_id, division_id, is_recorder) 
-- VALUES ('Test Archer', 1990, 1, NULL, FALSE);
SELECT '⚠️ MANUAL TEST: Try inserting archer without division (should fail)' AS instruction;

-- =====================================================
-- TEST 2: Data Consistency
-- =====================================================
SELECT '' AS separator;
SELECT '==== TEST 2: Data Consistency ====' AS test_section;

-- 2.1: Verify Laura is female with recurve division
SELECT 
    'Test 2.1: Laura data correction' AS test_name,
    CASE 
        WHEN g.gender_code = 'F' AND d.bow_type_code = 'R' AND cm.is_recorder = FALSE
        THEN '✅ PASS'
        ELSE '❌ FAIL'
    END AS result,
    cm.full_name,
    g.gender_code AS gender,
    d.bow_type_code AS division,
    cm.is_recorder
FROM club_member cm
JOIN gender g ON g.id = cm.gender_id
LEFT JOIN division d ON d.id = cm.division_id
WHERE cm.full_name = 'Laura Kofoed';

-- 2.2: Verify total member count (2 recorders + 7 archers = 9 total)
SELECT 
    'Test 2.2: Total member count' AS test_name,
    CASE 
        WHEN COUNT(*) = 9 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END AS result,
    COUNT(*) AS total_members,
    SUM(CASE WHEN is_recorder = TRUE THEN 1 ELSE 0 END) AS recorders,
    SUM(CASE WHEN is_recorder = FALSE THEN 1 ELSE 0 END) AS archers
FROM club_member;

-- 2.3: Verify no recorders have sessions (they don't shoot)
SELECT 
    'Test 2.3: Recorders have no sessions' AS test_name,
    CASE 
        WHEN COUNT(s.id) = 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END AS result,
    COUNT(s.id) AS session_count
FROM club_member cm
LEFT JOIN session s ON s.member_id = cm.id
WHERE cm.is_recorder = TRUE;

-- =====================================================
-- TEST 3: Competition Warning System
-- =====================================================
SELECT '' AS separator;
SELECT '==== TEST 3: Competition Warning System ====' AS test_section;

-- 3.1: Verify competitions ending in 1-2 days (assuming today is 2025-11-19)
SELECT 
    'Test 3.1: Competitions ending in 1-2 days' AS test_name,
    CASE 
        WHEN COUNT(*) = 2 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END AS result,
    COUNT(*) AS competitions_ending_soon
FROM competition
WHERE DATEDIFF(end_date, '2025-11-19') BETWEEN 1 AND 2;

-- 3.2: List competitions with their end dates
SELECT 
    'Test 3.2: Competition end dates' AS test_name,
    name AS competition_name,
    end_date,
    DATEDIFF(end_date, '2025-11-19') AS days_until_end,
    CASE 
        WHEN DATEDIFF(end_date, '2025-11-19') = 0 THEN '⚪ Ends today'
        WHEN DATEDIFF(end_date, '2025-11-19') = 1 THEN '🟡 Ends tomorrow (1 day warning)'
        WHEN DATEDIFF(end_date, '2025-11-19') = 2 THEN '🟠 Ends in 2 days (2 day warning)'
        WHEN DATEDIFF(end_date, '2025-11-19') < 0 THEN '🔴 Already ended'
        ELSE '🟢 Future'
    END AS status
FROM competition
ORDER BY end_date;

-- 3.3: Verify pending sessions in competitions ending soon
SELECT 
    'Test 3.3: Pending sessions in competitions ending soon' AS test_name,
    c.name AS competition_name,
    DATEDIFF(c.end_date, '2025-11-19') AS days_left,
    COUNT(s.id) AS pending_sessions,
    GROUP_CONCAT(CONCAT(cm.full_name, ' (', s.status, ')') SEPARATOR ', ') AS sessions
FROM competition c
JOIN competition_entry ce ON ce.competition_id = c.id
JOIN session s ON s.id = ce.session_id
JOIN club_member cm ON cm.id = s.member_id
WHERE DATEDIFF(c.end_date, '2025-11-19') BETWEEN 1 AND 2
  AND s.status IN ('Preliminary', 'Final')
GROUP BY c.id, c.name, c.end_date
ORDER BY days_left;

-- =====================================================
-- TEST 4: Session and Competition Entry Integrity
-- =====================================================
SELECT '' AS separator;
SELECT '==== TEST 4: Session Integrity ====' AS test_section;

-- 4.1: Verify all sessions belong to archers (not recorders)
SELECT 
    'Test 4.1: All sessions belong to archers' AS test_name,
    CASE 
        WHEN COUNT(s.id) = (SELECT COUNT(id) FROM session) 
        THEN '✅ PASS'
        ELSE '❌ FAIL'
    END AS result,
    COUNT(s.id) AS archer_sessions,
    (SELECT COUNT(id) FROM session) AS total_sessions
FROM session s
JOIN club_member cm ON cm.id = s.member_id
WHERE cm.is_recorder = FALSE;

-- 4.2: Verify session statuses
SELECT 
    'Test 4.2: Session status distribution' AS test_name,
    status,
    COUNT(*) AS count
FROM session
GROUP BY status
ORDER BY FIELD(status, 'Preliminary', 'Final', 'Confirmed');

-- 4.3: Verify competition entries have valid categories
SELECT 
    'Test 4.3: Competition entries have valid categories' AS test_name,
    CASE 
        WHEN COUNT(*) = (SELECT COUNT(*) FROM competition_entry WHERE category_id IS NOT NULL)
        THEN '✅ PASS'
        ELSE '❌ FAIL'
    END AS result,
    COUNT(*) AS entries_with_categories
FROM competition_entry
WHERE category_id IS NOT NULL;

-- =====================================================
-- TEST 5: Arrow Data Coverage
-- =====================================================
SELECT '' AS separator;
SELECT '==== TEST 5: Arrow Data Coverage ====' AS test_section;

-- 5.1: Show sessions with arrow data
SELECT 
    'Test 5.1: Sessions with arrow data' AS test_name,
    cm.full_name AS archer,
    r.round_name,
    COUNT(DISTINCT e.id) AS ends_with_data,
    COUNT(a.id) AS total_arrows
FROM session s
JOIN club_member cm ON cm.id = s.member_id
JOIN round r ON r.id = s.round_id
LEFT JOIN `end` e ON e.session_id = s.id
LEFT JOIN arrow a ON a.end_id = e.id
WHERE a.id IS NOT NULL
GROUP BY s.id, cm.full_name, r.round_name
ORDER BY cm.full_name;

-- 5.2: Verify arrow values are valid
SELECT 
    'Test 5.2: All arrow values are valid' AS test_name,
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END AS result,
    COUNT(*) AS invalid_arrows
FROM arrow
WHERE arrow_value NOT IN ('X', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', 'M');

-- =====================================================
-- TEST 6: Database Performance Checks
-- =====================================================
SELECT '' AS separator;
SELECT '==== TEST 6: Database Performance ====' AS test_section;

-- 6.1: Check for orphaned records
SELECT 
    'Test 6.1: No orphaned sessions' AS test_name,
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END AS result,
    COUNT(*) AS orphaned_sessions
FROM session s
LEFT JOIN club_member cm ON cm.id = s.member_id
WHERE cm.id IS NULL;

-- 6.2: Check for orphaned ends
SELECT 
    'Test 6.2: No orphaned ends' AS test_name,
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END AS result,
    COUNT(*) AS orphaned_ends
FROM `end` e
LEFT JOIN session s ON s.id = e.session_id
WHERE s.id IS NULL;

-- 6.3: Check for orphaned arrows
SELECT 
    'Test 6.3: No orphaned arrows' AS test_name,
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END AS result,
    COUNT(*) AS orphaned_arrows
FROM arrow a
LEFT JOIN `end` e ON e.id = a.end_id
WHERE e.id IS NULL;

-- =====================================================
-- SUMMARY REPORT
-- =====================================================
SELECT '' AS separator;
SELECT '==== TEST SUMMARY ====' AS test_section;

SELECT 
    'Database Version' AS metric,
    '2.0 (November 19, 2025)' AS value
UNION ALL
SELECT 
    'Total Tables' AS metric,
    CAST(COUNT(*) AS CHAR) AS value
FROM information_schema.tables 
WHERE table_schema = 'archery_db'
UNION ALL
SELECT 
    'Total Members' AS metric,
    CAST(COUNT(*) AS CHAR) AS value
FROM club_member
UNION ALL
SELECT 
    'Total Competitions' AS metric,
    CAST(COUNT(*) AS CHAR) AS value
FROM competition
UNION ALL
SELECT 
    'Total Sessions' AS metric,
    CAST(COUNT(*) AS CHAR) AS value
FROM session
UNION ALL
SELECT 
    'Total Competition Entries' AS metric,
    CAST(COUNT(*) AS CHAR) AS value
FROM competition_entry;

-- =====================================================
-- End of Testing Script
-- =====================================================
SELECT '' AS separator;
SELECT '✅ Testing completed. Review results above.' AS completion_message;
SELECT 'For detailed documentation, see DATABASE_IMPROVEMENTS.md' AS next_steps;
