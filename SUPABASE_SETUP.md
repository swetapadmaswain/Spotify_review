# Supabase Setup Instructions

This project now uses Supabase as the primary database. Follow these steps to configure the connection.

## Prerequisites

- A Supabase project (create one at https://supabase.com)
- Your Supabase project URL and API keys

## Configuration Steps

### 1. Get Supabase Credentials

1. Go to your Supabase project dashboard
2. Navigate to Settings → API
3. Copy the following:
   - **Project URL**: `https://[project-ref].supabase.co`
   - **anon public key**: Found under "Project API keys"
   - **service_role key**: Found under "Project API keys" (for backend operations)

### 2. Configure Backend (.env)

Update your `.env` file with Supabase credentials:

```bash
# Database Configuration - Supabase
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
DB_HOST=db.[YOUR-PROJECT-REF].supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=[YOUR-DATABASE-PASSWORD]
```

**Note**: The database password is different from the anon/service_role keys. You can find/set it in:
- Supabase Dashboard → Settings → Database → Connection string

### 3. Configure Dashboard (.env)

Create or update `.env` in the `dashboard/` directory:

```bash
VITE_SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
VITE_SUPABASE_ANON_KEY=[YOUR-ANON-KEY]
VITE_API_URL=http://localhost:8000
```

### 4. Run Database Migrations

Apply the Supabase schema migrations in order:

```bash
# From the project root
supabase db push
```

Or manually run the SQL files in `supabase/migrations/`:
1. `001_initial_schema.sql` - Core tables
2. `002_seed_insights.sql` - Sample data (optional)
3. `003_fix_rls_policies.sql` - Security policies
4. `004_add_entity_analysis.sql` - Entity analysis table

### 5. Verify Connection

Test the backend connection:

```bash
cd "c:\Graduation Project - Spotify"
python -c "from app.database.connection import init_db; init_db()"
```

### 6. Start Services

```bash
# Start backend API
python -m uvicorn app.api.server:app --reload --host 0.0.0.0 --port 8000

# Start dashboard (in new terminal)
cd dashboard
npm run dev
```

## Data Collection

To populate the database with reviews:

```bash
# Run data collection (will fetch up to 10,000 reviews)
python scripts/collect_reviews.py

# Run AI analysis
python scripts/run_analysis.py

# Generate insights
python -c "from app.services.insight_engine import InsightEngine; InsightEngine().run()"
```

## Troubleshooting

### Connection Issues

If you see "connection refused" errors:
- Verify your DATABASE_URL is correct
- Check that your Supabase project is active
- Ensure your IP is allowed in Supabase settings (if IP restrictions are enabled)

### Dashboard Shows No Data

1. Check that the backend API is running on port 8000
2. Verify VITE_API_URL is set correctly
3. Run the insight generation pipeline:
   ```bash
   curl -X POST http://localhost:8000/api/insights/generate
   ```

### Permission Errors

If you see RLS (Row Level Security) errors:
- Ensure migration `003_fix_rls_policies.sql` has been applied
- Check that service_role key is being used for backend operations

## Architecture Changes

- **Backend** now connects directly to Supabase PostgreSQL
- **Dashboard** fetches data via backend API endpoints (not direct Supabase queries)
- **All tables** use UUID primary keys matching Supabase schema
- **Data limit** increased from 500 to 10,000 reviews per collection run
