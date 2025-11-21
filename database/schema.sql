-- ============================================================================
-- CINEFORGE AI - Database Schema
-- MySQL Database Schema for Script-to-Visual AI Platform
-- Created: November 13, 2025
-- Author: Collins Ndege Mwangi
-- ============================================================================

-- Drop existing database if exists and create fresh
DROP DATABASE IF EXISTS cineforge_ai;
CREATE DATABASE cineforge_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cineforge_ai;

-- ============================================================================
-- USER MANAGEMENT & AUTHENTICATION
-- ============================================================================

-- Users table - Core user accounts
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    profile_pic_url VARCHAR(500),
    bio TEXT,
    role ENUM('student', 'filmmaker', 'professional', 'admin') DEFAULT 'filmmaker',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    reset_token VARCHAR(255),
    reset_token_expiry DATETIME,
    last_login DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB;

-- User sessions for authentication tracking
CREATE TABLE user_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_session_token (session_token),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB;

-- ============================================================================
-- PROJECT MANAGEMENT
-- ============================================================================

-- Projects table - Main film projects
CREATE TABLE projects (
    project_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    logline TEXT,
    synopsis TEXT,
    genre VARCHAR(100),
    target_length INT COMMENT 'Target film length in minutes',
    budget_range VARCHAR(50),
    production_stage ENUM('concept', 'pre-production', 'production', 'post-production', 'completed') DEFAULT 'concept',
    created_by INT NOT NULL,
    thumbnail_url VARCHAR(500),
    is_public BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_created_by (created_by),
    INDEX idx_genre (genre),
    INDEX idx_production_stage (production_stage),
    INDEX idx_is_archived (is_archived)
) ENGINE=InnoDB;

