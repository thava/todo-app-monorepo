-- Migration: Prepare schema for OAuth support
-- Rename email to local_username and password_hash_primary to local_password_hash
-- Add OAuth provider fields (Google, Microsoft)
-- Add contact_email for future use

-- Step 1: Add new columns
ALTER TABLE users ADD COLUMN contact_email VARCHAR(255);
ALTER TABLE users ADD COLUMN google_sub VARCHAR(255);
ALTER TABLE users ADD COLUMN google_email VARCHAR(255);
ALTER TABLE users ADD COLUMN ms_oid UUID;
ALTER TABLE users ADD COLUMN ms_tid UUID;
ALTER TABLE users ADD COLUMN ms_email VARCHAR(255);
ALTER TABLE users ADD COLUMN local_enabled BOOLEAN DEFAULT false NOT NULL;
ALTER TABLE users ADD COLUMN local_username VARCHAR(255);
ALTER TABLE users ADD COLUMN local_password_hash TEXT;

-- Step 2: Migrate existing data (email -> local_username, password_hash_primary -> local_password_hash)
UPDATE users SET local_username = email;
UPDATE users SET local_password_hash = password_hash_primary;
UPDATE users SET local_enabled = true;

-- Step 3: Drop old columns and constraints
ALTER TABLE users DROP CONSTRAINT users_email_unique;
ALTER TABLE users DROP COLUMN email;
ALTER TABLE users DROP COLUMN password_hash_primary;

-- Step 4: Add unique constraints
ALTER TABLE users ADD CONSTRAINT users_google_sub_unique UNIQUE(google_sub);
ALTER TABLE users ADD CONSTRAINT users_local_username_unique UNIQUE(local_username);

-- Step 5: Add unique constraint for Microsoft identity (ms_tid, ms_oid) combination
ALTER TABLE users ADD CONSTRAINT users_ms_identity_unique UNIQUE(ms_tid, ms_oid);

-- Step 6: Update indexes
DROP INDEX IF EXISTS idx_users_email;
CREATE INDEX idx_users_local_username ON users(local_username);
CREATE INDEX idx_users_google_sub ON users(google_sub);
CREATE INDEX idx_users_ms_identity ON users(ms_tid, ms_oid);
