# Streamlit External Access Setup Guide

This guide explains how to expose the Streamlit-based Pharmacovigilance solution to the outside world.

## 🌐 Public Access URLs

**Streamlit Application:**
```
http://49.36.80.21:8501
```

**Backend API:**
```
http://49.36.80.21:5000/api
```

**Health Check:**
```
http://49.36.80.21:5000/health
```

## 📋 Overview

The Streamlit solution includes:
- **Backend Service**: Flask API on port 5000
- **Streamlit Frontend**: Web interface on port 8501

Both services are configured to accept external connections.

## 🚀 Quick Start

### 1. Set Environment Variables

Create a `.env` file in the project root:

```bash
# API Keys (Required)
OPENAI_API_KEY=your_openai_api_key_here
PUBMED_API_KEY=your_pubmed_api_key_here
PUBMED_EMAIL=your_email@example.com

# OpenAI Configuration
OPENAI_MODEL=gpt-4.1-mini

# PubMed Configuration
MAX_ARTICLES_PER_SEARCH=100

# CORS Configuration (allow all origins for development)
CORS_ORIGINS=*

# Optional: Secret Key for Flask
SECRET_KEY=your-secret-key-here
```

### 2. Start the Services

```bash
cd c:\Office_Work\Hikma\pharma_pv_poc
docker-compose -f docker-compose.streamlit.yml up -d
```

### 3. Verify Services Are Running

```bash
docker-compose -f docker-compose.streamlit.yml ps
```

Expected output:
```
NAME                  IMAGE                     COMMAND                  SERVICE     STATUS      PORTS
pharma_pv_backend     pharma_pv_poc-backend     "/app/docker-entrypo…"   backend     running     0.0.0.0:5000->5000/tcp
pharma_pv_streamlit   pharma_pv_poc-streamlit   "streamlit run app.p…"   streamlit   running     0.0.0.0:8501->8501/tcp
```

## 🔐 Configure Windows Firewall

### Using PowerShell (Administrator Required)

Open PowerShell as **Administrator** and run:

```powershell
# Allow Backend API (Port 5000)
New-NetFirewallRule -DisplayName "Pharma PV Backend" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow

# Allow Streamlit App (Port 8501)
New-NetFirewallRule -DisplayName "Pharma PV Streamlit" -Direction Inbound -LocalPort 8501 -Protocol TCP -Action Allow
```

### Verify Firewall Rules

```powershell
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Pharma PV*"} | Select-Object DisplayName, Enabled
```

## 🌍 Router Configuration (For Internet Access)

If you're behind a home/office router and want internet access:

### Step 1: Access Your Router

1. Find your router's IP address (usually `192.168.1.1` or `192.168.31.1`)
2. Open it in a web browser
3. Log in with admin credentials

### Step 2: Configure Port Forwarding

Add these port forwarding rules:

| Service           | External Port | Internal IP      | Internal Port | Protocol |
|-------------------|---------------|------------------|---------------|----------|
| Streamlit         | 8501          | 192.168.31.151   | 8501          | TCP      |
| Backend API       | 5000          | 192.168.31.151   | 5000          | TCP      |

### Step 3: Find Your Public IP

**Windows PowerShell:**
```powershell
Invoke-RestMethod -Uri "https://api.ipify.org"
```

**Command Prompt:**
```cmd
curl https://api.ipify.org
```

## ✅ Test External Access

### Test From Your Computer

**Test Streamlit:**
```powershell
Start-Process "http://49.36.80.21:8501"
```

**Test Backend:**
```powershell
curl http://49.36.80.21:5000/health
```

Expected response:
```json
{
  "service": "Pharmacovigilance Literature Monitoring",
  "status": "healthy"
}
```

### Test From Another Device

1. Connect your phone/tablet to mobile data (not WiFi)
2. Open browser and navigate to: `http://49.36.80.21:8501`
3. You should see the Streamlit interface

## 📱 Access URLs Summary

| Access Type          | URL                                |
|----------------------|------------------------------------|
| **Local Computer**   | http://localhost:8501              |
| **Local Network**    | http://192.168.31.151:8501         |
| **Internet (Public)**| http://49.36.80.21:8501            |

## 🔧 Streamlit Configuration

The application is configured with these settings in `.streamlit/config.toml`:

```toml
[server]
enableCORS = true              # Allow cross-origin requests
enableXsrfProtection = false   # Disable XSRF protection for external access
headless = true                # Run without browser popup
port = 8501                    # Port to listen on
address = "0.0.0.0"            # Listen on all interfaces

[browser]
gatherUsageStats = false       # Disable telemetry
serverAddress = "0.0.0.0"      # Public address
serverPort = 8501              # Public port
```

## 🛡️ Security Considerations

### For Development/Testing

