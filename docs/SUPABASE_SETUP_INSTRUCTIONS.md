# Supabase Setup Instructions

Quick reference for setting up your Supabase database for NC-ASK.

## Step 1: Create Supabase Project

1. Go to [Supabase](https://supabase.com) and sign in
2. Click **"New Project"**
3. Fill in:
   - **Organization**: Select or create one
   - **Name**: `nc-ask` (or your preference)
   - **Database Password**: Generate strong password (save it!)
   - **Region**: `us-east-1` (East US - closest to North Carolina)
4. Click **"Create new project"**
5. Wait for project to initialize (~2 minutes)

## Step 2: Run SQL Setup Script

1. Navigate to **SQL Editor** in left sidebar
2. Click **"New query"**
3. Open file: `backend/scripts/supabase_setup.sql`
4. Copy the **entire contents** of the file
5. Paste into Supabase SQL Editor
6. Click **"Run"** (or press Ctrl+Enter / Cmd+Enter)
7. Verify success - should see "Success. No rows returned"

### What This Script Does

- ✅ Enables `pgvector` extension for vector similarity search
- ✅ Creates 3 tables:
  - `documents` - Source document metadata
  - `document_chunks` - Text chunks with embeddings
  - `crisis_resources` - Crisis intervention resources
- ✅ Creates vector similarity search function `match_document_chunks()`
- ✅ Creates indexes for fast queries
- ✅ Sets up Row Level Security (RLS) policies
- ✅ Inserts default crisis resources
- ✅ Creates helpful views

## Step 3: Verify Tables Were Created

1. Click **"Table Editor"** in left sidebar
2. You should see 3 tables:
   - `documents`
   - `document_chunks`
   - `crisis_resources`
3. Click `crisis_resources` - should see 4 rows (988 Lifeline, Crisis Text Line, etc.)

## Step 4: Create Storage Bucket

1. Click **"Storage"** in left sidebar
2. Click **"Create a new bucket"**
3. Fill in:
   - **Name**: `documents`
   - **Public bucket**: Toggle **OFF** (keep private)
   - **File size limit**: `52428800` (50 MB)
   - **Allowed MIME types**: Add these one by one:
     - `application/pdf`
     - `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
     - `text/html`
     - `text/plain`
4. Click **"Create bucket"**

## Step 5: Get Your API Credentials

1. Click **"Settings"** (gear icon) in left sidebar
2. Click **"API"** under Project Settings
3. Copy these values to your `.env` file:

   **Project URL** (e.g., `https://abcdefghijklmnop.supabase.co`)
   ```bash
   SUPABASE_URL=https://your-project-id.supabase.co
   ```

   **anon/public key** (long string starting with `eyJ...`)
   ```bash
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

   **service_role key** (long string starting with `eyJ...`, KEEP SECRET!)
   ```bash
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

   ⚠️ **Important**: Never commit `service_role` key to git!

## Step 6: Test Database Connection

From your backend directory:

```bash
cd backend
python -c "from services.supabase_client import get_supabase; print('Connected!'); print(get_supabase().table('crisis_resources').select('*').execute())"
```

You should see the crisis resources data.

## Complete SQL Schema Reference

### Tables

#### `documents`
Stores metadata about source documents.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| title | TEXT | Document title |
| source_url | TEXT | Optional source URL |
| content_type | VARCHAR(50) | File type (PDF, DOCX, etc.) |
| file_path | TEXT | Supabase Storage path |
| metadata | JSONB | Additional metadata |
| upload_date | TIMESTAMP | Upload timestamp |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

#### `document_chunks`
Stores text chunks with vector embeddings.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| document_id | INTEGER | FK to documents |
| chunk_text | TEXT | Text content |
| chunk_index | INTEGER | Chunk order |
| embedding | vector(384) | Embedding vector |
| metadata | JSONB | Additional metadata |
| created_at | TIMESTAMP | Creation timestamp |

**Index**: IVFFlat index on `embedding` for vector similarity search

#### `crisis_resources`
Stores crisis intervention resources.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| name | TEXT | Resource name |
| phone | TEXT | Phone number |
| url | TEXT | Website URL |
| description | TEXT | Description |
| priority | INTEGER | Display priority |
| active | BOOLEAN | Is active |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### Functions

#### `match_document_chunks()`
Vector similarity search function.

**Parameters**:
- `query_embedding` - vector(384): Query embedding vector
- `match_threshold` - float (default 0.1): Minimum similarity score
- `match_count` - int (default 5): Number of results

**Returns**: Table with matched chunks, similarity scores, and document info

**Usage**:
```sql
SELECT * FROM match_document_chunks(
    '[0.1, 0.2, ...]'::vector(384),
    0.1,
    5
);
```

### Row Level Security (RLS)

**Policies**:
- `documents`: Service role has full access, anon has read access
- `document_chunks`: Service role has full access, anon has read access
- `crisis_resources`: Public read access for active resources

## Troubleshooting

### Error: "extension vector does not exist"
**Solution**: Rerun the SQL script - pgvector installation may have failed

### Error: "permission denied for table"
**Solution**: Check you're using the correct API key (service_role for writes)

### No data in tables
**Solution**:
1. Check Table Editor to verify tables exist
2. Rerun SQL script
3. Check for error messages in SQL Editor

### Vector search returns no results
**Solution**:
1. Ensure you've ingested at least one document
2. Verify embeddings were generated (check `document_chunks` table)
3. IVFFlat index requires ~1000 rows for optimal performance

### Storage bucket not found
**Solution**:
1. Go to Storage tab
2. Verify `documents` bucket exists
3. Check bucket is private (not public)

## Verification Queries

Run these in SQL Editor to verify everything is set up:

```sql
-- Check tables exist
SELECT tablename FROM pg_tables
WHERE schemaname = 'public';

-- Count documents
SELECT COUNT(*) as document_count FROM documents;

-- Count chunks
SELECT COUNT(*) as chunk_count FROM document_chunks;

-- View crisis resources
SELECT name, phone, priority FROM crisis_resources
WHERE active = true
ORDER BY priority;

-- Check vector search function exists
SELECT routine_name FROM information_schema.routines
WHERE routine_name = 'match_document_chunks';

-- Test document statistics view
SELECT * FROM document_statistics;
```

## Next Steps

After Supabase is set up:

1. ✅ Copy credentials to `.env` file
2. ✅ Add documents to `backend/data/`
3. ✅ Run ingestion script: `python backend/scripts/ingest_documents.py`
4. ✅ Start backend: `python -m uvicorn main:app --reload`
5. ✅ Start frontend: `npm run dev`
6. ✅ Test queries at `http://localhost:5173`

## Support Resources

- [Supabase Documentation](https://supabase.com/docs)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Supabase Storage Guide](https://supabase.com/docs/guides/storage)
- Project docs: `docs/SETUP.md`
