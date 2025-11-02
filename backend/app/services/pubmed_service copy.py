"""
PubMed service for searching and retrieving articles
"""
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from Bio import Entrez

logger = logging.getLogger(__name__)


class PubMedService:
    """Service for interacting with PubMed API"""
    
    def __init__(self, api_key: str = None, email: str = "user@example.com", rate_limit: int = 10):
        """
        Initialize PubMed service
        
        Args:
            api_key: PubMed API key (optional, increases rate limit)
            email: Email for Entrez (required by NCBI)
            rate_limit: Maximum requests per second
        """
        self.api_key = api_key
        self.email = email
        self.rate_limit = rate_limit
        self.last_request_time = 0
        
        # Configure Entrez
        Entrez.email = email
        if api_key:
            Entrez.api_key = api_key
    
    def _rate_limit_wait(self):
        """Enforce rate limiting"""
        if self.rate_limit > 0:
            min_interval = 1.0 / self.rate_limit
            elapsed = time.time() - self.last_request_time
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()
    
    def search(
        self,
        query: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        max_results: int = 100
    ) -> List[str]:
        """
        Search PubMed for articles
        
        Args:
            query: Search query string
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            max_results: Maximum number of results to return
            
        Returns:
            List of PMIDs
        """
        try:
            self._rate_limit_wait()
            
            # Build date range if provided
            date_range = ""
            if date_from and date_to:
                date_range = f" AND ({date_from}[PDAT]:{date_to}[PDAT])"
            
            full_query = query + date_range
            logger.info(f"Searching PubMed: {full_query}")
            
            # Execute search
            handle = Entrez.esearch(
                db="pubmed",
                term=full_query,
                retmax=max_results,
                sort="relevance"
            )
            record = Entrez.read(handle)
            handle.close()

            print("\n\nRecord: ", record, "\n\n")
            
            pmids = record.get("IdList", [])
            logger.info(f"Found {len(pmids)} articles")
            
            # return pmids
            return [40746504]
            
        except Exception as e:
            logger.error(f"Error searching PubMed: {str(e)}")
            raise
    
    def fetch_article_details(self, pmid: str) -> Optional[Dict]:
        """
        Fetch detailed information for a single article
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Dictionary with article details
        """
        try:
            self._rate_limit_wait()
            
            logger.info(f"Fetching details for PMID: {pmid}")
            
            # Fetch article details
            handle = Entrez.efetch(
                db="pubmed",
                id=pmid,
                rettype="medline",
                retmode="xml"
            )
            records = Entrez.read(handle)
            handle.close()
            
            if not records.get("PubmedArticle"):
                logger.warning(f"No data found for PMID: {pmid}")
                return None
            
            article_data = records["PubmedArticle"][0]
            medline_citation = article_data.get("MedlineCitation", {})
            article = medline_citation.get("Article", {})
            
            # Extract article information
            title = article.get("ArticleTitle", "")
            
            # Extract abstract
            abstract_parts = article.get("Abstract", {}).get("AbstractText", [])
            if isinstance(abstract_parts, list):
                abstract = " ".join([str(part) for part in abstract_parts])
            else:
                abstract = str(abstract_parts) if abstract_parts else ""
            
            # Extract authors
            author_list = article.get("AuthorList", [])
            authors = []
            first_author = ""
            for author in author_list:
                last_name = author.get("LastName", "")
                initials = author.get("Initials", "")
                if last_name:
                    author_str = f"{last_name} {initials}".strip()
                    authors.append(author_str)
                    if not first_author:
                        first_author = author_str
            
            # Extract journal information
            journal = article.get("Journal", {})
            journal_title = journal.get("Title", "")
            
            # Extract publication date
            pub_date = journal.get("JournalIssue", {}).get("PubDate", {})
            pub_year = pub_date.get("Year", "")
            
            # Extract article IDs
            article_ids = article_data.get("PubmedData", {}).get("ArticleIdList", [])
            pmcid = ""
            doi = ""
            for article_id in article_ids:
                id_type = article_id.attributes.get("IdType", "")
                if id_type == "pmc":
                    pmcid = str(article_id)
                elif id_type == "doi":
                    doi = str(article_id)
            
            # Extract create date
            date_created = medline_citation.get("DateCreated", {})
            create_date = None
            if date_created:
                try:
                    year = int(date_created.get("Year", 0))
                    month = int(date_created.get("Month", 1))
                    day = int(date_created.get("Day", 1))
                    create_date = datetime(year, month, day).date()
                except (ValueError, TypeError):
                    pass
            
            # Build citation
            citation = self._build_citation(
                first_author,
                journal_title,
                pub_year,
                article.get("Pagination", {}).get("MedlinePgn", "")
            )
            
            result = {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "authors": "; ".join(authors),
                "first_author": first_author,
                "journal": journal_title,
                "publication_year": int(pub_year) if pub_year else None,
                "create_date": create_date,
                "pmcid": pmcid,
                "doi": doi,
                "citation": citation,
                "full_text_available": bool(pmcid),  # PMC articles typically have full text
            }
            print("\n\nResult: ", result, "\n\n")
            
            logger.info(f"Successfully fetched details for PMID: {pmid}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching article details for PMID {pmid}: {str(e)}")
            return None
    
    def fetch_multiple_articles(self, pmids: List[str]) -> List[Dict]:
        """
        Fetch details for multiple articles
        
        Args:
            pmids: List of PubMed IDs
            
        Returns:
            List of article detail dictionaries
        """
        articles = []
        for pmid in pmids:
            article = self.fetch_article_details(pmid)
            if article:
                articles.append(article)
        return articles
    
    def _build_citation(
        self,
        first_author: str,
        journal: str,
        year: str,
        pages: str
    ) -> str:
        """Build citation string"""
        parts = []
        if first_author:
            parts.append(f"{first_author} et al.")
        if journal:
            parts.append(journal)
        if year:
            parts.append(f"{year}")
        if pages:
            parts.append(f"{pages}")
        
        return ". ".join(parts) + "." if parts else ""
    
    def test_connection(self) -> bool:
        """
        Test PubMed API connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            pmids = self.search("aspirin", max_results=1)
            return len(pmids) > 0
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False

