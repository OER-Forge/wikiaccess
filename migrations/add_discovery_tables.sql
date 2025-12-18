-- Migration: Add discovery tables and columns for page discovery system
-- This migration adds tables to track discovered pages and extends existing tables
-- Safe to run multiple times (uses IF NOT EXISTS)

-- Add new columns to conversion_batches table
ALTER TABLE conversion_batches ADD COLUMN discovery_enabled BOOLEAN DEFAULT 0;
ALTER TABLE conversion_batches ADD COLUMN pages_discovered_count INTEGER DEFAULT 0;
ALTER TABLE conversion_batches ADD COLUMN parent_batch_id TEXT;
ALTER TABLE conversion_batches ADD COLUMN discovery_depth INTEGER DEFAULT 0;

-- Add new column to pages table
ALTER TABLE pages ADD COLUMN discovery_depth INTEGER DEFAULT 0;

-- Create discovered_pages table
CREATE TABLE IF NOT EXISTS discovered_pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_page_id TEXT NOT NULL UNIQUE,
    wiki_url TEXT NOT NULL,
    discovery_depth INTEGER NOT NULL DEFAULT 1,
    discovery_status TEXT NOT NULL CHECK(
        discovery_status IN ('discovered', 'approved', 'skipped', 'failed_404', 'converted')
    ),

    -- Discovery metadata
    first_discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    first_discovered_by_batch TEXT,
    reference_count INTEGER DEFAULT 0,

    -- Decision tracking
    decision_made_at TIMESTAMP,
    decision_reason TEXT,

    -- Conversion tracking
    converted_at TIMESTAMP,
    converted_batch_id TEXT,

    -- 404 tracking
    http_status_code INTEGER,
    last_check_at TIMESTAMP,
    check_attempt_count INTEGER DEFAULT 0,

    FOREIGN KEY(first_discovered_by_batch) REFERENCES conversion_batches(batch_id),
    FOREIGN KEY(converted_batch_id) REFERENCES conversion_batches(batch_id)
);

-- Create indexes for discovered_pages
CREATE INDEX IF NOT EXISTS idx_discovered_status ON discovered_pages(discovery_status, discovery_depth);
CREATE INDEX IF NOT EXISTS idx_discovered_page_id ON discovered_pages(target_page_id);
CREATE INDEX IF NOT EXISTS idx_discovered_batch ON discovered_pages(first_discovered_by_batch);
CREATE INDEX IF NOT EXISTS idx_discovered_wiki_url ON discovered_pages(wiki_url, discovery_status);

-- Create discovery_sources table
CREATE TABLE IF NOT EXISTS discovery_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discovered_page_id INTEGER NOT NULL,
    source_page_id TEXT NOT NULL,
    link_text TEXT,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    batch_id TEXT NOT NULL,

    FOREIGN KEY(discovered_page_id) REFERENCES discovered_pages(id),
    FOREIGN KEY(batch_id) REFERENCES conversion_batches(batch_id)
);

-- Create indexes for discovery_sources
CREATE INDEX IF NOT EXISTS idx_discovery_sources_page ON discovery_sources(discovered_page_id);
CREATE INDEX IF NOT EXISTS idx_discovery_sources_batch ON discovery_sources(batch_id);
CREATE INDEX IF NOT EXISTS idx_discovery_sources_source ON discovery_sources(source_page_id);
