# 🐛 Dashboard Fetching Issues - Troubleshooting Guide

## Common Error Messages

### 1. "Failed to fetch"
**Cause:** Dashboard can't reach the backend API

**Solution:**
- Check if backend is running on port 8000
- Verify `VITE_API_URL` in `dashboard/.env` matches your backend URL
- Check browser console for CORS errors

### 2. "API error: 404"
**Cause:** The endpoint doesn't exist on the backend

**Solution:**
- Ensure backend is deployed correctly
- Verify backend routes match expected paths (`/api/insights/summary`, etc.)

### 3. "API error: 500"
**Cause:** Backend encountered an error

**Solution:**
- Check backend logs
- Verify database connection
- Check environment variables are set

### 4. "Network error" or "Connection refused"
**Cause:** Backend not running or not accessible

**Solution:**
- Start backend: `python app/api/server.py`
- Check if backend is listening on port 8000

---

## Quick Diagnosis Checklist

### 1. Test Backend Directly
```bash
# Check if backend is responding
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","database":"connected","timestamp":"..."}
```

### 2. Check Dashboard Environment
```bash
# In dashboard folder, verify .env
cat dashboard/.env
# Should have: VITE_API_URL=http://localhost:8000 (for local)
```

### 3. Browser Console
Open browser DevTools (F12) → Console tab:
- Look for fetch errors
- Check if requests are going to correct URL
- Check for CORS errors

---

## Vercel Deployment Issues

### Problem: Backend not deployed

**Solution:**
1. Deploy backend to Vercel:
```bash
vercel --prod
```

2. Get your backend URL from Vercel dashboard:
```
https://your-app.vercel.app
```

3. Update `dashboard/.env`:
```env
VITE_API_URL=https://your-app.vercel.app
```

4. Redeploy dashboard

### Problem: Backend environment variables missing

**Solution:**
In Vercel Dashboard → Settings → Environment Variables, add:
```
DATABASE_URL
SUPABASE_URL
SUPABASE_KEY
OPENAI_API_KEY
```

---

## Local Development Setup

### Step 1: Start Backend
```bash
python app/api/server.py
```

Backend should start at `http://localhost:8000`

### Step 2: Start Dashboard
```bash
cd dashboard
npm run dev
```

Dashboard should start at `http://localhost:5173`

### Step 3: Verify Connection
Open `http://localhost:5173` in browser and check:
- Data loads correctly
- No errors in browser console
- API calls show 200 OK status

---

## Network Troubleshooting

### Test Backend API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Summary endpoint
curl http://localhost:8000/api/insights/summary

# Patterns endpoint
curl http://localhost:8000/api/insights/patterns

# Segments endpoint
curl http://localhost:8000/api/insights/segments

# Root causes endpoint
curl http://localhost:8000/api/insights/root-causes

# Unmet needs endpoint
curl http://localhost:8000/api/insights/unmet-needs
```

### Check if Backend is Listening
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

---

## CORS Issues

If you see CORS errors in browser console:

**Backend needs CORS configured:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-vercel-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Your backend already has this configured!

---

## Database Connection Issues

### Backend logs show:
```
Error: connection refused
```

**Fix:**
1. Verify Supabase credentials in `.env`:
```
DATABASE_URL=postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres
```

2. Check Supabase is accessible:
```bash
psql "postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres"
```

3. Verify database tables exist:
```sql
SELECT * FROM sentiment_analysis LIMIT 5;
SELECT * FROM topic_analysis LIMIT 5;
```

---

## Environment Variables Missing

### Symptoms:
- Backend starts but fails to process data
- Logs show "OPENAI_API_KEY not set"

**Solution:**
Create `.env` file with required variables:
```env
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_KEY=...
OPENAI_API_KEY=sk-...
```

---

## Vercel-Specific Issues

### Problem: Dashboard builds but fetch fails

**Check Vercel logs:**
1. Go to Vercel Dashboard → Deployments → Logs
2. Look for build errors
3. Check if environment variables are set

### Problem: Environment variables not updating

**Solution:**
1. In Vercel Dashboard → Settings → Environment Variables
2. Delete old variables
3. Re-add new variables
4. Redeploy

---

## Debug Mode

### Add Debug Logging to Dashboard

Temporarily update `dashboard/src/api/client.ts`:
```typescript
async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  console.log('🔍 Fetching:', `${API_BASE}${path}`);
  const res = await fetch(`${API_BASE}${path}`, options);
  console.log('📥 Response:', res.status, res.ok);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const json = await res.json();
  console.log('📝 Data:', json);
  return json.data ?? json;
}
```

---

## Need Help?

1. **Check browser console** - Most errors appear here
2. **Check backend logs** - Look for database/LLM errors
3. **Test endpoints directly** - Use curl or Postman
4. **Verify environment variables** - Ensure all required vars are set
5. **Check Vercel logs** - For deployment issues
