# Quick Start: Dashboard Data Pipeline Fix

## What Was Broken
The dashboard showed **no data** despite having 10,000+ reviews because:
1. **ProcessedReview table didn't exist** - blocking the entire analysis pipeline
2. **Hardcoded fallback data** - causing repetitive patterns, segments, and recommendations
3. **Silent query failures** - no errors shown when databases couldn't be queried
4. **Extremely low sampling** - only analyzing 20 reviews out of 10,000 per analysis type

## What We Fixed
✅ Added missing `ProcessedReview` model  
✅ Increased data sampling (20→100-200 reviews per analysis)  
✅ Enhanced error logging (no more silent failures)  
✅ Improved LLM context window (4000→8000 chars)  
✅ Diversified fallback recommendations (5→8 unique options)  
✅ Fixed hardcoded pattern defaults (only use if data is truly empty)  

---

## How to Verify Fixes

### Step 1: Run Diagnostics
```bash
cd "c:\Graduation Project - Spotify"
python scripts/diagnose_dashboard.py
```

**Expected Output:**
- ✅ Raw reviews: 10,000+
- ✅ Patterns detected: 10+
- ✅ Segments created: 5+
- ✅ Recommendations generated: 5+

### Step 2: Trigger Data Analysis
**Option A: Via Dashboard**
1. Open dashboard in browser
2. Click "Run AI Analysis" button
3. Wait for notification

**Option B: Via API**
```bash
curl -X POST http://localhost:8000/api/insights/generate
```

**Option C: Manual Python**
```bash
python -c "from app.services.insight_engine import InsightEngine; InsightEngine().run()"
```

### Step 3: Check Results
After analysis completes:

1. **Check Dashboard Tabs:**
   - Executive: Should show total reviews count
   - Patterns: Should show 10+ patterns with different types
   - Segments: Should show 5+ user segments
   - Deep Insights: Should show root causes (not repetitive)
   - Actions: Should show 5-8 diverse recommendations

2. **Check Dashboard Export:**
   - Click "Export Report"
   - Verify PDF/Markdown contains accumulated insights
   - Check that data varies (not the same 3 patterns every time)

3. **Check Logs:**
```bash
# Look for these success indicators
tail -f logs/app.log | grep -E "Persisted|Pattern|Segment|Root Cause|Recommendation"
```

---

## Common Issues & Solutions

### Issue: "Patterns: 0 items" / "No findings yet"
**Solution:**
1. Run diagnostics: `python scripts/diagnose_dashboard.py`
2. Check sentiment_analysis table count - if 0, data wasn't processed
3. Ensure LLM keys are set (.env file)
4. Run insight generation: `POST /api/insights/generate`

### Issue: Recommendations are repetitive
**Solution:**
1. Check logs for "Using heuristic recommendations"
2. Set LLM provider keys in `.env`:
   ```
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-...
   # OR
   ANTHROPIC_API_KEY=sk-ant-...
   ```
3. Re-run: `POST /api/insights/generate`

### Issue: Export/Report not working
**Solution:**
1. Check `./reports` directory exists (will be created automatically)
2. Verify write permissions: `mkdir ./reports 2>/dev/null || true`
3. Check logs for file path: `grep "Report saved to" logs/app.log`

### Issue: Database connection errors
**Solution:**
1. Verify PostgreSQL is running
2. Check `.env` DATABASE_URL is correct
3. Run diagnostics to confirm database connectivity

---

## Verification Checklist

- [ ] Run diagnostics script shows ✅ all green
- [ ] Dashboard shows total_reviews count > 0
- [ ] Patterns tab shows 10+ items (different types)
- [ ] Segments tab shows 5+ user segments
- [ ] Deep Insights tab shows root causes
- [ ] Actions tab shows 5-8 recommendations
- [ ] Export report generates file successfully
- [ ] Sentiment distribution shows negative/positive/neutral
- [ ] Each run generates different insights (not repetitive)

---

## File Changes Summary

| File | Change | Impact |
|------|--------|--------|
| `app/database/models.py` | Added ProcessedReview | Unblocks entire analysis pipeline |
| `app/services/root_cause.py` | 20→100 samples | Better root cause analysis |
| `app/services/unmet_needs.py` | 20→200 samples | Detects more user needs |
| `app/services/recommendation_engine.py` | 4000→8000 context | Better recommendations |
| `app/services/pattern_detection.py` | Fixed queries | Prevents silent failures |
| `app/services/segmentation.py` | Smarter fallbacks | Only fallback if no real data |
| `app/services/analysis_store.py` | Better logging | Error visibility |
| `scripts/diagnose_dashboard.py` | **NEW** | Verify pipeline health |

---

## Expected Results After Fixes

### Before:
- Dashboard shows "0 items" everywhere
- Patterns: always same 3 (negative sentiment, cross-platform, discover weekly)
- Segments: "High-Frustration Users", "Discovery Enthusiasts" (generic)
- Recommendations: repetitive
- Export: no data

### After:
- Dashboard shows counts for all metrics
- Patterns: 10+ unique patterns based on actual data
- Segments: realistic user groups with actual data
- Recommendations: diverse, data-driven
- Export: comprehensive report with accumulated insights
- Each run shows slightly different insights (analysis learns more)

---

## Monitoring Dashboard Health

### Daily Checks:
```bash
# Quick health check
curl http://localhost:8000/api/insights/summary
```

Should return:
```json
{
  "success": true,
  "data": {
    "pattern_count": 10+,
    "segment_count": 5+,
    "root_cause_count": 2+,
    "unmet_need_count": 3+,
    "total_reviews": 10000+
  }
}
```

### Weekly Full Diagnostics:
```bash
python scripts/diagnose_dashboard.py
```

---

## Questions?

If dashboard still shows no data after following these steps:

1. **Check logs**: Look for error messages with timestamps
2. **Run diagnostics**: `python scripts/diagnose_dashboard.py`
3. **Verify database**: Check if tables have any data at all
4. **Check LLM keys**: Ensure API keys are valid (test with curl)
5. **Review FIXES_APPLIED.md**: Detailed explanation of each fix

---

## Next Steps

Once dashboard is working:

1. **Monitor data quality**: Review insights for accuracy
2. **Collect feedback**: Share dashboard with stakeholders
3. **Iterate analysis**: Refine LLM prompts for better insights
4. **Add more data sources**: Instagram, YouTube, etc.
5. **Set up automation**: Schedule insight generation daily/weekly

---

**Status**: ✅ All critical issues fixed. Dashboard ready for testing.
