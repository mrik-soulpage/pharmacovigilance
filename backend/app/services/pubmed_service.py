"""
PubMed service for searching and retrieving articles
"""
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from Bio import Entrez

import requests
from bs4 import BeautifulSoup

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
        
        # Configure Entrez with required parameters
        Entrez.email = email
        Entrez.tool = "PharmaVigilanceLiteratureMonitoring"  # Required by NCBI
        if api_key:
            Entrez.api_key = api_key
        
        logger.info(f"PubMed service initialized with email: {email}, API key: {'Set' if api_key else 'Not set'}")
    
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
            date_from: Start date (YYYY/MM/DD or YYYY-MM-DD)
            date_to: End date (YYYY/MM/DD or YYYY-MM-DD)
            max_results: Maximum number of results to return
            
        Returns:
            List of PMIDs
        """
        try:
            self._rate_limit_wait()
            
            # Build date range if provided
            date_range = ""
            if date_from and date_to:
                # PubMed accepts same dates for single-day searches
                date_range = f" AND ({date_from}[PDAT]:{date_to}[PDAT])"
                if date_from == date_to:
                    logger.info(f"Searching for articles published on single date: {date_from}")
            elif date_from:
                # If only date_from is provided, search from that date onwards
                date_range = f" AND ({date_from}[PDAT]:3000[PDAT])"
            elif date_to:
                # If only date_to is provided, search up to that date
                date_range = f" AND (1900[PDAT]:{date_to}[PDAT])"
            
            full_query = query + date_range
            logger.info(f"Searching PubMed with query: {full_query}")
            logger.info(f"Using email: {Entrez.email}, tool: {Entrez.tool}")
            
            # Execute search with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    handle = Entrez.esearch(
                        db="pubmed",
                        term=full_query,
                        retmax=max_results,
                        sort="relevance"
                    )
                    record = Entrez.read(handle)
                    handle.close()
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed, retrying... Error: {str(e)}")
                        time.sleep(2)  # Wait 2 seconds before retry
                    else:
                        raise

            pmids = record.get("IdList", [])
            logger.info(f"Found {len(pmids)} articles")
            
            return pmids
            # return [40746504]
            # return [40967794]
            
        except Exception as e:
            logger.error(f"Error searching PubMed: {str(e)}")
            logger.error(f"Query attempted: {full_query if 'full_query' in locals() else 'N/A'}")
            logger.error(f"Email configured: {Entrez.email}")
            logger.error(f"API key configured: {'Yes' if Entrez.api_key else 'No'}")
            
            # Provide more helpful error message
            if "500" in str(e):
                logger.error("PubMed returned HTTP 500 - this often means:")
                logger.error("1. The query is malformed or too complex")
                logger.error("2. Date range issues (future dates, invalid format)")
                logger.error("3. PubMed server is temporarily unavailable")
                logger.error("Try: Simplifying the query or using a different date range")
            
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
            
            # # Extract abstract
            # abstract_parts = article.get("Abstract", {}).get("AbstractText", [])
            # if isinstance(abstract_parts, list):
            #     abstract = " ".join([str(part) for part in abstract_parts])
            # else:
            #     abstract = str(abstract_parts) if abstract_parts else ""
            
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

            abstract_flag = False
            if pmcid == "":
                abstract_flag = True
            else:
                url = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"

                try:
                    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
                    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
                    html_content = response.text

                    soup = BeautifulSoup(html_content, 'html.parser')

                    abstract = soup.get_text(separator='\n', strip=True)

                except Exception as e:
                    logger.error(f"Error fetching article details for PMID {pmid}: {str(e)}")
                    abstract_flag = True
                    return None

            if abstract_flag:
                # Extract abstract
                abstract_parts = article.get("Abstract", {}).get("AbstractText", [])
                if isinstance(abstract_parts, list):
                    abstract = " ".join([str(part) for part in abstract_parts])
                else:
                    abstract = str(abstract_parts) if abstract_parts else ""
            
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

