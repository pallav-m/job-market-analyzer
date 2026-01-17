"""
Base Scraper - Step 6.1
Abstract base class for all job scrapers
"""

import time
import random
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import hashlib

class BaseScraper(ABC):
    """Abstract base class for job scrapers"""
    
    def __init__(self, source_name: str, rate_limit: float = 2.0):
        """
        Initialize scraper
        
        Args:
            source_name: Name of the job board (e.g., "indeed", "linkedin")
            rate_limit: Seconds to wait between requests
        """
        self.source_name = source_name
        self.rate_limit = rate_limit
        self.session = self._create_session()
        self.jobs_scraped = []
    
    def _create_session(self):
        """Create HTTP session with headers"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        return session
    
    def _fetch_page(self, url: str, max_retries: int = 3) -> Optional[str]:
        """
        Fetch HTML content from URL with retry logic
        
        Args:
            url: URL to fetch
            max_retries: Number of retry attempts
            
        Returns:
            HTML content or None if failed
        """
        for attempt in range(max_retries):
            try:
                # Rate limiting
                time.sleep(self.rate_limit + random.uniform(0, 1))
                
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 429:
                    # Rate limited - wait longer
                    wait_time = (attempt + 1) * 10
                    print(f"   ⚠️  Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"   ⚠️  Status {response.status_code} for {url}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ⚠️  Request error (attempt {attempt+1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
        
        return None
    
    def _parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content"""
        return BeautifulSoup(html, 'html.parser')
    
    def _generate_job_id(self, job_title: str, company: str, location: str) -> str:
        """Generate unique job ID"""
        content = f"{self.source_name}_{job_title}_{company}_{location}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    @abstractmethod
    def scrape_jobs(self, job_title: str, location: str, num_pages: int = 3) -> List[Dict]:
        """
        Scrape jobs for given search criteria
        Must be implemented by subclasses
        
        Args:
            job_title: Job title to search for
            location: Location to search in
            num_pages: Number of pages to scrape
            
        Returns:
            List of job dictionaries
        """
        pass
    
    @abstractmethod
    def _parse_job_card(self, card_element) -> Optional[Dict]:
        """
        Parse individual job card from search results
        Must be implemented by subclasses
        
        Args:
            card_element: BeautifulSoup element containing job card
            
        Returns:
            Job dictionary or None if parsing failed
        """
        pass
    
    def get_scraped_jobs(self) -> List[Dict]:
        """Get all scraped jobs"""
        return self.jobs_scraped
    
    def clear_scraped_jobs(self):
        """Clear scraped jobs list"""
        self.jobs_scraped = []


# Self-test
if __name__ == "__main__":
    print("🧪 Testing Base Scraper...")
    
    # Test session creation
    class TestScraper(BaseScraper):
        def scrape_jobs(self, job_title, location, num_pages=1):
            return []
        
        def _parse_job_card(self, card_element):
            return None
    
    scraper = TestScraper("test_source")
    
    print("\n1️⃣ Test: Session Creation")
    print(f"   ✅ Session created: {scraper.session is not None}")
    print(f"   ✅ User-Agent set: {'User-Agent' in scraper.session.headers}")
    
    print("\n2️⃣ Test: Text Cleaning")
    dirty_text = "  Job   Title   with    extra   spaces  "
    clean = scraper._clean_text(dirty_text)
    print(f"   ✅ Cleaned: '{clean}'")
    
    print("\n3️⃣ Test: Job ID Generation")
    job_id = scraper._generate_job_id("Financial Analyst", "HDFC Bank", "Mumbai")
    print(f"   ✅ Generated ID: {job_id}")
    
    print("\n" + "="*50)
    print("🎉 BASE SCRAPER TEST PASSED!")
    print("="*50)
