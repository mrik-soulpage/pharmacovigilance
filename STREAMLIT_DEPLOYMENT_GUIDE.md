# 🚀 Streamlit Deployment Guide
## PharmaVigilance AI - LangGraph ReAct Agent

This guide covers deploying the Dockerized PharmaVigilance application with Streamlit frontend.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Docker Deployment](#local-docker-deployment)
3. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Usage Guide](#usage-guide)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### Required Software
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: For cloning the repository (if needed)

### Required API Keys
- **OpenAI API Key**: Required for LangGraph ReAct Agent
- **PubMed API Key**: Optional but recommended for better rate limits

### System Requirements
- **RAM**: Minimum 4GB, Recommended 8GB
- **Disk Space**: Minimum 2GB free space
- **Ports**: 5000 (Backend), 8501 (Streamlit)

---

## 🐳 Local Docker Deployment

### Step 1: Navigate to Project

```bash
cd C:\Office_Work\Hikma\pharma_pv_poc
```

### Step 2: Create Environment File

Create a `.env` file from the example:

```bash
# Copy the example file
copy env.example.txt .env

# Edit the .env file with your actual values
notepad .env
```

**Required Environment Variables:**

```env
# REQUIRED: Your OpenAI API Key
OPENAI_API_KEY=sk-proj-your-actual-api-key-here

# REQUIRED: OpenAI Model
OPENAI_MODEL=gpt-4-turbo-preview

# OPTIONAL: PubMed API Key
PUBMED_API_KEY=your-pubmed-api-key
PUBMED_EMAIL=your-email@example.com

# Flask Secret Key (generate a random string)
SECRET_KEY=your-secret-key-change-this-in-production
```

### Step 3: Build and Run with Docker Compose

```bash
# Build the images
docker-compose -f docker-compose.streamlit.yml build

# Start the services
docker-compose -f docker-compose.streamlit.yml up -d

# View logs
docker-compose -f docker-compose.streamlit.yml logs -f
```

### Step 4: Wait for Startup

The backend will automatically:
1. Initialize the database
2. Import products from `synthetic_data/products.json`
3. Start the API server

**Expected logs:**
```
==================================
Starting PharmaVigilance Backend
==================================
Initializing database...
Database initialized
Importing products from JSON...
✅ Successfully imported X products, skipped Y
Starting Gunicorn...
```

### Step 5: Access the Application

Once the containers are running:

- **Streamlit Frontend**: http://localhost:8501
- **Backend API**: http://localhost:5000

### Step 6: Stop the Application

```bash
# Stop all services
docker-compose -f docker-compose.streamlit.yml down

# Stop and remove volumes (WARNING: deletes data)
docker-compose -f docker-compose.streamlit.yml down -v
```

---

## ☁️ Streamlit Cloud Deployment

### Option 1: Deploy Backend Separately + Streamlit Cloud

#### 1. Deploy Backend to a Cloud Platform

**Option A: Deploy to Railway**
1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Set root directory to `/backend`
5. Add environment variables:
   ```
   OPENAI_API_KEY=your-key
   OPENAI_MODEL=gpt-4-turbo-preview
   PUBMED_API_KEY=your-key (optional)
   PUBMED_EMAIL=your-email
   ```
6. Railway will automatically detect the Dockerfile and deploy
7. Note the deployment URL (e.g., `https://your-app.up.railway.app`)

**Option B: Deploy to Render**
1. Go to https://render.com
2. Create New → Web Service
3. Connect your GitHub repository
4. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 600 run:app`
5. Add environment variables
6. Note the deployment URL

#### 2. Deploy Streamlit Frontend to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Configure:
   - **Repository**: Your GitHub repo
   - **Branch**: main
   - **Main file path**: `streamlit_app/app.py`
5. Click "Advanced settings"
6. Add to `secrets.toml`:
   ```toml
   API_BASE_URL = "https://your-backend-url.com"
   ```
7. Deploy!

### Option 2: Full Docker Deployment on VPS

If you have a VPS (DigitalOcean, AWS EC2, Azure VM, etc.):

```bash
# SSH into your server
ssh user@your-server-ip

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install docker-compose-plugin

# Clone your repository
git clone https://github.com/your-repo/pharma_pv_poc.git
cd pharma_pv_poc

# Create .env file with your keys
nano .env

# Build and run
docker-compose -f docker-compose.streamlit.yml up -d

# Set up reverse proxy (Nginx) for HTTPS
sudo apt-get install nginx certbot python3-certbot-nginx

# Configure Nginx
sudo nano /etc/nginx/sites-available/pharma-pv
```

**Nginx Configuration Example:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/pharma-pv /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

---

## ⚙️ Environment Configuration

### Essential Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | ✅ Yes | OpenAI API key for ReAct Agent | `sk-proj-...` |
| `OPENAI_MODEL` | ✅ Yes | Model to use | `gpt-4-turbo-preview` |
| `PUBMED_API_KEY` | ❌ No | PubMed API key | `your-key` |
| `PUBMED_EMAIL` | ✅ Yes | Email for PubMed | `user@example.com` |
| `SECRET_KEY` | ✅ Yes | Flask session key | Random string |
| `DATABASE_URL` | ❌ No | Database connection | `sqlite:///pharma_pv.db` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_ARTICLES_PER_SEARCH` | 100 | Max articles to fetch |
| `CONFIDENCE_THRESHOLD_HIGH` | 0.85 | High confidence threshold |
| `CONFIDENCE_THRESHOLD_MEDIUM` | 0.60 | Medium confidence threshold |

---

## 📖 Usage Guide

### 1. Adding Products

Products are **automatically loaded** from `synthetic_data/products.json` on startup!

**To add more products manually:**
1. Go to "📦 Products" page
2. Click "➕ Add Product" tab
3. Fill in product details:
   - **INN** (e.g., "methotrexate")
   - **Search Strategy** (PubMed query)
   - **Territories** (comma-separated, optional)
   - **Dosage Forms** (comma-separated, optional)
   - **Routes** (comma-separated, optional)
   - **EU Product** checkbox
   - **Marketing Status** dropdown
4. Click "Add Product"

### 2. Searching for Articles

1. Go to "🔍 Search" page
2. Select a product from dropdown
3. Choose date range (default: last 30 days)
4. Click "🔍 Search Articles"
5. Wait for AI analysis (10-30s per article)
6. See success message directing you to Results tab

### 3. Reviewing Results

1. Go to "📋 Results" page
2. See tabs for each product at the top
3. Click a product tab to see its searches
4. Each search shows:
   - Timestamp and date range
   - Summary metrics (Total, ICSRs, High Confidence)
   - Article list with filters
5. Click an article to expand and see:
   - Full details (Title, PMID, Abstract)
   - ICSR status and confidence score
   - ICSR criteria checklist
   - Adverse events list
   - AI reasoning
   - Evidence quotes (click checkbox to show)

### 4. Exporting Results

1. Go to "📥 Export" page
2. Choose between:

**Tab 1: Export Individual Search**
- Select a search from dropdown
- Choose format: Excel or JSON
- Choose filter: All / ICSRs Only / High Confidence Only
- Click "Generate Export"
- Download the file

**Tab 2: Export All Searches**
- Export all searches as combined JSON
- Download summary table as CSV
- Complete audit trail

### 5. Monitoring Dashboard

Go to "📊 Dashboard" to see:
- Total products monitored
- Total searches performed
- Articles analyzed count
- ICSRs detected count
- ICSR detection rate
- Recent activity (last 5 searches)
- Products overview table

---

## 🔍 Features

### AI Analysis Capabilities

The system analyzes each article for:
- ✅ **Identifiable Patient**: Age, gender, initials, or patient ID
- ✅ **Identifiable Reporter**: Doctor name, hospital, or contact info
- ✅ **Suspected Drug**: Specific medication name and dosage
- ✅ **Adverse Reaction**: Specific side effect or safety concern

**All 4 criteria = ICSR** (Individual Case Safety Report)

### Search Filters (Results Tab)

- **ICSR Status**: All / ICSR Only / Non-ICSR Only
- **Confidence Level**: All / High (>85%) / Medium (60-85%) / Low (<60%)
- **Sort By**: Date (Newest/Oldest) / Confidence (High/Low)

### Export Options

**Formats:**
- Excel (.xlsx) - Professional format for regulatory submissions
- JSON (.json) - Structured data for further analysis
- CSV (.csv) - Summary tables

**Filters:**
- All Articles
- ICSRs Only
- High Confidence Only

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "Cannot Connect to Backend API"

**Error**: Streamlit can't reach backend

**Solutions**:
```bash
# Check if backend is running
docker ps

# Check backend logs
docker-compose -f docker-compose.streamlit.yml logs backend

# Restart services
docker-compose -f docker-compose.streamlit.yml restart
```

#### 2. OpenAI API Errors

**Error**: "OpenAI API key not found" or authentication errors

**Solutions**:
1. Check your `.env` file has correct `OPENAI_API_KEY`
2. Verify the API key is valid: https://platform.openai.com/api-keys
3. Restart the containers after updating `.env`:
   ```bash
   docker-compose -f docker-compose.streamlit.yml down
   docker-compose -f docker-compose.streamlit.yml up -d
   ```

#### 3. Slow Analysis

**Issue**: AI analysis takes long time

**This is NORMAL!** The AI uses multi-step reasoning:
- Expected time: 10-30 seconds per article
- For 20 articles: 5-10 minutes total

**To speed up:**
- Use `gpt-4-mini` instead of `gpt-4-turbo-preview`
- Search shorter date ranges (7 days)
- Reduce max articles in config

#### 4. Port Already in Use

**Error**: "Port 5000/8501 is already allocated"

**Solutions**:
```bash
# Windows - Find process using the port
netstat -ano | findstr :5000
netstat -ano | findstr :8501

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change the port in docker-compose.streamlit.yml
# Change "8501:8501" to "8502:8501"
```

#### 5. Products Not Loading

**Error**: No products in dropdown

**Solutions**:
```bash
# Check if products were imported
docker-compose -f docker-compose.streamlit.yml logs backend | findstr "imported"

# Manually import products
docker exec -it pharma_pv_backend python init_products.py

# Verify products exist
docker exec -it pharma_pv_backend python -c "from app import create_app; from app.models import Product; app = create_app(); app.app_context().push(); print(f'Products: {Product.query.count()}')"
```

### Viewing Logs

```bash
# View all logs
docker-compose -f docker-compose.streamlit.yml logs -f

# View backend logs only
docker-compose -f docker-compose.streamlit.yml logs -f backend

# View streamlit logs only
docker-compose -f docker-compose.streamlit.yml logs -f streamlit
```

### Health Checks

```bash
# Check backend health
curl http://localhost:5000/api/config/test-connection

# Check Streamlit health
curl http://localhost:8501/_stcore/health
```

---

## 📊 Performance Tips

### 1. Optimize Search Range
- Start with shorter date ranges (7-14 days)
- Expand to 30 days once you're familiar with the tool

### 2. Use Filters Effectively
- Filter by "ICSR Only" to review critical cases first
- Filter by "High Confidence" to prioritize reliable detections

### 3. Model Selection
- **gpt-4-turbo-preview**: Most accurate, slower, more expensive
- **gpt-4-mini**: Faster, cheaper, slightly less accurate
- **gpt-4**: Balanced option

### 4. Batch Processing
- Add multiple products and search them one by one
- Export results regularly to avoid data loss

---

## 🔒 Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use strong SECRET_KEY** for Flask sessions
3. **Rotate API keys** regularly
4. **Use HTTPS** in production (enable SSL/TLS)
5. **Implement authentication** for production deployments
6. **Restrict CORS** origins to your domain only
7. **Regular backups** of the database

---

## 📈 Scaling Considerations

### Horizontal Scaling
```yaml
# In docker-compose.streamlit.yml
backend:
  deploy:
    replicas: 3
  # Add load balancer
```

### Database Migration
For production, migrate from SQLite to PostgreSQL:
1. Uncomment PostgreSQL service in `docker-compose.streamlit.yml`
2. Update `DATABASE_URL` in `.env`:
   ```
   DATABASE_URL=postgresql://pharma_admin:password@db:5432/pharma_pv
   ```

### Caching
Implement Redis for caching API responses:
```yaml
redis:
  image: redis:alpine
  ports:
    - "6379:6379"
```

---

## 📞 Common Questions

**Q: How much does it cost to run?**
A: Main cost is OpenAI API usage. Expect $0.01-0.03 per article analyzed with GPT-4.

**Q: Can I use a different AI model?**
A: Yes, update `OPENAI_MODEL` in `.env`. Must be OpenAI-compatible.

**Q: How do I backup my data?**
A: Copy the `backend/data` folder regularly or use PostgreSQL with automated backups.

**Q: Can I deploy without Docker?**
A: Yes, but Docker is highly recommended. Manual setup requires configuring Python environments, dependencies, and reverse proxy.

**Q: How do I update the products?**
A: Edit `synthetic_data/products.json` and restart containers, or add products via the UI.

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] OpenAI API key obtained
- [ ] PubMed email configured
- [ ] Docker and Docker Compose installed
- [ ] `.env` file created and configured
- [ ] Ports 5000 and 8501 available

### Deployment
- [ ] Docker images built successfully
- [ ] Containers running without errors
- [ ] Backend health check passes
- [ ] Streamlit health check passes
- [ ] Products auto-imported successfully
- [ ] Frontend can connect to backend

### Post-Deployment
- [ ] Test connection from Streamlit
- [ ] Verify products appear in dropdown
- [ ] Perform test search
- [ ] Verify AI analysis works
- [ ] Export results successfully
- [ ] Set up backups (if production)
- [ ] Configure HTTPS (if production)

---

## 🎉 Success!

Your PharmaVigilance AI application with LangGraph ReAct Agent is now deployed and ready to monitor literature for ICSRs!

**Quick Start:**
1. Open http://localhost:8501 (or your deployed URL)
2. Products are auto-loaded
3. Run a search in the Search tab
4. Review results in the Results tab
5. Export using the Export tab

**Next Steps:**
- Run regular monitoring searches
- Review results systematically
- Export for regulatory compliance
- Track trends in Dashboard

---

**Version**: 2.0.0  
**Last Updated**: November 1, 2025  
**Powered by**: LangGraph ReAct Agent + Streamlit + Flask + Docker

