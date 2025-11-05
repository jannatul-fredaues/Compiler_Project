
-- Panic Mode Recovery Compiler Database Schema
CREATE DATABASE IF NOT EXISTS panicmode_compiler;
USE panicmode_compiler;


-- 2. Languages Table
CREATE TABLE IF NOT EXISTS languages (
    lang_id INT AUTO_INCREMENT PRIMARY KEY,
    lang_name VARCHAR(50) NOT NULL,
    file_extension VARCHAR(10),
    compiler_command VARCHAR(100)
);

-- 3. Codes Table
CREATE TABLE IF NOT EXISTS codes (
    code_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    lang_id INT,
    code_text TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (lang_id) REFERENCES languages(lang_id)
);

-- 4. Errors Table
CREATE TABLE IF NOT EXISTS errors (
    error_id INT AUTO_INCREMENT PRIMARY KEY,
    code_id INT,
    error_message TEXT,
    line_number INT,
    error_type VARCHAR(100),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (code_id) REFERENCES codes(code_id)
);

-- 5. Recovery Actions Table
CREATE TABLE IF NOT EXISTS recovery_actions (
    recovery_id INT AUTO_INCREMENT PRIMARY KEY,
    error_id INT,
    action_description TEXT,
    recovery_status ENUM('SUCCESS', 'FAILED', 'SKIPPED') DEFAULT 'SUCCESS',
    recovered_code TEXT,
    recovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (error_id) REFERENCES errors(error_id)
);

-- 6. Feedback Table
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Insert Default Languages
INSERT INTO languages (lang_name, file_extension, compiler_command) VALUES
('C', '.c', 'gcc'),
('C++', '.cpp', 'g++'),
('Python', '.py', 'python'),
('Java', '.java', 'javac');
