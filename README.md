# Spotify Review Discovery Engine - Phase 1: Data Collection Infrastructure

This project implements Phase 1 of the AI-Powered Review Discovery Engine for Spotify music discovery analysis. It provides a comprehensive data collection infrastructure that gathers user feedback from multiple sources.

## Overview

Phase 1 focuses on building the data collection infrastructure to gather user feedback from:
- Play Store reviews (✓ Working - collects 10,000 reviews per run)
- App Store reviews (✗ Not working - RSS feed deprecated)
- Spotify Community Forums (✗ Not working - complex HTML structure)
- Reddit discussions (requires API credentials)
- Social media conversations (requires API credentials)

**Current Deployment:**
- Frontend: Vercel (React dashboard)
- Backend: Supabase (PostgreSQL database)
- Automation: GitHub Actions (daily data collection)

**Data Collection:**
- Currently collects 10,000 reviews from Play Store per run
- GitHub Actions runs daily at 2 AM UTC (7:30 AM IST)

## Project Structure

```
spotify-review-engine/
├── app/
│   ├── connectors/          # Data source connectors
│   │   ├── app_store.py     # App Store RSS feed (not working)
│   │   ├── play_store.py    # Play Store scraper (working)
│   │   ├── reddit.py        # Reddit API (requires credentials)
│   │   ├── forum.py         # Spotify Community Forums (not working)
│   │   └── social_media.py  # Twitter/Facebook (requires credentials)
│   ├── database/            # Database models and connection
│   │   ├── models.py
│   │   └── connection.py
│   └── api/                 # API routes
├── dashboard/               # React frontend for Vercel
│   ├── src/
│   │   ├── api/             # API client
│   │   ├── components/      # React components
│   │   └── App.tsx
│   └── package.json
├── scripts/                 # Data collection and analysis scripts
│   ├── run_collection.py    # Main data collection script
│   └── run_analysis.py      # Sentiment and topic analysis
├── supabase/
│   └── migrations/          # SQL migrations for Supabase
│       ├── 001_initial_schema.sql
│       ├── 002_seed_insights.sql
│       └── 003_fix_rls_policies.sql
├── .github/
│   └── workflows/
│       └── data-collection.yml  # GitHub Actions workflow
├── config/
│   └── settings.py          # Configuration settings
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md              # This file
```

## Prerequisites

- Python 3.9 or higher
- Supabase account (for database and hosting)
- GitHub account (for GitHub Actions automation)
- Vercel account (for frontend deployment)

## Installation

### 1. Clone the repository

```bash
cd "c:\Graduation Project - Spotify"
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up Supabase

1. Create a new project at https://supabase.com
2. Run the SQL migrations in Supabase SQL Editor:
   - `supabase/migrations/001_initial_schema.sql`
   - `supabase/migrations/002_seed_insights.sql`
   - `supabase/migrations/003_fix_rls_policies.sql`
3. Get your Supabase URL and service role key from Project Settings

### 4. Configure GitHub Secrets

Add the following secrets to your GitHub repository:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key

### 5. Deploy to Vercel

1. Connect your GitHub repository to Vercel
2. Set root directory to `dashboard`
3. Add environment variables:
   - `VITE_SUPABASE_URL`: Your Supabase project URL
   - `VITE_SUPABASE_ANON_KEY`: Your Supabase anon key
4. Deploy

## Usage

### Automated Data Collection

The system uses GitHub Actions for automated data collection:

1. GitHub Actions runs daily at 2 AM UTC (7:30 AM IST)
2. Collects 10,000 reviews from Play Store using google-play-scraper
3. Stores data in Supabase database
4. Runs sentiment and topic analysis
5. Generates insights

### Manual Data Collection

To run data collection manually:

```bash
# Set environment variables
export SUPABASE_URL=your_supabase_url
export SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Run collection script
python scripts/run_collection.py

# Run analysis script
python scripts/run_analysis.py
```

### View Dashboard

Access the React dashboard at your Vercel deployment URL to:
- View collected reviews
- See sentiment analysis
- Explore topic analysis
- Read generated insights

### Using Connectors Directly

You can use the connectors directly in Python scripts:

```python
from app.connectors.play_store import PlayStoreConnector

# Fetch Play Store reviews
play_store = PlayStoreConnector(package_name='com.spotify.music')
reviews = play_store.fetch_reviews(sort='newest', count=100)
```

## Database Schema

### data_collection_runs
Tracks data collection runs with status and metadata.

### raw_reviews
Stores raw review data from all sources (Play Store, App Store, Forums, etc.).

### sentiment_analysis
Stores sentiment analysis results for each review.

### topic_analysis
Stores topic analysis results for each review.

### insights
Stores generated insights from the analysis (patterns, root causes, segments, etc.).

## Connector Status

### Play Store Connector ✓ Working
- Uses google-play-scraper library
- Successfully fetches real reviews
- Collects 10,000 reviews per run
- No API key required

### App Store Connector ✗ Not Working
- RSS feed returns 200 but 0 entries
- Apple may have deprecated the RSS feed format
- Requires alternative approach (official API or different scraping method)

### Forum Connector ✗ Not Working
- Updated URLs to working categories (Help, Ideas, Account, Subscriptions)
- HTML structure is complex/dynamic (Lithium platform)
- Current parsing logic returns 0 threads
- Requires more sophisticated parsing or API access

### Reddit Connector ✗ Requires Credentials
- Requires PRAW library and Reddit API credentials
- Not configured in current deployment

### Social Media Connector ✗ Requires Credentials
- Requires Twitter/Facebook API credentials
- Not configured in current deployment

## Troubleshooting

### GitHub Actions Not Running

- Check that GitHub Secrets are configured correctly
- Verify SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set
- Check workflow logs in GitHub Actions tab

### Data Not Appearing in Dashboard

- Verify SQL migrations were run in Supabase
- Check RLS policies are correctly configured
- Ensure Vercel environment variables are set
- Check Supabase Table Editor for data

### Play Store Scraper Fails

- Ensure google-play-scraper is installed (version 1.2.7)
- Check internet connectivity
- Verify package name is correct (com.spotify.music)

## Development

### Running Tests

```bash
pytest tests/
```

### Adding New Connectors

1. Create a new file in `src/connectors/`
2. Implement the connector class with `fetch_*` methods
3. Add import to `src/connectors/__init__.py`
4. Add API endpoint in `src/api/server.py`
5. Create n8n workflow configuration

### Database Migrations

For schema changes, use Alembic:

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Next Steps (Phase 2)

Phase 2 will implement the AI Analysis Engine:

- Vector database setup (ChromaDB)
- RAG system implementation
- LLM processing pipeline
- Sentiment, topic, and entity analysis
- Batch and real-time processing

## License

This project is part of a graduation project for Spotify music discovery analysis.

## Support

For issues or questions, refer to the architectural implementation document: `architectural_implementation.md`
