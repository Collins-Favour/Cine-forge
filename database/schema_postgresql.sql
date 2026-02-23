-- ============================================================================
-- CINEFORGE AI - Database Schema (PostgreSQL/Supabase)
-- PostgreSQL Database Schema for Script-to-Visual AI Platform
-- Created: November 13, 2025
-- Migrated to PostgreSQL: February 23, 2026
-- Author: Collins Ndege Mwangi
-- ============================================================================

-- Drop existing schema objects if they exist
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;

-- Create ENUM types for PostgreSQL
CREATE TYPE user_role AS ENUM ('student', 'filmmaker', 'professional', 'admin', 'investor', 'actor', 'crew_member');
CREATE TYPE production_stage AS ENUM ('concept', 'pre-production', 'production', 'post-production', 'completed');
CREATE TYPE collaborator_role AS ENUM ('owner', 'director', 'writer', 'editor', 'viewer');
CREATE TYPE invitation_status AS ENUM ('pending', 'accepted', 'declined');
CREATE TYPE character_role AS ENUM ('protagonist', 'antagonist', 'supporting', 'minor');
CREATE TYPE time_of_day AS ENUM ('dawn', 'day', 'dusk', 'night', 'golden-hour');
CREATE TYPE interior_exterior AS ENUM ('INT', 'EXT', 'INT/EXT');
CREATE TYPE pacing AS ENUM ('slow', 'medium', 'fast');
CREATE TYPE shot_type AS ENUM ('close-up', 'medium', 'wide', 'establishing', 'over-shoulder', 'pov');
CREATE TYPE generation_status AS ENUM ('pending', 'generating', 'completed', 'failed');
CREATE TYPE checklist_category AS ENUM ('props', 'wardrobe', 'location', 'cast', 'equipment', 'vfx', 'sound', 'other');
CREATE TYPE priority_level AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE message_type AS ENUM ('text', 'annotation', 'feedback', 'approval', 'file');
CREATE TYPE ai_operation AS ENUM ('script_analysis', 'scene_breakdown', 'image_generation', 'mood_suggestion', 'location_suggestion', 'auto_script_generation', 'storyboard_image_generation', 'mood_board_generation');
CREATE TYPE processing_status AS ENUM ('pending', 'processing', 'completed', 'failed');
CREATE TYPE notification_type AS ENUM ('collaboration_invite', 'message', 'task_assigned', 'generation_complete', 'mention', 'system');
CREATE TYPE export_type AS ENUM ('storyboard_pdf', 'script_pdf', 'checklist_pdf', 'full_package');
CREATE TYPE setting_type AS ENUM ('string', 'number', 'boolean', 'json');

-- ============================================================================
-- FUNCTION: Update updated_at timestamp automatically
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ============================================================================
-- USER MANAGEMENT & AUTHENTICATION
-- ============================================================================

-- Users table - Core user accounts
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    profile_pic_url TEXT, -- Stores base64-encoded profile picture
    bio TEXT,
    phone VARCHAR(20),
    location VARCHAR(255),
    role user_role DEFAULT 'filmmaker',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    reset_token VARCHAR(255),
    reset_token_expiry TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_is_active ON users(is_active);

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- User sessions for authentication tracking
CREATE TABLE user_sessions (
    session_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);

-- ============================================================================
-- PROJECT MANAGEMENT
-- ============================================================================

