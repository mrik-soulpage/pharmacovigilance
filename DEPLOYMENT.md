# Pharmacovigilance Literature Monitoring - Deployment Guide

This document provides comprehensive instructions for deploying the Pharmacovigilance Literature Monitoring PoC application in both local and cloud environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Deployment](#local-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Git** (for cloning the repository)

### Required API Keys

1. **PubMed API Key** (optional but recommended)
   - Register at: https://www.ncbi.nlm.nih.gov/account/
   - Increases rate limit from 3 to 10 requests/second

2. **OpenAI API Key** (required)
   - Get from: https://platform.openai.com/api-keys
   - Required for AI-powered ICSR detection

---

## Local Deployment

### Option 1: Docker Compose (Recommended)

#### Step 1: Clone or Extract the Project

```bash
cd /path/to/pharma_pv_poc
```

#### Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp backend/.env.template .env
```

Edit the `.env` file with your API keys:

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# PubMed API Configuration
PUBMED_API_KEY=your-pubmed-api-key-here
PUBMED_EMAIL=your-email@example.com
PUBMED_RATE_LIMIT=10

# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4.1-mini

# Application Settings
MAX_ARTICLES_PER_SEARCH=100
```

#### Step 3: Build and Start Services

```bash
docker-compose up -d --build
```

This will:
- Build the backend and frontend Docker images
- Start the backend API server on port 5000
- Start the frontend web application on port 80
- Create persistent volumes for data and exports

#### Step 4: Verify Deployment

1. Check service status:
```bash
docker-compose ps
```

2. View logs:
```bash
docker-compose logs -f
```

3. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost:5000
   - Health check: http://localhost:5000/health

#### Step 5: Load Sample Data

```bash
# Copy synthetic data to backend container
docker cp synthetic_data/products.json pharma_pv_backend:/app/data/

# Import products via API
curl -X POST http://localhost:5000/api/products/import \
  -H "Content-Type: application/json" \
  -d @synthetic_data/products.json
```

#### Step 6: Stop Services

```bash
docker-compose down
```

To remove all data:
```bash
docker-compose down -v
```

### Option 2: Manual Setup (Development)

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your API keys

# Run the application
python run.py
```

Backend will be available at: http://localhost:5000

#### Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Configure environment
cp .env.template .env
# Edit .env if needed (default points to localhost:5000)

# Run development server
pnpm run dev
```

Frontend will be available at: http://localhost:5173

---

## Cloud Deployment

### AWS Deployment

#### Architecture

- **Compute**: ECS Fargate for containers
- **Database**: RDS PostgreSQL (optional, for production)
- **Storage**: S3 for exports
- **Load Balancer**: Application Load Balancer

#### Deployment Steps

1. **Prepare Docker Images**

```bash
# Build images
docker build -t pharma-pv-backend:latest ./backend
docker build -t pharma-pv-frontend:latest ./frontend

# Tag for ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker tag pharma-pv-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/pharma-pv-backend:latest
docker tag pharma-pv-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/pharma-pv-frontend:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/pharma-pv-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/pharma-pv-frontend:latest
```

2. **Create ECS Task Definition**

```json
{
  "family": "pharma-pv-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/pharma-pv-backend:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "FLASK_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "PUBMED_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account-id:secret:pubmed-api-key"
        },
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account-id:secret:openai-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/pharma-pv-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

3. **Create ECS Service**

```bash
aws ecs create-service \
  --cluster pharma-pv-cluster \
  --service-name pharma-pv-backend \
  --task-definition pharma-pv-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

4. **Configure Secrets Manager**

```bash
# Store PubMed API key
aws secretsmanager create-secret \
  --name pubmed-api-key \
  --secret-string "your-pubmed-api-key"

# Store OpenAI API key
aws secretsmanager create-secret \
  --name openai-api-key \
  --secret-string "your-openai-api-key"
```

### Azure Deployment

#### Architecture

- **Compute**: Azure Container Instances or Azure App Service
- **Database**: Azure Database for PostgreSQL
- **Storage**: Azure Blob Storage

#### Deployment Steps

1. **Create Resource Group**

```bash
az group create --name pharma-pv-rg --location eastus
```

2. **Create Container Registry**

```bash
az acr create --resource-group pharma-pv-rg --name pharmapvacr --sku Basic
```

3. **Build and Push Images**

```bash
az acr build --registry pharmapvacr --image pharma-pv-backend:latest ./backend
az acr build --registry pharmapvacr --image pharma-pv-frontend:latest ./frontend
```

4. **Create Container Instances**

```bash
az container create \
  --resource-group pharma-pv-rg \
  --name pharma-pv-backend \
  --image pharmapvacr.azurecr.io/pharma-pv-backend:latest \
  --cpu 1 \
  --memory 2 \
  --registry-login-server pharmapvacr.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --ports 5000 \
  --environment-variables \
    FLASK_ENV=production \
    PUBMED_EMAIL=your-email@example.com \
  --secure-environment-variables \
    PUBMED_API_KEY=<your-key> \
    OPENAI_API_KEY=<your-key>
```

### Google Cloud Platform (GCP) Deployment

#### Architecture

- **Compute**: Cloud Run
- **Database**: Cloud SQL PostgreSQL
- **Storage**: Cloud Storage

#### Deployment Steps

1. **Enable Required APIs**

```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

2. **Build and Push Images**

```bash
# Build backend
gcloud builds submit --tag gcr.io/PROJECT_ID/pharma-pv-backend ./backend

# Build frontend
gcloud builds submit --tag gcr.io/PROJECT_ID/pharma-pv-frontend ./frontend
```

3. **Deploy to Cloud Run**

```bash
# Deploy backend
gcloud run deploy pharma-pv-backend \
  --image gcr.io/PROJECT_ID/pharma-pv-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FLASK_ENV=production \
  --set-secrets PUBMED_API_KEY=pubmed-api-key:latest,OPENAI_API_KEY=openai-api-key:latest

# Deploy frontend
gcloud run deploy pharma-pv-frontend \
  --image gcr.io/PROJECT_ID/pharma-pv-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars VITE_API_BASE_URL=https://pharma-pv-backend-xxx.run.app/api
```

4. **Create Secrets**

```bash
# Create PubMed API key secret
echo -n "your-pubmed-api-key" | gcloud secrets create pubmed-api-key --data-file=-

# Create OpenAI API key secret
echo -n "your-openai-api-key" | gcloud secrets create openai-api-key --data-file=-
```

---

## Configuration

### Environment Variables

#### Backend Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `FLASK_ENV` | Flask environment (development/production) | No | development |
| `SECRET_KEY` | Flask secret key for sessions | Yes | - |
| `DATABASE_URL` | Database connection string | No | sqlite:///pharma_pv.db |
| `PUBMED_API_KEY` | PubMed API key | No | - |
| `PUBMED_EMAIL` | Email for PubMed API | Yes | - |
| `PUBMED_RATE_LIMIT` | Requests per second | No | 10 |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `OPENAI_MODEL` | OpenAI model name | No | gpt-4.1-mini |
| `MAX_ARTICLES_PER_SEARCH` | Maximum articles per search | No | 100 |
| `CORS_ORIGINS` | Allowed CORS origins | No | http://localhost:3000 |

#### Frontend Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `VITE_API_BASE_URL` | Backend API URL | Yes | http://localhost:5000/api |

### Database Configuration

#### SQLite (Local Development)

```env
DATABASE_URL=sqlite:///data/pharma_pv.db
```

#### PostgreSQL (Production)

```env
DATABASE_URL=postgresql://username:password@host:port/database
```

Example for AWS RDS:
```env
DATABASE_URL=postgresql://admin:password@pharma-pv.xxxxx.us-east-1.rds.amazonaws.com:5432/pharmapv
```

---

## Troubleshooting

### Common Issues

#### 1. Backend fails to start

**Symptom**: Backend container exits immediately

**Solutions**:
- Check logs: `docker-compose logs backend`
- Verify environment variables are set correctly
- Ensure API keys are valid
- Check database connection

#### 2. Frontend cannot connect to backend

**Symptom**: API requests fail with CORS or connection errors

**Solutions**:
- Verify `VITE_API_BASE_URL` is set correctly
- Check CORS_ORIGINS in backend configuration
- Ensure backend is running and accessible
- Check network connectivity between containers

#### 3. PubMed API rate limiting

**Symptom**: "Rate limit exceeded" errors

**Solutions**:
- Add PubMed API key to increase limit to 10 req/sec
- Reduce `PUBMED_RATE_LIMIT` value
- Add delays between batch searches

#### 4. OpenAI API errors

**Symptom**: "Invalid API key" or "Model not found"

**Solutions**:
- Verify OpenAI API key is correct
- Check API key has sufficient credits
- Verify model name (use gpt-4.1-mini or gpt-4.1-nano)
- Check OpenAI API status

#### 5. Database connection errors

**Symptom**: "Unable to connect to database"

**Solutions**:
- For SQLite: Ensure data directory exists and is writable
- For PostgreSQL: Verify connection string format
- Check database server is running
- Verify network connectivity and firewall rules

### Health Checks

#### Backend Health Check

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Pharmacovigilance Literature Monitoring"
}
```

#### Test API Connections

```bash
# Test PubMed connection
curl -X POST http://localhost:5000/api/config/test-pubmed

# Test OpenAI connection
curl -X POST http://localhost:5000/api/config/test-openai
```

### Logs

#### View Docker Compose Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

#### View Container Logs

```bash
# Backend
docker logs pharma_pv_backend

# Frontend
docker logs pharma_pv_frontend
```

---

## Performance Optimization

### Backend Optimization

1. **Increase Workers**
   - Edit `backend/Dockerfile` and increase gunicorn workers:
   ```
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "8", "--timeout", "120", "run:app"]
   ```

2. **Add Redis Caching**
   - Add Redis service to `docker-compose.yml`
   - Configure Flask-Caching

3. **Use PostgreSQL**
   - Replace SQLite with PostgreSQL for better concurrency
   - Add connection pooling

### Frontend Optimization

1. **Enable Compression**
   - Already configured in nginx.conf

2. **CDN Integration**
   - Deploy static assets to CDN
   - Update asset URLs in production build

---

## Security Considerations

### API Keys

- Never commit API keys to version control
- Use environment variables or secrets management
- Rotate keys regularly

### HTTPS

For production deployments:
- Use SSL/TLS certificates
- Configure reverse proxy (nginx, CloudFront, etc.)
- Enforce HTTPS redirects

### Authentication

Current PoC does not include authentication. For production:
- Implement user authentication (OAuth, JWT)
- Add role-based access control
- Secure API endpoints

---

## Backup and Recovery

### Database Backup

#### SQLite

```bash
# Backup
docker cp pharma_pv_backend:/app/data/pharma_pv.db ./backup/pharma_pv_$(date +%Y%m%d).db

# Restore
docker cp ./backup/pharma_pv_20250115.db pharma_pv_backend:/app/data/pharma_pv.db
```

#### PostgreSQL

```bash
# Backup
docker exec pharma_pv_backend pg_dump -U username database > backup.sql

# Restore
docker exec -i pharma_pv_backend psql -U username database < backup.sql
```

### Export Files Backup

```bash
# Backup exports directory
docker cp pharma_pv_backend:/app/exports ./backup/exports_$(date +%Y%m%d)
```

---

## Monitoring

### Recommended Monitoring Tools

- **Application Performance**: New Relic, Datadog
- **Logs**: ELK Stack, CloudWatch, Stackdriver
- **Uptime**: Pingdom, UptimeRobot
- **Errors**: Sentry

### Metrics to Monitor

- API response times
- PubMed API rate limit usage
- OpenAI API usage and costs
- Database query performance
- Container resource usage (CPU, memory)
- Error rates

---

## Support

For issues or questions:
- Check the troubleshooting section above
- Review application logs
- Verify configuration settings
- Test API connections

---

## License

This is a Proof of Concept (PoC) application developed for demonstration purposes.

