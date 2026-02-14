# Security Documentation

## Overview

This document describes the security measures implemented in the Athlete Performance Report Generator application.

## Security Features Implemented

### 1. Input Validation & Sanitization

**CSV Security Checks:**
- Maximum file size: 10MB (configurable)
- Maximum rows: 500 athletes per upload
- Maximum columns: 50
- Maximum cell length: 200 characters

**CSV Injection Prevention:**
The following patterns are detected and neutralized:
- Formula injection (`=`, `@`, `+`, `-`, `!`)
- Command injection (`|`, `;`)
- XSS attempts (`<script`, `javascript:`, `data:`)
- Event handler injection (`onclick=`, etc.)

When dangerous patterns are detected, cells are prefixed with a single quote (`'`) to prevent formula execution in spreadsheet applications.

### 2. Rate Limiting

Per-session rate limits (1-hour window):
| Action | Limit |
|--------|-------|
| CSV Uploads | 20/hour |
| PDF Reports | 50/hour |
| Team Reports (ZIP) | 5/hour |

Rate limits are enforced per browser session and reset after one hour.

### 3. Usage Logging

All significant events are logged to `logs/app.log`:
- CSV uploads (session ID, athlete count, available tests)
- PDF generations (session ID, season type)
- Team report downloads (session ID, athlete count)
- Errors (type, details)

**Privacy Considerations:**
- Athlete names are NOT logged
- Session IDs are anonymized hashes
- Email addresses are hashed in logs

### 4. Email Collection

- Optional email collection in sidebar
- Email validation (format, common typos)
- Consent checkbox required
- Stored securely in `logs/collected_emails.json`
- Not exposed via any API

## Configuration

Security settings can be adjusted in `security.py`:

```python
# Rate limiting configuration
RATE_LIMITS = {
    "uploads_per_hour": 20,
    "pdfs_per_hour": 50,
    "team_reports_per_hour": 5,
}

# CSV validation limits
CSV_LIMITS = {
    "max_rows": 500,
    "max_columns": 50,
    "max_cell_length": 200,
    "max_file_size_mb": 10,
}
```

## Data Handling

### Data Storage
- **In-Memory Only**: Uploaded CSV data is processed in memory and not persisted
- **Session Isolation**: Each user session is isolated
- **Auto-Cleanup**: Data is cleared when sessions end

### Data NOT Stored
- Uploaded CSV files
- Athlete names (except in generated PDFs during session)
- Performance data

### Data Stored (Optional)
- Email addresses (if user subscribes)
- Anonymous usage logs

## Deployment Security

### Streamlit Configuration (`.streamlit/config.toml`)

```toml
[server]
enableCORS = true
enableXsrfProtection = false  # Required for iframe embedding
maxUploadSize = 50  # MB, additional limit in security.py
fileWatcherType = "none"

[browser]
gatherUsageStats = false
```

### Docker Security
- Non-root execution (Python slim image default)
- Minimal base image
- No secrets in image
- Health checks enabled

## Recommendations for Production

### Immediate (Implemented)
- [x] Input validation and sanitization
- [x] Rate limiting
- [x] Usage logging
- [x] File size limits

### Recommended Additions

#### 1. Cloudflare Protection
Add Cloudflare in front of your deployment for:
- **DDoS Protection**: Automatic mitigation of volumetric attacks
- **WAF (Web Application Firewall)**: Block common attack patterns
- **Bot Protection**: Filter out malicious bots
- **SSL/TLS**: Free SSL certificates
- **Rate Limiting**: Additional layer of rate limiting

**Setup Steps:**
1. Create Cloudflare account (free tier available)
2. Add your domain to Cloudflare
3. Update nameservers at your registrar
4. Enable "Under Attack Mode" if needed
5. Configure WAF rules

#### 2. Authentication Layer
For membership integration:
- WordPress authentication via cookies/tokens
- API key validation
- OAuth2 integration

#### 3. Database Logging
For better analytics:
- PostgreSQL for structured logging
- Grafana/Prometheus for monitoring
- Alert rules for suspicious activity

## Monitoring

### Log Analysis
View recent logs:
```bash
tail -f logs/app.log
```

### Usage Statistics
The `security.py` module provides:
```python
from security import get_usage_stats
stats = get_usage_stats()
print(f"Total uploads: {stats['total_uploads']}")
print(f"Unique sessions: {stats['unique_sessions']}")
print(f"Emails collected: {stats['emails_collected']}")
```

## Incident Response

### If You Detect Abuse
1. Check logs for suspicious patterns
2. Identify session IDs involved
3. Consider reducing rate limits temporarily
4. Enable Cloudflare "Under Attack Mode" if available
5. Review and tighten validation rules

### If Data Breach Suspected
1. Rotate any API keys/secrets
2. Review collected emails file
3. Check Docker container for unauthorized access
4. Review Coolify deployment logs

## Security Contacts

For security concerns or to report vulnerabilities:
- Repository: https://github.com/Coachcalixte/Perf-Chart-Gen
- Create a private security advisory on GitHub

## Changelog

| Date | Change |
|------|--------|
| 2026-02-14 | Initial security implementation |
| | - CSV validation and sanitization |
| | - Rate limiting (uploads, PDFs, team reports) |
| | - Usage logging |
| | - Optional email collection |
| | - Optional email collection |
