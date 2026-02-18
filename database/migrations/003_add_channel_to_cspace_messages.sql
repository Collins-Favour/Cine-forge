-- ============================================================================
-- Migration 003: Add channel column to cspace_messages table
-- Created: November 28, 2025
-- Description: Adds channel support for organizing messages in CSpace
-- ============================================================================

USE cineforge_ai;

-- Add channel column to cspace_messages
ALTER TABLE cspace_messages 
ADD COLUMN channel VARCHAR(50) DEFAULT 'general' NOT NULL 
COMMENT 'Channel name (general, production, creative, budget, etc.)'
AFTER message_type;

-- Add index for better query performance
CREATE INDEX idx_channel ON cspace_messages(channel);

-- Update existing messages to have 'general' channel
UPDATE cspace_messages SET channel = 'general' WHERE channel IS NULL OR channel = '';

SELECT 'Migration 003 completed successfully!' AS status;
