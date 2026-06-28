# Vercel Environment Variables Setup

To deploy the production backend to Vercel with real Supabase data, add these environment variables in your Vercel project settings:

## Required Environment Variables

Go to your Vercel project → Settings → Environment Variables and add:

### Database (Supabase)
```
DATABASE_URL=postgresql://postgres:Blo$$om26937791@db.jmcvdljhlqmswsgkextg.supabase.co:5432/postgres
DB_HOST=db.jmcvdljhlqmswsgkextg.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=Blo$$om26937791
```

### API Configuration
```
API_HOST=0.0.0.0
API_PORT=8000
```

### Data Collection
```
APP_STORE_APP_ID=324684580
PLAY_STORE_PACKAGE_NAME=com.spotify.music
REVIEWS_LIMIT=10000
BATCH_SIZE=1000
```

### LLM (Optional - for AI features)
```
OPENAI_API_KEY=your_openai_api_key
```

### Optional (can be left blank)
```
APP_STORE_API_KEY=
PLAY_STORE_JSON_KEY=
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=
TWITTER_BEARER_TOKEN=
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=
FACEBOOK_ACCESS_TOKEN=
S3_ENDPOINT_URL=
S3_ACCESS_KEY=
S3_SECRET_KEY=
S3_BUCKET=
S3_REGION=us-east-1
API_AUTH_TOKEN=
REPORTS_OUTPUT_DIR=./reports
DASHBOARD_URL=https://your-dashboard-domain.com
```

## Deployment Steps

1. **Push changes to Git**
   ```bash
   git add .
   git commit -m "Update backend to use real Supabase data"
   git push
   ```

2. **Vercel will auto-deploy** from your Git repository

3. **Verify deployment** at:
   - Backend: https://spotify-review-kr9es1bgd-swetapadmaswains-projects.vercel.app
   - Health check: https://spotify-review-kr9es1bgd-swetapadmaswains-projects.vercel.app/health

4. **Test API endpoints**:
   - https://spotify-review-kr9es1bgd-swetapadmaswains-projects.vercel.app/api/insights/summary
   - https://spotify-review-kr9es1bgd-swetapadmaswains-projects.vercel.app/api/roadmap

## Troubleshooting

If the deployment fails:
1. Check Vercel deployment logs for specific errors
2. Ensure all required environment variables are set
3. Verify Supabase database is accessible from Vercel (no IP restrictions)
4. Check that Python dependencies are correctly specified in requirements.txt
