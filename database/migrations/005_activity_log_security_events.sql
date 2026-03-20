-- Migration: Make activity_log support system-level events (login, register, etc.)
-- Date: 2026-03-12
-- Description: Make project_id nullable and add ip_address column for security event tracking

-- Make project_id nullable for system-level events (login, register, logout)
ALTER TABLE activity_log MODIFY COLUMN project_id INT NULL;

-- Make user_id nullable for anonymous events (failed login with unknown email)
ALTER TABLE activity_log MODIFY COLUMN user_id INT NULL;

-- Add ip_address column for security tracking
ALTER TABLE activity_log ADD COLUMN ip_address VARCHAR(45) NULL AFTER activity_metadata;

-- Add index on activity_type for security stats queries
ALTER TABLE activity_log ADD INDEX idx_activity_type (activity_type);