-- Project collaborators - Team members and roles
CREATE TABLE project_collaborators (
    collaboration_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    user_id INT NOT NULL,
    role ENUM('owner', 'director', 'writer', 'editor', 'viewer') NOT NULL DEFAULT 'viewer',
    permissions JSON COMMENT 'Custom permissions: {"can_edit": true, "can_delete": false, "can_invite": true}',
    invited_by INT,
    invitation_status ENUM('pending', 'accepted', 'declined') DEFAULT 'accepted',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (invited_by) REFERENCES users(user_id) ON DELETE SET NULL,
    UNIQUE KEY unique_project_user (project_id, user_id),
    INDEX idx_project_id (project_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB;

-- ============================================================================
-- SCRIPT MANAGEMENT
-- ============================================================================

-- Script versions - Version control for scripts
CREATE TABLE script_versions (
    version_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    script_content LONGTEXT NOT NULL,
    version_number INT NOT NULL DEFAULT 1,
    version_name VARCHAR(100),
    word_count INT,
    page_count INT,
    estimated_runtime INT COMMENT 'Estimated runtime in minutes',
    changes_summary TEXT,
    created_by INT NOT NULL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_version_number (version_number)
) ENGINE=InnoDB;

-- Characters - Extracted from script analysis
CREATE TABLE characters (
    character_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    character_name VARCHAR(255) NOT NULL,
    description TEXT,
    role_type ENUM('protagonist', 'antagonist', 'supporting', 'minor') DEFAULT 'supporting',
    age_range VARCHAR(50),
    gender VARCHAR(50),
    personality_traits JSON,
    dialogue_count INT DEFAULT 0,
    first_appearance INT COMMENT 'Scene number of first appearance',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_character_name (character_name)
) ENGINE=InnoDB;

-- ============================================================================
-- SCENE MANAGEMENT
-- ============================================================================

-- Scenes - Scene breakdown and analysis
CREATE TABLE scenes (
    scene_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    scene_number INT NOT NULL,
    slug VARCHAR(255) COMMENT 'Scene heading/slug line',
    description TEXT,
    location VARCHAR(255),
    time_of_day ENUM('dawn', 'day', 'dusk', 'night', 'golden-hour') DEFAULT 'day',
    interior_exterior ENUM('INT', 'EXT', 'INT/EXT') DEFAULT 'INT',
    page_length DECIMAL(4,2) COMMENT 'Scene length in pages',
    estimated_duration INT COMMENT 'Estimated duration in seconds',
    narrative_purpose TEXT,
    emotional_tone VARCHAR(100),
    pacing ENUM('slow', 'medium', 'fast') DEFAULT 'medium',
    
    -- AI-generated suggestions
    location_suggestion TEXT,
    mood_suggestion TEXT,
    lighting_suggestion TEXT,
    cinematography_notes TEXT,
    sound_design_notes TEXT,
    
    -- Metadata
    is_action_scene BOOLEAN DEFAULT FALSE,
    is_dialogue_heavy BOOLEAN DEFAULT FALSE,
    vfx_required BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_scene_number (scene_number),
    INDEX idx_location (location)
) ENGINE=InnoDB;

-- Scene characters - Character appearances in scenes
CREATE TABLE scene_characters (
    scene_character_id INT AUTO_INCREMENT PRIMARY KEY,
    scene_id INT NOT NULL,
    character_id INT NOT NULL,
    dialogue_lines INT DEFAULT 0,
    is_main_focus BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (scene_id) REFERENCES scenes(scene_id) ON DELETE CASCADE,
    FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE,
    UNIQUE KEY unique_scene_character (scene_id, character_id),
    INDEX idx_scene_id (scene_id),
    INDEX idx_character_id (character_id)
) ENGINE=InnoDB;

-- ============================================================================
-- STORYBOARD & VISUAL GENERATION
-- ============================================================================

-- Storyboard panels - AI-generated visual panels
CREATE TABLE storyboard_panels (
    panel_id INT AUTO_INCREMENT PRIMARY KEY,
    scene_id INT NOT NULL,
    panel_number INT NOT NULL,
    
    -- Image generation prompts
    image_prompt TEXT NOT NULL,
    negative_prompt TEXT,
    style_reference VARCHAR(255) COMMENT 'Art style: realistic, animated, sketch, etc.',
    
    -- Generated images
    generated_image_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    manual_image_url VARCHAR(500) COMMENT 'User-uploaded alternative',
    
    -- Generation metadata
    ai_model_used VARCHAR(100) COMMENT 'Stable Diffusion, DALL-E, Midjourney',
    generation_settings JSON COMMENT 'Model parameters used',
    generation_timestamp DATETIME,
    
    -- Panel details
    camera_angle VARCHAR(100),
    shot_type ENUM('close-up', 'medium', 'wide', 'establishing', 'over-shoulder', 'pov') DEFAULT 'medium',
    movement VARCHAR(255) COMMENT 'Pan, tilt, dolly, etc.',
    notes TEXT,
    
    -- Status
    status ENUM('pending', 'generating', 'completed', 'failed') DEFAULT 'pending',
    is_approved BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (scene_id) REFERENCES scenes(scene_id) ON DELETE CASCADE,
    INDEX idx_scene_id (scene_id),
    INDEX idx_panel_number (panel_number),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- Visual style references - Project-wide visual consistency
CREATE TABLE visual_styles (
    style_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    style_name VARCHAR(255) NOT NULL,
    description TEXT,
    reference_images JSON COMMENT 'Array of reference image URLs',
    color_palette JSON COMMENT 'Hex color codes',
    mood_keywords JSON COMMENT 'Keywords for AI generation',
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id)
) ENGINE=InnoDB;

-- ============================================================================
-- PRODUCTION CHECKLISTS & TASKS
-- ============================================================================

-- Checklist items - Scene-specific production tasks
CREATE TABLE checklist_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    scene_id INT NOT NULL,
    category ENUM('props', 'wardrobe', 'location', 'cast', 'equipment', 'vfx', 'sound', 'other') NOT NULL,
    item_text VARCHAR(500) NOT NULL,
    description TEXT,
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    is_completed BOOLEAN DEFAULT FALSE,
    assigned_to INT,
    due_date DATE,
    completed_at DATETIME,
    completed_by INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (scene_id) REFERENCES scenes(scene_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (completed_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_scene_id (scene_id),
    INDEX idx_category (category),
    INDEX idx_is_completed (is_completed)
) ENGINE=InnoDB;

-- Budget items - Scene-specific budget tracking
CREATE TABLE budget_items (
    budget_item_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    scene_id INT,
    category VARCHAR(100) NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    estimated_cost DECIMAL(10,2),
    actual_cost DECIMAL(10,2),
    currency VARCHAR(10) DEFAULT 'USD',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (scene_id) REFERENCES scenes(scene_id) ON DELETE SET NULL,
    INDEX idx_project_id (project_id),
    INDEX idx_scene_id (scene_id),
    INDEX idx_category (category)
) ENGINE=InnoDB;

-- ============================================================================
-- C-SPACE COLLABORATION
-- ============================================================================

-- C-Space messages - Real-time collaboration messages
CREATE TABLE cspace_messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    user_id INT NOT NULL,
    parent_message_id INT COMMENT 'For threaded replies',
    message_type ENUM('text', 'annotation', 'feedback', 'approval', 'file') DEFAULT 'text',
    message_content TEXT NOT NULL,
    
    -- Attachments and references
    attached_file_url VARCHAR(500),
    attached_thumbnail VARCHAR(500),
    referenced_scene_id INT,
    referenced_panel_id INT,
    
    -- Annotations for visual feedback
    annotation_data JSON COMMENT 'Coordinates and markup data for image annotations',
    
    -- Status
    is_resolved BOOLEAN DEFAULT FALSE,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_edited BOOLEAN DEFAULT FALSE,
    edited_at DATETIME,
    
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_message_id) REFERENCES cspace_messages(message_id) ON DELETE CASCADE,
    FOREIGN KEY (referenced_scene_id) REFERENCES scenes(scene_id) ON DELETE SET NULL,
    FOREIGN KEY (referenced_panel_id) REFERENCES storyboard_panels(panel_id) ON DELETE SET NULL,
    INDEX idx_project_id (project_id),
    INDEX idx_user_id (user_id),
    INDEX idx_sent_at (sent_at)
) ENGINE=InnoDB;

-- Message reactions - Emoji reactions to messages
CREATE TABLE message_reactions (
    reaction_id INT AUTO_INCREMENT PRIMARY KEY,
    message_id INT NOT NULL,
    user_id INT NOT NULL,
    reaction_type VARCHAR(50) NOT NULL COMMENT 'emoji or reaction name',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES cspace_messages(message_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_message_user_reaction (message_id, user_id, reaction_type),
    INDEX idx_message_id (message_id)
) ENGINE=InnoDB;

-- ============================================================================
-- AI PROCESSING & ANALYTICS
-- ============================================================================

-- AI processing logs - Track AI operations
CREATE TABLE ai_processing_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    user_id INT NOT NULL,
    operation_type ENUM('script_analysis', 'scene_breakdown', 'image_generation', 'mood_suggestion', 'location_suggestion') NOT NULL,
    input_data JSON,
    output_data JSON,
    ai_model VARCHAR(100) COMMENT 'GPT-4, Gemini, Stable Diffusion, etc.',
    processing_time_ms INT,
    tokens_used INT,
    cost_estimate DECIMAL(10,6),
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_operation_type (operation_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;

-- Usage analytics - Track feature usage
CREATE TABLE usage_analytics (
    analytics_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_event_type (event_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;

-- ============================================================================
-- NOTIFICATIONS & ACTIVITY
-- ============================================================================

-- Notifications - User notifications
CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    notification_type ENUM('collaboration_invite', 'message', 'task_assigned', 'generation_complete', 'mention', 'system') NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    link_url VARCHAR(500),
    is_read BOOLEAN DEFAULT FALSE,
    read_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;

-- Activity log - Project activity tracking
CREATE TABLE activity_log (
    activity_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    user_id INT NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    activity_description TEXT,
    entity_type VARCHAR(50) COMMENT 'scene, panel, message, etc.',
    entity_id INT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;

-- ============================================================================
-- FILE STORAGE & EXPORTS
-- ============================================================================

-- Project exports - Generated PDF/exports
CREATE TABLE project_exports (
    export_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    export_type ENUM('storyboard_pdf', 'script_pdf', 'checklist_pdf', 'full_package') NOT NULL,
    file_url VARCHAR(500),
    file_size_kb INT,
    generated_by INT NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    download_count INT DEFAULT 0,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (generated_by) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_export_type (export_type)
) ENGINE=InnoDB;

-- Uploaded files - User file uploads
CREATE TABLE uploaded_files (
    file_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT,
    user_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(100),
    file_url VARCHAR(500) NOT NULL,
    file_size_kb INT,
    upload_purpose VARCHAR(100) COMMENT 'reference, storyboard, script, etc.',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB;

-- ============================================================================
-- SYSTEM CONFIGURATION
-- ============================================================================

-- System settings - Application configuration
CREATE TABLE system_settings (
    setting_id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE COMMENT 'Can be accessed by frontend',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================================
-- DEFAULT SYSTEM DATA
-- ============================================================================

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, description, is_public) VALUES
('max_free_projects', '3', 'number', 'Maximum number of free projects per user', TRUE),
('max_scenes_per_project', '100', 'number', 'Maximum scenes allowed per project', TRUE),
('max_panels_per_scene', '10', 'number', 'Maximum storyboard panels per scene', TRUE),
('ai_generation_timeout', '60', 'number', 'AI generation timeout in seconds', FALSE),
('max_file_upload_mb', '50', 'number', 'Maximum file upload size in MB', TRUE),
('maintenance_mode', 'false', 'boolean', 'Enable maintenance mode', TRUE),
('app_version', '1.0.0', 'string', 'Current application version', TRUE);

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
