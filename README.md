# Pharmacovigilance Literature Monitoring - PoC

A comprehensive Proof of Concept (PoC) application for automated pharmacovigilance literature monitoring, featuring AI-powered ICSR (Individual Case Safety Report) detection and classification.

## Overview

This application automates the process of monitoring medical literature for adverse drug reactions and safety information. It integrates with PubMed for literature searches and uses AI (OpenAI GPT models) to analyze articles for:

- **ICSR Detection**: Identifies articles containing individual case safety reports
- **Ownership Analysis**: Determines if cases can be excluded based on product ownership criteria
- **Safety Classification**: Categorizes articles as relevant or irrelevant safety information
- **Automated Workflow**: Generates Excel trackers matching existing pharmacovigilance workflows

## Key Features

### 1. Product Management
- Add and manage pharmaceutical products (INN-based)
- Configure PubMed search strategies (simple and complex/EU products)
- Define territories, dosage forms, and routes of administration
- Import products from JSON files

### 2. Literature Search
- **Single Search**: Search for one product at a time
- **Batch Search**: Search multiple products simultaneously
- Date range filtering
- Integration with PubMed E-utilities API
- Automatic article metadata extraction (PMID, DOI, authors, journal, etc.)

### 3. AI-Powered Analysis
- **ICSR Detection**: Identifies case reports with adverse events
- **Ownership Exclusion**: Analyzes if cases can be excluded based on:
  - Product territories
  - Dosage forms
  - Routes of administration
- **Safety Information Classification**: Determines relevance of articles
- **Confidence Scoring**: Provides confidence levels for AI decisions

### 4. Results Management
- View search results with detailed AI analysis
- Filter by ICSR status, relevance, and other criteria
- Review article abstracts and metadata
- Direct links to PubMed articles
- Manual review and annotation capabilities

### 5. Excel Export
- Generate Excel trackers matching existing workflow format
- Includes 30+ columns with comprehensive data
- Two sheets: Main tracker (Week XX) and Legends
- Compatible with existing pharmacovigilance processes

### 6. Configuration
- Test API connections (PubMed and OpenAI)
- View configuration status
- Environment-based configuration for local and cloud deployments

## Architecture

### Backend (Python/Flask)
- **Framework**: Flask with RESTful API design
- **Database**: SQLAlchemy ORM (SQLite for local, PostgreSQL for cloud)
- **Services**:
  - `PubMedService`: PubMed API integration with rate limiting
  - `AIService`: OpenAI GPT integration for article analysis
  - `ExcelService`: Excel tracker generation with openpyxl
- **API Endpoints**: 20+ endpoints for products, searches, results, and exports

### Frontend (React)
- **Framework**: React 18 with React Router
- **UI Library**: shadcn/ui components with Tailwind CSS
- **Pages**:
  - Dashboard: Overview and statistics
  - Products: Product management
  - Search: Execute literature searches
  - Results: Review AI-analyzed articles
  - Export: Generate Excel trackers
  - Configuration: API settings and testing

### AI Analysis Pipeline

1. **Article Retrieval**: Fetch articles from PubMed based on search strategy
2. **ICSR Detection**: Analyze title and abstract for:
   - Patient/case description
   - Adverse events or reactions
   - Drug/product mention
   - Temporal relationship
3. **Ownership Analysis**: Evaluate if case can be excluded based on:
   - Geographic location vs. product territories
   - Dosage form mentioned vs. marketed forms
   - Route of administration vs. approved routes
4. **Safety Classification**: Determine if article contains:
   - Relevant safety information (efficacy, drug interactions, etc.)
   - Irrelevant information (animal studies, protocols, etc.)
5. **Confidence Scoring**: Assign confidence level (High: >85%, Medium: 60-85%, Low: <60%)

## Technology Stack

### Backend
- Python 3.11
- Flask 3.0
- SQLAlchemy 2.0
- OpenAI Python SDK
- Biopython (for PubMed)
- openpyxl (for Excel generation)
- Flask-CORS
- python-dotenv
- gunicorn (production server)

### Frontend
- React 18
- React Router 6
- Vite (build tool)
- Tailwind CSS
- shadcn/ui components
- Lucide icons
- Recharts (for visualizations)

### Deployment
- Docker & Docker Compose
- nginx (frontend reverse proxy)
- Support for AWS, Azure, GCP

## Project Structure