-- Projects table - Main film projects
CREATE TABLE projects (
    project_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    logline TEXT,
    synopsis TEXT,
    genre VARCHAR(100),
    target_length INTEGER, -- Target film length in minutes
    budget_range VARCHAR(50),
    production_stage production_stage DEFAULT 'concept',
    created_by INTEGER NOT NULL,
    thumbnail_url TEXT, -- Stores base64-encoded project thumbnail
    is_public BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_projects_created_by ON projects(created_by);
CREATE INDEX idx_projects_genre ON projects(genre);
CREATE INDEX idx_projects_stage ON projects(production_stage);
CREATE INDEX idx_projects_archived ON projects(is_archived);

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Project collaborators - Team members and roles
CREATE TABLE project_collaborators (
    collaboration_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role collaborator_role NOT NULL DEFAULT 'viewer',
    permissions JSONB, -- Custom permissions: {"can_edit": true, "can_delete": false, "can_invite": true}
    invited_by INTEGER,
    invitation_status invitation_status DEFAULT 'accepted',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (invited_by) REFERENCES users(user_id) ON DELETE SET NULL,
    UNIQUE (project_id, user_id)
);

CREATE INDEX idx_collaborators_project ON project_collaborators(project_id);
CREATE INDEX idx_collaborators_user ON project_collaborators(user_id);

-- ============================================================================
-- SCRIPT MANAGEMENT
-- ============================================================================

-- Script versions - Version control for scripts
CREATE TABLE script_versions (
    version_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    script_content TEXT NOT NULL,
    version_number INTEGER NOT NULL DEFAULT 1,
    version_name VARCHAR(100),
    word_count INTEGER,
    page_count INTEGER,
    estimated_runtime INTEGER, -- Estimated runtime in minutes
    changes_summary TEXT,
    created_by INTEGER NOT NULL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_versions_project ON script_versions(project_id);
CREATE INDEX idx_versions_number ON script_versions(version_number);

-- Characters - Extracted from script analysis
CREATE TABLE characters (
    character_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    character_name VARCHAR(255) NOT NULL,
    description TEXT,
    role_type character_role DEFAULT 'supporting',
    age_range VARCHAR(50),
    gender VARCHAR(50),
    personality_traits JSONB,
    dialogue_count INTEGER DEFAULT 0,
    first_appearance INTEGER, -- Scene number of first appearance
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

CREATE INDEX idx_characters_project ON characters(project_id);
CREATE INDEX idx_characters_name ON characters(character_name);

CREATE TRIGGER update_characters_updated_at BEFORE UPDATE ON characters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SCENE MANAGEMENT
-- ============================================================================

-- Scenes - Scene breakdown and analysis
CREATE TABLE scenes (
    scene_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    scene_number INTEGER NOT NULL,
    slug VARCHAR(255), -- Scene heading/slug line
    description TEXT,
    location VARCHAR(255),
    time_of_day time_of_day DEFAULT 'day',
    interior_exterior interior_exterior DEFAULT 'INT',
    page_length DECIMAL(4,2), -- Scene length in pages
    estimated_duration INTEGER, -- Estimated duration in seconds
    narrative_purpose TEXT,
    emotional_tone VARCHAR(100),
    pacing pacing DEFAULT 'medium',
    
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

CREATE INDEX idx_scenes_project ON scenes(project_id);
CREATE INDEX idx_scenes_number ON scenes(scene_number);
CREATE INDEX idx_scenes_location ON scenes(location);

CREATE TRIGGER update_scenes_updated_at BEFORE UPDATE ON scenes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Scene characters - Character appearances in scenes
CREATE TABLE scene_characters (
    scene_character_id SERIAL PRIMARY KEY,
    scene_id INTEGER NOT NULL,
    character_id INTEGER NOT NULL,
    dialogue_lines INTEGER DEFAULT 0,
    is_main_focus BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (scene_id) REFERENCES scenes(scene_id) ON DELETE CASCADE,
    FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE,
    UNIQUE (scene_id, character_id)
);

CREATE INDEX idx_scene_chars_scene ON scene_characters(scene_id);
CREATE INDEX idx_scene_chars_character ON scene_characters(character_id);

-- ============================================================================
-- STORYBOARD & VISUAL GENERATION
-- ============================================================================

-- Storyboard panels - AI-generated visual panels
CREATE TABLE storyboard_panels (
    panel_id SERIAL PRIMARY KEY,
    scene_id INTEGER NOT NULL,
    panel_number INTEGER NOT NULL,
    
    -- Image generation prompts
    image_prompt TEXT NOT NULL,
    negative_prompt TEXT,
    style_reference VARCHAR(255), -- Art style: realistic, animated, sketch, etc.
    
    -- Generated images
    generated_image_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    manual_image_url VARCHAR(500), -- User-uploaded alternative
    
    -- Generation metadata
    ai_model_used VARCHAR(100), -- Stable Diffusion, DALL-E, Midjourney
    generation_settings JSONB, -- Model parameters used
    generation_timestamp TIMESTAMP,
    
    -- Panel details
    camera_angle VARCHAR(100),
    shot_type shot_type DEFAULT 'medium',
    movement VARCHAR(255), -- Pan, tilt, dolly, etc.
    notes TEXT,
    
    -- Status
    status generation_status DEFAULT 'pending',
    is_approved BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (scene_id) REFERENCES scenes(scene_id) ON DELETE CASCADE
);

CREATE INDEX idx_panels_scene ON storyboard_panels(scene_id);
CREATE INDEX idx_panels_number ON storyboard_panels(panel_number);
CREATE INDEX idx_panels_status ON storyboard_panels(status);

CREATE TRIGGER update_panels_updated_at BEFORE UPDATE ON storyboard_panels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Visual style references - Project-wide visual consistency
CREATE TABLE visual_styles (
    style_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    style_name VARCHAR(255) NOT NULL,
    description TEXT,
    reference_images JSONB, -- Array of reference image URLs
    color_palette JSONB, -- Hex color codes
    mood_keywords JSONB, -- Keywords for AI generation
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

CREATE INDEX idx_styles_project ON visual_styles(project_id);

-- ============================================================================
-- PRODUCTION CHECKLISTS & TASKS
-- ============================================================================

-- Checklist items - Scene-specific production tasks
CREATE TABLE checklist_items (
    item_id SERIAL PRIMARY KEY,
    scene_id INTEGER NOT NULL,
    category checklist_category NOT NULL,
    item_text VARCHAR(500) NOT NULL,
    description TEXT,
    priority priority_level DEFAULT 'medium',
    is_completed BOOLEAN DEFAULT FALSE,
    assigned_to INTEGER,
    due_date DATE,
    completed_at TIMESTAMP,
    completed_by INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scene_id) REFERENCES scenes(scene_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (completed_by) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX idx_checklist_scene ON checklist_items(scene_id);
CREATE INDEX idx_checklist_category ON checklist_items(category);
CREATE INDEX idx_checklist_completed ON checklist_items(is_completed);

CREATE TRIGGER update_checklist_updated_at BEFORE UPDATE ON checklist_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Budget items - Scene-specific budget tracking
CREATE TABLE budget_items (
    budget_item_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    scene_id INTEGER,
    category VARCHAR(100) NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    estimated_cost DECIMAL(10,2),
    actual_cost DECIMAL(10,2),
    currency VARCHAR(10) DEFAULT 'USD',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (scene_id) REFERENCES scenes(scene_id) ON DELETE SET NULL
);

CREATE INDEX idx_budget_project ON budget_items(project_id);
CREATE INDEX idx_budget_scene ON budget_items(scene_id);
CREATE INDEX idx_budget_category ON budget_items(category);

CREATE TRIGGER update_budget_updated_at BEFORE UPDATE ON budget_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- C-SPACE COLLABORATION
-- ============================================================================

-- C-Space messages - Real-time collaboration messages
CREATE TABLE cspace_messages (
    message_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    parent_message_id INTEGER, -- For threaded replies
    message_type message_type DEFAULT 'text',
    channel VARCHAR(50) DEFAULT 'general' NOT NULL, -- Channel name (general, production, creative, budget, etc.)
    message_content TEXT NOT NULL,
    
    -- Attachments and references
    attached_file_url VARCHAR(500),
    attached_thumbnail VARCHAR(500),
    referenced_scene_id INTEGER,
    referenced_panel_id INTEGER,
    
    -- Annotations for visual feedback
    annotation_data JSONB, -- Coordinates and markup data for image annotations
    
    -- Status
    is_resolved BOOLEAN DEFAULT FALSE,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMP,
    
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_message_id) REFERENCES cspace_messages(message_id) ON DELETE CASCADE,
    FOREIGN KEY (referenced_scene_id) REFERENCES scenes(scene_id) ON DELETE SET NULL,
    FOREIGN KEY (referenced_panel_id) REFERENCES storyboard_panels(panel_id) ON DELETE SET NULL
);

CREATE INDEX idx_messages_project ON cspace_messages(project_id);
CREATE INDEX idx_messages_user ON cspace_messages(user_id);
CREATE INDEX idx_messages_sent ON cspace_messages(sent_at);
CREATE INDEX idx_messages_channel ON cspace_messages(channel);

-- Message reactions - Emoji reactions to messages
CREATE TABLE message_reactions (
    reaction_id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    reaction_type VARCHAR(50) NOT NULL, -- emoji or reaction name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES cspace_messages(message_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE (message_id, user_id, reaction_type)
);

CREATE INDEX idx_reactions_message ON message_reactions(message_id);

-- ============================================================================
-- AI PROCESSING & ANALYTICS
-- ============================================================================

-- AI processing logs - Track AI operations
CREATE TABLE ai_processing_logs (
    log_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    operation_type ai_operation NOT NULL,
    input_data JSONB,
    output_data JSONB,
    ai_model VARCHAR(100), -- GPT-4, Gemini, Stable Diffusion, etc.
    processing_time_ms INTEGER,
    tokens_used INTEGER,
    cost_estimate DECIMAL(10,6),
    status processing_status DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_logs_project ON ai_processing_logs(project_id);
CREATE INDEX idx_logs_operation ON ai_processing_logs(operation_type);
CREATE INDEX idx_logs_created ON ai_processing_logs(created_at);

-- Usage analytics - Track feature usage
CREATE TABLE usage_analytics (
    analytics_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_analytics_user ON usage_analytics(user_id);
CREATE INDEX idx_analytics_event ON usage_analytics(event_type);
CREATE INDEX idx_analytics_created ON usage_analytics(created_at);

-- ============================================================================
-- NOTIFICATIONS & ACTIVITY
-- ============================================================================

-- Notifications - User notifications
CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    notification_type notification_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    link_url VARCHAR(500),
    action_data TEXT, -- JSON string for additional data
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);
CREATE INDEX idx_notifications_created ON notifications(created_at);

-- Activity log - Project activity tracking
CREATE TABLE activity_log (
    activity_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    activity_description TEXT,
    entity_type VARCHAR(50), -- scene, panel, message, etc.
    entity_id INTEGER,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_activity_project ON activity_log(project_id);
CREATE INDEX idx_activity_user ON activity_log(user_id);
CREATE INDEX idx_activity_created ON activity_log(created_at);

-- ============================================================================
-- FILE STORAGE & EXPORTS
-- ============================================================================

-- Project exports - Generated PDF/exports
CREATE TABLE project_exports (
    export_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    export_type export_type NOT NULL,
    file_url VARCHAR(500),
    file_size_kb INTEGER,
    generated_by INTEGER NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    download_count INTEGER DEFAULT 0,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (generated_by) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_exports_project ON project_exports(project_id);
CREATE INDEX idx_exports_type ON project_exports(export_type);

-- Uploaded files - User file uploads
CREATE TABLE uploaded_files (
    file_id SERIAL PRIMARY KEY,
    project_id INTEGER,
    user_id INTEGER NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(100),
    file_url VARCHAR(500) NOT NULL,
    file_size_kb INTEGER,
    upload_purpose VARCHAR(100), -- reference, storyboard, script, etc.
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_files_project ON uploaded_files(project_id);
CREATE INDEX idx_files_user ON uploaded_files(user_id);

-- ============================================================================
-- SYSTEM CONFIGURATION
-- ============================================================================

-- System settings - Application configuration
CREATE TABLE system_settings (
    setting_id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type setting_type DEFAULT 'string',
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE, -- Can be accessed by frontend
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_settings_updated_at BEFORE UPDATE ON system_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

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
-- ROW LEVEL SECURITY (RLS) - Optional for Supabase
-- ============================================================================
-- Uncomment these if using Supabase with RLS enabled

-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE project_collaborators ENABLE ROW LEVEL SECURITY;
-- etc...

-- Create policies for accessing data
-- Example: Users can only update their own profile
-- CREATE POLICY users_update_own ON users FOR UPDATE
--     USING (auth.uid()::text = user_id::text);

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
