# 🚀 Complete Vercel Deployment Guide

## Overview

Your **dashboard is already on Vercel** ✅. This guide will help you deploy the **backend API** to Vercel and connect them together.

---

## Architecture After Deployment

```
┌─────────────────────────────────────────────────────────────────┐
│                         Vercel                                  │
│  ┌────────────────────┐         ┌────────────────────────┐     │
│  │  Dashboard (SPA)   │         │   Backend API (FastAPI)│     │
│  │  /dist (React)     │───────> │  /vercel.py (Serverless)│    │
│  └────────────────────┘         └────────────────────────┘     │
│         │                                 │                     │
│         │                                 ▼                     │
│         │                          ┌─────────────────┐         │
│         │                          │   Supabase      │         │
│         │                          │   PostgreSQL    │         │
│         │                          └─────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Prepare Your Project Structure

### Current Structure
```
Graduation Project - Spotify/
├── app/
│   └── api/
│       └── server.py          # Your FastAPI app
├── dashboard/
│   ├── src/
│   └── package.json
├── vercel.json                # ✅ Already exists
├── vercel.py                  # ✅ Created for backend
├── requirements.txt           # ✅ Updated with FastAPI deps
└── ...
```

### What We Added
1. **`vercel.py`** - Vercel serverless entry point for FastAPI
2. **`vercel-backend.json`** - Alternative Vercel config (optional)
3. **Updated `requirements.txt`** - FastAPI + dependencies
4. **Updated `vercel.json`** - Routing configuration

---

## Step 2: Update Vercel Configuration

### Current `vercel.json`
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

This configuration:
- ✅ Serves dashboard from `/dist` (React build)
- ✅ Routes `/api/*` requests to `vercel.py` (FastAPI backend)
- ✅ All other routes go to React app

---

## Step 3: Configure Environment Variables on Vercel

### Go to Vercel Dashboard
1. Visit [vercel.com](https://vercel.com)
2. Select your project
3. Go to **Settings** → **Environment Variables**

### Add These Variables

| Variable Name | Value | Type |
|--------------|-------|------|
| `DATABASE_URL` | `postgresql://postgres:PASSWORD@db.YOUR_PROJECT_ID.supabase.co:5432/postgres` | Production |
| `SUPABASE_URL` | `https://YOUR_PROJECT_ID.supabase.co` | Production |
| `SUPABASE_KEY` | `YOUR_SERVICE_ROLE_KEY` | Production |
| `OPENAI_API_KEY` | `sk-...` | Production |
| `API_HOST` | `0.0.0.0` | Production |
| `API_PORT` | `8000` | Production |

### How to Get Supabase Credentials
1. Go to [supabase.com](https://supabase.com)
2. Select your project
3. Go to **Settings** → **Database**
4. Copy `Connection string` (DATABASE_URL)
5. Go to **Settings** → **API**
6. Copy `service_role` key (SUPABASE_KEY)

---

## Step 4: Deploy Backend to Vercel

### Option A: Deploy via Vercel CLI (Recommended)

```bash
# Install Vercel CLI if not installed
npm i -g vercel

# Deploy backend
vercel --prod

# Or deploy with specific build command
vercel --build-env BUILD_MODE=backend --prod
```

### Option B: Deploy via GitHub Integration

1. Push all changes to GitHub:
```bash
git add .
git commit -m "chore: Add backend deployment config"
git push origin main
```

2. In Vercel Dashboard:
   - Go to **Settings** → **Git**
   - Ensure your repo is connected
   - Vercel will auto-deploy on push

### Option C: Deploy via Dashboard UI

1. In Vercel Dashboard:
   - Go to **Deployments**
   - Click **Redeploy** (if auto-deploy is enabled)
   - Or click **Create Deployment** manually

---

## Step 5: Verify Backend Deployment

### Test Your Backend API

```bash
# Test health endpoint
curl https://your-app.vercel.app/health

# Test root endpoint
curl https://your-app.vercel.app/

# Test insights summary
curl https://your-app.vercel.app/api/insights/summary

# Test patterns
curl https://your-app.vercel.app/api/insights/patterns
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-06-28T..."
}
```

---

## Step 6: Update Dashboard to Use Backend

### Update Dashboard `.env`

```env
VITE_API_URL=https://your-app.vercel.app
VITE_SUPABASE_URL=https://jmcvdljhlqmswsgkextg.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImptY3ZkbGpobHFtc3dzZ2tleHRnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI0NjE0OTksImV4cCI6MjA5ODAzNzQ5OX0.LTiXHF_hTaLWrbPorLw9PuFw9J0TH76dJyWOuUalhwo
```

### Note on CORS

Your backend `app/api/server.py` already has CORS enabled for all origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This is fine for development. For production, update to:
```python
allow_origins=[
    "https://your-app.vercel.app",      # Dashboard
    "https://your-domain.com",           # Custom domain
]
```

---

## Step 7: Redeploy Dashboard

After updating the environment variables:

1. Dashboard will auto-rebuild on Vercel (if GitHub integration is set up)
2. Or manually trigger deployment in Vercel Dashboard
3. Dashboard will now use `https://your-app.vercel.app` as the API backend

---

## Step 8: Test Production Connection

### Check Dashboard
1. Visit `https://your-app.vercel.app`
2. Open browser console (F12)
3. Check for API calls to your backend

### Expected API Calls
```
GET /api/insights/summary          ✅ 200 OK
GET /api/insights/patterns         ✅ 200 OK
GET /api/insights/segments         ✅ 200 OK
GET /api/insights/root-causes      ✅ 200 OK
GET /api/insights/unmet-needs      ✅ 200 OK
GET /api/analytics/...             ✅ 200 OK
```

### If You See Errors

| Error | Solution |
|-------|----------|
| `Failed to fetch` | Backend URL incorrect in `.env` |
| `CORS error` | Update CORS in backend server.py |
| `500 error` | Check backend environment variables |
| `404 error` | Verify backend deployment |

---

## Step 9: Set Up Production Environment Variables

### Backend `.env` (on Vercel)
| Variable | Required | Example |
|----------|----------|---------|
| `DATABASE_URL` | ✅ | `postgresql://...` |
| `SUPABASE_URL` | ✅ | `https://...supabase.co` |
| `SUPABASE_KEY` | ✅ | `eyJhbGc...` |
| `OPENAI_API_KEY` | ✅ | `sk-...` |
| `API_HOST` | ⚠️ | `0.0.0.0` |
| `API_PORT` | ⚠️ | `8000` |

### Dashboard `.env` (on Vercel)
| Variable | Required | Example |
|----------|----------|---------|
| `VITE_API_URL` | ✅ | `https://your-app.vercel.app` |
| `VITE_SUPABASE_URL` | Optional | `https://...` |
| `VITE_REQUEST_TIMEOUT` | Optional | `30000` |

---

## Step 10: Monitor and Debug

### View Logs on Vercel
1. Go to Vercel Dashboard
2. Select your deployment
3. Click **Logs** tab
4. Monitor for errors

### Common Issues

#### 1. Backend Not Found (404)
```
Error: Cannot find module './app/api/server.py'
```
**Fix**: Ensure `vercel.py` is in project root and imports are correct

#### 2. Database Connection Failed
```
Error: connection refused
```
**Fix**: Check `DATABASE_URL` environment variable is set correctly

#### 3. OpenAI API Key Missing
```
Error: OPENAI_API_KEY not set
```
**Fix**: Add `OPENAI_API_KEY` to environment variables

#### 4. CORS Error
```
Access to fetch...has been blocked by CORS policy
```
**Fix**: Backend already has `allow_origins=["*"]` - should work

---

## Quick Reference Commands

### Development
```bash
# Start backend locally
python app/api/server.py

# Start dashboard locally
cd dashboard
npm run dev
```

### Deployment
```bash
# Deploy to Vercel
vercel --prod

# Check deployment status
vercel ls

# View logs
vercel logs
```

### Environment Setup
```bash
# Set local environment variables
source .env

# Or on Windows
. .env
```

---

## Post-Deployment Checklist

- [ ] Backend deployed to Vercel
- [ ] Environment variables configured
- [ ] Dashboard `.env` updated with backend URL
- [ ] Dashboard redeployed
- [ ] All API endpoints working (`/api/insights/summary`, etc.)
- [ ] Data showing correctly on dashboard
- [ ] Report generation working
- [ ] No CORS errors in browser console
- [ ] No 500 errors in Vercel logs
- [ ] Database connection successful

---

## Support

### If Something Goes Wrong

1. **Check Vercel Logs** - Most errors appear here
2. **Verify Environment Variables** - Make sure all required variables are set
3. **Test Backend Directly** - Use curl to test endpoints
4. **Check Supabase Connection** - Verify credentials are correct
5. **Review GitHub Actions** - Check if auto-deploy failed

### Vercel Resources
- [FastAPI on Vercel](https://vercel.com/docs/frameworks/fastapi)
- [Environment Variables](https://vercel.com/docs/environment-variables)
- [Serverless Functions](https://vercel.com/docs/serverless-functions)

### Supabase Resources
- [Connection Strings](https://supabase.com/docs/guides/database/connecting)
- [API Keys](https://supabase.com/docs/guides/platform/api-keys)
