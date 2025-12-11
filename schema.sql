-- Trip Finance Tracker Database Schema
-- Run this in Supabase SQL Editor

-- Create trips table
CREATE TABLE IF NOT EXISTS trips (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    destination TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    currency TEXT NOT NULL,
    travelers TEXT DEFAULT '[]',
    expenses TEXT DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_trips_created_at ON trips(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_trips_id ON trips(id);

-- Enable Row Level Security (RLS)
ALTER TABLE trips ENABLE ROW LEVEL SECURITY;

-- Drop existing policy if it exists
DROP POLICY IF EXISTS "Allow all operations on trips" ON trips;

-- Create policy to allow public access (no authentication required)
CREATE POLICY "Allow all operations on trips" ON trips
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Create or replace the updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop existing trigger if it exists
DROP TRIGGER IF EXISTS update_trips_updated_at ON trips;

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_trips_updated_at 
    BEFORE UPDATE ON trips
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Verify table was created
SELECT 'Table created successfully!' as status;
SELECT COUNT(*) as trip_count FROM trips;
