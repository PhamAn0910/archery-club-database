-- =====================================================
-- ADDITIONAL COMPETITION ENTRIES FOR AUTUMN CLASSIC
-- Purpose: Add more archers to existing categories for visualization testing
-- Competition: Autumn Classic (2025-09-15) - Short Canberra round
-- =====================================================

USE archery_db;

-- Get competition ID for Autumn Classic
SET @autumn_comp_id = (SELECT id FROM competition WHERE name = 'Autumn Classic');
SET @short_can_round_id = (SELECT id FROM round WHERE round_name = 'Short Canberra');

-- =====================================================
-- 1. ADD MORE SESSIONS FOR SHORT CANBERRA ROUND
-- =====================================================

-- Additional sessions for existing members shooting Short Canberra
INSERT INTO session (member_id, round_id, division_id, shoot_date, status) VALUES
    -- More 50+ Male Recurve (same category as Robert Taylor)
    ((SELECT id FROM club_member WHERE full_name = 'Thomas Anderson'), @short_can_round_id, 
     (SELECT division_id FROM club_member WHERE full_name = 'Thomas Anderson'), '2025-09-15', 'Confirmed'),
    
    -- More U14 Male Compound (same category as Jake Miller)  
    ((SELECT id FROM club_member WHERE full_name = 'Oliver Davis'), @short_can_round_id,
     (SELECT division_id FROM club_member WHERE full_name = 'Oliver Davis'), '2025-09-15', 'Confirmed'),
    
    -- More Open Male Longbow (same category as Jessica Kerr)
    ((SELECT id FROM club_member WHERE full_name = 'James Garcia'), @short_can_round_id,
     (SELECT division_id FROM club_member WHERE full_name = 'James Garcia'), '2025-09-15', 'Confirmed'),
    
    -- More 70+ Male Longbow (same category as William Clark)
    -- We need to create a new member since there's only one 70+ Male Longbow archer
    
    -- Additional Open category archers
    ((SELECT id FROM club_member WHERE full_name = 'David Wilson'), @short_can_round_id,
     (SELECT division_id FROM club_member WHERE full_name = 'David Wilson'), '2025-09-15', 'Confirmed'),
     
    ((SELECT id FROM club_member WHERE full_name = 'Sarah Mitchell'), @short_can_round_id,
     (SELECT division_id FROM club_member WHERE full_name = 'Sarah Mitchell'), '2025-09-15', 'Confirmed'),
     
    ((SELECT id FROM club_member WHERE full_name = 'Michael Chen'), @short_can_round_id,
     (SELECT division_id FROM club_member WHERE full_name = 'Michael Chen'), '2025-09-15', 'Confirmed');

-- =====================================================
-- 2. CREATE ADDITIONAL COMPETITION ENTRIES
-- =====================================================

-- 50+ Male Recurve category (Robert Taylor + Thomas Anderson)
INSERT INTO competition_entry (session_id, competition_id, category_id, final_total, rank_in_category) VALUES
    ((SELECT s.id FROM session s 
      JOIN club_member cm ON s.member_id = cm.id 
      WHERE cm.full_name = 'Thomas Anderson' AND s.round_id = @short_can_round_id AND s.shoot_date = '2025-09-15'), 
     @autumn_comp_id,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.full_name = 'Thomas Anderson'
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = '50+' AND g.id = cm.gender_id AND d.id = cm.division_id),
     395, 2); -- Robert has 410 (1st), Thomas has 395 (2nd)

-- U14 Male Compound category (Jake Miller + Oliver Davis - but Oliver is U16, so we need different approach)
-- Let's add more U14 entries by creating sessions for existing U14 members

-- First, let's add Isabella Chen (U16 Female Compound) to a different category
INSERT INTO competition_entry (session_id, competition_id, category_id, final_total, rank_in_category) VALUES
    ((SELECT s.id FROM session s 
      JOIN club_member cm ON s.member_id = cm.id 
      WHERE cm.full_name = 'Oliver Davis' AND s.round_id = @short_can_round_id AND s.shoot_date = '2025-09-15'), 
     @autumn_comp_id,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.full_name = 'Oliver Davis'
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'U16' AND g.id = cm.gender_id AND d.id = cm.division_id),
     360, 1); -- New U16 Male Recurve Barebow category

