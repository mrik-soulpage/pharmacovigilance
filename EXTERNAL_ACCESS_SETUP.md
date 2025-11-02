# External Access Setup Guide

This guide provides step-by-step instructions to expose the Pharma PV POC (non-Streamlit) Docker solution to the outside world.

## Overview

The application consists of two main services:
- **Backend (Flask API)**: Exposed on port `5000`
- **Frontend (React/Vite)**: Exposed on port `5174`

## Prerequisites

- Docker and Docker Compose installed
- Network access to your server (local network or internet)
- Firewall permissions to open necessary ports
- Required API keys (PubMed, OpenAI)

## Step 1: Configure Environment Variables

Create a `.env` file in the project root directory with the following variables:

```bash
# API Keys (Required)
PUBMED_API_KEY=your_pubmed_api_key_here
PUBMED_EMAIL=your_email@example.com
OPENAI_API_KEY=your_openai_api_key_here

# OpenAI Configuration
OPENAI_MODEL=gpt-4.1-mini

# PubMed Search Configuration
MAX_ARTICLES_PER_SEARCH=100

# External Access Configuration
# Set PUBLIC_HOST to your server's public IP address or domain name
PUBLIC_HOST=http://YOUR_SERVER_IP_OR_DOMAIN

# CORS Configuration
# For development: CORS_ORIGINS=*
# For production: CORS_ORIGINS=http://your-domain.com,https://your-domain.com
CORS_ORIGINS=*
```

### Setting PUBLIC_HOST

Replace `YOUR_SERVER_IP_OR_DOMAIN` with:

- **Local Network Access**: Use your server's local IP address
  ```bash
  PUBLIC_HOST=http://192.168.1.100
  ```
  
- **Public Internet Access**: Use your public IP or domain
  ```bash
  PUBLIC_HOST=http://203.0.113.45
  # or
  PUBLIC_HOST=http://yourdomain.com
  ```

- **HTTPS (with SSL certificate)**: Use https protocol
  ```bash
  PUBLIC_HOST=https://yourdomain.com
  ```

### Finding Your Server IP Address

**Windows:**
```powershell
# Local IP address
ipconfig | findstr IPv4

# Public IP address
Invoke-RestMethod -Uri "https://api.ipify.org"
```

**Linux/Mac:**
```bash
# Local IP address
hostname -I

# Public IP address
curl https://api.ipify.org
```

## Step 2: Configure Firewall Rules

### Windows Firewall

Open PowerShell as Administrator and run:

```powershell
# Allow Backend port
New-NetFirewallRule -DisplayName "Pharma PV Backend" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow

# Allow Frontend port
New-NetFirewallRule -DisplayName "Pharma PV Frontend" -Direction Inbound -LocalPort 5174 -Protocol TCP -Action Allow
```

### Linux (UFW)

```bash
sudo ufw allow 5000/tcp
sudo ufw allow 5174/tcp
sudo ufw reload
```

### Linux (iptables)

```bash
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 5174 -j ACCEPT
sudo iptables-save
```

### Router/Cloud Provider Configuration

If accessing from outside your local network, you'll also need to:

1. **Port Forwarding (Home/Office Router)**:
   - Log into your router's admin panel
   - Navigate to Port Forwarding settings
   - Forward external port 5000 to internal IP:5000
   - Forward external port 5174 to internal IP:5174

2. **Cloud Provider (AWS/Azure/GCP)**:
   - Configure Security Groups (AWS) or Network Security Groups (Azure)
   - Allow inbound traffic on ports 5000 and 5174
   - Ensure the instance has a public IP address

## Step 3: Build and Start the Services

```bash
# Navigate to project directory
cd c:\Office_Work\Hikma\pharma_pv_poc

# Build and start services
docker-compose up --build -d

# Verify services are running
docker-compose ps
```

Expected output:
```
NAME                   COMMAND                  SERVICE    STATUS      PORTS
pharma_pv_backend      "python -m flask run…"   backend    running     0.0.0.0:5000->5000/tcp
pharma_pv_frontend     "/docker-entrypoint.…"   frontend   running     0.0.0.0:5174->80/tcp
```

## Step 4: Verify External Access

### Local Testing (from the server)

```bash
# Test backend health endpoint
curl http://localhost:5000/health

# Test frontend
curl http://localhost:5174
```

### Remote Testing (from another device)

Replace `YOUR_SERVER_IP` with your actual server IP address:

**Test Backend:**
```bash
# Using curl
curl http://YOUR_SERVER_IP:5000/health

# Using browser
# Navigate to: http://YOUR_SERVER_IP:5000/health
```

**Test Frontend:**
```bash
# Using browser
# Navigate to: http://YOUR_SERVER_IP:5174
```

