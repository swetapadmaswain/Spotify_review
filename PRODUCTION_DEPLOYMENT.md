# Production Deployment Guide

## Dashboard Production Configuration

### Step 1: Choose Your Production Backend URL

Decide on the URL where your backend will be hosted:

| Deployment Option | Example URL |
|-------------------|-------------|
| Vercel | `https://your-app.vercel.app` |
| Railway/Render | `https://your-app.onrender.com` |
| Custom Domain | `https://api.yourdomain.com` |
| Vercel (Backend only) | `https://spotify-analysis-api.vercel.app` |

### Step 2: Update Dashboard .env

Edit `dashboard/.env` with your production backend URL:

```env
# Dashboard Environment Configuration

# Backend API Configuration - UPDATE THIS FOR PRODUCTION
VITE_API_URL=https://your-production-backend-url.com

# Supabase Configuration (optional - currently unused)
VITE_SUPABASE_URL=https://jmcvdljhlqmswsgkextg.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImptY3ZkbGpobHFtc3dzZ2tleHRnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI0NjE0OTksImV4cCI6MjA5ODAzNzQ5OX0.LTiXHF_hTaLWrbPorLw9PuFw9J0TH76dJyWOuUalhwo

# API Request Configuration
VITE_REQUEST_TIMEOUT=30000
VITE_RETRY_ATTEMPTS=3

# Features
VITE_ENABLE_REAL_TIME_UPDATES=true
VITE_ENABLE_EXPORT=true
VITE_ENABLE_ANALYTICS=true
```

### Step 3: Configure Backend CORS

When deploying your backend, ensure CORS is configured to allow requests from your dashboard domain.

**In `app/api/server.py`, add your dashboard domain:**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Local development
        "https://your-dashboard.netlify.app",   # Production dashboard
        "https://your-dashboard.vercel.app",    # Vercel deployment
        "https://yourdomain.com",    # Custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 4: Update Backend Environment

Ensure `app/database/supabase_config.py` is configured with production credentials:

**In `app/database/supabase_config.py`:**

```python
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jmcvdljhlqmswsgkextg.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-service-role-key-here")
```

**Or set environment variables on your production server:**

```bash
export SUPABASE_URL=https://jmcvdljhlqmswsgkextg.supabase.co
export SUPABASE_KEY=your-service-role-key
```

### Step 5: Deploy Backend First

Deploy your backend to a hosting service that supports FastAPI:

| Platform | Command/Method |
|----------|---------------|
| Vercel (with FastAPI) | `vercel deploy` |
| Railway | `git push railway main` |
| Render | `git push origin main` |
| AWS EC2 | `pm2 start main.py --name api` |

### Step 6: Deploy Dashboard

After backend is live, deploy the dashboard:

```bash
cd dashboard
npm install
npm run build
# Deploy the dist/ folder to your hosting
```

### Step 7: Verify Production Connection

Test your production deployment:

1. Visit your dashboard URL
2. Check browser console for API calls
3. Verify data loads correctly
4. Test report generation

---

## Quick Production Setup Script

Run this to update dashboard configuration:

```bash
# Linux/Mac
export DASHBOARD_BACKEND_URL="https://your-backend-url.com"
sed -i "s|VITE_API_URL=http://localhost:8000|VITE_API_URL=${DASHBOARD_BACKEND_URL}|g" dashboard/.env

# Windows (PowerShell)
$env:DASHBOARD_BACKEND_URL="https://your-backend-url.com"
((Get-Content -path dashboard\.env -Raw) -replace 'VITE_API_URL=http://localhost:8000',"VITE_API_URL=${env:DASHBOARD_BACKEND_URL}") | Set-Content -Path dashboard\.env
```

---

## Common Production Issues

### 1. CORS Errors
**Error:** `Access to fetch...has been blocked by CORS policy`

**Fix:** Add dashboard domain to backend CORS origins

### 2. Connection Refused
**Error:** `Failed to fetch` or `NetworkError`

**Fix:** Verify backend URL in `dashboard/.env` matches production URL

### 3. Data Not Loading
**Error:** Dashboard shows "No data" or loading forever

**Fix:** 
- Check backend logs for database connection errors
- Verify Supabase credentials are correct
- Run `python scripts/verify_production_readiness.py` on server

---

## Environment Variables Reference

### Backend (.env)
| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ Yes | Supabase PostgreSQL connection |
| `SUPABASE_URL` | ✅ Yes | Supabase project URL |
| `SUPABASE_KEY` | ✅ Yes | Supabase service role key |
| `OPENAI_API_KEY` | ✅ Yes | OpenAI API for LLM analysis |
| `API_AUTH_TOKEN` | Optional | Authentication token |
| `S3_*` | Optional | S3 storage configuration |

### Dashboard (dashboard/.env)
| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | ✅ Yes | Backend API URL |
| `VITE_SUPABASE_URL` | Optional | Supabase URL (unused currently) |
| `VITE_REQUEST_TIMEOUT` | Optional | Request timeout in ms |