-- Open Male Longbow category (Jessica Kerr + James Garcia)
INSERT INTO competition_entry (session_id, competition_id, category_id, final_total, rank_in_category) VALUES
    ((SELECT s.id FROM session s 
      JOIN club_member cm ON s.member_id = cm.id 
      WHERE cm.full_name = 'James Garcia' AND s.round_id = @short_can_round_id AND s.shoot_date = '2025-09-15'), 
     @autumn_comp_id,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.full_name = 'James Garcia'
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'Open' AND g.id = cm.gender_id AND d.id = cm.division_id),
     355, 2); -- Jessica has 370 (1st), James has 355 (2nd)

-- Open Male Recurve Barebow (David Wilson)
INSERT INTO competition_entry (session_id, competition_id, category_id, final_total, rank_in_category) VALUES
    ((SELECT s.id FROM session s 
      JOIN club_member cm ON s.member_id = cm.id 
      WHERE cm.full_name = 'David Wilson' AND s.round_id = @short_can_round_id AND s.shoot_date = '2025-09-15'), 
     @autumn_comp_id,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.full_name = 'David Wilson'
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'Open' AND g.id = cm.gender_id AND d.id = cm.division_id),
     380, 1); -- New category winner

-- Open Female Recurve (Sarah Mitchell) 
INSERT INTO competition_entry (session_id, competition_id, category_id, final_total, rank_in_category) VALUES
    ((SELECT s.id FROM session s 
      JOIN club_member cm ON s.member_id = cm.id 
      WHERE cm.full_name = 'Sarah Mitchell' AND s.round_id = @short_can_round_id AND s.shoot_date = '2025-09-15'), 
     @autumn_comp_id,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.full_name = 'Sarah Mitchell'
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'Open' AND g.id = cm.gender_id AND d.id = cm.division_id),
     420, 1); -- New category winner

-- Open Male Compound (Michael Chen)
INSERT INTO competition_entry (session_id, competition_id, category_id, final_total, rank_in_category) VALUES
    ((SELECT s.id FROM session s 
      JOIN club_member cm ON s.member_id = cm.id 
      WHERE cm.full_name = 'Michael Chen' AND s.round_id = @short_can_round_id AND s.shoot_date = '2025-09-15'), 
     @autumn_comp_id,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.full_name = 'Michael Chen'
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'Open' AND g.id = cm.gender_id AND d.id = cm.division_id),
     450, 1); -- New category winner

-- =====================================================
-- 3. ADD MORE COMPETITORS TO EXISTING CATEGORIES
-- Let's add more members to create multiple competitors per category
-- =====================================================

-- Add more members for better category competition
INSERT INTO club_member (full_name, birth_year, gender_id, division_id, is_recorder) VALUES
    -- More 50+ Male Recurve competitors
    ('Frank Wilson', 1968,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'R'),
     0),
     
    ('Mark Thompson', 1971,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'R'),
     0),
     
    -- More U14 Male Compound competitors  
    ('Ethan Brown', 2013,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'C'),
     0),
     
    ('Lucas Davis', 2014,
     (SELECT id FROM gender WHERE gender_code = 'M'),
     (SELECT id FROM division WHERE bow_type_code = 'C'),
     0);

-- Create sessions for new members
INSERT INTO session (member_id, round_id, division_id, shoot_date, status) VALUES
    ((SELECT id FROM club_member WHERE full_name = 'Frank Wilson'), @short_can_round_id,
     (SELECT division_id FROM club_member WHERE full_name = 'Frank Wilson'), '2025-09-15', 'Confirmed'),
     
    ((SELECT id FROM club_member WHERE full_name = 'Mark Thompson'), @short_can_round_id,
     (SELECT division_id FROM club_member WHERE full_name = 'Mark Thompson'), '2025-09-15', 'Confirmed'),
     
    ((SELECT id FROM club_member WHERE full_name = 'Ethan Brown'), @short_can_round_id,
     (SELECT division_id FROM club_member WHERE full_name = 'Ethan Brown'), '2025-09-15', 'Confirmed'),
     
    ((SELECT id FROM club_member WHERE full_name = 'Lucas Davis'), @short_can_round_id,
     (SELECT division_id FROM club_member WHERE full_name = 'Lucas Davis'), '2025-09-15', 'Confirmed');

