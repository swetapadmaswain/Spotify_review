# Spotify Review Analysis Backend

FastAPI backend for Spotify Review Discovery Engine.

## Features

- Review data collection (App Store, Play Store, Reddit, Social Media)
- Sentiment analysis
- Pattern detection
- User segmentation
- Root cause analysis
- Unmet needs identification
- AI-powered recommendations

## Environment Variables

Copy `.env.example` to `.env` and configure:

### Required for Vercel Deployment
| Variable | Description |
|----------|-------------|
| DATABASE_URL | Supabase PostgreSQL connection string |
| SUPABASE_URL | Supabase project URL |
| SUPABASE_KEY | Supabase service role key |
| DB_HOST | Supabase database host |
| DB_PORT | Database port (default: 5432) |
| DB_NAME | Database name (default: postgres) |
| DB_USER | Database user (default: postgres) |
| DB_PASSWORD | Database password |

### Optional for Data Collection
| Variable | Description |
|----------|-------------|
| APP_STORE_APP_ID | Apple App Store app ID |
| PLAY_STORE_PACKAGE_NAME | Google Play package name |
| REDDIT_CLIENT_ID | Reddit API client ID |
| REDDIT_CLIENT_SECRET | Reddit API client secret |
| TWITTER_API_KEY | Twitter API key |
| OPENAI_API_KEY | OpenAI API key for LLM analysis |

## Deployment

### Vercel Deployment

1. **Set up Supabase**
   - Create a Supabase project at https://supabase.com
   - Get your database credentials from project settings
   - Set up the required tables using the SQL schema

2. **Configure Vercel Environment Variables**
   - In Vercel dashboard, go to Settings > Environment Variables
   - Add all required variables from `.env.example`
   - Ensure `DATABASE_URL` is properly formatted

3. **Deploy**
   ```bash
   vercel --prod
   ```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your credentials
# Then run:
python app.py
```

## API Endpoints

### Health & Status
- `GET /` - Root health check
- `GET /health` - Detailed health check
- `GET /metrics` - Prometheus metrics

### Data Collection
- `POST /api/appstore/reviews` - Fetch App Store reviews
- `POST /api/playstore/reviews` - Fetch Play Store reviews
- `POST /api/reddit/posts` - Fetch Reddit posts
- `POST /api/forum/threads` - Fetch forum threads
- `POST /api/social/mentions` - Fetch social media mentions
- `GET /api/collection/status` - Get collection status

### Insights & Analysis
- `GET /api/insights/summary` - Summary insights
- `GET /api/insights/patterns` - Detected patterns
- `GET /api/insights/segments` - User segments
- `GET /api/insights/root-causes` - Root cause analyses
- `GET /api/insights/unmet-needs` - Unmet needs

### Recommendations
- `GET /api/recommendations` - AI recommendations
- `GET /api/roadmap` - Product roadmap

## Troubleshooting

### Import Errors
If you encounter import errors, ensure:
- The `config` directory exists in the backend folder
- All dependencies are installed via `pip install -r requirements.txt`

### Database Connection
- Verify `DATABASE_URL` is correctly formatted
- Check Supabase project is active
- Ensure database credentials are correct

### Vercel Build Failures
- Check build logs for specific errors
- Verify Python runtime version (3.9+)
- Ensure all dependencies are in requirements.txt

## License

MIT
