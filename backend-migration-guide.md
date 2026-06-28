# 🚀 Moving Backend to Separate Repository

This guide helps you move your FastAPI backend to a separate GitHub repository.

---

## Step 1: Create New Backend Repository

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `spotify-backend` (or your preferred name)
3. Public/Private: Choose your preference
4. Click **Create repository**

---

## Step 2: Prepare Backend Files

The following files should be moved to the new backend repository:

### Core Backend Files (Keep in backend repo):
```
app/
├── api/
│   ├── server.py
│   ├── insights_routes.py
│   ├── reporting_routes.py
│   ├── monitoring.py
│   └── __init__.py
├── connectors/
├── database/
│   ├── connection.py
│   ├── models.py
│   ├── supabase_config.py
│   └── __init__.py
├── models/
├── services/
└── __init__.py

config/
└── settings.py

requirements.txt
vercel.py
vercel-build.sh
vercel.json

LICENSE
README.md
```

### Files to Remove/Exclude:
- `dashboard/` - Keep this in your main repo
- `docs/` - Keep in main repo
- `.github/` - Keep in main repo (or move if needed)
- `scripts/` - Keep in main repo (or move if needed)
- `supabase/` - Keep in main repo

---

## Step 3: Create New Backend Repo Structure

### Create `backend/vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "vercel.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "vercel.py"
    }
  ]
}
```

### Create `backend/vercel.py`:

```python
"""
Vercel Serverless Function Entry Point for FastAPI Backend
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.api.server import app

handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Create `backend/requirements.txt`:

```txt
# Core dependencies
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
```

---

## Step 4: Initialize New Backend Repository

### Option A: Create New Repo from Scratch

```bash
mkdir spotify-backend
cd spotify-backend

# Copy backend files
cp -r ../"Graduation Project - Spotify"/app .
cp -r ../"Graduation Project - Spotify"/config .
cp ../"Graduation Project - Spotify"/vercel.py .
cp ../"Graduation Project - Spotify"/vercel.json .
cp ../"Graduation Project - Spotify"/requirements.txt .
cp ../"Graduation Project - Spotify"/README-backend.md .

git init
git add .
git commit -m "Initial backend commit"
git branch -m main
git remote add origin https://github.com/YOUR_USERNAME/spotify-backend.git
git push -u origin main
```

### Option B: Use GitHub CLI

```bash
# Create new repo
gh repo create spotify-backend --public --source=. --remote=backend-origin

# Push backend files
git subtree push --prefix=backend backend-origin main
```

---

## Step 5: Set Environment Variables on Vercel

For your new backend repo, set these environment variables in Vercel:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `postgresql://postgres:Blo$$om26937791@db.jmcvdljhlqmswsgkextg.supabase.co:5432/postgres` |
| `SUPABASE_URL` | `https://jmcvdljhlqmswsgkextg.supabase.co` |
| `SUPABASE_KEY` | `eyJhbGc...` (your service_role key) |
| `OPENAI_API_KEY` | `sk-...` (your OpenAI key) |

---

## Step 6: Deploy Backend to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click **New Project**
3. Import your new `spotify-backend` repo
4. Set environment variables
5. Click **Deploy**

---

## Step 7: Update Dashboard to Use New Backend

Update your dashboard's `dashboard/.env`:

```env
VITE_API_URL=https://your-new-backend.vercel.app
```

---

## Step 8: Update Main Repository

In your main repository (`spotify_review`), remove backend files:

```bash
# Remove backend folder
rm -rf app/
rm -rf config/
rm vercel.py
rm vercel.json
rm vercel-build.sh

# Update requirements.txt (remove backend-specific deps if needed)
# Or create a separate requirements file for dashboard

git add .
git commit -m "Remove backend, move to separate repository"
git push origin main
```

---

## Step 9: Test Everything

1. **Test Backend:**
   ```
   https://your-backend.vercel.app/health
   ```

2. **Test Dashboard:**
   - Visit your dashboard
   - Check browser console for API calls
   - Verify data loads correctly

---

## Summary

### Before
```
spotify_review/ (backend + dashboard)
├── app/ (backend)
├── dashboard/ (frontend)
├── vercel.py
└── vercel.json
```

### After
```
spotify_review/ (dashboard only)
└── dashboard/

spotify-backend/ (backend only)
├── app/
├── vercel.py
└── vercel.json
```

---

## Files to Keep in Main Repo (Dashboard)

- `dashboard/`
- `scripts/`
- `docs/`
- `supabase/`
- `.github/`
- All documentation files

## Files to Move to Backend Repo

- `app/`
- `config/`
- `vercel.py`
- `vercel.json`
- `vercel-build.sh`
- `requirements.txt`

---

## Need Help?

If you encounter any issues:
1. Check Vercel logs for build errors
2. Verify environment variables are set
3. Test backend endpoints directly
4. Check CORS configuration