-- Add competition entries for new members
INSERT INTO competition_entry (session_id, competition_id, category_id, final_total, rank_in_category) VALUES
    -- 50+ Male Recurve: Robert (410-1st), Frank (400-2nd), Thomas (395-3rd), Mark (385-4th)
    ((SELECT s.id FROM session s 
      JOIN club_member cm ON s.member_id = cm.id 
      WHERE cm.full_name = 'Frank Wilson' AND s.round_id = @short_can_round_id AND s.shoot_date = '2025-09-15'), 
     @autumn_comp_id,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.full_name = 'Frank Wilson'
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = '50+' AND g.id = cm.gender_id AND d.id = cm.division_id),
     400, 2),
     
    ((SELECT s.id FROM session s 
      JOIN club_member cm ON s.member_id = cm.id 
      WHERE cm.full_name = 'Mark Thompson' AND s.round_id = @short_can_round_id AND s.shoot_date = '2025-09-15'), 
     @autumn_comp_id,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.full_name = 'Mark Thompson'
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = '50+' AND g.id = cm.gender_id AND d.id = cm.division_id),
     385, 4),
     
    -- U14 Male Compound: Jake (385-1st), Ethan (375-2nd), Lucas (360-3rd)
    ((SELECT s.id FROM session s 
      JOIN club_member cm ON s.member_id = cm.id 
      WHERE cm.full_name = 'Ethan Brown' AND s.round_id = @short_can_round_id AND s.shoot_date = '2025-09-15'), 
     @autumn_comp_id,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.full_name = 'Ethan Brown'
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'U14' AND g.id = cm.gender_id AND d.id = cm.division_id),
     375, 2),
     
    ((SELECT s.id FROM session s 
      JOIN club_member cm ON s.member_id = cm.id 
      WHERE cm.full_name = 'Lucas Davis' AND s.round_id = @short_can_round_id AND s.shoot_date = '2025-09-15'), 
     @autumn_comp_id,
     (SELECT c.id FROM category c 
      JOIN club_member cm ON cm.full_name = 'Lucas Davis'
      JOIN age_class ac ON c.age_class_id = ac.id 
      JOIN gender g ON c.gender_id = g.id 
      JOIN division d ON c.division_id = d.id
      WHERE ac.age_class_code = 'U14' AND g.id = cm.gender_id AND d.id = cm.division_id),
     360, 3);

-- =====================================================
-- 4. UPDATE EXISTING RANKINGS TO REFLECT NEW COMPETITORS
-- =====================================================

-- Update Thomas Anderson's rank (was 2nd, now 3rd after Frank Wilson)
UPDATE competition_entry SET rank_in_category = 3 WHERE
    session_id = (SELECT s.id FROM session s 
                  JOIN club_member cm ON s.member_id = cm.id 
                  WHERE cm.full_name = 'Thomas Anderson' AND s.round_id = @short_can_round_id AND s.shoot_date = '2025-09-15')
    AND competition_id = @autumn_comp_id;

-- =====================================================
-- VERIFICATION QUERY
-- Run this to see the updated competition results
-- =====================================================
SELECT 
    ce.rank_in_category AS 'Rank',
    m.full_name AS 'Archer',
    CONCAT(ac.age_class_code, ' ', g.gender_code, ' ', d.bow_type_code) AS 'Category',
    ce.final_total AS 'Score'
FROM competition_entry ce
JOIN session s ON s.id = ce.session_id
JOIN club_member m ON m.id = s.member_id
JOIN category cat ON cat.id = ce.category_id
JOIN age_class ac ON ac.id = cat.age_class_id
JOIN gender g ON g.id = cat.gender_id
JOIN division d ON d.id = cat.division_id
WHERE ce.competition_id = @autumn_comp_id
ORDER BY CONCAT(ac.age_class_code, ' ', g.gender_code, ' ', d.bow_type_code), ce.rank_in_category;