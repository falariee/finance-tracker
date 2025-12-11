# Database Setup Guide for Vercel Deployment

## Problem
- JSON files don't persist on Vercel (serverless = ephemeral filesystem)
- Shared trip links don't work for other users
- Trip data is lost on page refresh

## Solution: Supabase (PostgreSQL)

### Step 1: Create Supabase Account
1. Go to [https://supabase.com](https://supabase.com)
2. Sign up for free account
3. Create a new project

### Step 2: Create Database Table

Run this SQL in Supabase SQL Editor:

```sql
-- Create trips table
CREATE TABLE trips (
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
CREATE INDEX idx_trips_created_at ON trips(created_at DESC);

-- Enable Row Level Security (RLS) but allow all operations for now
ALTER TABLE trips ENABLE ROW LEVEL SECURITY;

-- Create policies to allow public access (no auth required)
CREATE POLICY "Allow all operations on trips" ON trips
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_trips_updated_at BEFORE UPDATE ON trips
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Step 3: Get Supabase Credentials

1. In Supabase dashboard, go to **Settings** → **API**
2. Copy these values:
   - **Project URL** (e.g., https://xxxxx.supabase.co)
   - **anon/public API key** (starts with eyJ...)

### Step 4: Configure Vercel Environment Variables

1. Go to your Vercel project dashboard
2. Go to **Settings** → **Environment Variables**
3. Add these variables:
   - `SUPABASE_URL` = your Project URL
   - `SUPABASE_KEY` = your anon/public key
   - `SECRET_KEY` = any random string for Flask sessions

4. Redeploy your app for changes to take effect

### Step 5: Test

1. Create a new trip
2. Refresh the page - trip should still be there
3. Copy the invite link and open in incognito - should work
4. Add expenses - they persist across refreshes

## Alternative: Vercel Postgres

If you prefer Vercel's built-in database:

1. In Vercel, go to **Storage** → **Create Database** → **Postgres**
2. Connect it to your project
3. Update `utils/database.py` to use Vercel Postgres connection string
4. Run the same SQL schema

## Fallback Mode

If no database is configured, the app will:
- Show a warning message
- Still work for single session (data lost on refresh)
- This is fine for local testing

## Security Notes

- Current setup allows public read/write (no authentication)
- For production, implement proper authentication
- Consider adding rate limiting
- Add data validation
