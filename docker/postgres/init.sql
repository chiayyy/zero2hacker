-- Initialize Zero2Hacker CTF Database

-- Create database if not exists
CREATE DATABASE zero2hacker_ctf;

-- Connect to the database
\c zero2hacker_ctf;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create default categories
INSERT INTO categories (name, slug, description, icon, color, is_active, sort_order) VALUES
('Web Security', 'web-security', 'Web application security challenges including XSS, SQL injection, and more', '🌐', '#3B82F6', true, 1),
('Cryptography', 'cryptography', 'Challenges involving encryption, hashing, and cryptanalysis', '🔐', '#8B5CF6', true, 2),
('Network Security', 'network-security', 'Network analysis, packet inspection, and protocol exploitation', '🌐', '#10B981', true, 3),
('Steganography', 'steganography', 'Hidden information in images, audio, and other media', '🖼️', '#F59E0B', true, 4),
('Forensics', 'forensics', 'Digital forensics and investigation challenges', '🔍', '#EF4444', true, 5),
('Reverse Engineering', 'reverse-engineering', 'Binary analysis and code reversing challenges', '⚙️', '#6B7280', true, 6),
('Pwning', 'pwning', 'Binary exploitation and buffer overflow challenges', '💥', '#DC2626', true, 7),
('Miscellaneous', 'miscellaneous', 'Various other security challenges and puzzles', '❓', '#64748B', true, 8)
ON CONFLICT (slug) DO NOTHING;

-- Create sample challenges
INSERT INTO challenges (title, slug, description, short_description, category_id, difficulty, points, flag, hints, status) VALUES
('First Steps', 'first-steps', 'Welcome to Zero2Hacker! This is your first challenge to get familiar with the platform.', 'A simple introduction challenge', 1, 'beginner', 10, 'flag{welcome_to_zero2hacker}', '["Look at the page source", "The flag is right in front of you"]', 'active'),
('Basic SQL Injection', 'basic-sql-injection', 'Find and exploit a SQL injection vulnerability in this web application.', 'Classic SQL injection challenge', 1, 'easy', 50, 'flag{sql_injection_basics}', '["Try common SQL injection payloads", "Look for error messages"]', 'active'),
('Caesar Cipher', 'caesar-cipher', 'Decrypt this message that has been encoded with a Caesar cipher.', 'Classical cryptography challenge', 2, 'beginner', 25, 'flag{ancient_crypto}', '["This is a simple substitution cipher", "Try different shift values"]', 'active'),
('Hidden Message', 'hidden-message', 'There''s a secret message hidden in this image. Can you find it?', 'Basic steganography challenge', 4, 'easy', 40, 'flag{hidden_in_plain_sight}', '["Use steganography tools", "Check the LSB of the image"]', 'active')
ON CONFLICT (slug) DO NOTHING;

-- Create admin user (password should be changed in production)
INSERT INTO users (firebase_uid, email, username, display_name, role, skill_level, is_active, is_verified) VALUES
('admin_firebase_uid', 'admin@zero2hacker.com', 'admin', 'System Administrator', 'admin', 'expert', true, true)
ON CONFLICT (firebase_uid) DO NOTHING;