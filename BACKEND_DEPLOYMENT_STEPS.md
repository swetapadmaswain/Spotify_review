# 🚀 Complete Backend Deployment Guide for Vercel

This is a detailed step-by-step guide to deploy your FastAPI backend to Vercel.

---

## Prerequisites

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Prepare Your Backend Code
Make sure your backend has:
- `vercel.py` file (created in previous steps)
- `requirements.txt` with all dependencies
- `app/` folder with FastAPI app
- `.git` initialized

---

## Step-by-Step Deployment

### Step 1: Create a New Vercel Project

#### Option A: Via Vercel CLI
```bash
cd "c:\Graduation Project - Spotify"
vercel
```

When prompted:
- **Set up and deploy?** → `Y`
- **Which scope?** → Select your account
- **Link to existing project?** → `N`
- **Project name?** → `spotify-backend` (or any name)
- **Directory?** → `.` (current directory)
- **Ignore build step?** → `Y`
- **Ignore development server?** → `Y`

This creates a Vercel project and gives you a URL like:
```
https://spotify-backend.vercel.app
```

#### Option B: Via Vercel Dashboard
1. Go to [vercel.com](https://vercel.com)
2. Click **New Project**
3. Import your GitHub repository
4. Set **Root Directory** to root
5. Click **Deploy**

---

### Step 2: Configure Build Settings

#### Create `vercel.json` in project root

Your `vercel.json` should look like this:

```json
{
  "buildCommand": "pip install -r requirements.txt",
  "outputDirectory": "dist",
  "installCommand": "pip install -r requirements.txt",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/vercel.py"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

**Or use the one we already created:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/vercel.py"
    },
    {
      "source": "/(.*)",
      "destination": "/dashboard/$1"
    }
  ]
}
```

---

### Step 3: Create vercel.py Entry Point

**Location:** Root of your project

```python
"""
Vercel Serverless Function Entry Point for FastAPI Backend

This file bridges Vercel's serverless environment with your FastAPI application.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import your FastAPI app
from app.api.server import app

# Vercel handler
handler = app

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### Step 4: Update requirements.txt

**Location:** `requirements.txt`

Make sure you have these FastAPI dependencies:

```txt
# Core dependencies for data collection
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
google-play-scraper==1.2.7

# Cloud Deployment
supabase==2.5.0

# Utilities
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Logging
loguru==0.7.2

# FastAPI and Server
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
asyncpg==0.29.0

# LLM Integration
openai==1.3.5

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1
```

---

### Step 5: Set Environment Variables on Vercel

Go to Vercel Dashboard → Your Project → Settings → Environment Variables

Add these variables:

| Variable Name | Value | Environment |
|--------------|-------|-------------|
| `DATABASE_URL` | `postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres` | Production |
| `SUPABASE_URL` | `https://PROJECT_ID.supabase.co` | Production |
| `SUPABASE_KEY` | `YOUR_SERVICE_ROLE_KEY` | Production |
| `OPENAI_API_KEY` | `sk-...` | Production |
| `API_HOST` | `0.0.0.0` | Production |
| `API_PORT` | `8000` | Production |

**How to get Supabase credentials:**
1. Go to [supabase.com](https://supabase.com)
2. Select your project
3. Go to **Settings** → **Database**
4. Copy the **Connection string** (DATABASE_URL)
5. Go to **Settings** → **API**
6. Copy the **service_role** key (SUPABASE_KEY)

---

### Step 6: Update Backend CORS Configuration

**File:** `app/api/server.py`

Make sure CORS is configured to allow your dashboard:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for now, or specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Your backend already has this configured! ✅

---

### Step 7: Deploy to Vercel

#### Option A: Via Vercel CLI
```bash
vercel --prod
```

#### Option B: Via GitHub (Auto-deploy)
1. Push all changes to GitHub:
```bash
git add .
git commit -m "chore: Add backend deployment config"
git push origin main
```

2. Vercel will auto-deploy

#### Option C: Via Dashboard
1. Go to Vercel Dashboard
2. Click **Redeploy** on the latest deployment

---

### Step 8: Verify Deployment

#### Check Backend URL
After deployment, Vercel will give you a URL:
```
https://your-project.vercel.app
```

#### Test Backend Endpoints

Open these URLs in browser or use curl:

```bash
# Health check
curl https://your-project.vercel.app/health

# Root endpoint
curl https://your-project.vercel.app/

# Insights summary
curl https://your-project.vercel.app/api/insights/summary

# Patterns
curl https://your-project.vercel.app/api/insights/patterns

# Segments
curl https://your-project.vercel.app/api/insights/segments
```

Expected response for health check:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-06-28T..."
}
```

---

### Step 9: Update Dashboard to Use Backend

**File:** `dashboard/.env`

Update the `VITE_API_URL` with your backend URL:

```env
VITE_API_URL=https://your-project.vercel.app
VITE_SUPABASE_URL=https://jmcvdljhlqmswsgkextg.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImptY3ZkbGpobHFtc3dzZ2tleHRnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI0NjE0OTksImV4cCI6MjA5ODAzNzQ5OX0.LTiXHF_hTaLWrbPorLw9PuFw9J0TH76dJyWOuUalhwo
```

---

### Step 10: Redeploy Dashboard

1. Push the updated `dashboard/.env` to GitHub
2. Or use Vercel CLI:
```bash
cd dashboard
vercel --prod
```

3. Or manually redeploy in Vercel Dashboard

---

## Troubleshooting

### Issue 1: "Module not found" errors

**Fix:**
- Ensure all files are committed to GitHub
- Check `vercel.json` points to correct files
- Verify `requirements.txt` has all dependencies

### Issue 2: "ImportError: No module named 'app'"

**Fix:**
- Make sure `app/__init__.py` exists
- Check `vercel.py` imports are correct
- Verify directory structure:

```
project/
├── app/
│   ├── __init__.py
│   └── api/
│       └── server.py
├── vercel.py
└── requirements.txt
```

### Issue 3: "500 Internal Server Error"

**Fix:**
- Check Vercel logs for error details
- Verify environment variables are set
- Check database connection string

### Issue 4: "CORS error" in browser

**Fix:**
- Backend already has CORS configured with `allow_origins=["*"]`
- This allows all origins (remove for production if needed)

### Issue 5: Build times out

**Fix:**
- Add build timeout to `vercel.json`:
```json
{
  "buildCommand": "pip install -r requirements.txt && echo 'Build complete'",
  "timeout": 600
}
```

---

## Post-Deployment Checklist

- [ ] Backend deployed at `https://your-project.vercel.app`
- [ ] Health check returns 200 OK
- [ ] All API endpoints respond correctly
- [ ] Database connection is working
- [ ] Environment variables are set
- [ ] Dashboard updated with backend URL
- [ ] Dashboard deployed and working
- [ ] No CORS errors in browser console

---

## Quick Test Commands

```bash
# Test health endpoint
curl https://your-project.vercel.app/health

# Test summary endpoint
curl https://your-project.vercel.app/api/insights/summary | jq

# Test patterns endpoint
curl https://your-project.vercel.app/api/insights/patterns | jq

# Test segments endpoint
curl https://your-project.vercel.app/api/insights/segments | jq
```

---

## Monitoring

### View Logs
```bash
vercel logs
```

Or in Vercel Dashboard → Deployments → Logs

### Check Deployment Status
```bash
vercel ls
vercel ls --prod
```

### View Environment Variables
```bash
vercel env ls
vercel env ls --prod
```

---

## Support

If you encounter any issues:

1. **Check Vercel logs** - Most errors appear here
2. **Verify environment variables** - Make sure all required vars are set
3. **Test locally** - `python app/api/server.py` to test before deploying
4. **Check Supabase connection** - Ensure credentials are correct
5. **Review this guide** - Common issues and solutions are documented above