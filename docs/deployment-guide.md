# Deployment Guide - Vercel + Supabase

This guide provides step-by-step instructions for deploying the Spotify Review Discovery Engine using Vercel for frontend hosting and Supabase for backend services.

## Prerequisites

- GitHub account (for GitHub Actions)
- Vercel account (free tier)
- Supabase account (free tier)
- Node.js 18+ installed locally
- Python 3.12 installed locally

## Overview

**Deployment Architecture:**
- **Frontend**: React dashboard deployed on Vercel
- **Database**: PostgreSQL hosted on Supabase (free tier: 500MB)
- **Storage**: Supabase Storage (free tier: 1GB)
- **Data Collection**: GitHub Actions (scheduled daily)
- **Analysis**: Python scripts with simple rule-based NLP (free)

**Total Cost**: $0/month (free tiers)

## Step 1: Supabase Setup

### 1.1 Create Supabase Project

1. Go to https://supabase.com and sign up
2. Click "New Project"
3. Enter project details:
   - Name: `spotify-review-engine`
   - Database Password: (generate strong password, save it)
   - Region: Choose closest to your users
4. Wait for project provisioning (2-3 minutes)
5. Save the following from project settings:
   - Project URL
   - anon public key
   - service_role secret key

### 1.2 Run Database Migrations

1. Go to Supabase Dashboard → SQL Editor
2. Copy the contents of `supabase/migrations/001_initial_schema.sql`
3. Paste into SQL Editor
4. Click "Run" to execute the migration
5. Verify tables were created in Database → Tables

### 1.3 Configure Storage

1. Go to Storage section in Supabase Dashboard
2. Create new bucket: `raw-data`
3. Make bucket public:
   - Click on bucket
   - Go to Policies
   - Add policy for public read access
4. Create folders:
   - `appstore/`
   - `playstore/`
   - `reddit/`
   - `forums/`

### 1.4 Get API Keys

1. Go to Settings → API
2. Copy these keys:
   - `Project URL` → `SUPABASE_URL`
   - `anon public key` → `SUPABASE_ANON_KEY`
   - `service_role secret key` → `SUPABASE_SERVICE_ROLE_KEY`

**Important**: Never commit service_role key to public repositories. Use it only in server-side code.

## Step 2: Vercel Setup

### 2.1 Install Vercel CLI

```bash
npm install -g vercel
```

### 2.2 Deploy Dashboard

1. Navigate to dashboard directory:
```bash
cd dashboard
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

4. Follow the prompts:
   - Link to existing project or create new
   - Project name: `spotify-dashboard`
   - Build settings: (accept defaults)

5. Configure environment variables in Vercel:
   - Go to Vercel Dashboard → Project → Settings → Environment Variables
   - Add:
     - `VITE_SUPABASE_URL`: Your Supabase project URL
     - `VITE_SUPABASE_ANON_KEY`: Your Supabase anon key

6. Redeploy to apply environment variables:
```bash
vercel --prod
```

### 2.3 Configure Custom Domain (Optional)

1. Buy domain (e.g., from Namecheap, GoDaddy) - ~$10-15/year
2. Go to Vercel Dashboard → Project → Settings → Domains
3. Add your domain
4. Update DNS records as instructed by Vercel
5. Vercel handles SSL automatically

## Step 3: GitHub Actions Setup

### 3.1 Add Secrets to GitHub

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Add the following secrets:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service_role key
   - `REDDIT_CLIENT_ID`: (optional, if using Reddit API)
   - `REDDIT_CLIENT_SECRET`: (optional, if using Reddit API)
   - `OPENAI_API_KEY`: (optional, if using OpenAI)

### 3.2 Enable GitHub Actions

1. The workflow file is already at `.github/workflows/data-collection.yml`
2. Go to Actions tab in GitHub
3. Enable workflows if prompted
4. The workflow will run daily at 2 AM UTC
5. You can also trigger manually via "Run workflow" button

## Step 4: Local Development Setup

### 4.1 Environment Variables

Create `.env.local` in dashboard directory:
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 4.2 Install Dependencies

```bash
cd dashboard
npm install
```

### 4.3 Run Locally

```bash
npm run dev
```

Dashboard will be available at `http://localhost:5173`

## Step 5: Testing the Deployment

### 5.1 Test Database Connection

