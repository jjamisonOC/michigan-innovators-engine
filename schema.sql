-- Michigan Startup Ecosystem & Incubator Intelligence Engine
-- Supabase PostgreSQL Schema

-- Enable UUID generation extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Custom ENUM types for strict taxonomy classification
DO $$ BEGIN
    CREATE TYPE organization_type_enum AS ENUM (
        'State SmartZone',
        'University Incubator',
        'Private Accelerator',
        'Local/Regional Hub',
        'Coworking/Makerspace',
        'Non-Profit Support'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE ownership_type_enum AS ENUM (
        'Public',
        'Private',
        'Public-Private Partnership',
        'University'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 2. Organizations Table
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    url TEXT,
    org_type organization_type_enum NOT NULL,
    ownership ownership_type_enum NOT NULL,
    address TEXT,
    city TEXT,
    region TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    description TEXT,
    application_url TEXT,
    contact_email TEXT,
    industry_specialties TEXT[] DEFAULT '{}',
    specialized_equipment TEXT[] DEFAULT '{}',
    services_and_curriculum TEXT[] DEFAULT '{}',
    last_quarterly_scrape TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast geospatial, regional, and array tag filtering
CREATE INDEX IF NOT EXISTS idx_organizations_slug ON organizations(slug);
CREATE INDEX IF NOT EXISTS idx_organizations_org_type ON organizations(org_type);
CREATE INDEX IF NOT EXISTS idx_organizations_region ON organizations(region);
CREATE INDEX IF NOT EXISTS idx_organizations_industry_specialties ON organizations USING GIN (industry_specialties);
CREATE INDEX IF NOT EXISTS idx_organizations_specialized_equipment ON organizations USING GIN (specialized_equipment);
CREATE INDEX IF NOT EXISTS idx_organizations_services_curriculum ON organizations USING GIN (services_and_curriculum);

-- 3. Mentors Table
CREATE TABLE IF NOT EXISTS mentors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    role_at_incubator TEXT,
    current_title_company TEXT,
    bio_summary TEXT,
    expertise_tags TEXT[] DEFAULT '{}',
    linkedin_url TEXT,
    confidence_score DOUBLE PRECISION DEFAULT 0.0 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, full_name)
);

CREATE INDEX IF NOT EXISTS idx_mentors_organization_id ON mentors(organization_id);
CREATE INDEX IF NOT EXISTS idx_mentors_expertise_tags ON mentors USING GIN (expertise_tags);

-- 4. Events Table
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    event_date TIMESTAMPTZ NOT NULL,
    event_type TEXT NOT NULL CHECK (
        event_type IN (
            'Seminar',
            'Pitch Competition',
            'Workshop',
            'Networking',
            'Cohort Deadline'
        )
    ),
    description TEXT,
    registration_url TEXT,
    last_checked TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, title, event_date)
);

CREATE INDEX IF NOT EXISTS idx_events_organization_id ON events(organization_id);
CREATE INDEX IF NOT EXISTS idx_events_event_date ON events(event_date);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
