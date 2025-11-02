"""
Search API routes
"""
import logging
import threading
from datetime import datetime, date
from flask import request, jsonify, current_app
from app.api import api_bp
from app.models import db, Product, SearchJob, Article, SearchResult
from app.services.pubmed_service import PubMedService
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


def get_pubmed_service():
    """Get PubMed service instance"""
    return PubMedService(
        api_key=current_app.config.get('PUBMED_API_KEY'),
        email=current_app.config.get('PUBMED_EMAIL'),
        rate_limit=current_app.config.get('PUBMED_RATE_LIMIT', 10)
    )


def get_ai_service():
    """Get AI service instance"""
    return AIService(
        api_key=current_app.config.get('OPENAI_API_KEY'),
        model=current_app.config.get('OPENAI_MODEL', 'gpt-4.1-mini')
    )


def process_search_background(app, job_id, product_id, date_from, date_to):
    """
    Process search in background thread
    
    Args:
        app: Flask application instance
        job_id: Search job ID
        product_id: Product ID to search
        date_from: Start date
        date_to: End date
    """
    with app.app_context():
        try:
            logger.info(f"Background processing started for job {job_id}")
            
            # Get job and product
            search_job = SearchJob.query.get(job_id)
            product = Product.query.get(product_id)
            
            if not search_job or not product:
                logger.error(f"Job {job_id} or product {product_id} not found")
                return
            
            # Execute PubMed search
            pubmed = get_pubmed_service()
            pmids = pubmed.search(
                query=product.search_strategy,
                date_from=date_from,
                date_to=date_to,
                max_results=app.config.get('MAX_ARTICLES_PER_SEARCH', 100)
            )
            
            logger.info(f"Found {len(pmids)} articles for {product.inn}")
            
            # Update job with total articles found
            search_job.total_articles = len(pmids)
            db.session.commit()
            
            # Fetch article details and analyze
            ai_service = get_ai_service()
            results_count = 0
            
            for idx, pmid in enumerate(pmids):
                try:
                    # Fetch article details
                    article_data = pubmed.fetch_article_details(pmid)
                    if not article_data:
                        logger.warning(f"Could not fetch details for PMID {pmid}, skipping...")
                        continue
                    
                    # Check if article already exists
                    article = Article.query.filter_by(pmid=pmid).first()
                    if not article:
                        article = Article(**article_data)
                        db.session.add(article)
                        db.session.flush()
                    
                    # Analyze article with AI
                    analysis = ai_service.analyze_article(
                        title=article.title or "",
                        # abstract=article.abstract or "",
                        abstract=article_data.get('abstract', ''),
                        product_name=product.inn,
                        product_territories=product.territories,
                        product_dosage_forms=product.dosage_forms
                    )
                    
                    if analysis:
                        # Create search result
                        search_result = SearchResult(
                            search_job_id=search_job.id,
                            product_id=product.id,
                            article_id=article.id,
                            is_icsr=analysis.get('is_icsr'),
                            icsr_description=analysis.get('icsr_description', ''),
                            ownership_excluded=analysis.get('ownership_analysis', {}).get('can_exclude'),
                            exclusion_reason=analysis.get('ownership_analysis', {}).get('exclusion_reason', ''),
                            minimum_criteria_available=analysis.get('minimum_criteria_available'),
                            other_safety_info=analysis.get('safety_classification', {}).get('has_relevant_safety_info'),
                            safety_info_justification=analysis.get('safety_classification', {}).get('justification', ''),
                            confidence_score=analysis.get('confidence_score'),
                            ai_analysis=analysis
                        )
                        db.session.add(search_result)
                        results_count += 1
                    
                    # Commit every 5 articles to avoid losing progress
                    if (idx + 1) % 5 == 0:
                        db.session.commit()
                        logger.info(f"Processed {idx + 1}/{len(pmids)} articles")
                
                except Exception as e:
                    logger.error(f"Error processing article {pmid}: {str(e)}")
                    continue
            
            # Update search job
            search_job.status = 'completed'
            search_job.processed_products = 1
            search_job.total_articles = results_count
            search_job.completed_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Background search completed for job {job_id}. Found {results_count} articles.")
            
        except Exception as e:
            logger.error(f"Error in background search for job {job_id}: {str(e)}")
            try:
                search_job = SearchJob.query.get(job_id)
                if search_job:
                    search_job.status = 'failed'
                    search_job.error_message = str(e)
                    db.session.commit()
            except:
                pass


