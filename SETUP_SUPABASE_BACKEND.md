# Setup Guide: Supabase Backend + Dashboard API Integration

## Overview

This guide configures:
1. ✅ Backend to use Supabase PostgreSQL database
2. ✅ Dashboard to communicate with backend API
3. ✅ Proper connection pooling and error handling
4. ✅ Startup verification and health checks

---

## Step 1: Verify Environment Variables

### Backend Configuration (.env)

Ensure these variables are set:

```env
# Supabase Database Connection
DATABASE_URL=postgresql://postgres:Blo$$om26937791@db.jmcvdljhlqmswsgkextg.supabase.co:5432/postgres
DB_HOST=db.jmcvdljhlqmswsgkextg.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=Blo$$om26937791

# Supabase API Configuration (optional, for REST API access)
VITE_SUPABASE_URL=https://jmcvdljhlqmswsgkextg.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Backend API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Dashboard URL
DASHBOARD_URL=http://localhost:5173

# LLM Configuration (optional)
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
```

### Dashboard Configuration (dashboard/.env)

```env
# Backend API Endpoint
VITE_API_URL=http://localhost:8000

# Supabase Configuration (currently unused)
VITE_SUPABASE_URL=https://jmcvdljhlqmswsgkextg.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Step 2: Install Dependencies

### Backend Dependencies

```bash
cd "c:\Graduation Project - Spotify"

# Core dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary loguru pydantic-settings

# Supabase support (optional, for REST API)
pip install supabase

# Data analysis
pip install pandas numpy

# AI/ML
pip install openai anthropic

# All in one
pip install -r requirements.txt
```

### Dashboard Dependencies

```bash
cd dashboard

# Install Node dependencies
npm install

# Verify environment file exists
# Should have .env with VITE_API_URL=http://localhost:8000
```

---

## Step 3: Start the Backend

### Option A: Using the Startup Script (Recommended)

```bash
cd "c:\Graduation Project - Spotify"

# Run the startup script
python scripts/start_backend.py
```

**What this does:**
1. ✅ Verifies all configuration
2. ✅ Tests database connection
3. ✅ Creates tables if needed
4. ✅ Shows detailed startup information
5. ✅ Starts the FastAPI server

**Expected Output:**
```
============================================================
BACKEND STARTUP - Configuration Verification
============================================================

1. Database Configuration:
   ✓ DATABASE_URL set: postgresql://postgres:***@db.jmcvd...

2. Supabase Configuration:
   ✓ SUPABASE_URL: https://jmcvdljhlqmswsgkextg.supabase.co
   ✓ SUPABASE_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

3. API Configuration:
   ✓ API Host: 0.0.0.0
   ✓ API Port: 8000
   ✓ Dashboard URL: http://localhost:5173

✅ Configuration verification passed

============================================================
DATABASE CONNECTION VERIFICATION
============================================================

1. Initializing database connection...
✓ Database connection established

2. Verifying tables...
   ✓ raw_reviews: 10247 rows
   ✓ sentiment_analysis: 9854 rows
   ✓ topic_analysis: 9854 rows
   ✓ pattern_insights: 12 rows
   ✓ user_segments: 7 rows
   ✓ recommendations: 8 rows

✅ Database verification passed

============================================================
STARTING FASTAPI SERVER
============================================================

🚀 Starting server on http://0.0.0.0:8000
📊 API Documentation: http://0.0.0.0:8000/docs
🎨 Dashboard: http://localhost:5173

Server is running. Press Ctrl+C to stop.
```

### Option B: Manual Start

```bash
cd "c:\Graduation Project - Spotify"

# Direct start
python -m app.api.server

# Or with specific host/port
python -m uvicorn app.api.server:app --host 0.0.0.0 --port 8000 --reload
```

---

## Step 4: Start the Dashboard

In a new terminal:

```bash
cd "c:\Graduation Project - Spotify\dashboard"

# Start development server
npm run dev

# Or build for production
npm run build
npm run preview
```

**Expected Output:**
```
  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

---

## Step 5: Verify Everything is Connected

