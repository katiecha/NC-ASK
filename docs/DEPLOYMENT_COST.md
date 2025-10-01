# NC-ASK Deployment & Cost Analysis

## Updated Architecture: Supabase + FastAPI

### Technology Stack Summary
- **Frontend**: React + TypeScript (Vite) → Vercel (Free)
- **Backend**: FastAPI (Python) → Render/Railway (Free tier available)
- **Database**: Supabase PostgreSQL + pgvector (Free: 500MB)
- **Storage**: Supabase Storage (Free: 1GB)
- **LLM**: Google Gemini 2.5 Flash-lite (User has Gemini Pro)
- **Email**: SendGrid (Free: 100 emails/day)

## Cost Breakdown

### 🆓 Free Tier Deployment (MVP Launch)

| Service | Free Tier Limits | Cost |
|---------|------------------|------|
| **Vercel** (Frontend) | Unlimited bandwidth, 100GB/month | $0 |
| **Render** (FastAPI) | 750 hours/month, sleeps after 15min | $0 |
| **Supabase** (Database) | 500MB database, 2GB bandwidth/month | $0 |
| **Supabase** (Storage) | 1GB file storage | $0 |
| **Gemini API** | User has Gemini Pro | $0 |
| **SendGrid** | 100 emails/day | $0 |
| **GitHub Actions** | 2000 minutes/month | $0 |
| **Total Monthly Cost** | | **$0** |

### 📊 Free Tier Reality Check

**What 500MB Database Supports:**
- ~50,000 document chunks (200-800 tokens each)
- ~50,000 embeddings (384 dimensions = ~75MB)
- ~25MB metadata
- **Total**: ~400MB used, 100MB buffer

**What 1GB Storage Supports:**
- ~200-300 PDF documents (average 3-5MB each)
- Perfect for NC autism services documentation

**Expected Usage (MVP):**
- 50 users/month
- 500 queries/month
- 50 source documents
- Well within all free tier limits

### ⚠️ Free Tier Limitations

**Render Free Tier:**
- **Cold starts**: 10-30 second delay after 15 minutes of inactivity
- **750 hours/month**: ~25 hours/day (sufficient for MVP)
- **No custom domains** on free tier

**Supabase Free Tier:**
- **500MB database**: Hard limit, need to monitor
- **2GB bandwidth/month**: ~67MB/day (should be sufficient)
- **No point-in-time recovery**

## 💰 Paid Tier Migration Path

### When to Upgrade (Triggers)
1. **Backend cold starts** become user experience issue
2. **Database approaching 400MB** (80% of limit)
3. **Bandwidth approaching 1.5GB/month** (75% of limit)
4. **More than 100 users/month**

### Minimal Paid Setup ($7-15/month)

| Service | Plan | Cost | Benefits |
|---------|------|------|----------|
| **Vercel** | Free | $0 | Still free |
| **Render** | Starter | $7/month | No cold starts, custom domain |
| **Supabase** | Free | $0 | Still within limits |
| **Total** | | **$7/month** | Eliminates cold starts |

### Production Ready Setup ($25-35/month)

| Service | Plan | Cost | Benefits |
|---------|------|------|----------|
| **Vercel** | Pro | $20/month | Team features, analytics |
| **Render** | Starter | $7/month | No cold starts |
| **Supabase** | Pro | $25/month | 8GB database, daily backups |
| **Total** | | **$52/month** | Production grade |

**Note**: You'd likely only need Render Starter ($7/month) for quite a while.

## 🚀 Deployment Guide

### Phase 1: Free Tier Setup

