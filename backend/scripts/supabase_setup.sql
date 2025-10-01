-- ============================================
-- NC-ASK Supabase Database Setup Script
-- ============================================
-- Run this script in your Supabase SQL Editor to set up the complete database schema
-- Instructions: https://app.supabase.com/project/YOUR_PROJECT/sql

-- ============================================
-- 1. Enable Required Extensions
-- ============================================

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 2. Create Tables
-- ============================================

-- Documents table
-- Stores metadata about source documents
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    source_url TEXT,
    content_type VARCHAR(50) NOT NULL,
    file_path TEXT NOT NULL,  -- Supabase Storage path
    metadata JSONB DEFAULT '{}'::jsonb,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add index on upload_date for sorting
CREATE INDEX IF NOT EXISTS idx_documents_upload_date ON documents(upload_date DESC);

-- Add index on content_type for filtering
CREATE INDEX IF NOT EXISTS idx_documents_content_type ON documents(content_type);

-- Document chunks table
-- Stores text chunks with embeddings for vector search
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding vector(384),  -- Dimension for all-MiniLM-L6-v2
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add index on document_id for faster joins
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_chunks(document_id);

-- Add index on chunk_index for ordering
CREATE INDEX IF NOT EXISTS idx_chunks_chunk_index ON document_chunks(chunk_index);

-- Create vector similarity search index using IVFFlat
-- Note: This requires at least 1000 rows for optimal performance
-- For development, you can start without this and add it later
CREATE INDEX IF NOT EXISTS idx_chunks_embedding
ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Alternative: HNSW index (better for larger datasets, available in newer Supabase)
-- CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw
-- ON document_chunks
-- USING hnsw (embedding vector_cosine_ops);

-- Crisis resources table
-- Stores crisis intervention resources
CREATE TABLE IF NOT EXISTS crisis_resources (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    url TEXT,
    description TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 100,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add index on priority for sorting
CREATE INDEX IF NOT EXISTS idx_crisis_priority ON crisis_resources(priority, active);

-- ============================================
-- 3. Create Vector Search Function
-- ============================================

-- Function to match document chunks using vector similarity
CREATE OR REPLACE FUNCTION match_document_chunks(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.1,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id int,
    document_id int,
    chunk_text text,
    chunk_index int,
    metadata jsonb,
    similarity float,
    document_title text,
    source_url text
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.document_id,
        dc.chunk_text,
        dc.chunk_index,
        dc.metadata,
        1 - (dc.embedding <=> query_embedding) AS similarity,
        d.title AS document_title,
        d.source_url
    FROM document_chunks dc
    JOIN documents d ON dc.document_id = d.id
    WHERE 1 - (dc.embedding <=> query_embedding) > match_threshold
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ============================================
-- 4. Insert Default Crisis Resources
-- ============================================

INSERT INTO crisis_resources (name, phone, url, description, priority, active)
VALUES
    (
        '988 Suicide & Crisis Lifeline',
        '988',
        'https://988lifeline.org/',
        '24/7 free and confidential support for people in distress',
        1,
        true
    ),
    (
        'Crisis Text Line',
        'Text HOME to 741741',
        'https://www.crisistextline.org/',
        '24/7 text-based crisis support',
        2,
        true
    ),
    (
        'NC Hope4NC Helpline',
        '1-855-587-3463',
        'https://www.mhanc.org/hope4nc/',
        'North Carolina''s free 24/7 crisis and emotional support line',
        3,
        true
    ),
    (
        'Emergency Services',
        '911',
        NULL,
        'For immediate life-threatening emergencies',
        4,
        true
    )
ON CONFLICT DO NOTHING;

-- ============================================
-- 5. Create Storage Bucket
-- ============================================

-- Note: Storage buckets are created via Supabase Dashboard or Storage API
-- Go to: https://app.supabase.com/project/YOUR_PROJECT/storage/buckets
-- Create a bucket named "documents" with the following settings:
--   - Name: documents
--   - Public: false (private)
--   - File size limit: 50MB
--   - Allowed MIME types: application/pdf, application/vnd.openxmlformats-officedocument.wordprocessingml.document, text/html, text/plain

-- ============================================
-- 6. Set Up Row Level Security (RLS)
-- ============================================

-- Enable RLS on all tables
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE crisis_resources ENABLE ROW LEVEL SECURITY;

-- Policy: Allow public read access to crisis resources
CREATE POLICY "Public read access to crisis resources"
ON crisis_resources
FOR SELECT
USING (active = true);

-- Policy: Allow service role full access to documents
CREATE POLICY "Service role full access to documents"
ON documents
FOR ALL
USING (auth.role() = 'service_role');

-- Policy: Allow service role full access to document_chunks
CREATE POLICY "Service role full access to document_chunks"
ON document_chunks
FOR ALL
USING (auth.role() = 'service_role');

-- Policy: Allow anon read access to documents (for queries)
CREATE POLICY "Anon read access to documents"
ON documents
FOR SELECT
USING (true);

-- Policy: Allow anon read access to document_chunks (for queries)
CREATE POLICY "Anon read access to document_chunks"
ON document_chunks
FOR SELECT
USING (true);

-- ============================================
-- 7. Create Triggers for Updated Timestamps
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for documents table
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for crisis_resources table
CREATE TRIGGER update_crisis_resources_updated_at
    BEFORE UPDATE ON crisis_resources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 8. Create Helpful Views (Optional)
-- ============================================

-- View: Document statistics
CREATE OR REPLACE VIEW document_statistics AS
SELECT
    d.id,
    d.title,
    d.content_type,
    d.upload_date,
    COUNT(dc.id) AS chunk_count,
    AVG(LENGTH(dc.chunk_text)) AS avg_chunk_length
FROM documents d
LEFT JOIN document_chunks dc ON d.id = dc.document_id
GROUP BY d.id, d.title, d.content_type, d.upload_date;

-- ============================================
-- Setup Complete!
-- ============================================

-- Verification queries:
-- SELECT * FROM documents;
-- SELECT * FROM document_chunks LIMIT 10;
-- SELECT * FROM crisis_resources;
-- SELECT * FROM document_statistics;

-- Test vector search function:
-- SELECT * FROM match_document_chunks(
--     (SELECT embedding FROM document_chunks LIMIT 1),
--     0.1,
--     5
-- );
