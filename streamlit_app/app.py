"""
Streamlit Frontend for Pharmacovigilance Literature Monitoring
AI-Powered ICSR Detection
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import time
from io import BytesIO

# Configuration
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://backend:5000")

# Page Configuration
st.set_page_config(
    page_title="PharmaVigilance AI - Literature Monitoring",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper Functions - Define these FIRST before using them
def test_api_connection():
    """Test API connection"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/config/test-connection", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_products():
    """Fetch products from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/products", timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Ensure we return a list
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Backend returns: {"success": true, "data": [...], "count": N}
                if 'data' in data:
                    return data['data']
                elif 'products' in data:
                    return data['products']
                else:
                    st.warning(f"Unexpected API response format. Keys: {list(data.keys())}")
                    return []
            else:
                st.warning(f"Unexpected API response type: {type(data)}")
                return []
        else:
            st.warning(f"API returned status code: {response.status_code}")
            return []
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend API. Please ensure the backend is running.")
        return []
    except requests.exceptions.Timeout:
        st.error("API request timed out. Please try again.")
        return []
    except Exception as e:
        st.error(f"Error fetching products: {str(e)}")
        return []

def get_products_map():
    """Get products as a dictionary for quick lookup"""
    products = get_products()
    if products and isinstance(products, list):
        return {p['id']: p for p in products if isinstance(p, dict)}
    return {}

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6B7280;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
    }
    .icsr-positive {
        background-color: #FEE2E2;
        border-left-color: #EF4444;
    }
    .icsr-negative {
        background-color: #DBEAFE;
        border-left-color: #3B82F6;
    }
    .confidence-high {
        color: #10B981;
        font-weight: bold;
    }
    .confidence-medium {
        color: #F59E0B;
        font-weight: bold;
    }
    .confidence-low {
        color: #EF4444;
        font-weight: bold;
    }
    /* Reduce font size for metric values - more compact */
    [data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        font-weight: 500;
    }
    /* Even smaller for very dense displays */
    .small-metric [data-testid="stMetricValue"] {
        font-size: 0.95rem !important;
    }
    .small-metric [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
    }
</style>
""", unsafe_allow_html=True)

def load_active_jobs_from_backend():
    """Load active/recent jobs from backend on app start"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/search/jobs", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                jobs = data.get('data', [])
                
                # Get jobs from last 24 hours that are running or recently completed
                recent_jobs = []
                for job in jobs[:10]:  # Last 10 jobs
                    if job.get('status') in ['running', 'completed']:
                        recent_jobs.append(job)
                
                return recent_jobs
        return []
    except:
        return []

def get_products_map():
    """Get products as a dictionary for quick lookup"""
    products = get_products()
    if products and isinstance(products, list):
        return {p['id']: p for p in products if isinstance(p, dict)}
    return {}

# Initialize session state with persistence
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    
    # Load recent jobs from backend on first load
    backend_jobs = load_active_jobs_from_backend()
    products_map = get_products_map()
    
    if backend_jobs:
        for job in backend_jobs:
            if job.get('status') == 'running':
                # Add to active jobs
                product_id = job.get('product_id')
                product = products_map.get(product_id, {})
                
                job_info = {
                    'job_id': job.get('id'),
                    'product': product,
                    'product_name': product.get('inn', 'Unknown'),
                    'date_range': {
                        'start': job.get('date_from', ''),
                        'end': job.get('date_to', '')
                    },
                    'timestamp': job.get('created_at', ''),
                    'status': 'running'
                }
                if 'active_jobs' not in st.session_state:
                    st.session_state.active_jobs = []
                st.session_state.active_jobs.append(job_info)

if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None
if 'all_search_results' not in st.session_state:
    st.session_state.all_search_results = []  # Store all search results with metadata
if 'active_jobs' not in st.session_state:
    st.session_state.active_jobs = []  # Store active search jobs [{'job_id': X, 'product': Y, ...}]

# Continue with other helper functions
def search_articles(product_id, start_date, end_date):
    """Search articles using the API"""
    try:
        params = {
            'product_id': product_id,
            'start_date': start_date,
            'end_date': end_date
        }
        with st.spinner('🤖 AI analyzing articles...'):
            response = requests.post(
                f"{API_BASE_URL}/api/search/pubmed",
                json=params,
                timeout=300
            )
        
        if response.status_code == 200:
            data = response.json()
            # Handle both old and new response formats
            if isinstance(data, dict):
                if 'success' in data and not data.get('success'):
                    st.error(f"Search failed: {data.get('error', 'Unknown error')}")
                    return None
                elif 'articles' in data:
                    return data
                else:
                    # Old format - might be wrapped in data
                    return data
            return data
        elif response.status_code == 404:
            st.error("Search endpoint not found. Please ensure backend is running with the latest code.")
            st.info("Try rebuilding the backend: `docker-compose -f docker-compose.streamlit.yml build backend`")
            return None
        else:
            try:
                error_data = response.json()
                st.error(f"Search failed: {error_data.get('error', response.text)}")
            except:
                st.error(f"Search failed with status {response.status_code}")
            return None
    except requests.exceptions.Timeout:
        st.error("Search timed out. This can happen with large date ranges. Try a shorter date range.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend API. Please ensure Docker is running.")
        return None
    except Exception as e:
        st.error(f"Error during search: {str(e)}")
        return None

def export_to_excel(articles, product_name):
    """Export articles to Excel format using pandas"""
    try:
        # Prepare data for Excel
        excel_data = []
        for article in articles:
            ai_analysis = article.get('ai_analysis', {})
            criteria = ai_analysis.get('criteria_present', {})
            evidence = ai_analysis.get('criteria_evidence', {})
            
            excel_data.append({
                'PMID': article.get('pmid', ''),
                'Title': article.get('title', ''),
                'Abstract': article.get('abstract', ''),
                'Publication Date': article.get('pub_date', ''),
                'Journal': article.get('journal', ''),
                'Authors': article.get('authors', ''),
                'Is ICSR': 'Yes' if article.get('is_icsr') else 'No',
                'Confidence Score': f"{article.get('confidence_score', 0):.0%}",
                'Patient Identified': 'Yes' if criteria.get('identifiable_patient') else 'No',
                'Reporter Identified': 'Yes' if criteria.get('identifiable_reporter') else 'No',
                'Drug Identified': 'Yes' if criteria.get('suspected_drug') else 'No',
                'Adverse Reaction': 'Yes' if criteria.get('adverse_reaction') else 'No',
                'Adverse Events': ', '.join(ai_analysis.get('adverse_events', [])),
                'Reasoning': ai_analysis.get('reasoning', ''),
                'Patient Evidence': evidence.get('patient_info', ''),
                'Reporter Evidence': evidence.get('reporter_info', ''),
                'Drug Evidence': evidence.get('drug_info', ''),
                'Reaction Evidence': evidence.get('reaction_info', ''),
            })
        
        # Create DataFrame
        df = pd.DataFrame(excel_data)
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='ICSR Analysis', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['ICSR Analysis']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
        output.seek(0)
        return output.getvalue()
        
    except Exception as e:
        st.error(f"Error generating Excel: {str(e)}")
        return None

def start_async_search(product_id, start_date, end_date):
    """Start an asynchronous search job"""
    try:
        params = {
            'product_id': product_id,
            'date_from': start_date,
            'date_to': end_date
        }
        response = requests.post(
            f"{API_BASE_URL}/api/search/execute",
            json=params,
            timeout=10
        )
        
        # Backend returns 202 (Accepted) for async jobs
        if response.status_code in [200, 202]:
            data = response.json()
            if data.get('success'):
                return data.get('job_id')
        
        # Show error if failed
        try:
            error_data = response.json()
            st.error(f"Search failed: {error_data.get('error', 'Unknown error')}")
        except:
            st.error(f"Search failed with status {response.status_code}")
        
        return None
    except Exception as e:
        st.error(f"Error starting search: {str(e)}")
        return None

def get_job_status(job_id):
    """Get status of a search job"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/search/jobs/{job_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('data')
        return None
    except Exception as e:
        return None

