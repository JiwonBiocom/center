-- Auto-generated schema fix SQL
-- Generated at: 2025-08-17T03:53:11.429660
-- Run this in Supabase SQL Editor

ALTER TABLE notifications ADD COLUMN IF NOT EXISTS user_id INTEGER;
UPDATE notifications SET user_id = 1 WHERE user_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);

-- Verification queries
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'notifications' AND column_name = 'user_id';
SELECT COUNT(*) as notifications_with_user_id FROM notifications WHERE user_id IS NOT NULL;
