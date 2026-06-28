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

| Variable | Description |
|----------|-------------|
| DATABASE_URL | Supabase PostgreSQL connection |
| SUPABASE_URL | Supabase project URL |
| SUPABASE_KEY | Supabase service role key |
| OPENAI_API_KEY | OpenAI API key for LLM analysis |

## Deployment

### Vercel

1. Connect this repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy

### Local Development

```bash
pip install -r requirements.txt
python app/api/server.py
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/insights/summary` - Summary insights
- `GET /api/insights/patterns` - Detected patterns
- `GET /api/insights/segments` - User segments
- `GET /api/insights/root-causes` - Root cause analyses
- `GET /api/insights/unmet-needs` - Unmet needs
- `GET /api/recommendations` - AI recommendations
- `GET /api/roadmap` - Product roadmap

## License

MIT