def get_job_results(job_id):
    """Get results of a completed search job"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/search/jobs/{job_id}/results",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                # Backend returns: {'success': True, 'job': {...}, 'results': [...], 'count': X}
                return data  # Return the whole data object
        return None
    except Exception as e:
        st.error(f"Error fetching job results: {str(e)}")
        return None

def format_confidence(confidence):
    """Format confidence score with color"""
    if confidence >= 0.85:
        return f'<span class="confidence-high">{confidence:.0%}</span>'
    elif confidence >= 0.60:
        return f'<span class="confidence-medium">{confidence:.0%}</span>'
    else:
        return f'<span class="confidence-low">{confidence:.0%}</span>'

# Sidebar
with st.sidebar:
    st.markdown("### 💊 PharmaVigilance AI")
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["🔍 Search", "📋 Results", "📥 Export", "📊 Dashboard", "📦 Products"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("#### About")
    st.markdown("""
    AI-powered literature monitoring system for 
    pharmacovigilance and ICSR detection.
    
    **Features:**
    - AI-powered ICSR detection
    - Multi-step reasoning
    - Evidence extraction
    - Ownership analysis
    """)

# Main Content
if page == "🔍 Search":
    st.markdown('<div class="main-header">📚 Literature Search</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Search PubMed for potential ICSRs using AI analysis</div>', unsafe_allow_html=True)
    
    # Search Form
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Product Selection
        products = get_products()
        if products and isinstance(products, list) and len(products) > 0:
            try:
                # Backend returns 'inn' field, not 'name'
                product_options = {p.get('inn', 'Unknown'): p['id'] for p in products if isinstance(p, dict) and 'id' in p}
                if not product_options:
                    st.warning("No valid products found. Please add products in the Products page.")
                    selected_product_id = None
                    selected_product_data = None
                else:
                    selected_product_name = st.selectbox(
                        "Select Product (INN)",
                        options=list(product_options.keys()),
                        help="Choose the product to monitor"
                    )
                    selected_product_id = product_options[selected_product_name]
                    
                    # Get product details
                    selected_product_data = next((p for p in products if p['id'] == selected_product_id), None)
            except Exception as e:
                st.error(f"Error processing products: {str(e)}")
                selected_product_id = None
                selected_product_data = None
        else:
            st.warning("No products found. Please add products in the Products page.")
            selected_product_id = None
            selected_product_data = None
    
    with col2:
        # Date Range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        date_range = st.date_input(
            "Date Range",
            value=(start_date, end_date),
            help="Select the date range to search"
        )
        
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = end_date - timedelta(days=30)
    
    # Display Product Info
    if selected_product_data:
        st.markdown("#### Selected Product Details")
        cols = st.columns(4)
        with cols[0]:
            st.metric("INN", selected_product_data.get('inn', 'N/A'))
        with cols[1]:
            territories = selected_product_data.get('territories', [])
            st.metric("Territories", len(territories) if territories else 0)
        with cols[2]:
            dosage_forms = selected_product_data.get('dosage_forms', [])
            st.metric("Dosage Forms", len(dosage_forms) if dosage_forms else 0)
        with cols[3]:
            marketing_status = selected_product_data.get('marketing_status', 'N/A')
            st.metric("Status", marketing_status)
    
    # Search Button
    if st.button("🔍 Search Articles", type="primary", disabled=not selected_product_id):
        # Start async search job
        job_id = start_async_search(
            selected_product_id,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        if job_id:
            # Add to active jobs
            job_info = {
                'job_id': job_id,
                'product': selected_product_data,
                'product_name': selected_product_data.get('inn', 'Unknown'),
                'date_range': {
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d')
                },
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'running'
            }
            st.session_state.active_jobs.append(job_info)
            
            st.success(f"✅ Search started for **{selected_product_data.get('inn', 'Unknown')}**")
        else:
            st.error("❌ Failed to start search. Please try again.")
    

elif page == "📋 Results":
    st.markdown('<div class="main-header">📋 Search Results</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">View all search results categorized by product and date</div>', unsafe_allow_html=True)
    
    # Add manual refresh button
    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button("🔄 Get Results for Latest Search", type="primary", use_container_width=True):
            # Fetch all jobs and find the most recent completed one
            try:
                response = requests.get(f"{API_BASE_URL}/api/search/jobs", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        jobs = data.get('data', [])
                        
                        # Find most recent completed job
                        completed_jobs = [j for j in jobs if j.get('status') == 'completed']
                        if completed_jobs:
                            latest_job = completed_jobs[0]  # Already sorted by created_at desc
                            job_id = latest_job.get('id')
                            
                            # Fetch results for this job
                            results_response = requests.get(
                                f"{API_BASE_URL}/api/search/jobs/{job_id}/results",
                                timeout=10
                            )
                            
                            if results_response.status_code == 200:
                                results_data = results_response.json()
                                if results_data.get('success'):
                                    job_results = results_data.get('results', [])
                                    
                                    # Get product info
                                    product_id = latest_job.get('product_id')
                                    products_map = get_products_map()
                                    product = products_map.get(product_id, {})
                                    
                                    # Convert to display format
                                    articles = []
                                    for result in job_results:
                                        article_info = result.get('article', {})
                                        articles.append({
                                            'pmid': article_info.get('pmid', ''),
                                            'title': article_info.get('title', ''),
                                            'abstract': article_info.get('abstract', ''),
                                            'pub_date': str(article_info.get('create_date', '')) if article_info.get('create_date') else article_info.get('publication_year', ''),
                                            'authors': article_info.get('authors', ''),
                                            'journal': article_info.get('journal', ''),
                                            'is_icsr': result.get('is_icsr', False),
                                            'confidence_score': result.get('confidence_score', 0),
                                            'ai_analysis': result.get('ai_analysis', {})
                                        })
                                    
                                    # Check if this result already exists
                                    job_exists = any(
                                        s.get('timestamp') == latest_job.get('created_at') 
                                        for s in st.session_state.all_search_results
                                    )
                                    
                                    if not job_exists and articles:
                                        # Add to results
                                        search_metadata = {
                                            'timestamp': latest_job.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                                            'product': product,
                                            'product_name': product.get('inn', 'Unknown'),
                                            'date_range': {
                                                'start': latest_job.get('date_from', ''),
                                                'end': latest_job.get('date_to', '')
                                            },
                                            'results': {'articles': articles},
                                            'summary': {
                                                'total': len(articles),
                                                'icsr_count': sum(1 for a in articles if a.get('is_icsr')),
                                                'high_confidence': sum(1 for a in articles if a.get('confidence_score', 0) >= 0.85)
                                            }
                                        }
                                        
                                        st.session_state.all_search_results.insert(0, search_metadata)
                                        st.success(f"✅ Loaded results for **{product.get('inn', 'Unknown')}**: {len(articles)} articles with {sum(1 for a in articles if a.get('is_icsr'))} ICSRs")
                                        st.rerun()
                                    elif job_exists:
                                        st.info("ℹ️ Latest search results are already displayed below")
                                    else:
                                        st.warning("⚠️ No articles found in the latest search")
                                else:
                                    st.error("❌ Could not fetch results")
                            else:
                                st.error(f"❌ Failed to fetch results (HTTP {results_response.status_code})")
                        else:
                            st.info("ℹ️ No completed searches found. Please run a search first.")
                    else:
                        st.error("❌ Could not fetch jobs from backend")
                else:
                    st.error(f"❌ Backend error (HTTP {response.status_code})")
            except Exception as e:
                st.error(f"❌ Error fetching results: {str(e)}")
    
    st.markdown("---")
    
    # Process active jobs and check their status
    jobs_to_remove = []
    newly_completed = []
    
    for idx, job_info in enumerate(st.session_state.active_jobs):
        job_status = get_job_status(job_info['job_id'])
        
        if job_status:
            status = job_status.get('status')
            
            if status == 'completed':
                # Fetch results from backend
                job_results_response = get_job_results(job_info['job_id'])
                
                if job_results_response and job_results_response.get('success'):
                    job_results = job_results_response.get('results', [])
                    
                    # Convert backend results to our display format
                    articles = []
                    for result in job_results:
                        article_info = result.get('article', {})
                        
                        articles.append({
                            'pmid': article_info.get('pmid', ''),
                            'title': article_info.get('title', ''),
                            'abstract': article_info.get('abstract', ''),
                            'pub_date': str(article_info.get('create_date', '')) if article_info.get('create_date') else article_info.get('publication_year', ''),
                            'authors': article_info.get('authors', ''),
                            'journal': article_info.get('journal', ''),
                            'is_icsr': result.get('is_icsr', False),
                            'confidence_score': result.get('confidence_score', 0),
                            'ai_analysis': result.get('ai_analysis', {})
                        })
                    
                    # Create search metadata
                    search_metadata = {
                        'timestamp': job_info['timestamp'],
                        'product': job_info['product'],
                        'product_name': job_info['product_name'],
                        'date_range': job_info['date_range'],
                        'results': {'articles': articles},
                        'summary': {
                            'total': len(articles),
                            'icsr_count': sum(1 for a in articles if a.get('is_icsr')),
                            'high_confidence': sum(1 for a in articles if a.get('confidence_score', 0) >= 0.85)
                        }
                    }
                    
                    # Add to completed results
                    st.session_state.all_search_results.insert(0, search_metadata)
                    
                    # Keep only last 50 searches
                    if len(st.session_state.all_search_results) > 50:
                        st.session_state.all_search_results = st.session_state.all_search_results[:50]
                    
                    # Track newly completed for notification
                    newly_completed.append({
                        'product_name': job_info['product_name'],
                        'total': len(articles),
                        'icsr_count': sum(1 for a in articles if a.get('is_icsr'))
                    })
                
                # Mark job for removal
                jobs_to_remove.append(idx)
            
            elif status == 'failed':
                st.error(f"❌ Search failed for {job_info['product_name']}: {job_status.get('error_message', 'Unknown error')}")
                jobs_to_remove.append(idx)
    
    # Remove completed/failed jobs from active list
    for idx in reversed(jobs_to_remove):
        st.session_state.active_jobs.pop(idx)
    
    # Show notifications for newly completed searches
    for completed_job in newly_completed:
        st.success(f"✅ Search completed for **{completed_job['product_name']}**! Found {completed_job['total']} articles with {completed_job['icsr_count']} potential ICSRs.")
    
    # If we just completed jobs, trigger a rerun to update the display
    if newly_completed:
        time.sleep(1)  # Brief pause to show success message
        st.rerun()
    
    # Show SINGLE progress bar for all active jobs
    if st.session_state.active_jobs:
        st.markdown("### 🔄 Active Searches")
        
        # Collect all job info
        all_jobs_info = []
        total_processed = 0
        total_articles_all_jobs = 0
        
        for job_info in st.session_state.active_jobs:
            job_status = get_job_status(job_info['job_id'])
            
            if job_status:
                status = job_status.get('status', 'unknown')
                total_articles = job_status.get('total_articles', 0)
                
                # Get processed count
                processed_count = 0
                if status == 'running' and total_articles > 0:
                    try:
                        response = requests.get(
                            f"{API_BASE_URL}/api/search/jobs/{job_info['job_id']}/results",
                            timeout=5
                        )
                        if response.status_code == 200:
                            data = response.json()
                            processed_count = data.get('count', 0)
                    except:
                        processed_count = 0
                
                all_jobs_info.append({
                    'product_name': job_info['product_name'],
                    'status': status,
                    'total_articles': total_articles,
                    'processed_count': processed_count
                })
                
                total_processed += processed_count
                total_articles_all_jobs += total_articles
        
        # Display single progress bar for all jobs
        if total_articles_all_jobs > 0:
            overall_progress = total_processed / total_articles_all_jobs if total_articles_all_jobs > 0 else 0
            
            # Show product names
            product_names = [job['product_name'] for job in all_jobs_info]
            if len(product_names) == 1:
                progress_text = f"🔬 Analyzing: {product_names[0]} ({total_processed}/{total_articles_all_jobs} articles)"
            else:
                progress_text = f"🔬 Analyzing: {total_processed}/{total_articles_all_jobs} articles"
            
            st.progress(overall_progress, text=progress_text)
            
            # Show individual job statuses below
            st.markdown("---")
            for job in all_jobs_info:
                if job['status'] == 'running':
                    if job['total_articles'] > 0:
                        st.caption(f"📦 **{job['product_name']}**: {job['processed_count']}/{job['total_articles']} articles analyzed")
                    else:
                        st.caption(f"📦 **{job['product_name']}**: Searching PubMed...")
        else:
            # Still searching, no articles found yet
            st.info(f"🔍 Searching PubMed database...")
        
        # Auto-refresh every 3 seconds
        time.sleep(3)
        st.rerun()
    
    if not st.session_state.all_search_results and not st.session_state.active_jobs:
        st.info("🔍 No search results yet. Go to the 'Search' tab to run your first search!")
    elif st.session_state.all_search_results:
        # Header with clear button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### Total Searches: {len(st.session_state.all_search_results)}")
        with col2:
            if st.button("🗑️ Clear All Results", type="secondary"):
                st.session_state.all_search_results = []
                st.rerun()
        
        # Group results by product
        results_by_product = {}
        for search in st.session_state.all_search_results:
            product_name = search['product_name']
            if product_name not in results_by_product:
                results_by_product[product_name] = []
            results_by_product[product_name].append(search)
        
        # Create tabs for each product (instead of nested expanders)
        product_tabs = st.tabs([f"📦 {pname} ({len(searches)})" for pname, searches in results_by_product.items()])
        
        for tab_idx, (product_name, product_searches) in enumerate(results_by_product.items()):
            with product_tabs[tab_idx]:
                
                for search_idx, search in enumerate(product_searches):
                    st.markdown("---")
                    
                    # Search metadata
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Search Date", search['timestamp'].split()[0])
                    with col2:
                        st.metric("Search Time", search['timestamp'].split()[1])
                    with col3:
                        st.metric("Date Range", f"{search['date_range']['start']} to {search['date_range']['end']}")
                    with col4:
                        st.metric("Total Articles", search['summary']['total'])
                    
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Potential ICSRs", search['summary']['icsr_count'])
                    with col2:
                        st.metric("High Confidence", search['summary']['high_confidence'])
                    with col3:
                        review_required = search['summary']['total'] - search['summary']['icsr_count']
                        st.metric("Review Required", review_required)
                    
                    # Get articles
                    articles = search['results'].get('articles', [])
                    
                    if articles:
                        # Filters
                        st.markdown("#### Filters")
                        filter_col1, filter_col2, filter_col3 = st.columns(3)
                        
                        with filter_col1:
                            filter_icsr = st.selectbox(
                                "ICSR Status", 
                                ["All", "ICSR Only", "Non-ICSR Only"],
                                key=f"filter_icsr_{product_name}_{search_idx}"
                            )
                        with filter_col2:
                            filter_confidence = st.selectbox(
                                "Confidence", 
                                ["All", "High (>85%)", "Medium (60-85%)", "Low (<60%)"],
                                key=f"filter_conf_{product_name}_{search_idx}"
                            )
                        with filter_col3:
                            sort_by = st.selectbox(
                                "Sort By", 
                                ["Date (Newest)", "Date (Oldest)", "Confidence (High)", "Confidence (Low)"],
                                key=f"sort_{product_name}_{search_idx}"
                            )
                        
                        # Apply Filters
                        filtered_articles = articles.copy()
                        
                        if filter_icsr == "ICSR Only":
                            filtered_articles = [a for a in filtered_articles if a.get('is_icsr')]
                        elif filter_icsr == "Non-ICSR Only":
                            filtered_articles = [a for a in filtered_articles if not a.get('is_icsr')]
                        
                        if filter_confidence == "High (>85%)":
                            filtered_articles = [a for a in filtered_articles if a.get('confidence_score', 0) >= 0.85]
                        elif filter_confidence == "Medium (60-85%)":
                            filtered_articles = [a for a in filtered_articles if 0.60 <= a.get('confidence_score', 0) < 0.85]
                        elif filter_confidence == "Low (<60%)":
                            filtered_articles = [a for a in filtered_articles if a.get('confidence_score', 0) < 0.60]
                        
                        # Sort
                        if sort_by == "Date (Newest)":
                            filtered_articles.sort(key=lambda x: x.get('pub_date', ''), reverse=True)
                        elif sort_by == "Date (Oldest)":
                            filtered_articles.sort(key=lambda x: x.get('pub_date', ''))
                        elif sort_by == "Confidence (High)":
                            filtered_articles.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)
                        elif sort_by == "Confidence (Low)":
                            filtered_articles.sort(key=lambda x: x.get('confidence_score', 0))
                        
                        # Display Articles
                        st.markdown(f"#### Articles ({len(filtered_articles)} shown)")
                        
                        for idx, article in enumerate(filtered_articles, 1):
                            is_icsr = article.get('is_icsr', False)
                            confidence = article.get('confidence_score', 0)
                            
                            with st.expander(
                                f"{'🔴' if is_icsr else '🔵'} [{idx}] {article.get('title', 'Untitled')[:80]}... | "
                                f"Confidence: {confidence:.0%}",
                                expanded=False
                            ):
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.markdown(f"**Title:** {article.get('title', 'N/A')}")
                                    st.markdown(f"**PMID:** {article.get('pmid', 'N/A')}")
                                    st.markdown(f"**Publication Date:** {article.get('pub_date', 'N/A')}")
                                    st.markdown(f"**Abstract:**")
                                    st.text_area(
                                        "Article Abstract", 
                                        article.get('abstract', 'N/A'), 
                                        height=100, 
                                        key=f"abstract_{product_name}_{search_idx}_{idx}", 
                                        label_visibility="collapsed"
                                    )
                                
                                with col2:
                                    st.markdown("**Analysis**")
                                    st.markdown(f"**ICSR:** {'✅ Yes' if is_icsr else '❌ No'}")
                                    st.markdown(f"**Confidence:** {confidence:.0%}")
                                    
                                    # Criteria
                                    ai_analysis = article.get('ai_analysis', {})
                                    criteria = ai_analysis.get('criteria_present', {})
                                    
                                    if criteria:
                                        st.markdown("**Criteria:**")
                                        st.markdown(f"- Patient: {'✓' if criteria.get('identifiable_patient') else '✗'}")
                                        st.markdown(f"- Reporter: {'✓' if criteria.get('identifiable_reporter') else '✗'}")
                                        st.markdown(f"- Drug: {'✓' if criteria.get('suspected_drug') else '✗'}")
                                        st.markdown(f"- Reaction: {'✓' if criteria.get('adverse_reaction') else '✗'}")
                                
                                # Adverse Events
                                adverse_events = ai_analysis.get('adverse_events', [])
                                if adverse_events:
                                    st.markdown("**⚠️ Adverse Events:**")
                                    for event in adverse_events:
                                        st.markdown(f"- {event}")
                                
                                # Reasoning
                                reasoning = ai_analysis.get('reasoning', '')
                                if reasoning:
                                    st.markdown("**💭 AI Reasoning:**")
                                    st.info(reasoning)
                                
                                # Evidence - Use checkbox instead of nested expander
                                evidence = ai_analysis.get('criteria_evidence', {})
                                if evidence and any(evidence.values()):
                                    show_evidence = st.checkbox(
                                        "📝 Show Evidence Details", 
                                        key=f"evidence_{product_name}_{search_idx}_{idx}"
                                    )
                                    if show_evidence:
                                        st.markdown("**Evidence Quotes:**")
                                        for key, value in evidence.items():
                                            if value:
                                                st.markdown(f"**{key.replace('_', ' ').title()}:**")
                                                st.markdown(f"> {value}")

elif page == "📥 Export":
    st.markdown('<div class="main-header">📥 Export Results</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Export search results to Excel format for regulatory compliance</div>', unsafe_allow_html=True)
    
    if not st.session_state.all_search_results:
        st.info("🔍 No search results available to export. Run a search first!")
    else:
        # Export Statistics
        total_searches = len(st.session_state.all_search_results)
        total_articles = sum(s['summary']['total'] for s in st.session_state.all_search_results)
        total_icsrs = sum(s['summary']['icsr_count'] for s in st.session_state.all_search_results)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Searches", total_searches)
        with col2:
            st.metric("Total Articles", total_articles)
        with col3:
            st.metric("Total ICSRs", total_icsrs)
        with col4:
            icsr_rate = (total_icsrs / total_articles * 100) if total_articles > 0 else 0
            st.metric("ICSR Rate", f"{icsr_rate:.1f}%")
        
        st.markdown("---")
        
        # Export Tabs
        tab1, tab2 = st.tabs(["📄 Export Individual Search", "📊 Export All Searches"])
        
        with tab1:
            st.markdown("### Export Individual Search Result")
            
            # Create options for export
            export_options = []
            for idx, search in enumerate(st.session_state.all_search_results):
                option_text = (
                    f"{search['product_name']} | "
                    f"{search['timestamp']} | "
                    f"Articles: {search['summary']['total']} | "
                    f"ICSRs: {search['summary']['icsr_count']}"
                )
                export_options.append(option_text)
            
            selected_export = st.selectbox("Choose a search result to export:", export_options)
            
            if selected_export:
                selected_idx = export_options.index(selected_export)
                selected_search = st.session_state.all_search_results[selected_idx]
                
                # Display summary
                st.markdown("---")
                st.markdown("### Export Preview")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Product:** {selected_search['product_name']}")
                    st.markdown(f"**Search Timestamp:** {selected_search['timestamp']}")
                    st.markdown(f"**Date Range:** {selected_search['date_range']['start']} to {selected_search['date_range']['end']}")
                
                with col2:
                    st.markdown(f"**Total Articles:** {selected_search['summary']['total']}")
                    st.markdown(f"**Potential ICSRs:** {selected_search['summary']['icsr_count']}")
                    st.markdown(f"**High Confidence:** {selected_search['summary']['high_confidence']}")
                
                st.markdown("---")
                
                # Export options
                col1, col2 = st.columns(2)
                
                with col1:
                    export_format = st.radio("Export Format:", ["Excel (.xlsx)", "JSON (.json)"])
                
                with col2:
                    include_filter = st.radio("Include:", ["All Articles", "ICSRs Only", "High Confidence Only"])
                
                # Export button
                if st.button("📥 Generate Export", type="primary"):
                    articles = selected_search['results'].get('articles', [])
                    
                    # Apply filter
                    if include_filter == "ICSRs Only":
                        articles = [a for a in articles if a.get('is_icsr')]
                    elif include_filter == "High Confidence Only":
                        articles = [a for a in articles if a.get('confidence_score', 0) >= 0.85]
                    
                    if export_format == "Excel (.xlsx)":
                        # Generate Excel using pandas
                        export_data = export_to_excel(articles, selected_search['product_name'])
                        
                        if export_data:
                            filename = f"pharma_pv_{selected_search['product_name']}_{selected_search['timestamp'].replace(':', '-').replace(' ', '_')}.xlsx"
                            st.download_button(
                                label="⬇️ Download Excel File",
                                data=export_data,
                                file_name=filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                type="primary"
                            )
                            st.success(f"✅ Excel export ready! ({len(articles)} articles)")
                        else:
                            st.error("❌ Failed to generate Excel export.")
                    
                    elif export_format == "JSON (.json)":
                        # Export as JSON
                        export_json = {
                            'export_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'product': selected_search['product_name'],
                            'search_timestamp': selected_search['timestamp'],
                            'date_range': selected_search['date_range'],
                            'summary': selected_search['summary'],
                            'articles': articles
                        }
                        
                        json_str = json.dumps(export_json, indent=2)
                        filename = f"pharma_pv_{selected_search['product_name']}_{selected_search['timestamp'].replace(':', '-').replace(' ', '_')}.json"
                        
                        st.download_button(
                            label="⬇️ Download JSON File",
                            data=json_str,
                            file_name=filename,
                            mime="application/json",
                            type="primary"
                        )
                        st.success(f"✅ JSON export ready! ({len(articles)} articles)")
        
        with tab2:
            st.markdown("### Export All Search Results (Combined)")
            
            st.info(f"📊 This will export all {total_searches} searches with {total_articles} total articles.")
            
            # Export all as JSON
            if st.button("📥 Export All as JSON", type="primary"):
                all_export = {
                    'export_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_searches': total_searches,
                    'total_articles': total_articles,
                    'total_icsrs': total_icsrs,
                    'searches': st.session_state.all_search_results
                }
                
                json_str = json.dumps(all_export, indent=2)
                filename = f"pharma_pv_all_searches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                st.download_button(
                    label="⬇️ Download Combined JSON",
                    data=json_str,
                    file_name=filename,
                    mime="application/json",
                    type="primary"
                )
                st.success(f"✅ Combined export ready! ({total_searches} searches, {total_articles} articles)")
            
            st.markdown("---")
            st.markdown("### Export Summary Table")
            
            # Create summary dataframe
            summary_data = []
            for search in st.session_state.all_search_results:
                summary_data.append({
                    'Product': search['product_name'],
                    'Timestamp': search['timestamp'],
                    'Date Range': f"{search['date_range']['start']} to {search['date_range']['end']}",
                    'Total Articles': search['summary']['total'],
                    'ICSRs': search['summary']['icsr_count'],
                    'High Confidence': search['summary']['high_confidence'],
                    'ICSR Rate': f"{(search['summary']['icsr_count'] / search['summary']['total'] * 100):.1f}%" if search['summary']['total'] > 0 else "0%"
                })
            
            df = pd.DataFrame(summary_data)
            st.dataframe(df, use_container_width=True)
            
            # Export summary as CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download Summary as CSV",
                data=csv,
                file_name=f"pharma_pv_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

elif page == "📊 Dashboard":
    st.markdown('<div class="main-header">📊 Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Overview of literature monitoring activities</div>', unsafe_allow_html=True)
    
    # Summary Statistics
    products = get_products()
    
    # Ensure products is a list
    if not isinstance(products, list):
        products = []
    
    # Calculate search statistics
    total_searches = len(st.session_state.all_search_results)
    total_articles = sum(s['summary']['total'] for s in st.session_state.all_search_results) if st.session_state.all_search_results else 0
    total_icsrs = sum(s['summary']['icsr_count'] for s in st.session_state.all_search_results) if st.session_state.all_search_results else 0
    
    # Top row metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Products", len(products))
    col2.metric("Total Searches", total_searches)
    col3.metric("Articles Analyzed", total_articles)
    col4.metric("ICSRs Detected", total_icsrs)
    
    # Second row metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Products", sum(1 for p in products if isinstance(p, dict) and p.get('marketing_status') == 'Active'))
    col2.metric("AI Analysis", "Active ✅")
    icsr_rate = (total_icsrs / total_articles * 100) if total_articles > 0 else 0
    col3.metric("ICSR Detection Rate", f"{icsr_rate:.1f}%")
    col4.metric("Last Update", datetime.now().strftime("%Y-%m-%d"))
    
    st.markdown("---")
    
    # Recent Activity
    st.markdown("### 📈 Recent Activity")
    
    if st.session_state.all_search_results:
        st.markdown("#### Latest Searches")
        recent_searches = st.session_state.all_search_results[:5]  # Show last 5
        
        for search in recent_searches:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"**{search['product_name']}**")
            with col2:
                st.markdown(f"🕐 {search['timestamp']}")
            with col3:
                st.markdown(f"📄 {search['summary']['total']} articles")
            with col4:
                st.markdown(f"🔴 {search['summary']['icsr_count']} ICSRs")
        
        st.markdown("---")
    else:
        st.info("🤖 The AI system is ready to monitor literature for potential ICSRs using multi-step reasoning and evidence extraction.")
        st.info("🔍 Run your first search to see activity here!")
    
    # Product Summary
    if products and len(products) > 0:
        st.markdown("### 📦 Products Overview")
        try:
            df = pd.DataFrame([{
                'INN': p.get('inn', 'N/A'),
                'Territories': len(p.get('territories', [])),
                'Dosage Forms': len(p.get('dosage_forms', [])),
                'Marketing Status': p.get('marketing_status', 'N/A'),
                'EU Product': '✅' if p.get('is_eu_product') else '❌'
            } for p in products if isinstance(p, dict)])
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error displaying products: {str(e)}")

elif page == "📦 Products":
    st.markdown('<div class="main-header">📦 Product Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Manage products for literature monitoring</div>', unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2 = st.tabs(["📋 View Products", "➕ Add Product"])
    
    with tab1:
        products = get_products()
        
        # Ensure products is a list
        if not isinstance(products, list):
            products = []
        
        if products and len(products) > 0:
            try:
                for product in products:
                    if isinstance(product, dict):
                        with st.expander(f"📦 {product.get('inn', 'Unknown')}", expanded=False):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"**INN:** {product.get('inn', 'N/A')}")
                                st.markdown(f"**Marketing Status:** {product.get('marketing_status', 'N/A')}")
                                st.markdown(f"**EU Product:** {'✅ Yes' if product.get('is_eu_product') else '❌ No'}")
                                st.markdown(f"**Search Strategy:** {product.get('search_strategy', 'N/A')[:100]}...")
                            
                            with col2:
                                territories = product.get('territories', [])
                                dosage_forms = product.get('dosage_forms', [])
                                routes = product.get('routes_of_administration', [])
                                
                                st.markdown(f"**Territories ({len(territories)}):**")
                                st.markdown(", ".join(territories) if territories else "None")
                                
                                st.markdown(f"**Dosage Forms ({len(dosage_forms)}):**")
                                st.markdown(", ".join(dosage_forms) if dosage_forms else "None")
                                
                                st.markdown(f"**Routes ({len(routes)}):**")
                                st.markdown(", ".join(routes) if routes else "None")
            except Exception as e:
                st.error(f"Error displaying products: {str(e)}")
        else:
            st.info("No products found. Add products using the 'Add Product' tab.")
    
    with tab2:
        st.markdown("### Add New Product")
        
        with st.form("add_product_form"):
            inn_name = st.text_input("INN (International Nonproprietary Name)*", 
                                     placeholder="e.g., methotrexate",
                                     help="The generic name of the drug")
            
            search_strategy = st.text_area(
                "Search Strategy*",
                placeholder='e.g., methotrexate[Title/Abstract] AND ("case report"[Title/Abstract] OR "adverse"[Title/Abstract])',
                help="PubMed search query for this product",
                height=100
            )
            
            territories_input = st.text_area(
                "Territories (comma-separated)",
                placeholder="e.g., United States, United Kingdom, Canada, Germany",
                help="Enter territories separated by commas (optional)"
            )
            
            dosage_forms_input = st.text_area(
                "Dosage Forms (comma-separated)",
                placeholder="e.g., Tablet, Injection, Oral Solution",
                help="Enter dosage forms separated by commas (optional)"
            )
            
            routes_input = st.text_area(
                "Routes of Administration (comma-separated)",
                placeholder="e.g., Oral, Intravenous, Intramuscular",
                help="Enter routes separated by commas (optional)"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                is_eu_product = st.checkbox("EU Product", value=False)
            with col2:
                marketing_status = st.selectbox("Marketing Status", 
                                               ["Active", "Suspended", "Withdrawn"],
                                               index=0)
            
            submitted = st.form_submit_button("Add Product", type="primary")
            
            if submitted:
                if inn_name and search_strategy:
                    territories = [t.strip() for t in territories_input.split(',')] if territories_input else []
                    dosage_forms = [d.strip() for d in dosage_forms_input.split(',')] if dosage_forms_input else []
                    routes = [r.strip() for r in routes_input.split(',')] if routes_input else []
                    
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/api/products",
                            json={
                                'inn': inn_name,
                                'search_strategy': search_strategy,
                                'territories': territories,
                                'dosage_forms': dosage_forms,
                                'routes_of_administration': routes,
                                'is_eu_product': is_eu_product,
                                'marketing_status': marketing_status
                            },
                            timeout=10
                        )
                        
                        if response.status_code == 201:
                            result = response.json()
                            st.success(f"✅ Product '{inn_name}' added successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            error_data = response.json()
                            error_msg = error_data.get('error', response.text)
                            st.error(f"Failed to add product: {error_msg}")
                    except requests.exceptions.Timeout:
                        st.error("Request timed out. Please try again.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.error("Please fill in the required fields (INN and Search Strategy)")

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #6B7280; padding: 1rem;">© 2025 PharmaVigilance AI - Powered by Advanced AI Analysis</div>',
    unsafe_allow_html=True
)

