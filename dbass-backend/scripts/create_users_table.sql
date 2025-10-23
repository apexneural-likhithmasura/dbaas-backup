-- Create Users Table for Authentication
-- This script creates the users table in the trending_data schema

-- Create the users table
CREATE TABLE IF NOT EXISTS trending_data.users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(30) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    date_of_birth DATE,
    gender VARCHAR(20),
    country VARCHAR(100),
    receive_newsletters BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON trending_data.users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON trending_data.users(username);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON trending_data.users(is_active);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION trending_data.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON trending_data.users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON trending_data.users
    FOR EACH ROW
    EXECUTE FUNCTION trending_data.update_updated_at_column();

-- Add comments to the table and columns
COMMENT ON TABLE trending_data.users IS 'User accounts for authentication system';
COMMENT ON COLUMN trending_data.users.id IS 'Unique user identifier';
COMMENT ON COLUMN trending_data.users.first_name IS 'User first name';
COMMENT ON COLUMN trending_data.users.last_name IS 'User last name';
COMMENT ON COLUMN trending_data.users.email IS 'User email address (unique)';
COMMENT ON COLUMN trending_data.users.username IS 'User username (unique)';
COMMENT ON COLUMN trending_data.users.password_hash IS 'Hashed password with salt';
COMMENT ON COLUMN trending_data.users.phone_number IS 'User phone number';
COMMENT ON COLUMN trending_data.users.date_of_birth IS 'User date of birth';
COMMENT ON COLUMN trending_data.users.gender IS 'User gender';
COMMENT ON COLUMN trending_data.users.country IS 'User country';
COMMENT ON COLUMN trending_data.users.receive_newsletters IS 'Newsletter subscription preference';
COMMENT ON COLUMN trending_data.users.is_active IS 'Whether user account is active';
COMMENT ON COLUMN trending_data.users.created_at IS 'Account creation timestamp';
COMMENT ON COLUMN trending_data.users.updated_at IS 'Last update timestamp';

-- Insert a sample user for testing (optional)
-- Password: "TestPassword123!" (hashed)
-- INSERT INTO trending_data.users (
--     first_name, last_name, email, username, password_hash,
--     phone_number, date_of_birth, gender, country, receive_newsletters
-- ) VALUES (
--     'Test', 'User', 'test@example.com', 'testuser',
--     'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6:1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7',
--     '+1234567890', '1990-01-01', 'other', 'United States', false
-- );

-- Verify table creation
SELECT 
    table_name, 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'trending_data' 
AND table_name = 'users'
ORDER BY ordinal_position;
