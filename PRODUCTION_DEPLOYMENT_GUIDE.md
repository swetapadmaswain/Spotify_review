# Complete Production Deployment Guide

This guide provides step-by-step instructions to deploy the entire Spotify Insights project to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Database Setup (Supabase)](#step-1-database-setup-supabase)
3. [Step 2: Backend Deployment](#step-2-backend-deployment)
4. [Step 3: Dashboard Deployment](#step-3-dashboard-deployment)
5. [Step 4: Testing & Verification](#step-4-testing--verification)
6. [Step 5: Monitoring & Maintenance](#step-5-monitoring--maintenance)

---

## Prerequisites

Before starting, ensure you have:

- **Accounts Created:**
  - [ ] Supabase account (free tier works)
  - [ ] Vercel account (free tier works)
  - [ ] GitHub account (for Git integration)

- **Tools Installed:**
  - [ ] Node.js 18+ ([Download](https://nodejs.org/))
  - [ ] Python 3.9+ ([Download](https://www.python.org/))
  - [ ] Git ([Download](https://git-scm.com/))
  - [ ] Vercel CLI: `npm install -g vercel`

- **Project Files Ready:**
  - [ ] All code committed to Git
  - [ ] `.env.example` files exist
  - [ ] Database migrations ready

---

## Step 1: Database Setup (Supabase)

### 1.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign in or create an account
4. Click "New Project"
5. Fill in project details:
   - **Name**: `spotify-insights-db`
   - **Database Password**: Generate a strong password (save it!)
   - **Region**: Choose closest to your users
   - **Pricing Plan**: Free tier
6. Click "Create new project"
7. Wait 2-3 minutes for project to initialize

### 1.2 Get Database Credentials

1. In your Supabase project, go to **Settings** → **Database**
2. Copy these credentials (save them securely):
   - **Project URL**: `https://xxxxx.supabase.co`
   - **Anon Public Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **Service Role Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (keep secret!)

### 1.3 Run Database Migrations

1. In Supabase dashboard, go to **SQL Editor**
2. Click "New Query"
3. Copy and run each migration file from `supabase/migrations/`:
   - `001_initial_schema.sql`
   - `002_seed_insights.sql`
   - `003_fix_rls_policies.sql`
   - `004_add_phase2_tables.sql`
   - `005_add_phase3_insight_tables.sql`

4. Verify tables created:
   - Go to **Table Editor**
   - You should see: `raw_reviews`, `sentiment_analysis`, `pattern_insights`, etc.

### 1.4 Configure Database Security

1. Go to **Authentication** → **Policies**
2. Ensure Row Level Security (RLS) is enabled
3. Review policies in `003_fix_rls_policies.sql`

### 1.5 Test Database Connection

Create a test script to verify connection:

```python
# test_db_connection.py
import os
from supabase import create_client

url = "your-supabase-url"
key = "your-anon-key"

client = create_client(url, key)

# Test connection
response = client.table('raw_reviews').select('count').execute()
print(f"Database connected! Reviews count: {response}")
```

---

## Step 2: Backend Deployment

### 2.1 Prepare Backend Code

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Test locally:
```bash
python app.py
```
- Visit `http://localhost:8000/docs` to see API documentation
- Test a few endpoints to ensure they work

### 2.2 Configure Environment Variables

Create `.env` file in `backend/` directory:

```env
# Database
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.jmcvdljhl.supabase.co:5432/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://your-dashboard-domain.vercel.app,https://localhost:5173

# Environment
ENVIRONMENT=production
DEBUG=false
```

**Important**: Replace placeholders with your actual values from Step 1.2.

### 2.3 Prepare for Vercel Deployment

Create `vercel.json` in backend directory:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "DATABASE_URL": "@database_url",
    "SUPABASE_URL": "@supabase_url",
    "SUPABASE_ANON_KEY": "@supabase_anon_key"
  }
}
```

### 2.4 Deploy Backend to Vercel

**Option A: Using Vercel CLI**

1. Login to Vercel:
```bash
vercel login
```

2. Deploy from backend directory:
```bash
cd backend
vercel
```

3. Follow prompts:
   - **Set up and deploy?** → Yes
   - **Which scope?** → Your account
   - **Link to existing project?** → No
   - **Project name**: `spotify-insights-backend`
   - **Directory**: `./`
   - **Want to modify settings?** → No

4. Add environment variables in Vercel dashboard:
   - Go to project settings → Environment Variables
   - Add all variables from `.env` file

5. Redeploy:
```bash
vercel --prod
```

**Option B: Using Vercel Dashboard**

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your Git repository
4. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `backend`
   - **Build Command**: (leave empty for Python)
   - **Output Directory**: (leave empty)
5. Add environment variables from `.env`
6. Click "Deploy"

### 2.5 Verify Backend Deployment

1. Vercel will provide a URL: `https://spotify-insights-backend.vercel.app`
2. Test the API:
```bash
curl https://your-backend-url.vercel.app/api/insights/summary
```

3. Check API documentation:
```
https://your-backend-url.vercel.app/docs
```

---

## Step 3: Dashboard Deployment

### 3.1 Configure Dashboard Environment Variables

Create `.env` file in `dashboard/` directory:

```env
VITE_API_URL=https://your-backend-url.vercel.app
```

Replace with your actual backend URL from Step 2.5.

### 3.2 Test Dashboard Locally

1. Navigate to dashboard directory:
```bash
cd dashboard
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

4. Visit `http://localhost:5173` to verify it works

### 3.3 Deploy Dashboard to Vercel

**Option A: Using Vercel CLI**

1. From dashboard directory:
```bash
cd dashboard
vercel
```

2. Follow prompts:
   - **Project name**: `spotify-insights-dashboard`
   - **Directory**: `./`

3. Add environment variable:
   - Go to project settings → Environment Variables
   - Add `VITE_API_URL` with your backend URL

4. Deploy to production:
```bash
vercel --prod
```

**Option B: Using Vercel Dashboard**

1. Go to Vercel dashboard
2. Click "Add New Project"
3. Import your Git repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `dashboard`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add `VITE_API_URL` environment variable
6. Click "Deploy"

### 3.4 Verify Dashboard Deployment

1. Visit your dashboard URL: `https://spotify-insights-dashboard.vercel.app`
2. Verify:
   - Dashboard loads without errors
   - Data displays correctly
   - API calls work (check browser console for errors)

---

## Step 4: Testing & Verification

### 4.1 Backend API Testing

Test all critical endpoints:

```bash
# Test summary endpoint
curl https://your-backend-url.vercel.app/api/insights/summary

# Test patterns endpoint
curl https://your-backend-url.vercel.app/api/insights/patterns

# Test segments endpoint
curl https://your-backend-url.vercel.app/api/insights/segments

# Test recommendations endpoint
curl https://your-backend-url.vercel.app/api/recommendations

# Test roadmap endpoint
curl https://your-backend-url.vercel.app/api/roadmap
```

### 4.2 Dashboard Testing

1. **Load Testing:**
   - Open dashboard in multiple browsers
   - Check for performance issues
   - Verify data loads correctly

2. **Functionality Testing:**
   - Test all tabs: Overview, Patterns, Deep Insights, Actions
   - Test filters and sorting
   - Test expand/collapse functionality
   - Test API calls on each tab

3. **Cross-Browser Testing:**
   - Chrome
   - Firefox
   - Safari
   - Edge

### 4.3 Integration Testing

1. **Database Connection:**
   - Verify backend connects to Supabase
   - Check data retrieval works
   - Test data insertion (if applicable)

2. **API-Dashboard Integration:**
   - Verify dashboard calls correct API endpoints
   - Check CORS is configured properly
   - Test error handling

### 4.4 Security Checklist

- [ ] Environment variables are set in Vercel (not in code)
- [ ] Database credentials are secure
- [ ] CORS is configured correctly
- [ ] API rate limiting is considered
- [ ] Sensitive data is not exposed in client-side code

---

## Step 5: Monitoring & Maintenance

### 5.1 Vercel Monitoring

1. **Backend Monitoring:**
   - Go to Vercel project dashboard
   - View **Analytics** tab for visitor stats
   - Check **Logs** for runtime errors
   - Monitor **Functions** for API performance

2. **Dashboard Monitoring:**
   - Similar monitoring for dashboard project
   - Check build logs for deployment issues

### 5.2 Supabase Monitoring

1. Go to Supabase project dashboard
2. Check **Database** → **Logs** for query performance
3. Monitor **Storage** usage
4. Review **API** usage limits

### 5.3 Error Tracking

Consider adding error tracking:
- **Sentry** for error monitoring
- **LogRocket** for session replay
- **Google Analytics** for user analytics

### 5.4 Backup Strategy

1. **Database Backups:**
   - Supabase provides automatic backups (free tier: 7 days)
   - Consider manual backups before major changes

2. **Code Backups:**
   - Git provides version control
   - Tag releases: `git tag v1.0.0`

### 5.5 Update Process

When updating the application:

1. **Backend Updates:**
   ```bash
   cd backend
   git pull
   vercel --prod
   ```

2. **Dashboard Updates:**
   ```bash
   cd dashboard
   git pull
   vercel --prod
   ```

3. **Database Updates:**
   - Run new migrations in Supabase SQL Editor
   - Test in staging environment first

---

## Troubleshooting

### Backend Issues

**Problem**: Backend won't start
- Check environment variables are set
- Verify database connection string
- Check Python dependencies are installed

**Problem**: API returns 500 errors
- Check Vercel logs
- Verify database connection
- Test API locally first

**Problem**: CORS errors
- Check `CORS_ORIGINS` in backend `.env`
- Verify dashboard URL is allowed

### Dashboard Issues

**Problem**: Dashboard won't build
- Check TypeScript errors: `npm run build`
- Verify all dependencies installed
- Check for missing imports

**Problem**: Dashboard can't connect to API
- Verify `VITE_API_URL` is set correctly
- Check backend is deployed and accessible
- Verify CORS configuration

**Problem**: Data not displaying
- Check browser console for errors
- Verify API returns data
- Check network tab in browser dev tools

### Database Issues

**Problem**: Can't connect to database
- Verify database URL is correct
- Check database is online in Supabase
- Verify credentials are correct

**Problem**: Tables missing
- Run all migrations in order
- Check SQL Editor for errors
- Verify table names match code

---

## Production Checklist

Before going live, verify:

- [ ] All environment variables are set in Vercel
- [ ] Database migrations are complete
- [ ] Backend API is accessible and working
- [ ] Dashboard builds and deploys successfully
- [ ] Dashboard connects to backend API
- [ ] All API endpoints return correct data
- [ ] Dashboard displays data correctly
- [ ] No console errors in browser
- [ ] CORS is configured properly
- [ ] Database credentials are secure
- [ ] Monitoring is set up
- [ ] Backup strategy is in place
- [ ] Team has access to all accounts
- [ ] Documentation is updated

---

## Cost Estimate

**Free Tier Limits:**
- **Vercel**: 100GB bandwidth/month, 6,000 minutes execution/month
- **Supabase**: 500MB database, 1GB file storage, 2GB bandwidth/month

**Estimated Monthly Costs (if limits exceeded):**
- **Vercel**: $20-100/month depending on traffic
- **Supabase**: $25/month for Pro tier

---

## Support & Resources

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Supabase Documentation**: [supabase.com/docs](https://supabase.com/docs)
- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **React Documentation**: [react.dev](https://react.dev)

---

## Next Steps After Deployment

1. **Set up custom domains** (optional)
2. **Configure SSL certificates** (automatic on Vercel)
3. **Set up analytics** (Google Analytics, etc.)
4. **Create monitoring alerts**
5. **Document API endpoints** for external use
6. **Set up CI/CD pipeline** (GitHub Actions)
7. **Create user documentation**
8. **Plan for scaling** if needed

---

## Emergency Rollback

If something goes wrong:

1. **Backend Rollback:**
   ```bash
   vercel rollback <deployment-url>
   ```

2. **Dashboard Rollback:**
   ```bash
   cd dashboard
   vercel rollback <deployment-url>
   ```

3. **Database Rollback:**
   - Use Supabase point-in-time recovery
   - Restore from backup

---

Congratulations! Your Spotify Insights project is now in production. 🎉
