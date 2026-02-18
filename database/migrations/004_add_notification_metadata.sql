"""
Add metadata column to notifications table
"""

ALTER TABLE notifications ADD COLUMN metadata TEXT AFTER link_url;
