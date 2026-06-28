# Quick Start: Backend + Dashboard

## Prerequisites

✅ Python 3.8+ installed
✅ Node.js 16+ installed  
✅ .env file with Supabase credentials
✅ Supabase account with PostgreSQL database

---

## 30-Second Startup

### 1. Install Python Dependencies

```bash
cd "c:\Graduation Project - Spotify"
pip install fastapi uvicorn sqlalchemy psycopg2-binary loguru pydantic-settings
```

### 2. Install Dashboard Dependencies

```bash
cd dashboard
npm install
cd ..
```

### 3. Start Backend

**Terminal 1:**
```bash
python scripts/start_backend.py
```

**Expected Output:**
```
🚀 Starting server on http://0.0.0.0:8000
📊 API Documentation: http://0.0.0.0:8000/docs
🎨 Dashboard: http://localhost:5173

Server is running. Press Ctrl+C to stop.
```

### 4. Start Dashboard

**Terminal 2:**
```bash
cd dashboard
npm run dev
```

**Expected Output:**
```
➜  Local:   http://localhost:5173/
```

### 5. Open Browser

```
http://localhost:5173
```

---

## What You Should See

### ✅ Dashboard Loads
- Executive Summary with metrics
- Patterns tab showing 10+ detected patterns
- Segments tab showing 5+ user segments
- Deep Insights with root causes
- Actions tab with 5-8 recommendations

### ✅ Data Flows From:
Supabase → Backend → Dashboard

### ✅ API Working
Open http://localhost:8000/docs to see all API endpoints

---

## Verify Connection

### Test 1: Backend Health
```bash
curl http://localhost:8000/health
```
Should return: `{"status": "healthy", ...}`

### Test 2: Dashboard Data
```bash
curl http://localhost:8000/api/insights/summary
```
Should return JSON with pattern_count, segment_count, etc.

### Test 3: Browser Console
Open DevTools (F12) → Network tab → Reload
Should see 10 requests to `http://localhost:8000/api/...`

---

## If No Data Shows

### Option 1: Trigger Analysis

```bash
curl -X POST http://localhost:8000/api/insights/generate
```

Wait 30 seconds, then refresh dashboard.

### Option 2: Run Diagnostics

```bash
python scripts/diagnose_dashboard.py
```

Shows what data is in database and any issues.

---

## Common Issues

| Issue | Solution |
|-------|----------|
| "Cannot connect to backend" | Check backend is running on 8000 |
| "No data on dashboard" | Run: `curl -X POST http://localhost:8000/api/insights/generate` |
| "Dashboard won't load" | Check npm is running, try `npm run dev` again |
| "Database connection error" | Verify DATABASE_URL in .env has Supabase credentials |
| "API returns 404" | Make sure you're calling `http://localhost:8000/api/...` not other URLs |

---

## Full Setup Reference

For complete setup with all options, see: **SETUP_SUPABASE_BACKEND.md**

For architecture details, see: **ARCHITECTURE_ANALYSIS.md**

---

## Project Structure

```
Project Root
├── app/
│   ├── api/
│   │   ├── server.py          ← FastAPI main app
│   │   ├── insights_routes.py ← /api/insights/* endpoints
│   │   └── reporting_routes.py← /api/recommendations, /api/reports/*
│   ├── database/
│   │   ├── connection.py      ← Supabase connection
│   │   ├── supabase_config.py ← Supabase utilities
│   │   └── models.py          ← Database tables
│   └── services/              ← Business logic
├── dashboard/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts      ← API calls to backend
│   │   ├── App.tsx            ← Main React component
│   │   └── components/        ← Dashboard tabs
│   ├── .env                   ← VITE_API_URL config
│   └── package.json
├── scripts/
│   ├── start_backend.py       ← Startup with verification
│   ├── diagnose_dashboard.py  ← System diagnostics
│   └── ...
├── config/
│   └── settings.py            ← All settings
├── .env                       ← Backend config
└── SETUP_SUPABASE_BACKEND.md  ← Full setup guide
```

---

## API Endpoints

### Insights
- `GET /api/insights/summary` - Overview of all insights
- `GET /api/insights/patterns` - Detected patterns (10+)
- `GET /api/insights/segments` - User segments (5+)
- `GET /api/insights/root-causes` - Root cause analysis
- `GET /api/insights/unmet-needs` - Feature requests
- `POST /api/insights/generate` - Trigger analysis

### Analytics
- `GET /api/analytics/sentiment-trends?days=30` - Sentiment over time
- `GET /api/analytics/topic-evolution?days=30` - Topics over time
- `GET /api/analytics/sentiment-distribution` - Sentiment breakdown
- `GET /api/analytics/top-topics?limit=10` - Top topics

### Recommendations & Reports
- `GET /api/recommendations` - Strategic recommendations
- `GET /api/roadmap` - Product roadmap
- `POST /api/reports/generate` - Generate comprehensive report

---

## Testing Workflow

1. **Start backend**: `python scripts/start_backend.py`
2. **Start dashboard**: `npm run dev` (in dashboard folder)
3. **Open dashboard**: http://localhost:5173
4. **Check data**: Should see patterns, segments, recommendations
5. **Generate insights**: Click "Run AI Analysis" button
6. **Export report**: Click "Export Report" button
7. **Verify**: Check PDF/Markdown has real data

---

## Production Commands

```bash
# Build dashboard
cd dashboard
npm run build

# Start production backend
gunicorn -w 4 -b 0.0.0.0:8000 app.api.server:app

# Or with uvicorn (production)
uvicorn app.api.server:app --host 0.0.0.0 --port 8000
```

---

## Stop/Restart

```bash
# Stop backend: Press Ctrl+C in backend terminal
# Stop dashboard: Press Ctrl+C in dashboard terminal

# Restart backend
python scripts/start_backend.py

# Restart dashboard
cd dashboard && npm run dev
```

---

## Next Steps

After verifying everything works:

1. Read full **SETUP_SUPABASE_BACKEND.md** for advanced options
2. Check **ARCHITECTURE_ANALYSIS.md** for technical details
3. Review **DASHBOARD_FIX_SUMMARY.txt** for what was fixed
4. Deploy to production following deployment checklist

---

**Status: ✅ Ready to Use**

Backend and Dashboard are properly configured and connected to Supabase!