@api_bp.route('/search/pubmed', methods=['POST'])
def search_pubmed_sync():
    """
    Synchronous PubMed search with AI analysis
    For Streamlit UI - returns results immediately
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        product_id = data.get('product_id')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        
        if not product_id:
            return jsonify({
                'success': False,
                'error': 'product_id is required'
            }), 400
        
        # Get product
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'success': False,
                'error': f'Product with ID {product_id} not found'
            }), 404
        
        logger.info(f"Starting synchronous search for product: {product.inn}")
        
        # Parse dates
        date_from = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        date_to = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        
        # Initialize services
        pubmed_service = get_pubmed_service()
        ai_service = get_ai_service()
        
        # Search PubMed for PMIDs
        logger.info(f"Searching PubMed with strategy: {product.search_strategy[:100]}...")
        
        # Convert dates to strings for PubMed
        date_from_str = date_from.strftime('%Y/%m/%d') if date_from else None
        date_to_str = date_to.strftime('%Y/%m/%d') if date_to else None
        
        pmids = pubmed_service.search(
            query=product.search_strategy,
            date_from=date_from_str,
            date_to=date_to_str,
            max_results=current_app.config.get('MAX_ARTICLES_PER_SEARCH', 100)
        )
        
        if not pmids:
            logger.info("No articles found")
            return jsonify({
                'success': True,
                'articles': [],
                'summary': {
                    'total': 0,
                    'icsr_count': 0,
                    'high_confidence': 0
                }
            })
        
        logger.info(f"Found {len(pmids)} PMIDs, fetching article details...")
        
        # Fetch article details
        articles_data = pubmed_service.fetch_multiple_articles(pmids)
        
        if not articles_data:
            logger.warning("Failed to fetch article details")
            return jsonify({
                'success': True,
                'articles': [],
                'summary': {
                    'total': 0,
                    'icsr_count': 0,
                    'high_confidence': 0
                }
            })
        
        logger.info(f"Fetched {len(articles_data)} articles, starting AI analysis...")
        
        # Analyze each article with AI
        results = []
        icsr_count = 0
        high_confidence = 0
        
        for idx, article_data in enumerate(articles_data, 1):
            try:
                logger.info(f"Analyzing article {idx}/{len(articles_data)}: {article_data.get('pmid')}")
                
                # AI analysis
                analysis = ai_service.analyze_article(
                    title=article_data.get('title', ''),
                    abstract=article_data.get('abstract', ''),
                    product_name=product.inn,
                    product_territories=product.territories or [],
                    product_dosage_forms=product.dosage_forms or []
                )
                
                if analysis:
                    is_icsr = analysis.get('is_icsr', False)
                    confidence = analysis.get('confidence_score', 0)
                    
                    if is_icsr:
                        icsr_count += 1
                    if confidence >= 0.85:
                        high_confidence += 1
                    
                    # Build result
                    result = {
                        'pmid': article_data.get('pmid'),
                        'title': article_data.get('title'),
                        'abstract': article_data.get('abstract'),
                        'pub_date': str(article_data.get('create_date', '')) if article_data.get('create_date') else article_data.get('publication_year', ''),
                        'authors': article_data.get('authors'),
                        'journal': article_data.get('journal'),
                        'is_icsr': is_icsr,
                        'confidence_score': confidence,
                        'ai_analysis': analysis
                    }
                    
                    results.append(result)
                    logger.info(f"  → ICSR: {is_icsr}, Confidence: {confidence:.2f}")
                else:
                    logger.warning(f"No analysis returned for article {article_data.get('pmid')}")
                    
            except Exception as e:
                logger.error(f"Error analyzing article {article_data.get('pmid')}: {str(e)}")
                continue
        
        logger.info(f"Analysis complete. Total: {len(results)}, ICSRs: {icsr_count}, High confidence: {high_confidence}")
        
        return jsonify({
            'success': True,
            'articles': results,
            'summary': {
                'total': len(results),
                'icsr_count': icsr_count,
                'high_confidence': high_confidence
            }
        })
        
    except Exception as e:
        logger.error(f"Error in synchronous search: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/search/execute', methods=['POST'])
def execute_search():
    """Execute a single product search (async background processing)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        product_id = data.get('product_id')
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        if not product_id:
            return jsonify({
                'success': False,
                'error': 'product_id is required'
            }), 400
        
        # Get product to validate it exists
        product = Product.query.get_or_404(product_id)
        
        # Create search job
        search_job = SearchJob(
            job_type='single',
            status='running',
            date_from=datetime.strptime(date_from, '%Y-%m-%d').date() if date_from else None,
            date_to=datetime.strptime(date_to, '%Y-%m-%d').date() if date_to else None,
            total_products=1,
            processed_products=0,
            total_articles=0
        )
        db.session.add(search_job)
        db.session.commit()
        
        job_id = search_job.id
        
        logger.info(f"Created search job {job_id} for product: {product.inn}")
        
        # Start background processing thread
        thread = threading.Thread(
            target=process_search_background,
            args=(current_app._get_current_object(), job_id, product_id, date_from, date_to),
            daemon=True
        )
        thread.start()
        
        logger.info(f"Background thread started for job {job_id}")
        
        # Return immediately with job ID
        return jsonify({
            'success': True,
            'job_id': job_id,
            'status': 'running',
            'message': f'Search started for {product.inn}. Use /api/search/jobs/{job_id} to check progress.'
        }), 202
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error starting search: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