```
pharma_pv_poc/
├── backend/
│   ├── app/
│   │   ├── __init__.py           # Flask app factory
│   │   ├── config.py             # Configuration classes
│   │   ├── models.py             # Database models
│   │   ├── api/                  # API routes
│   │   │   ├── __init__.py
│   │   │   ├── products.py       # Product endpoints
│   │   │   ├── search.py         # Search endpoints
│   │   │   ├── config.py         # Config endpoints
│   │   │   └── export.py         # Export endpoints
│   │   └── services/             # Business logic
│   │       ├── pubmed_service.py # PubMed integration
│   │       ├── ai_service.py     # AI analysis
│   │       └── excel_service.py  # Excel generation
│   ├── run.py                    # Application entry point
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile               # Docker configuration
│   └── .env.template            # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── pages/               # Page components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Products.jsx
│   │   │   ├── Search.jsx
│   │   │   ├── Results.jsx
│   │   │   ├── Export.jsx
│   │   │   └── Configuration.jsx
│   │   ├── components/          # Reusable components
│   │   ├── App.jsx             # Main app component
│   │   └── main.jsx            # Entry point
│   ├── public/                  # Static assets
│   ├── Dockerfile              # Docker configuration
│   ├── nginx.conf              # nginx configuration
│   └── .env.template           # Environment variables template
├── synthetic_data/              # Generated test data
│   ├── generate_data.py        # Data generation script
│   ├── products.json           # Sample products
│   ├── articles.json           # Sample articles
│   └── synthetic_tracker.xlsx  # Sample tracker
├── docker-compose.yml           # Docker Compose configuration
├── DEPLOYMENT.md               # Deployment guide
└── README.md                   # This file
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- PubMed API key (optional, but recommended)
- OpenAI API key (required)

### Installation

1. **Clone or extract the project**
   ```bash
   cd pharma_pv_poc
   ```

2. **Configure environment variables**
   ```bash
   cp backend/.env.template .env
   ```

   Edit `.env` with your API keys:
   ```env
   PUBMED_API_KEY=your-pubmed-api-key
   PUBMED_EMAIL=your-email@example.com
   OPENAI_API_KEY=your-openai-api-key
   OPENAI_MODEL=gpt-4.1-mini
   ```

3. **Start the application**
   ```bash
   docker-compose up -d --build
   ```

4. **Access the application**
   - Frontend: http://localhost
   - Backend API: http://localhost:5000
   - Health check: http://localhost:5000/health

5. **Load sample data**
   ```bash
   # Import sample products
   curl -X POST http://localhost:5000/api/products/import \
      -H "Content-Type: application/json" \
      -d @synthetic_data/products.json
   ```

### Development Setup

#### Backend Development

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
# Edit .env with your API keys
python run.py
```

Backend runs on: http://localhost:5000

#### Frontend Development

```bash
cd frontend
pnpm install
cp .env.template .env
# Edit .env if needed
pnpm run dev
```

Frontend runs on: http://localhost:5173

## Usage Guide

### 1. Configure API Keys

1. Navigate to **Configuration** page
2. Verify API keys are configured (set via environment variables)
3. Test connections:
   - Click "Test Connection" for PubMed
   - Click "Test Connection" for OpenAI

### 2. Add Products

1. Navigate to **Products** page
2. Click "Add Product"
3. Fill in product details:
   - INN (International Nonproprietary Name)
   - Search Strategy (PubMed Boolean query)
   - EU Product checkbox (for complex search strategies)
   - Territories (comma-separated)
   - Dosage Forms
   - Routes of Administration
4. Click "Create Product"

**Alternative**: Import products from JSON file using "Import" button

### 3. Execute Literature Search

1. Navigate to **Search** page
2. Select search type:
   - **Single**: Search one product
   - **Batch**: Search multiple products (or all if none selected)
3. Set date range (default: last 7 days)
4. Select products (for single search, select exactly one)
5. Click "Execute Search"
6. Wait for search to complete (may take several minutes for batch searches)

### 4. Review Results

1. Navigate to **Results** page (or click from search completion)
2. View search job information and statistics
3. Filter results:
   - **All**: All articles
   - **ICSRs**: Articles with identified case reports
   - **Relevant**: Articles with relevant safety information
   - **Irrelevant**: Articles without relevant information
4. Review each article:
   - Read AI analysis and justification
   - Check confidence scores
   - Click "PubMed" to view full article
5. Manually update classifications if needed

### 5. Export to Excel

1. Navigate to **Export** page
2. Enter week number (e.g., "42" or "XX")
3. Select a completed search job
4. Click "Export to Excel"
5. Excel file will be downloaded with:
   - **Week XX** sheet: Main tracker with all results
   - **Legends** sheet: Column descriptions

## API Documentation

### Products API

- `GET /api/products` - List all products
- `GET /api/products/:id` - Get product by ID
- `POST /api/products` - Create new product
- `PUT /api/products/:id` - Update product
- `DELETE /api/products/:id` - Delete product
- `POST /api/products/import` - Import products from JSON

### Search API

- `POST /api/search/execute` - Execute single product search
- `POST /api/search/batch` - Execute batch search
- `GET /api/search/jobs` - List all search jobs
- `GET /api/search/jobs/:id` - Get search job details
- `GET /api/search/jobs/:id/results` - Get search results
- `PUT /api/search/results/:id` - Update search result

### Configuration API

