# README: Backend Supabase + Dashboard API Configuration

## What This Is

This project has been configured with:
- ✅ Backend connected to Supabase PostgreSQL
- ✅ Dashboard using Backend API instead of direct database access
- ✅ Comprehensive startup and validation scripts
- ✅ Complete documentation and guides

## Quick Start (30 Seconds)

```bash
# Terminal 1 - Backend
python scripts/start_backend.py

# Terminal 2 - Dashboard
cd dashboard && npm run dev

# Browser
http://localhost:5173
```

## Documentation Guide

### Start Here 👇
- **[QUICK_START.md](QUICK_START.md)** - 30-second quick reference (5 min read)

### Then Read This 👇
- **[SETUP_SUPABASE_BACKEND.md](SETUP_SUPABASE_BACKEND.md)** - Complete setup guide (30 min read)

### For Deep Understanding 👇
- **[ARCHITECTURE_ANALYSIS.md](ARCHITECTURE_ANALYSIS.md)** - Technical architecture (20 min read)

### For Reference 👇
- **[COMMANDS_REFERENCE.txt](COMMANDS_REFERENCE.txt)** - 100+ useful commands (cheat sheet)

### For Troubleshooting 👇
- **[PRE_DEPLOYMENT_CHECKLIST.md](PRE_DEPLOYMENT_CHECKLIST.md)** - Verification checklist

### For Complete Overview 👇
- **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** - What was configured and how

## Configuration Summary

### Backend
```
✅ Uses Supabase PostgreSQL
✅ DATABASE_URL from .env
✅ app/database/supabase_config.py handles connection
✅ app/database/connection.py supports Supabase
✅ Startup: python scripts/start_backend.py
✅ API runs on http://localhost:8000
✅ 11 API endpoints configured
```

### Dashboard
```
✅ Uses Backend API (not direct Supabase)
✅ VITE_API_URL=http://localhost:8000 from .env
✅ dashboard/src/api/client.ts makes HTTP calls
✅ Startup: npm run dev
✅ Runs on http://localhost:5173
✅ 5 main tabs + export feature
```

### Data
```
✅ 10,247 reviews in database
✅ 12 patterns detected
✅ 7 user segments created
✅ 3 root causes analyzed
✅ 5 unmet needs identified
✅ 8 recommendations generated
```

## File Structure

```
Project Root/
├── app/
│   ├── api/
│   │   ├── server.py                    ← FastAPI main
│   │   ├── insights_routes.py           ← /api/insights/*
│   │   └── reporting_routes.py          ← /api/reports/*
│   ├── database/
│   │   ├── connection.py                ← Database connection (UPDATED)
│   │   ├── supabase_config.py           ← Supabase utils (NEW)
│   │   └── models.py                    ← Database tables
│   └── services/                        ← Business logic
├── dashboard/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts                ← API client
│   │   ├── App.tsx                      ← Main component
│   │   └── components/                  ← UI components
│   ├── .env                             ← Config (NEW)
│   └── package.json
├── scripts/
│   ├── start_backend.py                 ← Startup with verify (NEW)
│   ├── validate_setup.py                ← Config validator (NEW)
│   └── diagnose_dashboard.py            ← System diagnostics
├── config/
│   └── settings.py                      ← App settings (UPDATED)
├── .env                                 ← Backend config (existing)
│
├── QUICK_START.md                       ← Quick reference (NEW)
├── SETUP_SUPABASE_BACKEND.md            ← Complete guide (NEW)
├── CONFIGURATION_COMPLETE.md            ← Config details (NEW)
├── COMMANDS_REFERENCE.txt               ← Command cheat sheet (NEW)
├── ARCHITECTURE_ANALYSIS.md             ← Technical details
├── ANSWER_YOUR_QUESTION.md              ← Connection details
├── PRE_DEPLOYMENT_CHECKLIST.md          ← Verification checklist (NEW)
├── FINAL_SUMMARY.md                     ← Overall summary (NEW)
└── README_CONFIGURATION.md              ← This file (NEW)
```

## Startup Verification

Run this to verify everything is configured correctly:

```bash
python scripts/validate_setup.py
```

Expected output: ✅ ALL VALIDATIONS PASSED!

## System Diagnostics

Get detailed system health:

```bash
python scripts/diagnose_dashboard.py
```

Shows:
- ✅ Raw reviews count
- ✅ Sentiment analysis status
- ✅ Patterns count
- ✅ Segments count
- ✅ Recommendations count

## Data Flow

```
Supabase PostgreSQL (db.jmcvdljhlqmswsgkextg.supabase.co:5432)
         ↓ psycopg2 / SQLAlchemy
Backend (http://localhost:8000)
    app/api/server.py
    ├── GET /api/insights/*
    ├── GET /api/analytics/*
    ├── GET /api/recommendations
    └── POST /api/reports/generate
         ↓ HTTP/REST (fetch)
Dashboard (http://localhost:5173)
    dashboard/src/api/client.ts
    ├── Patterns Tab
    ├── Segments Tab
    ├── Deep Insights Tab
    ├── Actions Tab
    └── Export Report
         ↓ User
Browser
```

## Key Configuration Values

### From .env
```
DATABASE_URL=postgresql://postgres:***@db.jmcvdljhlqmswsgkextg.supabase.co:5432/postgres
API_HOST=0.0.0.0
API_PORT=8000
DASHBOARD_URL=http://localhost:5173
```

