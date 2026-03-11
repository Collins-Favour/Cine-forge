-- Performance Enhancement Indexes Migration
-- This migration adds indexes to improve query performance

-- Add composite indexes for frequently joined queries
CREATE INDEX IF NOT EXISTS idx_project_collaborators_user_status 
    ON project_collaborators(user_id, invitation_status);

CREATE INDEX IF NOT EXISTS idx_scenes_project_number 
    ON scenes(project_id, scene_number);

CREATE INDEX IF NOT EXISTS idx_storyboard_panels_scene 
    ON storyboard_panels(scene_id, panel_number);

CREATE INDEX IF NOT EXISTS idx_activity_log_project_created 
    ON activity_log(project_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_script_versions_project_version 
    ON script_versions(project_id, version_number DESC);

CREATE INDEX IF NOT EXISTS idx_characters_project 
    ON characters(project_id);

CREATE INDEX IF NOT EXISTS idx_checklist_items_scene 
    ON checklist_items(scene_id);

CREATE INDEX IF NOT EXISTS idx_notifications_user_read 
    ON notifications(user_id, is_read, created_at DESC);

-- Add indexes for search operations
CREATE INDEX IF NOT EXISTS idx_projects_genre 
    ON projects(genre) WHERE is_archived = false;

CREATE INDEX IF NOT EXISTS idx_scenes_location 
    ON scenes(location) WHERE location IS NOT NULL;

-- Add covering indexes for stats queries
CREATE INDEX IF NOT EXISTS idx_scenes_count 
    ON scenes(project_id) INCLUDE (scene_id);

CREATE INDEX IF NOT EXISTS idx_characters_count 
    ON characters(project_id) INCLUDE (character_id);

-- Update statistics for query optimizer
ANALYZE projects;
ANALYZE scenes;
ANALYZE project_collaborators;
ANALYZE storyboard_panels;
ANALYZE characters;
ANALYZE script_versions;
