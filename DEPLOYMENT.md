# Perf-Chart-Gen Docker Deployment Guide

Complete guide for deploying the Streamlit Performance Report Generator using Docker and Coolify.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [File Setup](#file-setup)
3. [Local Testing with Docker](#local-testing-with-docker)
4. [Coolify VPS Deployment](#coolify-vps-deployment)
5. [WordPress Integration](#wordpress-integration)
6. [Troubleshooting](#troubleshooting)
7. [Domain Migration](#domain-migration)

---

## Prerequisites

**On Your Mac (for local testing):**
- Docker Desktop installed
- Git installed
- Access to your GitHub repository (Coachcalixte/Perf-Chart-Gen)

**On Your VPS:**
- Coolify installed and configured
- Domain pointed to VPS: `tools-backend.hanstack.win`
- Port 80 and 443 open for HTTP/HTTPS

**WordPress Sites:**
- Local: `http://refsc.local` (WPLocal)
- Production: `https://wordpress.hanstack.win`

---

## File Setup

### Step 1: Copy Files to Your Perf-Chart-Gen Repository

All deployment files are in your WordPress theme at:
```
wp-content/themes/strength-conditioning-theme/docker-deployment/
```

**Copy these files to your Perf-Chart-Gen repository root:**

```bash
cd /path/to/Perf-Chart-Gen

# Copy all deployment files
cp /path/to/wordpress/wp-content/themes/strength-conditioning-theme/docker-deployment/Dockerfile .
cp /path/to/wordpress/wp-content/themes/strength-conditioning-theme/docker-deployment/.dockerignore .
cp /path/to/wordpress/wp-content/themes/strength-conditioning-theme/docker-deployment/docker-compose.yml .

# Copy Streamlit config (create directory if needed)
mkdir -p .streamlit
cp /path/to/wordpress/wp-content/themes/strength-conditioning-theme/docker-deployment/.streamlit/config.toml .streamlit/

# Optional: nginx config (for reference)
cp /path/to/wordpress/wp-content/themes/strength-conditioning-theme/docker-deployment/nginx-headers.conf .
```

### Step 2: Verify Repository Structure

Your Perf-Chart-Gen repository should now have:

```
Perf-Chart-Gen/
├── .devcontainer/
├── .streamlit/
│   └── config.toml          ← NEW
├── __pycache__/
├── athlete_report.py
├── athlete_report_streamlit.py
├── team_report_generator.py
├── sample_athletes.csv
├── requirements.txt
├── Dockerfile               ← NEW
├── .dockerignore           ← NEW
├── docker-compose.yml      ← NEW
├── nginx-headers.conf      ← NEW (optional)
└── README.md
```

### Step 3: Commit to Git

```bash
cd /path/to/Perf-Chart-Gen

git add Dockerfile .dockerignore docker-compose.yml .streamlit/config.toml nginx-headers.conf
git commit -m "Add Docker deployment configuration with iframe support"
git push origin main
```

---

## Local Testing with Docker

Test the Docker container locally before deploying to VPS.

### Build the Docker Image

```bash
cd /path/to/Perf-Chart-Gen

# Build the image
docker build -t perf-chart-gen:latest .
```

**Expected output:**
```
[+] Building 45.2s (14/14) FINISHED
 => [internal] load build definition
 => => transferring dockerfile: 1.23kB
 ...
 => exporting to image
Successfully tagged perf-chart-gen:latest
```

### Run with Docker Compose

```bash
# Start the container
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### Access the App Locally

Open your browser:
```
http://localhost:8501
```

You should see the Streamlit Performance Report Generator interface.

### Test iframe Embedding Locally

1. **Create a test HTML file** (`test-iframe.html`):

```html
<!DOCTYPE html>
<html>
<head>
    <title>Iframe Test</title>
</head>
<body>
    <h1>Testing Streamlit Iframe Embedding</h1>
    <iframe
        src="http://localhost:8501"
        width="100%"
        height="800px"
        style="border: 1px solid #ccc;"
        sandbox="allow-scripts allow-same-origin allow-forms allow-downloads"
    ></iframe>
</body>
</html>
```

2. **Open the HTML file** in your browser
3. **Verify** the Streamlit app loads inside the iframe

---

## Coolify VPS Deployment

### Step 1: Log in to Coolify Dashboard

1. Open your Coolify dashboard: `https://your-coolify-domain.com`
2. Navigate to **Applications** or **Projects**

### Step 2: Create New Application

**Click "New Application"** and configure:

**General Settings:**
- **Name:** `perf-chart-gen` or `test-report-generator`
- **Source:** GitHub Repository
- **Repository:** `Coachcalixte/Perf-Chart-Gen`
- **Branch:** `main`
- **Build Pack:** Dockerfile

**Domain Settings:**
- **Domain:** `tools-backend.hanstack.win`
- **Port:** `8501`
- **Protocol:** HTTPS (Coolify auto-manages SSL)

**Environment Variables:**
```env
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
ALLOWED_ORIGINS=http://refsc.local,https://wordpress.hanstack.win,https://tools-backend.hanstack.win
```

### Step 3: Configure Build Settings

**Dockerfile Path:** `./Dockerfile` (should be auto-detected)

**Build Command:** (Leave empty, Dockerfile handles this)

**Start Command:** (Leave empty, Dockerfile CMD handles this)

### Step 4: Configure Nginx for iframe Support (if needed)

If Coolify's default nginx config blocks iframes:

1. Go to **Advanced Settings** or **Custom Nginx Configuration**
2. Enable **Custom Nginx Config**
3. Paste the contents from `nginx-headers.conf`
4. **Important:** Update the domains in the configuration:

```nginx
add_header Content-Security-Policy "frame-ancestors 'self' https://wordpress.hanstack.win http://refsc.local https://*.hanstack.win" always;
```

### Step 5: Deploy

1. Click **Deploy** or **Save and Deploy**
2. Coolify will:
   - Clone your repository
   - Build the Docker image
   - Start the container
   - Configure SSL (Let's Encrypt)
   - Set up reverse proxy

### Step 6: Monitor Deployment

**Check deployment logs:**
- Watch build progress in Coolify dashboard
- Look for "Application is running" message

**Expected deployment time:** 2-5 minutes

### Step 7: Verify Deployment

**Access your app:**
```
https://tools-backend.hanstack.win
```

You should see the Streamlit Performance Report Generator.

**Check SSL:**
- Browser should show secure padlock
- Certificate should be valid (Let's Encrypt)

---

## WordPress Integration

### Step 1: Create WordPress Page (if not already done)

**In WordPress Admin:**

1. Go to **Pages → Add New**
2. **Title:** Test Report Generator
3. **Slug:** `test-report-generator`
4. **Template:** Select **"Iframe Tool"**
5. **Content:** Paste this URL:
   ```
   https://tools-backend.hanstack.win
   ```
6. **Excerpt:** (Optional)
   ```
   Generate comprehensive performance reports for athletes with visualizations and downloadable PDFs.
   ```
7. Click **Publish**

### Step 2: Test iframe Embedding from WPLocal

1. Open WPLocal site: `http://refsc.local`
2. Navigate to **Tools** page
3. Click **"Use Tool"** on Test Report Generator card
4. **Verify:**
   - Page loads with iframe
   - Streamlit app displays inside iframe
   - App is fully functional (upload CSV, generate reports)
   - No console errors (press F12 → Console tab)

### Step 3: Test from Production WordPress

1. Open production site: `https://wordpress.hanstack.win`
2. Navigate to Test Report Generator page
3. **Verify:** Same as Step 2

### Troubleshooting iframe Issues

**If iframe shows blank or errors:**

1. **Check browser console** (F12 → Console):
   - Look for CORS errors
   - Look for X-Frame-Options errors

2. **Common error messages and fixes:**

   **Error:** `Refused to display in a frame because it set 'X-Frame-Options' to 'deny'`
   - **Fix:** Add custom nginx config in Coolify (see [Step 4](#step-4-configure-nginx-for-iframe-support-if-needed))

   **Error:** `Blocked by Content Security Policy`
   - **Fix:** Update CSP headers in nginx config to include your WordPress domain

   **Error:** `Mixed Content: The page was loaded over HTTPS, but requested an insecure resource`
   - **Fix:** Ensure Streamlit app is accessed via HTTPS (should be automatic with Coolify)

3. **Verify Streamlit config:**
   - Check `.streamlit/config.toml` is in your repository
   - Verify `enableCORS = true`
   - Verify `enableXsrfProtection = false`

---

## Troubleshooting

### Container Won't Start

**Check logs:**
```bash
# If using Docker locally
docker-compose logs -f

# If using Coolify
# Check deployment logs in Coolify dashboard
```

**Common issues:**

1. **Port already in use:**
   ```
   Error: bind: address already in use
   ```
   - **Fix:** Change port in docker-compose.yml or stop conflicting service

2. **Missing dependencies:**
   ```
   ModuleNotFoundError: No module named 'streamlit'
   ```
   - **Fix:** Verify requirements.txt is copied correctly
   - Rebuild image: `docker-compose build --no-cache`

3. **File not found:**
   ```
   FileNotFoundError: [Errno 2] No such file or directory: 'athlete_report_streamlit.py'
   ```
   - **Fix:** Verify all Python files are in repository root
   - Check .dockerignore isn't excluding necessary files

### App Loads but Shows Errors

1. **CSV Upload Fails:**
   - Check file permissions in container
   - Verify `/app/reports` directory exists
   - Check Streamlit max upload size in config.toml

2. **PDF Generation Fails:**
   - Check reportlab is installed: `docker exec -it perf-chart-gen pip list | grep reportlab`
   - Verify system fonts are available

3. **Matplotlib Errors:**
   - Check system dependencies installed in Dockerfile
   - Verify libfreetype6-dev and libpng-dev are installed

### iframe Embedding Issues

**App works standalone but not in iframe:**

1. **Verify CORS headers:**
   ```bash
   curl -I https://tools-backend.hanstack.win
   ```
   Look for:
   ```
   Access-Control-Allow-Origin: *
   X-Frame-Options: ALLOW-FROM https://wordpress.hanstack.win
   Content-Security-Policy: frame-ancestors 'self' https://wordpress.hanstack.win
   ```

2. **Test in incognito/private window:**
   - Rules out browser cache or extension issues

3. **Check WordPress page:**
   - View page source
   - Verify iframe src is HTTPS (not HTTP)
   - Verify sandbox attributes are present

### Coolify Deployment Issues

1. **Build fails:**
   - Check Coolify has access to GitHub repository
   - Verify GitHub token/SSH key is configured
   - Check build logs for specific errors

2. **SSL certificate not working:**
   - Verify domain DNS points to VPS IP
   - Check Coolify SSL settings
   - May need to wait 5-10 minutes for Let's Encrypt

3. **Container crashes after deployment:**
   - Check Coolify logs
   - Verify environment variables are set correctly
   - Check health check settings

---

## Domain Migration

When you change to a new domain in the future:

### Step 1: Update Environment Variables

**In Coolify:**
1. Go to Application Settings
2. Update `ALLOWED_ORIGINS` environment variable:
   ```env
   ALLOWED_ORIGINS=https://new-domain.com,https://wordpress.new-domain.com
   ```
3. Redeploy application

### Step 2: Update Nginx Config (if using custom config)

Update the `Content-Security-Policy` and `X-Frame-Options` headers:

```nginx
add_header X-Frame-Options "ALLOW-FROM https://new-domain.com" always;
add_header Content-Security-Policy "frame-ancestors 'self' https://new-domain.com https://*.new-domain.com" always;
```

### Step 3: Update WordPress

1. Change iframe URL in WordPress page content
2. Update any hardcoded links

### Step 4: Update DNS

1. Point new domain to VPS IP
2. Update Coolify domain settings
3. Coolify will automatically request new SSL certificate

---

## Useful Commands

**Docker:**
```bash
# Build image
docker build -t perf-chart-gen:latest .

# Run container
docker run -d -p 8501:8501 --name perf-chart-gen perf-chart-gen:latest

# View logs
docker logs -f perf-chart-gen

# Stop container
docker stop perf-chart-gen

# Remove container
docker rm perf-chart-gen

# View running containers
docker ps

# Execute command in container
docker exec -it perf-chart-gen bash
```

**Docker Compose:**
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild and restart
docker-compose up -d --build

# Remove everything (including volumes)
docker-compose down -v
```

**Debugging:**
```bash
# Check if app is responding
curl -I https://tools-backend.hanstack.win

# Test iframe headers
curl -I https://tools-backend.hanstack.win | grep -i "frame\|csp\|cors"

# Check health endpoint
curl https://tools-backend.hanstack.win/_stcore/health
```

---

## Security Notes

1. **X-Frame-Options:**
   - Currently set to ALLOW-FROM specific domains
   - For maximum security, don't use `ALLOWALL`

2. **XSRF Protection:**
   - Disabled in Streamlit config for iframe support
   - Acceptable for read-only/public tools
   - If app handles sensitive data, reconsider

3. **CORS:**
   - Currently allows all origins (`*`)
   - Can restrict to specific WordPress domains if needed

4. **Container Security:**
   - Container runs as root (default for Streamlit)
   - For production, consider running as non-root user
   - Add security scanning to CI/CD pipeline

---

## Support and References

**Streamlit Documentation:**
- https://docs.streamlit.io/
- https://docs.streamlit.io/develop/concepts/configuration

**Coolify Documentation:**
- https://coolify.io/docs

**Docker Documentation:**
- https://docs.docker.com/

**iframe Embedding Resources:**
- MDN: X-Frame-Options
- MDN: Content-Security-Policy (CSP)

---

**Document Version:** 1.0
**Last Updated:** December 2024
**Maintained By:** Development Team
