🔧 Quick Schema Fix SQL Generator
==================================================

📝 Generated SQL Commands:

ALTER TABLE notifications ADD COLUMN IF NOT EXISTS user_id INTEGER;
UPDATE notifications SET user_id = 1 WHERE user_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);

✅ SQL saved to: schema_fix_20250820_033816.sql

📋 Next steps:
1. Copy the SQL above
2. Go to Supabase SQL Editor
3. Paste and execute
4. Verify the changes

::set-output name=sql_file::schema_fix_20250820_033816.sql
::set-output name=sql_content::-- Auto-generated schema fix SQL
-- Generated at: 2025-08-20T03:38:16.292347
-- Run this in Supabase SQL Editor

ALTER TABLE notifications ADD COLUMN IF NOT EXISTS user_id INTEGER;
UPDATE notifications SET user_id = 1 WHERE user_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);

-- Verification queries
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'notifications' AND column_name = 'user_id';
SELECT COUNT(*) as notifications_with_user_id FROM notifications WHERE user_id IS NOT NULL;