1. Go to Supabase Dashboard → SQL Editor
2. Run test query:
```sql
SELECT COUNT(*) FROM raw_reviews;
```

### 5.2 Test Dashboard

1. Visit your Vercel deployment URL
2. Check if dashboard loads
3. Verify no console errors

### 5.3 Test Data Collection

1. Go to GitHub Actions tab
2. Manually trigger the data collection workflow
3. Monitor the workflow logs
4. Check Supabase database for new data

### 5.4 Test API Endpoints

If you deployed API functions:
```bash
curl https://your-vercel-url/api/health
```

## Step 6: Monitoring

### 6.1 Vercel Analytics

- Go to Vercel Dashboard → Analytics
- Monitor page views, performance, errors
- Free tier includes basic analytics

### 6.2 Supabase Monitoring

- Go to Supabase Dashboard → Database → Reports
- Monitor database size, API usage
- Free tier includes basic monitoring

### 6.3 GitHub Actions Logs

- Go to Actions tab in GitHub
- View workflow run logs
- Check for any failures

## Step 7: Maintenance

### 7.1 Regular Tasks

**Daily:**
- Check GitHub Actions runs
- Verify data collection completed successfully

**Weekly:**
- Review database size in Supabase
- Check Vercel analytics
- Monitor for errors

**Monthly:**
- Update dependencies
- Review security advisories
- Check free tier usage limits

### 7.2 Backup Strategy

Supabase provides automatic daily backups (7-day retention on free tier). For additional safety:

1. Manual backup via SQL Editor:
```sql
-- Export all data
COPY raw_reviews TO '/tmp/raw_reviews.csv' CSV HEADER;
```

2. Use Supabase's built-in backup feature:
   - Go to Database → Backups
   - Create manual backup

### 7.3 Troubleshooting

**Dashboard not loading:**
- Check Vercel deployment logs
- Verify environment variables are set
- Check browser console for errors

**Data collection failing:**
- Check GitHub Actions logs
- Verify secrets are correctly set
- Check Supabase connection

**Database size growing too fast:**
- Implement data retention policy
- Archive old data
- Consider upgrading to Pro tier

## Free Tier Limits

### Vercel (Hobby Plan)
- Bandwidth: 100GB/month
- Execution minutes: 6,000/month
- Builds: 100/month
- Sufficient for <5 users

### Supabase (Free Tier)
- Database: 500MB
- Storage: 1GB
- Bandwidth: 2GB/month
- API Requests: 50,000/month
- Sufficient for small-scale usage

### GitHub Actions
- 2,000 minutes/month free for public repos
- 500 minutes/month free for private repos
- Sufficient for daily data collection

## Upgrade Path

If you exceed free tier limits:

**Vercel Pro ($20/month):**
- 1TB bandwidth
- Unlimited execution minutes
- Priority support

**Supabase Pro ($25/month):**
- 8GB database
- 100GB storage
- 100GB bandwidth
- Daily backups with 30-day retention

## Security Best Practices

1. **Never commit secrets**: Use environment variables
2. **Use RLS policies**: Already configured in database schema
3. **Regular updates**: Keep dependencies updated
4. **Monitor usage**: Watch for unusual activity
5. **Backup regularly**: Even with automatic backups

## Next Steps

1. Complete Supabase setup
2. Deploy dashboard to Vercel
3. Configure GitHub Actions
4. Test all components
5. Set up monitoring
6. Document any customizations

## Support

- **Vercel**: https://vercel.com/docs
- **Supabase**: https://supabase.com/docs
- **GitHub Actions**: https://docs.github.com/actions

## Cost Summary

| Service | Free Tier | Paid Tier | Current Cost |
|---------|-----------|-----------|--------------|
| Vercel | 100GB bandwidth, 6K minutes | $20/month | $0 |
| Supabase | 500MB DB, 1GB storage | $25/month | $0 |
| GitHub Actions | 2K minutes (public) | $4/500 minutes | $0 |
| Domain (optional) | - | $10-15/year | $0-15/year |
| **Total** | - | - | **$0-15/year** |

## Success Criteria

- Dashboard accessible via Vercel URL
- Data collection runs automatically daily
- Database stays within 500MB limit
- API response time < 2 seconds
- Uptime > 99%
- Total monthly cost: $0