The current configuration is suitable for development and testing with:
- CORS enabled for all origins (`*`)
- XSRF protection disabled
- All network interfaces exposed

### For Production Deployment

1. **Enable HTTPS:**
   - Use a reverse proxy (Nginx, Traefik)
   - Obtain SSL certificate (Let's Encrypt)
   - Update URLs to use `https://`

2. **Restrict CORS Origins:**
   ```bash
   CORS_ORIGINS=https://yourdomain.com
   ```

3. **Enable Authentication:**
   - Add user authentication to Streamlit
   - Implement API key authentication for backend

4. **Use a Domain Name:**
   - Register a domain
   - Point it to your public IP
   - Access via: `https://yourdomain.com:8501`

5. **Enable XSRF Protection:**
   ```toml
   [server]
   enableXsrfProtection = true
   ```

6. **Limit Access:**
   - Use VPN for administrative access
   - Implement IP whitelisting
   - Set up rate limiting

## 🔍 Troubleshooting

### Issue: Cannot Access From External Network

**Check 1: Verify Containers Are Running**
```bash
docker-compose -f docker-compose.streamlit.yml ps
```

**Check 2: Verify Ports Are Listening**
```powershell
netstat -ano | findstr ":8501"
netstat -ano | findstr ":5000"
```

Should show: `0.0.0.0:8501` and `0.0.0.0:5000`

**Check 3: Test Local Access First**
```bash
curl http://localhost:8501
curl http://localhost:5000/health
```

**Check 4: Verify Firewall Rules**
```powershell
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Pharma PV*"}
```

**Check 5: Check Router Port Forwarding**
- Ensure ports 8501 and 5000 are forwarded to 192.168.31.151

### Issue: Streamlit Shows "Connection Error"

**Solution 1: Check Backend is Running**
```bash
curl http://localhost:5000/health
```

**Solution 2: Restart Backend**
```bash
docker-compose -f docker-compose.streamlit.yml restart backend
```

**Solution 3: Check Backend Logs**
```bash
docker logs pharma_pv_backend --tail 50
```

### Issue: "Failed to Load Content"

**Solution: Clear Browser Cache**
1. Clear browser cache and cookies
2. Hard refresh: `Ctrl + F5` (Windows) or `Cmd + Shift + R` (Mac)
3. Try incognito/private mode

### Issue: Slow Performance

**Solution 1: Increase Docker Resources**
- Docker Desktop → Settings → Resources
- Increase CPU and Memory allocation

**Solution 2: Check Network Speed**
```powershell
Test-Connection -ComputerName 8.8.8.8 -Count 5
```

## 📊 Monitoring

### View Container Status
```bash
docker-compose -f docker-compose.streamlit.yml ps
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.streamlit.yml logs -f

# Backend only
docker logs pharma_pv_backend -f

# Streamlit only
docker logs pharma_pv_streamlit -f
```

### Check Resource Usage
```bash
docker stats
```

### Health Checks
```bash
# Backend health
curl http://localhost:5000/health

# Streamlit health
curl http://localhost:8501/_stcore/health
```

## 🔄 Managing the Application

### Start Services
```bash
docker-compose -f docker-compose.streamlit.yml up -d
```

### Stop Services
```bash
docker-compose -f docker-compose.streamlit.yml down
```

### Restart Services
```bash
docker-compose -f docker-compose.streamlit.yml restart
```

### Rebuild Services
```bash
docker-compose -f docker-compose.streamlit.yml up --build -d
```

### Update Application
```bash
# Stop services
docker-compose -f docker-compose.streamlit.yml down

# Pull latest changes (if from git)
git pull

# Rebuild and start
docker-compose -f docker-compose.streamlit.yml up --build -d
```

## 📞 Support

### Common Commands

**Get Your Local IP:**
```powershell
ipconfig | findstr IPv4
```

**Get Your Public IP:**
```powershell
Invoke-RestMethod -Uri "https://api.ipify.org"
```

**Test Port Accessibility:**
```powershell
Test-NetConnection -ComputerName 49.36.80.21 -Port 8501
```

### Logs Location

- **Backend Logs**: `docker logs pharma_pv_backend`
- **Streamlit Logs**: `docker logs pharma_pv_streamlit`
- **Docker Compose Logs**: `docker-compose -f docker-compose.streamlit.yml logs`

## 🎯 Summary

**To expose Streamlit to the world:**

1. ✅ **Services configured**: Ports bound to 0.0.0.0
2. ✅ **Streamlit config**: CORS enabled, headless mode
3. ⚠️ **Firewall**: Configure Windows Firewall (requires admin)
4. ⚠️ **Router**: Configure port forwarding (if behind router)

**Your public URL:** http://49.36.80.21:8501

---

**Last Updated**: November 2, 2025