- `GET /api/config` - Get configuration status
- `POST /api/config/test-pubmed` - Test PubMed connection
- `POST /api/config/test-openai` - Test OpenAI connection

### Export API

- `POST /api/export/excel/:job_id` - Export search results to Excel
- `GET /api/export/jobs` - List available export files

## Data Models

### Product
- INN (International Nonproprietary Name)
- Search Strategy (PubMed query)
- EU Product flag
- Territories
- Dosage Forms
- Routes of Administration
- Marketing Status

### Article
- PMID (PubMed ID)
- Title
- Abstract
- Authors
- Journal
- Publication Year
- DOI, PMCID
- Publication Date

### Search Result
- Product reference
- Article reference
- ICSR classification (Y/N/NA)
- ICSR description
- Ownership exclusion (Can exclude / Cannot exclude)
- Exclusion reason
- Safety information classification (Y/N/NA)
- Safety information justification
- Confidence score
- AI analysis (full JSON)
- Review tracking fields

## Configuration

### Environment Variables

#### Backend

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `PUBMED_API_KEY` | PubMed API key | No | - |
| `PUBMED_EMAIL` | Email for PubMed API | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `OPENAI_MODEL` | OpenAI model name | No | gpt-4.1-mini |
| `MAX_ARTICLES_PER_SEARCH` | Max articles per search | No | 100 |
| `DATABASE_URL` | Database connection string | No | sqlite:///pharma_pv.db |
| `CORS_ORIGINS` | Allowed CORS origins | No | http://localhost:3000 |

#### Frontend

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `VITE_API_BASE_URL` | Backend API URL | Yes | http://localhost:5000/api |

### Supported OpenAI Models

- `gpt-4.1-mini` (recommended, cost-effective)
- `gpt-4.1-nano` (faster, lower cost)
- `gemini-2.5-flash` (alternative)

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment instructions covering:

- Local deployment with Docker Compose
- Manual development setup
- AWS deployment (ECS, RDS, S3)
- Azure deployment (Container Instances, PostgreSQL)
- GCP deployment (Cloud Run, Cloud SQL)
- Configuration management
- Monitoring and troubleshooting

## Testing

### Backend Tests

```bash
python test_backend.py
```

Tests include:
- Module imports
- Flask app creation
- Database models
- Service initialization

### Manual Testing Checklist

- [ ] Add product
- [ ] Import products from JSON
- [ ] Execute single search
- [ ] Execute batch search
- [ ] View search results
- [ ] Filter results by classification
- [ ] Export to Excel
- [ ] Test API connections

## Synthetic Data

The project includes a synthetic data generator for testing:

```bash
cd synthetic_data
python generate_data.py
```

Generates:
- 15 sample products (5 EU, 10 non-EU)
- 100 sample articles with various classifications
- Excel tracker in production format
- Statistics summary

## Limitations and Future Enhancements

### Current Limitations

1. **Authentication**: No user authentication (PoC only)
2. **Rate Limiting**: Basic rate limiting for PubMed API
3. **Scalability**: SQLite for local deployment (use PostgreSQL for production)
4. **Manual Review**: Limited manual review workflow
5. **Notifications**: No email/alert notifications

### Potential Enhancements

1. **User Management**: Add authentication and role-based access control
2. **Advanced Workflows**: Multi-step review and approval process
3. **Notifications**: Email alerts for new ICSRs
4. **Reporting**: Advanced analytics and dashboards
5. **Integration**: Connect with safety databases (e.g., Argus, AERS)
6. **Full Text Analysis**: Analyze full article PDFs (not just abstracts)
7. **Multi-language Support**: Analyze non-English articles
8. **Scheduled Searches**: Automatic weekly/monthly searches
9. **API Rate Optimization**: Implement caching and batch processing
10. **Audit Trail**: Complete audit logging for regulatory compliance

## Troubleshooting

### Common Issues

1. **Backend fails to start**
   - Check API keys in `.env` file
   - Verify all dependencies are installed
   - Check logs: `docker-compose logs backend`

2. **Frontend cannot connect to backend**
   - Verify `VITE_API_BASE_URL` is correct
   - Check CORS configuration
   - Ensure backend is running

3. **PubMed API errors**
   - Verify API key is valid
   - Check rate limiting settings
   - Ensure email is configured

4. **OpenAI API errors**
   - Verify API key has sufficient credits
   - Check model name is correct
   - Review API usage limits

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting guide.

## License

This is a Proof of Concept (PoC) application developed for demonstration purposes.

## Support

For questions or issues:
- Review the [DEPLOYMENT.md](DEPLOYMENT.md) guide
- Check application logs
- Verify configuration settings
- Test API connections in Configuration page

## Acknowledgments

- PubMed E-utilities API for literature access
- OpenAI GPT models for AI-powered analysis
- shadcn/ui for React components
- Flask and React communities

---

**Version**: 1.0.0 (PoC)  
**Last Updated**: January 2025

