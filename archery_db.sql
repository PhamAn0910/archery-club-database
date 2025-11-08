-- -----------------------------------------------------
-- Archery Score Recording Database DDL Script
-- Scope: Outdoor Target Archery Discipline in 1 Archery Club
-- Course: COS20031 - Database Design Project
-- Group 2: Powerpuff Girls (Dung, Trang, and Que An)
-- -----------------------------------------------------

-- -----------------------------------------------------
-- 0. Create / Select archery_db schema
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS archery_db;
CREATE SCHEMA archery_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE archery_db;

-- -----------------------------------------------------
-- 1. Table: gender
-- Stores the gender options (M/F).
-- -----------------------------------------------------
CREATE TABLE gender (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gender_code ENUM('M', 'F') NOT NULL UNIQUE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 2. Table: division
-- Stores the equipment divisions (bow types).
-- -----------------------------------------------------
CREATE TABLE division (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bow_type_code ENUM('R', 'C', 'RB', 'CB', 'L', '') NOT NULL UNIQUE COMMENT 'R: Recurve, C: Compound, RB: Recurve Barebow, CB: Compound Barebow, L: Longbow',
    is_active BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 3. Table: age_class
-- Stores the age class definitions and their corresponding birth year policies.
-- -----------------------------------------------------
CREATE TABLE age_class (
    id INT AUTO_INCREMENT PRIMARY KEY,
    age_class_code VARCHAR(16) NOT NULL COMMENT 'e.g., U14, Open, 50+',
    min_birth_year YEAR NOT NULL,
    max_birth_year YEAR NOT NULL,
    policy_year YEAR NOT NULL COMMENT 'The year this age rule is valid for.',
    
    UNIQUE KEY uk_age_class_policy (age_class_code, policy_year)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 4. Table: round
-- Stores the definitions of named rounds (e.g., "WA 900", "Melbourne").
-- -----------------------------------------------------
CREATE TABLE round (
    id INT AUTO_INCREMENT PRIMARY KEY,
    round_name VARCHAR(64) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 5. Table: competition
-- Stores information about official club competitions.
-- -----------------------------------------------------
CREATE TABLE competition (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    rules_note TEXT NULL
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 6. Table: category
-- This is a junction table that defines a valid competition category 
-- by combining age, gender, and division.
-- -----------------------------------------------------
CREATE TABLE category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    age_class_id INT NOT NULL,
    gender_id INT NOT NULL,
    division_id INT NOT NULL,

    -- A category must be a unique combination of all three parts
    UNIQUE KEY uk_category_combination (age_class_id, gender_id, division_id),

    -- Foreign Key constraints
    CONSTRAINT fk_category_age_class
        FOREIGN KEY (age_class_id) 
        REFERENCES age_class(id) 
        ON DELETE RESTRICT,
    CONSTRAINT fk_category_gender
        FOREIGN KEY (gender_id) 
        REFERENCES gender(id) 
        ON DELETE RESTRICT,
    CONSTRAINT fk_category_division
        FOREIGN KEY (division_id) 
        REFERENCES division(id) 
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 7a. Table: club_member
-- Stores the archer and recorder details.
-- -----------------------------------------------------
CREATE TABLE club_member (
    id INT AUTO_INCREMENT PRIMARY KEY,
    av_number VARCHAR(16) UNIQUE,    -- e.g., 'VIC123', generated at database level (see below)
    full_name VARCHAR(100) NOT NULL,
    birth_year YEAR NOT NULL,
    gender_id INT NOT NULL,
    division_id INT NOT NULL,
    is_recorder BOOLEAN NOT NULL DEFAULT FALSE, -- role column: TRUE if recorder, FALSE if archer

    UNIQUE KEY uk_member_identity (full_name, birth_year, gender_id, division_id),

    -- Foreign Key constraints
    CONSTRAINT fk_member_gender
        FOREIGN KEY (gender_id) 
        REFERENCES gender(id) 
        ON DELETE RESTRICT,
    CONSTRAINT fk_member_division
        FOREIGN KEY (division_id) 
        REFERENCES division(id) 
        ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT = 100000;

-- -----------------------------------------------------
-- Function: generate_unique_av_number
-- Modular function to generate a unique AV number for club_member
-- -----------------------------------------------------
DELIMITER $$
CREATE FUNCTION generate_unique_av_number()
RETURNS VARCHAR(16)
DETERMINISTIC
BEGIN
    DECLARE new_av VARCHAR(16);
    DECLARE exists_count INT DEFAULT 1;
    WHILE exists_count > 0 DO
        SET new_av = CONCAT('VIC', LPAD(FLOOR(RAND() * 1000), 3, '0'));
        SELECT COUNT(*) INTO exists_count FROM club_member WHERE av_number = new_av;
    END WHILE;
    RETURN new_av;
END$$
DELIMITER ;

-- -----------------------------------------------------
-- Trigger: before_insert_club_member
-- Auto-generates AV number if not provided on insert
-- -----------------------------------------------------
DELIMITER $$
CREATE TRIGGER before_insert_club_member
BEFORE INSERT ON club_member
FOR EACH ROW
BEGIN
    IF NEW.av_number IS NULL OR NEW.av_number = '' THEN
        SET NEW.av_number = generate_unique_av_number();
    END IF;
END$$
DELIMITER ;

-- -----------------------------------------------------
-- 8. Table: round_range
-- Defines the components of a Round (e.g., Round "WA 900" 
-- is made of 3 ranges: 60m, 50m, 40m).
-- -----------------------------------------------------
CREATE TABLE round_range (
    id INT AUTO_INCREMENT PRIMARY KEY,
    round_id INT NOT NULL,
    distance_m SMALLINT NOT NULL COMMENT 'Distance in meters',
    face_size TINYINT NOT NULL COMMENT 'Target face size in cm (e.g., 80 or 122)',
    ends_per_range TINYINT NOT NULL COMMENT 'Number of ends in this range (e.g., 5 or 6)',
    
    -- A round cannot have duplicate ranges (e.g., two entries for 50m)
    UNIQUE KEY uk_round_distance (round_id, distance_m, face_size),

    -- Enforce business rules from the ERD
    CONSTRAINT chk_face_size CHECK (face_size IN (80, 122)),
    CONSTRAINT chk_ends_per_range CHECK (ends_per_range IN (5, 6)),

    -- Foreign Key constraint
    CONSTRAINT fk_round_range_round
        FOREIGN KEY (round_id) 
        REFERENCES round(id) 
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 9. Table: session
-- Represents a single shooting session (a "scoresheet") for an archer.
-- -----------------------------------------------------
CREATE TABLE session (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    round_id INT NOT NULL,
    shoot_date DATE NOT NULL,
    status ENUM('Preliminary', 'Final', 'Confirmed') NOT NULL DEFAULT 'Preliminary',

    -- Foreign Key constraints
    CONSTRAINT fk_session_member
        FOREIGN KEY (member_id) 
        REFERENCES club_member(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_session_round
        FOREIGN KEY (round_id) 
        REFERENCES round(id) 
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 10. Table: end
-- Represents one "end" (a set of 6 arrows) shot during a session.
-- We use backticks (`) for the table name `end` as it is a MySQL reserved keyword.
-- -----------------------------------------------------
CREATE TABLE `end` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    round_range_id INT NOT NULL COMMENT 'Links this end to a specific distance/face (e.g., the 50m range)',
    end_no TINYINT NOT NULL COMMENT 'The sequence number of this end (1-6)',
    
    -- An end must be unique for its session, range, and number
    UNIQUE KEY uk_session_range_end (session_id, round_range_id, end_no),

    -- Enforce business rule from the ERD
    CONSTRAINT chk_end_no CHECK (end_no BETWEEN 1 AND 6),

    -- Foreign Key constraints
    CONSTRAINT fk_end_session
        FOREIGN KEY (session_id) 
        REFERENCES session(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_end_round_range
        FOREIGN KEY (round_range_id) 
        REFERENCES round_range(id) 
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 11. Table: arrow
-- Stores a single arrow's value. This is a weak entity 
-- and depends on an `end` to exist.
-- -----------------------------------------------------
CREATE TABLE arrow (
    id INT AUTO_INCREMENT PRIMARY KEY,
    end_id INT NOT NULL,
    arrow_no TINYINT NOT NULL COMMENT 'The sequence number of this arrow (1-6)',
    arrow_value CHAR(2) NOT NULL COMMENT 'Score value: X, 10, 9...1, M',
    
    -- An arrow number must be unique within its end
    UNIQUE KEY uk_end_arrow (end_id, arrow_no),

    -- Enforce business rules from the ERD
    CONSTRAINT chk_arrow_no CHECK (arrow_no BETWEEN 1 AND 6),
    CONSTRAINT chk_arrow_value CHECK (arrow_value IN 
        ('X', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', 'M')
    ),

    -- Foreign Key constraint
    CONSTRAINT fk_arrow_end
        FOREIGN KEY (end_id) 
        REFERENCES `end`(id) 
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 12. Table: competition_entry
-- Links a single archer's session to an official competition,
-- assigns a category, and "freezes" the score.
-- -----------------------------------------------------
CREATE TABLE competition_entry (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    competition_id INT NOT NULL,
    category_id INT NOT NULL,
    final_total SMALLINT NULL COMMENT 'The "frozen" total score, copied from the session at time of confirmation.',
    rank_in_category TINYINT NULL COMMENT 'Final computed rank (1, 2, 3, etc.)',
    
    -- An archer's session can only be entered into a competition once
    UNIQUE KEY uk_competition_session (competition_id, session_id),

    -- Foreign Key constraints
    CONSTRAINT fk_competition_entry_session
        FOREIGN KEY (session_id) 
        REFERENCES session(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_competition_entry_competition
        FOREIGN KEY (competition_id) 
        REFERENCES competition(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_competition_entry_category
        FOREIGN KEY (category_id) 
        REFERENCES category(id) 
        ON DELETE RESTRICT
) ENGINE=InnoDB;