### Test 1: Backend Health Check

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-01-20T10:30:45.123456"
}
```

### Test 2: API Summary Endpoint

```bash
curl http://localhost:8000/api/insights/summary
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "total_reviews": 10247,
    "pattern_count": 12,
    "segment_count": 7,
    "root_cause_count": 3,
    "unmet_need_count": 5,
    "key_findings": [...],
    "top_unmet_needs": [...]
  }
}
```

### Test 3: Dashboard Connection

1. Open http://localhost:5173 in browser
2. Open DevTools → Network tab
3. Look for requests to `http://localhost:8000/api/...`
4. All should show status 200 ✅

---

## Step 6: Architecture Verification

### Verify Data Flow

```
✅ Dashboard (http://localhost:5173)
    ↓ HTTP/REST (VITE_API_URL)
✅ Backend (http://localhost:8000)
    ├─ GET /api/insights/summary
    ├─ GET /api/insights/patterns
    ├─ GET /api/insights/segments
    └─ ... 10 total API endpoints
    ↓ PostgreSQL (DATABASE_URL)
✅ Supabase PostgreSQL
    ├─ pattern_insights (12 rows)
    ├─ user_segments (7 rows)
    ├─ recommendations (8 rows)
    └─ ... 9 more tables
```

### Check Table Population

```bash
# Run diagnostic script
python scripts/diagnose_dashboard.py

# Expected output showing:
# ✅ Raw reviews: 10,247
# ✅ Patterns: 12
# ✅ Segments: 7
# ✅ Recommendations: 8
```

---

## Step 7: Generate Insights (First Time)

If database tables are empty, trigger analysis:

```bash
# Via API
curl -X POST http://localhost:8000/api/insights/generate

# Or via backend shell
python -c "from app.services.insight_engine import InsightEngine; InsightEngine().run()"
```

**Monitor Progress:**
```bash
# Watch logs
tail -f logs/backend.log | grep -E "Phase 3|Persisted|Pattern|Segment"
```

---

## Step 8: Test Export/Report Feature

### Generate Report

```bash
curl -X POST http://localhost:8000/api/reports/generate \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "generated_at": "2025-01-20T10:35:12.456789",
    "executive_summary": {...},
    "key_findings": [...],
    "recommendations": [...]
  },
  "file_path": "./reports/report_executive_20250120_103512.md"
}
```

### Check Report File

```bash
# Files should be created in ./reports/
ls -lah reports/
# Output: report_executive_20250120_*.md
```

---

## Configuration Files Summary

### Files Created/Modified

| File | Purpose | Location |
|------|---------|----------|
| `.env` | Backend configuration | Root |
| `dashboard/.env` | Dashboard configuration | dashboard/ |
| `app/database/supabase_config.py` | Supabase utilities | app/database/ |
| `app/database/connection.py` | Updated for Supabase | app/database/ |
| `config/settings.py` | Added Supabase settings | config/ |
| `scripts/start_backend.py` | Startup script | scripts/ |

---

## Troubleshooting

### Issue: "Database connection refused"

**Solution:**
```bash
# 1. Verify DATABASE_URL in .env
echo $DATABASE_URL

# 2. Test connection directly
psql postgresql://postgres:Blo$$om26937791@db.jmcvdljhlqmswsgkextg.supabase.co:5432/postgres

# 3. Check firewall/network
ping db.jmcvdljhlqmswsgkextg.supabase.co
```

### Issue: "Dashboard can't reach backend"

**Solution:**
```bash
# 1. Verify VITE_API_URL in dashboard/.env
cat dashboard/.env | grep VITE_API_URL

# 2. Test backend directly
curl http://localhost:8000/health

# 3. Check CORS in browser DevTools
# Look for CORS errors in Console tab
```

### Issue: "No data showing on dashboard"

**Solution:**
```bash
# 1. Check if analysis has run
python scripts/diagnose_dashboard.py

# 2. Trigger analysis if tables are empty
curl -X POST http://localhost:8000/api/insights/generate

# 3. Wait for completion (5-30 seconds)

# 4. Refresh dashboard
# Data should now appear
```

### Issue: "LLM recommendations are generic"

**Solution:**
```bash
# 1. Set OpenAI API key
export OPENAI_API_KEY=sk-...

# 2. Or set Anthropic key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Restart backend
python scripts/start_backend.py

# 4. Regenerate insights
curl -X POST http://localhost:8000/api/insights/generate
```

---

