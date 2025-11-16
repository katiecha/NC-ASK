# NC-ASK Administrator Manual

**Version 1.0**
**Last Updated: Nov 16 2025**

---

## Table of Contents

1. [Introduction](#introduction)
2. [Day-to-Day Operations](#operations)
3. [Monitoring and Maintenance](#monitoring)
4. [Backup and Disaster Recovery](#backup)
5. [Security and Compliance](#security)
6. [Troubleshooting](#troubleshooting)
7. [Support and Resources](#support)

---

<a name="introduction"></a>
## 1. Introduction

### About This Manual

This administrator manual provides guidance for operating and maintaining the NC-ASK (North Carolina Autism Support Knowledge) system. This manual assumes NC-ASK is already deployed.

**For setup and deployment instructions, see:**
- [03_DOCKER_SETUP.md](./03_DOCKER_SETUP.md) - Docker development setup
- [04_LOCAL_SETUP.md](./04_LOCAL_SETUP.md) - Local development setup
- [05_DEPLOYMENT.md](./05_DEPLOYMENT.md) - Cloud deployment guide
- [10_DEPLOYMENT.md](./10_DEPLOYMENT.md) - OpenShift deployment guide

### Who This Manual Is For

This manual is intended for:
- **System administrators** managing NC-ASK operations
- **IT staff** responsible for maintenance
- **Technical support** personnel troubleshooting issues

### About NC-ASK

NC-ASK is a question-answering system that provides evidence-based information about autism support resources in North Carolina.

---

<a name="operations"></a>
## 2. Day-to-Day Operations

### 2.1 Monitoring System Health

**What to monitor:**

1. **Application health**
   - Backend `/health` endpoint status
   - Frontend accessibility
   - Response times

2. **External services**
   - Supabase database availability
   - Gemini API quota and rate limits
   - API error rates

3. **Resource usage**
   - CPU and memory utilization
   - Disk space
   - Network bandwidth

**Monitoring tools:**
- Application logs
- Platform-specific dashboards (Vercel, Render, OpenShift)
- External monitoring (Sentry, Datadog, etc.)

### 2.2 Viewing Logs

**Docker deployment:**
```bash
# All services
docker-compose logs

# Backend only
docker-compose logs backend

# Follow logs in real-time
docker-compose logs -f
```

**Cloud deployment:**
- **Vercel**: Dashboard → Deployment → Logs
- **Render**: Dashboard → Service → Logs

**OpenShift:**
```bash
oc logs -f deployment/nc-ask-backend
```

[Image: Example log output showing successful query]

### 2.3 Restarting Services

**Docker:**
```bash
docker-compose restart
# Or specific service:
docker-compose restart backend
```

**Cloud:**
- Use platform dashboard to redeploy or restart

**OpenShift:**
```bash
oc rollout restart deployment/nc-ask-backend
```

### 2.4 Updating the Knowledge Base

When new autism resource documents become available:

1. **Prepare documents**
   - Validate format and content
   - Place in ingestion folder

2. **Run ingestion process**
   ```bash
   python -m app.scripts.ingest_documents --new-only
   ```

3. **Verify ingestion**
   - Check database for new entries
   - Test queries against new content

4. **Monitor performance**
   - Ensure vector search performance remains acceptable
   - May need to adjust database resources for large updates

**Recommended frequency:** Monthly, or as new resources become available

### 2.5 User Management (If Applicable)

**Note:** Current NC-ASK implementation does not include user accounts.

If your deployment adds authentication:
- Follow institutional identity management protocols
- Integrate with SSO/LDAP if available
- Maintain user access logs per compliance requirements

---

<a name="monitoring"></a>
## 3. Monitoring and Maintenance

### 3.1 Key Metrics to Track

**Application Metrics:**
- **Query volume**: Number of queries per day/hour
- **Response times**: Average and 95th percentile
- **Error rates**: 4xx and 5xx responses
- **Crisis detections**: Frequency of crisis keyword triggers

**Infrastructure Metrics:**
- **CPU usage**: Should stay below 80% average
- **Memory usage**: Monitor for memory leaks
- **Database connections**: Track active connections to Supabase
- **API quotas**: Monitor Gemini API usage against limits

**User Experience Metrics:**
- **Page load times**: Frontend performance
- **Time to first response**: User-perceived latency
- **Citation quality**: Manual spot-checks of response accuracy

### 3.2 Regular Maintenance Tasks

**Daily:**
- [ ] Review error logs for critical issues
- [ ] Check system health dashboard
- [ ] Monitor API quota usage

**Weekly:**
- [ ] Review query logs for trends or issues
- [ ] Check crisis detection logs
- [ ] Verify backup completion (if automated)
- [ ] Review resource usage trends

**Monthly:**
- [ ] Update knowledge base with new documents
- [ ] Review and update dependencies (security patches)
- [ ] Analyze usage patterns and performance trends
- [ ] Test disaster recovery procedures
- [ ] Review and rotate API keys (if policy requires)

**Quarterly:**
- [ ] Comprehensive security audit
- [ ] Review and update documentation
- [ ] Capacity planning review
- [ ] User feedback analysis

### 3.3 Performance Tuning

**If response times are slow:**

1. **Check Gemini API latency**
   - Review API response times in logs
   - Consider using faster models for embeddings

2. **Optimize vector search**
   - Review Supabase query performance
   - Consider indexing optimizations
   - May need to adjust similarity threshold

3. **Frontend optimization**
   - Review bundle size
   - Implement caching strategies
   - Optimize images and assets

4. **Scale resources**
   - Increase backend instances (if cloud)
   - Upgrade database tier (Supabase)
   - Enable CDN for frontend

### 3.4 Security Maintenance

**Regular security tasks:**

1. **Dependency updates**
   ```bash
   # Backend
   pip list --outdated
   pip install --upgrade [package]

   # Frontend
   npm outdated
   npm update
   ```

2. **Security scanning**
   - Run `npm audit` and `pip-audit`
   - Address high/critical vulnerabilities promptly

3. **API key rotation**
   - Follow organizational policy
   - Update across all environments
   - Revoke old keys after migration

4. **Access reviews**
   - Review who has deployment access
   - Audit Supabase and cloud platform permissions
   - Remove access for departed team members

**Security documentation:** See **[08_SAFETY.md](./08_SAFETY.md)** and **[09_NC_ASK_AI_SG_Guiding_Principles](./09_NC_ASK_AI_SG_Guiding_Principles_v0.docx)**

---

<a name="backup"></a>
## 4. Backup and Disaster Recovery

### 4.1 What to Back Up

**Critical data:**
1. **Supabase database**
   - Document embeddings
   - Chat history (if applicable)
   - Configuration tables

2. **Environment configurations**
   - `.env` files (stored securely, not in repo)
   - Deployment configurations

3. **Knowledge base source documents**
   - Original PDFs and source materials
   - Document metadata

**Not typically backed up:**
- Application code (stored in Git)
- Docker images (rebuilt from code)

### 4.2 Supabase Backup

**Automated backups:**
- Supabase Pro plan includes automatic daily backups
- Retained for 7-30 days depending on plan

**Manual backup:**
```bash
# Using Supabase CLI
supabase db dump -f backup.sql

# Or via pg_dump if direct access available
pg_dump [connection-string] > backup.sql
```

**Backup schedule recommendation:**
- **Daily**: Automated Supabase backups
- **Weekly**: Manual full database export
- **Before major updates**: Manual backup

### 4.3 Disaster Recovery Plan

**Recovery Time Objective (RTO):** Target 4 hours
**Recovery Point Objective (RPO):** Maximum 24 hours data loss

**Recovery Procedure:**

1. **Assess the situation**
   - Identify what failed (application, database, external service)
   - Determine data loss extent

2. **Restore database** (if needed)
   ```bash
   # Restore from Supabase backup
   supabase db restore [backup-id]

   # Or from manual backup
   psql [connection-string] < backup.sql
   ```

3. **Redeploy application**
   - Rebuild from Git repository
   - Reconfigure environment variables
   - Deploy using standard procedures

4. **Verify restoration**
   - Run health checks
   - Test critical functionality
   - Verify data integrity

5. **Post-incident review**
   - Document what happened
   - Identify root cause
   - Update procedures to prevent recurrence

### 4.4 Testing Disaster Recovery

**Recommended:** Test recovery procedures every 6 months

**Test procedure:**
1. Create test environment separate from production
2. Restore from backup to test environment
3. Verify application functionality
4. Document any issues or gaps in procedures
5. Update DR plan as needed

---

<a name="security"></a>
## 5. Security and Compliance

### 5.1 Security Best Practices

**Application security:**

1. **Environment variables**
   - Never commit secrets to Git
   - Use platform secret management (Vercel secrets, OpenShift secrets)
   - Rotate API keys regularly
   - Use different keys for dev/staging/production

2. **CORS configuration**
   - Set specific origins in production (not `*`)
   - Update when domain changes
   - Test thoroughly after changes

3. **HTTPS/TLS**
   - Always use HTTPS in production
   - Verify SSL certificate validity
   - Enable HSTS headers

4. **Dependencies**
   - Regular security updates
   - Automated vulnerability scanning
   - Review dependency licenses

**Infrastructure security:**

1. **Access control**
   - Principle of least privilege
   - Multi-factor authentication for cloud platforms
   - Regular access audits

2. **Network security**
   - Firewall rules limiting access
   - VPN for administrative access (if on-premises)
   - Monitoring for suspicious activity

3. **Logging and monitoring**
   - Centralized logging
   - Alerting for security events
   - Regular log review

### 5.2 Crisis Detection and Safety

NC-ASK includes built-in crisis detection for user safety.

**How it works:**
- Monitors queries for crisis keywords (suicide, self-harm, danger)
- Displays prominent crisis resources when detected
- Logs crisis events for safety auditing

**Crisis keywords monitored:**
- Suicidal ideation
- Self-harm
- Harm to others
- Severe distress

**Administrator responsibilities:**

1. **Review crisis logs regularly**
   - Understand frequency of crisis detections
   - Identify trends or patterns
   - Report to appropriate institutional contacts if required

2. **Ensure crisis resources are current**
   - Verify phone numbers and links
   - Update if resources change
   - Test links periodically

3. **Crisis detection configuration**
   - Default: enabled
   - Can be configured via environment variables if needed

**Documentation:** See **[08_SAFETY.md](./08_SAFETY.md)**

[Image: Example crisis detection alert as shown to users]

### 5.3 Privacy and Data Handling

**NC-ASK privacy principles:**

1. **No personal data collection**
   - No user accounts or login
   - No tracking of individual users
   - Anonymous query logging

2. **Minimal logging**
   - Queries logged for improvement (anonymized)
   - Crisis detections logged for safety
   - No IP address logging (in default configuration)

3. **HIPAA considerations**
   - System designed to not require or collect PHI
   - Users should not enter personal health information
   - User guide instructs against including PHI in queries

**Compliance recommendations:**

- Review with institutional privacy/compliance team
- Ensure deployment meets local data protection requirements
- Consider adding privacy policy link in UI
- Document data retention and deletion procedures

### 5.4 Security Incident Response

**If you suspect a security incident:**

1. **Immediate actions**
   - Assess severity and scope
   - Contain if possible (e.g., take system offline if critical)
   - Document everything

2. **Notification**
   - Alert security team or institutional CISO
   - Follow institutional incident response procedures
   - Notify affected parties if required by policy/law

3. **Investigation**
   - Review logs for indicators of compromise
   - Identify attack vector
   - Determine data accessed or modified

4. **Remediation**
   - Patch vulnerabilities
   - Rotate compromised credentials
   - Restore from clean backups if needed

5. **Post-incident**
   - Document lessons learned
   - Update security procedures
   - Implement preventive measures

---

<a name="troubleshooting"></a>
## 6. Troubleshooting

### 6.1 Common Issues and Solutions

#### Backend Won't Start

**Symptoms:** Backend container or process fails to start

**Common causes:**
1. **Missing environment variables**
   - Check all required variables are set
   - Verify variable names match expected format

2. **Database connection failure**
   - Verify Supabase URL and keys
   - Check network connectivity to Supabase
   - Confirm pgvector extension is enabled

3. **Port already in use**
   - Check if another process is using port 8000
   - Kill conflicting process or change port

**Solution steps:**
```bash
# Check logs
docker-compose logs backend

# Verify environment variables
docker-compose config

# Test database connection
psql [SUPABASE_URL] -c "SELECT 1"
```

#### Frontend Can't Connect to Backend

**Symptoms:** Frontend loads but API calls fail, CORS errors

**Common causes:**
1. **Incorrect backend URL**
   - Check `VITE_API_URL` in frontend `.env`
   - Verify backend is running and accessible

2. **CORS configuration**
   - Backend `ALLOWED_ORIGINS` doesn't include frontend URL
   - Update backend `.env` and restart

**Solution:**
```bash
# Frontend .env
VITE_API_URL=http://localhost:8000

# Backend .env
ALLOWED_ORIGINS=http://localhost:5173
```

#### Queries Return No Results

**Symptoms:** User queries complete but show "No relevant information found"

**Common causes:**
1. **Empty knowledge base**
   - Documents not ingested
   - Run ingestion script

2. **Embedding model mismatch**
   - Query embeddings use different model than document embeddings
   - Re-ingest documents with correct model

3. **Similarity threshold too high**
   - Adjust threshold in backend code

**Solution:**
```bash
# Check document count in Supabase
# Should have rows in embeddings table

# Re-run ingestion
python -m app.scripts.ingest_documents
```

#### Crisis Detection Not Working

**Symptoms:** Crisis keywords don't trigger alert

**Common causes:**
1. **Crisis detection disabled**
   - Check `ENABLE_CRISIS_DETECTION` environment variable

2. **Keyword list outdated**
   - Review crisis keyword configuration

**Solution:**
```bash
# Backend .env
ENABLE_CRISIS_DETECTION=true

# Test with known crisis keyword
# Query: "I'm thinking about suicide"
# Should trigger crisis alert
```

#### High Response Times

**Symptoms:** Queries take >10 seconds to return

**Common causes:**
1. **Gemini API latency**
   - Network issues
   - API rate limiting
   - Model selection (some models are slower)

2. **Database performance**
   - Vector search on large dataset
   - Supabase tier limits

3. **Cold start**
   - First query after deployment slower (normal)

**Solution:**
```bash
# Check backend logs for timing breakdown
# Identify which step is slow (embedding, search, LLM)

# Consider:
# - Using faster embedding model
# - Upgrading Supabase tier
# - Optimizing vector search parameters
```

### 6.2 Diagnostic Commands

**Check service status:**
```bash
# Docker
docker-compose ps

# OpenShift
oc get pods
```

**View recent logs:**
```bash
# Docker
docker-compose logs --tail=50 backend

# OpenShift
oc logs --tail=50 deployment/nc-ask-backend
```

**Test backend health:**
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

**Test database connection:**
```bash
# From backend container
python -c "from app.db import get_supabase_client; print(get_supabase_client())"
```

**Check API quotas:**
- Gemini API: Check Google Cloud Console or AI Studio for usage

### 6.3 Getting Help

**Before requesting support:**
1. Check error logs for specific error messages
2. Review this troubleshooting section
3. Check setup documentation (03-10)
4. Search GitHub issues (if applicable)

**When requesting support, include:**
- Clear description of issue
- Steps to reproduce
- Error messages (full text)
- Environment details (deployment type, platform)
- Logs (relevant sections)

---

<a name="support"></a>
## 7. Support and Resources

### 7.1 Documentation Resources

**In this repository:**
- **[02_WHICH_SETUP.md](./02_WHICH_SETUP.md)** - Choosing deployment approach
- **[03_DOCKER_SETUP.md](./03_DOCKER_SETUP.md)** - Docker setup detailed guide
- **[04_LOCAL_SETUP.md](./04_LOCAL_SETUP.md)** - Local development setup
- **[05_DEPLOYMENT.md](./05_DEPLOYMENT.md)** - Cloud deployment guide
- **[06_ARCHITECTURE.md](./06_ARCHITECTURE.md)** - System architecture
- **[07_IMPLEMENTATION_SUMMARY.md](./07_IMPLEMENTATION_SUMMARY.md)** - Implementation details
- **[08_SAFETY.md](./08_SAFETY.md)** - Crisis detection and safety
- **[09_NC_ASK_AI_SG_Guiding_Principles](./09_NC_ASK_AI_SG_Guiding_Principles_v0.docx)** - Security and governance
- **[10_DEPLOYMENT.md](./10_DEPLOYMENT.md)** - OpenShift deployment
- **[CLAUDE.md](./CLAUDE.md)** - Developer guide and AI-assisted development

### 7.2 External Resources

**Technologies:**
- **Docker**: [docs.docker.com](https://docs.docker.com)
- **FastAPI**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **React**: [react.dev](https://react.dev)
- **Supabase**: [supabase.com/docs](https://supabase.com/docs)
- **Google Gemini**: [ai.google.dev](https://ai.google.dev)

**Deployment Platforms:**
- **Vercel**: [vercel.com/docs](https://vercel.com/docs)
- **Render**: [render.com/docs](https://render.com/docs)
- **OpenShift**: [docs.openshift.com](https://docs.openshift.com)

### 7.3 Community and Support

**Project Repository:**
- GitHub: [To be added]
- Issue Tracker: [To be added]

**Contact:**
- Technical Support: [To be added]
- Security Issues: [To be added]

### 7.4 Quick Reference

**Common Commands:**

```bash
# Docker Development
docker-compose up -d          # Start services in background
docker-compose down           # Stop and remove containers
docker-compose logs -f        # Follow logs
docker-compose restart        # Restart all services

# Health Checks
curl http://localhost:8000/health           # Backend health
curl http://localhost:8000/docs             # API documentation

# OpenShift
oc login                      # Login to cluster
oc get pods                   # List pods
oc logs -f <pod-name>         # Follow pod logs
oc rollout restart deploy/nc-ask-backend  # Restart deployment
```

**Important URLs:**
- Frontend: `http://localhost:5173` (dev) or production URL
- Backend: `http://localhost:8000` (dev) or production URL
- API Docs: `http://localhost:8000/docs`
- Supabase Dashboard: `https://app.supabase.com`

---

## Document Information

**Version:** 1.0
**Last Updated:** Nov 16 2025
**Maintained by:** NC-ASK Development Team

**For questions or feedback:**
[Contact information to be added]

---

**Related Documentation:**
- [User Guide](./USER_GUIDE.md) - For end users (patients, caregivers, providers)
- [Documentation Plan](./DOCUMENTATION_PLAN.md) - Overall documentation strategy
- [Video Scripts](./VIDEO_SCRIPTS.md) - Video production guides
