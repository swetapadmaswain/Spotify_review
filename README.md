# Spotify Review Discovery Engine - Phase 1: Data Collection Infrastructure

This project implements Phase 1 of the AI-Powered Review Discovery Engine for Spotify music discovery analysis. It provides a comprehensive data collection infrastructure that gathers user feedback from multiple sources.

## Overview

Phase 1 focuses on building the data collection infrastructure to gather user feedback from:
- App Store reviews
- Play Store reviews
- Reddit discussions
- Spotify Community Forums
- Social media conversations (Twitter, Facebook)

All data collection is limited to 500 records per source to control token usage and costs.

## Project Structure

```
spotify-review-engine/
├── src/
│   ├── connectors/          # Data source connectors
│   │   ├── app_store.py
│   │   ├── play_store.py
│   │   ├── reddit.py
│   │   ├── forum.py
│   │   └── social_media.py
│   ├── database/            # Database models and connection
│   │   ├── models.py
│   │   └── connection.py
│   ├── data_quality/        # Data validation and cleaning
│   │   └── service.py
│   └── api/                 # FastAPI server
│       └── server.py
├── n8n_workflows/           # n8n workflow configurations
│   ├── appstore_collection.json
│   ├── playstore_collection.json
│   ├── reddit_collection.json
│   ├── forum_collection.json
│   └── social_collection.json
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md              # This file
```

## Prerequisites

- Python 3.9 or higher
- PostgreSQL 12 or higher
- n8n (for workflow automation)
- S3-compatible storage (AWS S3 or MinIO)

## Installation

### 1. Clone the repository

```bash
cd "c:\Graduation Project - Spotify"
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up PostgreSQL database

```bash
# Create database
createdb spotify_reviews

# Or using psql
psql -U postgres
CREATE DATABASE spotify_reviews;
```

### 4. Configure environment variables

Copy the example environment file and update it with your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/spotify_reviews

# App Store Configuration
APP_STORE_APP_ID=324684580

# Play Store Configuration
PLAY_STORE_PACKAGE_NAME=com.spotify.music

# Reddit Configuration
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# Twitter Configuration
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# S3/MinIO Configuration
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=your_s3_access_key
S3_SECRET_KEY=your_s3_secret_key
S3_BUCKET=spotify-reviews-raw
```

### 5. Initialize database

```bash
python -c "from src.database import init_db; init_db()"
```

## Usage

### Starting the API Server

The FastAPI server provides REST endpoints for data collection:

```bash
python src/api/server.py
```

Or using uvicorn:

```bash
uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### Health Check
```bash
GET http://localhost:8000/
GET http://localhost:8000/health
```

#### Fetch App Store Reviews
```bash
POST http://localhost:8000/api/appstore/reviews
Content-Type: application/json

{
  "limit": 500
}
```

#### Fetch Play Store Reviews
```bash
POST http://localhost:8000/api/playstore/reviews
Content-Type: application/json

{
  "limit": 500
}
```

#### Fetch Reddit Posts
```bash
POST http://localhost:8000/api/reddit/posts
Content-Type: application/json

{
  "limit": 500,
  "category": "spotify"
}
```

#### Fetch Forum Threads
```bash
POST http://localhost:8000/api/forum/threads
Content-Type: application/json

{
  "limit": 500,
  "category": "discovery"
}
```

#### Fetch Social Media Mentions
```bash
POST http://localhost:8000/api/social/mentions
Content-Type: application/json

{
  "limit": 500,
  "query": "#spotify"
}
```

#### Get Collection Status
```bash
GET http://localhost:8000/api/collection/status
```

### Using Connectors Directly

You can also use the connectors directly in Python scripts:

```python
from src.connectors import AppStoreConnector, PlayStoreConnector

# Fetch App Store reviews
app_store = AppStoreConnector()
reviews = app_store.fetch_reviews(limit=500)

# Fetch Play Store reviews
play_store = PlayStoreConnector()
reviews = play_store.fetch_reviews(count=500)
```

### Using Data Quality Services

```python
from src.data_quality import DataQualityService, DeduplicationService

# Validate data
quality_service = DataQualityService()
validation = quality_service.validate_batch(reviews, 'appstore')

# Clean data
cleaned_reviews = quality_service.clean_data(reviews, 'appstore')

# Remove duplicates
dedup_service = DeduplicationService()
unique_reviews = dedup_service.remove_duplicates(cleaned_reviews)
```

## n8n Workflow Integration

The project includes pre-configured n8n workflows for automated data collection:

1. Import the workflow JSON files from `n8n_workflows/` directory into n8n
2. Configure the S3 credentials in n8n AWS S3 node
3. Configure Slack credentials for notifications (optional)
4. Activate the workflows

Each workflow:
- Runs daily (configurable)
- Calls the appropriate API endpoint
- Transforms and stores data in S3
- Sends success/error notifications

### Workflow Files

- `appstore_collection.json` - App Store review collection
- `playstore_collection.json` - Play Store review collection
- `reddit_collection.json` - Reddit posts collection
- `forum_collection.json` - Forum threads collection
- `social_collection.json` - Social media mentions collection

## Database Schema

### data_collection_runs
Tracks data collection runs with status and metadata.

### raw_data_metadata
Tracks raw data files and their processing status.

### processed_reviews
Stores processed and cleaned review data from all sources.

## Data Quality Features

### Validation
- Required field checking
- Data type validation
- Text encoding validation
- Rating range validation

### Cleaning
- HTML tag removal
- Whitespace normalization
- Missing value handling
- Author name normalization

### Deduplication
- Hash-based duplicate detection
- Similarity-based near-duplicate detection
- Cross-source deduplication

## Configuration

All configuration is managed through `config.py` and environment variables:

- `reviews_limit`: Default limit for data collection (default: 500)
- `batch_size`: Batch size for processing (default: 500)
- Database connection settings
- API credentials for each data source
- S3/MinIO storage settings

## Token Usage Control

To prevent excessive token usage:

- All connectors are limited to 500 records per collection
- Batch processing is limited to 500 records
- Rate limiting is implemented for all API calls
- Deduplication reduces redundant processing

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready

# Test connection
psql -U postgres -d spotify_reviews
```

### Reddit API Issues

- Ensure Reddit API credentials are correct
- Check that the Reddit app has the correct permissions
- Verify user agent string is unique

### Twitter API Issues

- Use bearer token for API v2 (recommended)
- Ensure API key has read permissions
- Check rate limits are not exceeded

### S3/MinIO Issues

- Verify endpoint URL is correct
- Check access key and secret key
- Ensure bucket exists or can be created

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