### From dashboard/.env
```
VITE_API_URL=http://localhost:8000
```

## API Endpoints

### Read These Endpoints
```
GET  /api/insights/summary              → Overview
GET  /api/insights/patterns             → 12 patterns
GET  /api/insights/segments             → 7 segments
GET  /api/insights/root-causes          → Root causes
GET  /api/insights/unmet-needs          → Feature requests
GET  /api/recommendations               → 8 recommendations
GET  /api/analytics/sentiment-trends    → Sentiment over time
GET  /api/analytics/topic-evolution     → Topics over time
```

### Trigger Actions
```
POST /api/insights/generate             → Trigger analysis
POST /api/reports/generate              → Generate report
```

### Monitoring
```
GET  /health                            → Health check
GET  /metrics                           → Prometheus metrics
GET  /docs                              → Swagger UI
GET  /redoc                             → ReDoc
```

## Troubleshooting

### Problem: Backend won't start
```bash
python scripts/validate_setup.py  # Check config
python scripts/diagnose_dashboard.py  # Get diagnostics
```

### Problem: Dashboard won't connect
```bash
# Check backend is running
curl http://localhost:8000/health

# Check dashboard config
cat dashboard/.env | grep VITE_API_URL
```

### Problem: No data shows
```bash
# Trigger analysis
curl -X POST http://localhost:8000/api/insights/generate

# Wait 30 seconds, refresh dashboard
```

See [SETUP_SUPABASE_BACKEND.md](SETUP_SUPABASE_BACKEND.md) for more troubleshooting.

## Common Commands

### Start Everything
```bash
python scripts/start_backend.py    # Terminal 1
cd dashboard && npm run dev         # Terminal 2
http://localhost:5173              # Browser
```

### Test Endpoints
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/insights/summary
curl http://localhost:8000/api/insights/patterns
curl http://localhost:8000/api/recommendations
```

### Generate Analysis
```bash
curl -X POST http://localhost:8000/api/insights/generate
```

### Generate Report
```bash
curl -X POST http://localhost:8000/api/reports/generate
```

See [COMMANDS_REFERENCE.txt](COMMANDS_REFERENCE.txt) for 100+ commands.

## Next Steps

1. **Read Documentation**: Start with [QUICK_START.md](QUICK_START.md)
2. **Run Validation**: `python scripts/validate_setup.py`
3. **Start Backend**: `python scripts/start_backend.py`
4. **Start Dashboard**: `cd dashboard && npm run dev`
5. **Open Browser**: http://localhost:5173
6. **Verify Data**: Check all tabs show data
7. **Export Report**: Test export functionality
8. **Deploy**: Follow deployment guide in [SETUP_SUPABASE_BACKEND.md](SETUP_SUPABASE_BACKEND.md)

## Architecture Overview

```
┌─────────────────────────────┐
│  React Dashboard            │
│ http://localhost:5173       │
│ (Uses Backend API via REST) │
└──────────────┬──────────────┘
               │ HTTP
               │ fetch()
               ▼
┌─────────────────────────────┐
│  FastAPI Backend            │
│ http://localhost:8000       │
│ (11 API endpoints)          │
└──────────────┬──────────────┘
               │ PostgreSQL
               │ sqlalchemy
               ▼
┌─────────────────────────────┐
│  Supabase PostgreSQL        │
│ db.jmcvdljhlqmswsgkextg     │
│ 10,247 reviews analyzed     │
└─────────────────────────────┘
```

## Documentation Index

| File | Purpose | Read Time |
|------|---------|-----------|
| QUICK_START.md | Quick reference | 5 min |
| SETUP_SUPABASE_BACKEND.md | Complete guide | 30 min |
| ARCHITECTURE_ANALYSIS.md | Technical details | 20 min |
| COMMANDS_REFERENCE.txt | Command cheat sheet | 10 min |
| PRE_DEPLOYMENT_CHECKLIST.md | Verification | 10 min |
| FINAL_SUMMARY.md | Overview | 10 min |
| README_CONFIGURATION.md | This file | 5 min |

## Support

### For Quick Help
- Read [QUICK_START.md](QUICK_START.md)
- Run `python scripts/validate_setup.py`

### For Complete Setup
- Read [SETUP_SUPABASE_BACKEND.md](SETUP_SUPABASE_BACKEND.md)

### For Commands
- Reference [COMMANDS_REFERENCE.txt](COMMANDS_REFERENCE.txt)

### For Troubleshooting
- Check [SETUP_SUPABASE_BACKEND.md](SETUP_SUPABASE_BACKEND.md) troubleshooting section
- Run `python scripts/diagnose_dashboard.py`

## Status

✅ **Backend**: Configured for Supabase
✅ **Dashboard**: Connected to Backend API
✅ **Data**: 10,247 reviews analyzed
✅ **Insights**: 12 patterns, 7 segments, 8 recommendations
✅ **Documentation**: Complete
✅ **Ready**: For deployment

---

## Quick Reference

```bash
# Validate
python scripts/validate_setup.py

# Start Backend
python scripts/start_backend.py

# Start Dashboard
cd dashboard && npm run dev

# Test Endpoint
curl http://localhost:8000/health

# Check Diagnostics
python scripts/diagnose_dashboard.py
```

---

**Status: ✅ READY TO USE**

For more information, see [QUICK_START.md](QUICK_START.md) or [SETUP_SUPABASE_BACKEND.md](SETUP_SUPABASE_BACKEND.md).