def process_batch_search_background(app, job_id, product_ids, date_from, date_to):
    """Process batch search in background"""
    with app.app_context():
        try:
            logger.info(f"Background batch processing started for job {job_id}")
            
            search_job = SearchJob.query.get(job_id)
            if not search_job:
                logger.error(f"Job {job_id} not found")
                return
            
            if not product_ids:
                products = Product.query.all()
            else:
                products = Product.query.filter(Product.id.in_(product_ids)).all()
            
            pubmed = get_pubmed_service()
            ai_service = get_ai_service()
            total_articles = 0
            
            for idx, product in enumerate(products):
                logger.info(f"Processing product {idx+1}/{len(products)}: {product.inn}")
                
                try:
                    pmids = pubmed.search(
                        query=product.search_strategy,
                        date_from=date_from,
                        date_to=date_to,
                        max_results=app.config.get('MAX_ARTICLES_PER_SEARCH', 100)
                    )
                    
                    for pmid in pmids:
                        try:
                            article_data = pubmed.fetch_article_details(pmid)
                            if not article_data:
                                continue
                            
                            article = Article.query.filter_by(pmid=pmid).first()
                            if not article:
                                article = Article(**article_data)
                                db.session.add(article)
                                db.session.flush()
                            
                            analysis = ai_service.analyze_article(
                                title=article.title or "",
                                # abstract=article.abstract or "",
                                abstract=article_data.get('abstract', ''),
                                product_name=product.inn,
                                product_territories=product.territories,
                                product_dosage_forms=product.dosage_forms
                            )
                            
                            if analysis:
                                search_result = SearchResult(
                                    search_job_id=search_job.id,
                                    product_id=product.id,
                                    article_id=article.id,
                                    is_icsr=analysis.get('is_icsr'),
                                    icsr_description=analysis.get('icsr_description', ''),
                                    ownership_excluded=analysis.get('ownership_analysis', {}).get('can_exclude'),
                                    exclusion_reason=analysis.get('ownership_analysis', {}).get('exclusion_reason', ''),
                                    minimum_criteria_available=analysis.get('minimum_criteria_available'),
                                    other_safety_info=analysis.get('safety_classification', {}).get('has_relevant_safety_info'),
                                    safety_info_justification=analysis.get('safety_classification', {}).get('justification', ''),
                                    confidence_score=analysis.get('confidence_score'),
                                    ai_analysis=analysis
                                )
                                db.session.add(search_result)
                                total_articles += 1
                        except Exception as e:
                            logger.error(f"Error processing article {pmid}: {str(e)}")
                            continue
                    
                    search_job.processed_products = idx + 1
                    db.session.commit()
                    
                except Exception as e:
                    logger.error(f"Error processing product {product.inn}: {str(e)}")
                    continue
            
            search_job.status = 'completed'
            search_job.total_articles = total_articles
            search_job.completed_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Batch search completed for job {job_id}. Total: {total_articles} articles")
            
        except Exception as e:
            logger.error(f"Error in background batch search for job {job_id}: {str(e)}")
            try:
                search_job = SearchJob.query.get(job_id)
                if search_job:
                    search_job.status = 'failed'
                    search_job.error_message = str(e)
                    db.session.commit()
            except:
                pass


