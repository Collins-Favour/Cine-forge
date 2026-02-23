-- ============================================================================
-- CINEFORGE AI - Schema Migration Fix
-- This script fixes the schema mismatch between database and backend models
-- Run this to sync the database with the current backend code
-- ============================================================================

USE cineforge_ai;

-- Add phone column to users table
ALTER TABLE users ADD COLUMN phone VARCHAR(20) AFTER bio;

-- Add location column to users table
ALTER TABLE users ADD COLUMN location VARCHAR(255) AFTER phone;

-- Update role ENUM to include all role types from the model
ALTER TABLE users MODIFY COLUMN role ENUM('student', 'filmmaker', 'professional', 'admin', 'investor', 'actor', 'crew_member') DEFAULT 'filmmaker';
