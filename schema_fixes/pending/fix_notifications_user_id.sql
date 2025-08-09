-- Auto-generated schema fix
-- Safe operation: ADD COLUMN
-- Generated: 2025-06-21

ALTER TABLE notifications ADD COLUMN IF NOT EXISTS user_id INTEGER;
UPDATE notifications SET user_id = 1 WHERE user_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);