#### 1. Supabase Setup
```bash
# 1. Create account at https://supabase.com
# 2. Create new project
# 3. Enable pgvector extension:
CREATE EXTENSION vector;

# 4. Get your keys from Settings > API
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

#### 2. Render Setup (FastAPI)
```bash
# 1. Create account at https://render.com
# 2. Connect GitHub repository
# 3. Create Web Service
# 4. Configure:
#    - Build Command: pip install -r requirements.txt
#    - Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
#    - Environment: Python 3.11
# 5. Add environment variables (Supabase keys, Gemini API key)
```

#### 3. Vercel Setup (Frontend)
```bash
# 1. Create account at https://vercel.com
# 2. Connect GitHub repository
# 3. Configure:
#    - Framework: Vite
#    - Build Command: npm run build
#    - Output Directory: dist
# 4. Add environment variable:
#    VITE_API_BASE_URL=https://your-render-app.onrender.com
```

### Phase 2: Custom Domain Setup (Optional)
```bash
# Render (Backend)
# - Upgrade to Starter plan ($7/month)
# - Add custom domain: api.ncask.org

# Vercel (Frontend)  
# - Add custom domain: ncask.org (free on all plans)
# - Automatic HTTPS certificate
```

## 📈 Scaling Considerations

### Traffic Growth Projections

| Users/Month | Queries/Month | Database Size | Bandwidth | Recommended Setup |
|-------------|---------------|---------------|-----------|-------------------|
| 50 | 500 | 100MB | 500MB | Free tier |
| 200 | 2,000 | 200MB | 1GB | Free tier |
| 500 | 5,000 | 400MB | 2GB | Render Starter ($7) |
| 1,000 | 10,000 | 500MB+ | 4GB+ | + Supabase Pro ($25) |
| 2,000+ | 20,000+ | 1GB+ | 8GB+ | Consider optimization |

### Optimization Strategies (Before Scaling Up)

1. **Database Optimization**:
   - Archive old document chunks
   - Optimize embedding storage
   - Use JSONB compression

2. **Bandwidth Optimization**:
   - Implement response caching
   - Compress API responses
   - Use CDN for static assets

3. **Query Optimization**:
   - Cache frequent queries
   - Optimize pgvector indexes
   - Implement query result pagination

## 🔍 Monitoring & Alerts

### Key Metrics to Track

**Supabase Dashboard**:
- Database size (target: < 400MB)
- Bandwidth usage (target: < 1.5GB/month)
- Query performance
- Connection count

**Render Dashboard**:
- Response times
- Error rates
- Memory usage
- Uptime

**Custom Monitoring** (FastAPI):
```python
# Add to your FastAPI app
import logging

# Track database size
@app.get("/admin/stats")
async def get_stats():
    db_size = await get_database_size()
    return {
        "database_size_mb": db_size,
        "database_usage_percent": (db_size / 500) * 100
    }
```

### Automated Alerts
```python
# Set up alerts when approaching limits
if database_size > 400:  # 80% of 500MB
    send_alert("Database approaching limit")
    
if monthly_bandwidth > 1500:  # 75% of 2GB
    send_alert("Bandwidth approaching limit")
```

## 🎯 Recommendations

### For MVP Launch:
1. **Start with 100% free tier** - perfect for initial testing
2. **Monitor usage closely** - set up alerts at 75% of limits
3. **Plan for Render Starter upgrade** when cold starts become problematic
4. **Document scaling triggers** - know when to upgrade each service

### For Production:
1. **Render Starter ($7/month)** - eliminates cold starts
2. **Keep Supabase free** until you hit 400MB database
3. **Vercel stays free** - their free tier is very generous
4. **Total cost: $7/month** for production-ready setup

### Long-term:
1. **Monitor user growth** - scale proactively
2. **Consider caching layer** before upgrading database
3. **Optimize before scaling** - often more cost-effective
4. **Plan for success** - budget for growth

## 🔐 Security Considerations (Free Tier)

### Supabase Security:
- Row Level Security (RLS) policies
- API key rotation
- Database connection limits

### Render Security:
- HTTPS by default
- Environment variable encryption
- Automatic security updates

### Application Security:
- Rate limiting (10 queries/minute)
- Input validation
- No PII storage
- Crisis detection logging (de-identified)

---

**Bottom Line**: You can absolutely launch NC-ASK MVP for **$0/month** and scale to **$7/month** when needed. The free tiers are genuinely sufficient for MVP validation and early user growth.
