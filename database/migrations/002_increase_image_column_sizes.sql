-- ============================================================================
-- Migration: Increase image column sizes for base64 storage
-- Date: 2025-11-28
-- Description: Change profile_pic_url and thumbnail_url from VARCHAR(500) to LONGTEXT
--              to support base64-encoded images (which can be very large)
-- ============================================================================

USE cineforge_ai;

-- Increase profile_pic_url column size in users table
ALTER TABLE users 
MODIFY COLUMN profile_pic_url LONGTEXT;

-- Increase thumbnail_url column size in projects table
ALTER TABLE projects 
MODIFY COLUMN thumbnail_url LONGTEXT;

-- Verify changes
SELECT 
    'users' as table_name,
    COLUMN_NAME, 
    DATA_TYPE, 
    CHARACTER_MAXIMUM_LENGTH 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'cineforge_ai' 
AND TABLE_NAME = 'users' 
AND COLUMN_NAME = 'profile_pic_url'
UNION ALL
SELECT 
    'projects' as table_name,
    COLUMN_NAME, 
    DATA_TYPE, 
    CHARACTER_MAXIMUM_LENGTH 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'cineforge_ai' 
AND TABLE_NAME = 'projects' 
AND COLUMN_NAME = 'thumbnail_url';
