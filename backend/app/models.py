"""
Database models for Pharmacovigilance Literature Monitoring
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON

db = SQLAlchemy()


class Product(db.Model):
    """Product model - represents monitored pharmaceutical products"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    inn = db.Column(db.String(255), nullable=False, unique=True)
    search_strategy = db.Column(db.Text, nullable=False)
    is_eu_product = db.Column(db.Boolean, default=False)
    territories = db.Column(JSON)  # List of country codes
    dosage_forms = db.Column(JSON)  # List of dosage forms
    routes_of_administration = db.Column(JSON)  # List of routes
    marketing_status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    search_results = db.relationship('SearchResult', back_populates='product', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'inn': self.inn,
            'search_strategy': self.search_strategy,
            'is_eu_product': self.is_eu_product,
            'territories': self.territories,
            'dosage_forms': self.dosage_forms,
            'routes_of_administration': self.routes_of_administration,
            'marketing_status': self.marketing_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class SearchJob(db.Model):
    """Search job model - tracks batch search operations"""
    __tablename__ = 'search_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    job_type = db.Column(db.String(50))  # 'single' or 'batch'
    status = db.Column(db.String(50), default='pending')  # pending, running, completed, failed
    date_from = db.Column(db.Date)
    date_to = db.Column(db.Date)
    total_products = db.Column(db.Integer, default=0)
    processed_products = db.Column(db.Integer, default=0)
    total_articles = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    search_results = db.relationship('SearchResult', back_populates='search_job', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_type': self.job_type,
            'status': self.status,
            'date_from': self.date_from.isoformat() if self.date_from else None,
            'date_to': self.date_to.isoformat() if self.date_to else None,
            'total_products': self.total_products,
            'processed_products': self.processed_products,
            'total_articles': self.total_articles,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }


class Article(db.Model):
    """Article model - represents PubMed articles"""
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    pmid = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.Text)
    abstract = db.Column(db.Text)
    authors = db.Column(db.Text)
    first_author = db.Column(db.String(255))
    citation = db.Column(db.Text)
    journal = db.Column(db.String(255))
    publication_year = db.Column(db.Integer)
    create_date = db.Column(db.Date)
    pmcid = db.Column(db.String(50))
    nihms_id = db.Column(db.String(50))
    doi = db.Column(db.String(255))
    full_text_available = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    search_results = db.relationship('SearchResult', back_populates='article', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'pmid': self.pmid,
            'title': self.title,
            'abstract': self.abstract,
            'authors': self.authors,
            'first_author': self.first_author,
            'citation': self.citation,
            'journal': self.journal,
            'publication_year': self.publication_year,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'pmcid': self.pmcid,
            'nihms_id': self.nihms_id,
            'doi': self.doi,
            'full_text_available': self.full_text_available,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class SearchResult(db.Model):
    """Search result model - links articles to products and search jobs with AI analysis"""
    __tablename__ = 'search_results'
    
    id = db.Column(db.Integer, primary_key=True)
    search_job_id = db.Column(db.Integer, db.ForeignKey('search_jobs.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    
    # ICSR analysis
    is_icsr = db.Column(db.Boolean)
    icsr_description = db.Column(db.Text)
    ownership_excluded = db.Column(db.Boolean)
    exclusion_reason = db.Column(db.Text)
    is_duplicate = db.Column(db.Boolean, default=False)
    minimum_criteria_available = db.Column(db.Boolean)
    
    # Safety information
    other_safety_info = db.Column(db.Boolean)
    safety_info_justification = db.Column(db.Text)
    
    # AI analysis metadata
    confidence_score = db.Column(db.Float)
    ai_analysis = db.Column(JSON)  # Full AI response
    
    # Workflow tracking
    reviewed_by = db.Column(db.String(100))
    qc_by = db.Column(db.String(100))
    comments = db.Column(db.Text)
    date_sent_to_provider = db.Column(db.Date)
    icsr_code = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    search_job = db.relationship('SearchJob', back_populates='search_results')
    product = db.relationship('Product', back_populates='search_results')
    article = db.relationship('Article', back_populates='search_results')
    
    def to_dict(self, include_relations=False):
        result = {
            'id': self.id,
            'search_job_id': self.search_job_id,
            'product_id': self.product_id,
            'article_id': self.article_id,
            'is_icsr': self.is_icsr,
            'icsr_description': self.icsr_description,
            'ownership_excluded': self.ownership_excluded,
            'exclusion_reason': self.exclusion_reason,
            'is_duplicate': self.is_duplicate,
            'minimum_criteria_available': self.minimum_criteria_available,
            'other_safety_info': self.other_safety_info,
            'safety_info_justification': self.safety_info_justification,
            'confidence_score': self.confidence_score,
            'ai_analysis': self.ai_analysis,
            'reviewed_by': self.reviewed_by,
            'qc_by': self.qc_by,
            'comments': self.comments,
            'date_sent_to_provider': self.date_sent_to_provider.isoformat() if self.date_sent_to_provider else None,
            'icsr_code': self.icsr_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relations:
            result['product'] = self.product.to_dict() if self.product else None
            result['article'] = self.article.to_dict() if self.article else None
        
        return result


class Configuration(db.Model):
    """Configuration model - stores system configuration"""
    __tablename__ = 'configuration'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    encrypted = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': '***' if self.encrypted else self.value,
            'encrypted': self.encrypted,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