Expected backend response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-02T12:34:56.789Z"
}
```

## Step 5: Access the Application

### From External Devices

1. **Frontend Application**: 
   - Open browser and navigate to: `http://YOUR_SERVER_IP:5174`
   
2. **Backend API** (for direct API access):
   - API Base URL: `http://YOUR_SERVER_IP:5000/api`

### API Endpoints

Key endpoints available:
- `GET /health` - Health check
- `GET /api/drugs` - List all drugs
- `POST /api/drugs` - Create new drug
- `GET /api/searches` - List all searches
- `POST /api/searches` - Create new search
- `GET /api/articles` - List articles
- And more...

## Security Considerations

### For Development/Testing

The current configuration allows all CORS origins (`CORS_ORIGINS=*`), which is suitable for development but **NOT recommended for production**.

### For Production Deployment

1. **Use HTTPS**: Set up SSL/TLS certificates
   - Use Let's Encrypt for free SSL certificates
   - Update `PUBLIC_HOST` to use `https://`

2. **Restrict CORS Origins**:
   ```bash
   CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

3. **Use a Reverse Proxy** (Nginx or Traefik):
   - Handles SSL termination
   - Provides additional security layers
   - Enables better load balancing

4. **Secure API Keys**:
   - Never commit `.env` file to version control
   - Use secret management services (AWS Secrets Manager, Azure Key Vault, etc.)
   - Rotate keys regularly

5. **Network Security**:
   - Use VPN for administrative access
   - Implement rate limiting
   - Set up monitoring and alerting

6. **Update Docker Configuration**:
   ```yaml
   environment:
     - FLASK_ENV=production
     - CORS_ORIGINS=https://yourdomain.com
   ```

## Troubleshooting

### Cannot Access from External Device

1. **Check Docker containers are running**:
   ```bash
   docker-compose ps
   ```

2. **Check Docker logs**:
   ```bash
   # Backend logs
   docker logs pharma_pv_backend

   # Frontend logs
   docker logs pharma_pv_frontend
   ```

3. **Verify ports are listening**:
   
   **Windows:**
   ```powershell
   netstat -ano | findstr :5000
   netstat -ano | findstr :5174
   ```
   
   **Linux:**
   ```bash
   netstat -tulpn | grep :5000
   netstat -tulpn | grep :5174
   ```

4. **Check firewall rules**:
   ```powershell
   # Windows
   Get-NetFirewallRule | Where-Object {$_.LocalPort -eq 5000 -or $_.LocalPort -eq 5174}
   ```

5. **Verify environment variables**:
   ```bash
   docker exec pharma_pv_backend env | grep CORS
   docker exec pharma_pv_frontend env | grep VITE
   ```

### CORS Errors in Browser

If you see CORS errors in the browser console:

1. Check the `CORS_ORIGINS` environment variable in `.env`
2. Ensure `PUBLIC_HOST` is set correctly
3. Rebuild and restart containers:
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

### Backend Connection Refused

1. Verify backend is healthy:
   ```bash
   curl http://localhost:5000/health
   ```

2. Check backend logs for errors:
   ```bash
   docker logs pharma_pv_backend --tail 50
   ```

3. Ensure all required environment variables are set in `.env`

### Frontend Shows "Network Error"

1. Check that `PUBLIC_HOST` environment variable is correctly set
2. Verify backend is accessible from frontend:
   ```bash
   docker exec pharma_pv_frontend wget -O- http://backend:5000/health
   ```

3. Check frontend build configuration:
   ```bash
   docker exec pharma_pv_frontend env | grep VITE_API_BASE_URL
   ```

## Monitoring

### Check Service Health

```bash
# View all container status
docker-compose ps

# View resource usage
docker stats

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Health Check Endpoint

The backend includes a health check endpoint that Docker monitors automatically:

```bash
curl http://YOUR_SERVER_IP:5000/health
```

## Stopping the Services

```bash
# Stop services (containers remain)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop, remove containers, and remove volumes
docker-compose down -v
```

## Updating the Application

```bash
# Pull latest changes (if from git)
git pull

# Rebuild and restart services
docker-compose down
docker-compose up --build -d
```

## Advanced Configuration

### Using Nginx as Reverse Proxy

For production deployments, consider using Nginx as a reverse proxy:

1. Install Nginx on your server
2. Configure Nginx to proxy requests to Docker containers
3. Enable SSL/TLS with Let's Encrypt
4. Configure rate limiting and security headers

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:5174;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Support

For issues or questions:
1. Check Docker logs: `docker-compose logs`
2. Verify network connectivity: `curl http://YOUR_SERVER_IP:5000/health`
3. Review firewall settings
4. Check environment variables in `.env` file

---

**Last Updated**: November 2, 2025

