-- Migration: Add new AI operation types to enum
-- Date: 2026-02-23
-- Description: Adds auto_script_generation, storyboard_image_generation, and mood_board_generation to ai_operation enum

-- Add new enum values for AI operations
ALTER TYPE ai_operation ADD VALUE IF NOT EXISTS 'auto_script_generation';
ALTER TYPE ai_operation ADD VALUE IF NOT EXISTS 'storyboard_image_generation';
ALTER TYPE ai_operation ADD VALUE IF NOT EXISTS 'mood_board_generation';

-- Verify the enum values
-- SELECT unnest(enum_range(NULL::ai_operation));