@api_bp.route('/search/batch', methods=['POST'])
def execute_batch_search():
    """Execute batch search for multiple products (async background processing)"""
    try:
        data = request.get_json()
        
        product_ids = data.get('product_ids', [])
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        if not product_ids:
            products = Product.query.all()
        else:
            products = Product.query.filter(Product.id.in_(product_ids)).all()
        
        if not products:
            return jsonify({
                'success': False,
                'error': 'No products found'
            }), 404
        
        # Create search job
        search_job = SearchJob(
            job_type='batch',
            status='running',
            date_from=datetime.strptime(date_from, '%Y-%m-%d').date() if date_from else None,
            date_to=datetime.strptime(date_to, '%Y-%m-%d').date() if date_to else None,
            total_products=len(products),
            processed_products=0,
            total_articles=0
        )
        db.session.add(search_job)
        db.session.commit()
        
        job_id = search_job.id
        
        logger.info(f"Created batch search job {job_id} for {len(products)} products")
        
        # Start background thread
        thread = threading.Thread(
            target=process_batch_search_background,
            args=(current_app._get_current_object(), job_id, product_ids, date_from, date_to),
            daemon=True
        )
        thread.start()
        
        logger.info(f"Background thread started for batch job {job_id}")
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'status': 'running',
            'total_products': len(products),
            'message': f'Batch search started for {len(products)} products. Use /api/search/jobs/{job_id} to check progress.'
        }), 202
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error starting batch search: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/search/jobs', methods=['GET'])
def get_search_jobs():
    """Get all search jobs"""
    try:
        jobs = SearchJob.query.order_by(SearchJob.created_at.desc()).all()
        return jsonify({
            'success': True,
            'data': [job.to_dict() for job in jobs],
            'count': len(jobs)
        })
    except Exception as e:
        logger.error(f"Error fetching search jobs: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/search/jobs/<int:job_id>', methods=['GET'])
def get_search_job(job_id):
    """Get a specific search job"""
    try:
        job = SearchJob.query.get_or_404(job_id)
        return jsonify({
            'success': True,
            'data': job.to_dict()
        })
    except Exception as e:
        logger.error(f"Error fetching search job {job_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 404


@api_bp.route('/search/jobs/<int:job_id>/results', methods=['GET'])
def get_search_results(job_id):
    """Get results for a specific search job"""
    try:
        job = SearchJob.query.get_or_404(job_id)
        results = SearchResult.query.filter_by(search_job_id=job_id).all()
        
        return jsonify({
            'success': True,
            'job': job.to_dict(),
            'results': [r.to_dict(include_relations=True) for r in results],
            'count': len(results)
        })
    except Exception as e:
        logger.error(f"Error fetching search results for job {job_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/search/results/<int:result_id>', methods=['PUT'])
def update_search_result(result_id):
    """Update a search result (for manual review)"""
    try:
        result = SearchResult.query.get_or_404(result_id)
        data = request.get_json()
        
        # Update fields
        if 'is_icsr' in data:
            result.is_icsr = data['is_icsr']
        if 'icsr_description' in data:
            result.icsr_description = data['icsr_description']
        if 'ownership_excluded' in data:
            result.ownership_excluded = data['ownership_excluded']
        if 'exclusion_reason' in data:
            result.exclusion_reason = data['exclusion_reason']
        if 'other_safety_info' in data:
            result.other_safety_info = data['other_safety_info']
        if 'safety_info_justification' in data:
            result.safety_info_justification = data['safety_info_justification']
        if 'reviewed_by' in data:
            result.reviewed_by = data['reviewed_by']
        if 'qc_by' in data:
            result.qc_by = data['qc_by']
        if 'comments' in data:
            result.comments = data['comments']
        
        db.session.commit()
        
        logger.info(f"Updated search result {result_id}")
        
        return jsonify({
            'success': True,
            'data': result.to_dict(include_relations=True),
            'message': 'Search result updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating search result {result_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