## Monitoring and Maintenance

### Daily Health Check

```bash
# Quick status check
curl http://localhost:8000/api/insights/summary | python -m json.tool

# Should return non-zero counts for all metrics
```

### Weekly Full Diagnostics

```bash
# Complete system check
python scripts/diagnose_dashboard.py

# Should show all tables populated with data
```

### Performance Monitoring

```bash
# View metrics
curl http://localhost:8000/metrics

# Monitor logs
tail -f logs/backend.log

# Check database usage
psql $DATABASE_URL -c "SELECT tablename, pg_size_pretty(pg_total_relation_size(tablename)) FROM pg_tables WHERE tablename NOT LIKE 'pg_%' ORDER BY pg_total_relation_size(tablename) DESC;"
```

---

## Production Deployment Checklist

Before deploying to production:

- [ ] Set `API_HOST` to production IP
- [ ] Set `DASHBOARD_URL` to production domain
- [ ] Enable HTTPS on backend (use reverse proxy like nginx)
- [ ] Set strong `API_AUTH_TOKEN` if needed
- [ ] Configure LLM keys (OpenAI/Anthropic)
- [ ] Set up database backups (Supabase handles this)
- [ ] Configure monitoring and alerts
- [ ] Test disaster recovery
- [ ] Load test the system
- [ ] Document any custom configurations

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                     DEPLOYMENT ARCHITECTURE                  │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────┐         ┌────────────────────┐     │
│  │  React Dashboard    │         │   FastAPI Backend  │     │
│  │ (http://localhost   │◄────────►│ (http://localhost: │     │
│  │     :5173)          │  HTTP    │     8000)          │     │
│  │                     │          │                    │     │
│  │ • Patterns Tab      │          │ • /api/insights/*  │     │
│  │ • Segments Tab      │          │ • /api/analytics/*  │     │
│  │ • Deep Insights     │          │ • /api/recommendations │
│  │ • Actions Tab       │          │ • /api/reports/*   │     │
│  │ • Export Report     │          │                    │     │
│  └─────────────────────┘          └────────┬───────────┘     │
│                                             │                 │
│                      PostgreSQL Protocol    │                 │
│                      TCP:5432               │                 │
│                                             ▼                 │
│                          ┌──────────────────────────┐         │
│                          │  Supabase PostgreSQL     │         │
│                          │ db.jmcvdljhlqmswsgkextg  │         │
│                          │                          │         │
│                          │  Tables:                 │         │
│                          │  • raw_reviews           │         │
│                          │  • sentiment_analysis    │         │
│                          │  • topic_analysis        │         │
│                          │  • pattern_insights      │         │
│                          │  • user_segments         │         │
│                          │  • recommendations       │         │
│                          │  • generated_reports     │         │
│                          │  + 2 more tables         │         │
│                          └──────────────────────────┘         │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Commands Reference

### Quick Start

```bash
# Terminal 1: Backend
cd "c:\Graduation Project - Spotify"
python scripts/start_backend.py

# Terminal 2: Dashboard
cd "c:\Graduation Project - Spotify\dashboard"
npm run dev

# Terminal 3: Test/Monitoring
python scripts/diagnose_dashboard.py
```

### API Testing

```bash
# Health check
curl http://localhost:8000/health

# Get summary
curl http://localhost:8000/api/insights/summary

# Get patterns
curl http://localhost:8000/api/insights/patterns

# Get segments
curl http://localhost:8000/api/insights/segments

# Get recommendations
curl http://localhost:8000/api/recommendations

# Trigger analysis
curl -X POST http://localhost:8000/api/insights/generate

# Generate report
curl -X POST http://localhost:8000/api/reports/generate
```

### Database Access

```bash
# Connect to database
psql $DATABASE_URL

# Query tables
SELECT COUNT(*) FROM pattern_insights;
SELECT COUNT(*) FROM user_segments;
SELECT * FROM recommendations LIMIT 5;
```

---

## Next Steps

1. ✅ Start backend using `scripts/start_backend.py`
2. ✅ Start dashboard using `npm run dev`
3. ✅ Verify connection with health check
4. ✅ Generate insights if needed
5. ✅ Open dashboard and browse tabs
6. ✅ Export report to test functionality

**Status: Ready for Deployment ✅**
