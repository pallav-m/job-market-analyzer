"""
LinkedIn Selenium Scraper - Production Version
Scrapes job postings from LinkedIn
"""

import sys
from pathlib import Path
import time
import random

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import List, Dict
import urllib.parse
import hashlib

class LinkedInSeleniumScraper:
    """LinkedIn job scraper using Selenium"""
    
    def __init__(self, country: str = "in", headless: bool = True):
        """
        Initialize scraper
        
        Args:
            country: 'in' for India, 'com' for USA/Global
            headless: Run browser in background
        """
        self.country = country
        self.headless = headless
        
        # LinkedIn uses location codes
        if country == "in":
            self.base_url = "https://www.linkedin.com"
            self.location_country = "India"
            self.location_codes = {
                'Mumbai': '102713980',
                'Bangalore': '105214831',
                'Delhi': '106155005',
                'Hyderabad': '106808692',
                'Pune': '106808691'
            }
        else:
            self.base_url = "https://www.linkedin.com"
            self.location_country = "USA"
            self.location_codes = {
                'New York': '102571732',
                'San Francisco': '102277331',
                'Chicago': '103112676',
                'Boston': '100293800',
                'Los Angeles': '102448103'
            }
        
        self.driver = None
        self.wait = None
        self.jobs_scraped = []
    
    def _init_driver(self):
        """Initialize Chrome driver"""
        if self.driver is not None:
            return
        
        print("🌐 Starting Chrome browser for LinkedIn...")
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # LinkedIn-specific user agent
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
        print("✅ Browser ready\n")
    
    def scrape_jobs(self, job_title: str, location: str, num_pages: int = 3, max_jobs: int = 75) -> List[Dict]:
        """
        Scrape jobs from LinkedIn
        
        Args:
            job_title: Job title to search
            location: Location name (e.g., "Mumbai", "New York")
            num_pages: Number of pages to scrape (25 jobs per page)
            max_jobs: Maximum jobs to collect
            
        Returns:
            List of job dictionaries
        """
        self._init_driver()
        
        print(f"🔍 Scraping LinkedIn: '{job_title}' in '{location}'")
        print(f"   Target: {num_pages} pages, max {max_jobs} jobs\n")
        
        jobs = []
        
        try:
            # LinkedIn shows 25 jobs per page
            for page in range(num_pages):
                if len(jobs) >= max_jobs:
                    print(f"   ✅ Reached target of {max_jobs} jobs\n")
                    break
                
                start = page * 25
                url = self._build_url(job_title, location, start)
                
                print(f"   📄 Page {page + 1}/{num_pages}...")
                
                self.driver.get(url)
                time.sleep(random.uniform(3, 5))  # LinkedIn needs more time
                
                # Handle "See more jobs" button if present
                self._handle_see_more_button()
                
                page_jobs = self._extract_jobs_from_page(location)
                
                if len(page_jobs) == 0:
                    print(f"   ⚠️  No jobs found, stopping...")
                    break
                
                jobs.extend(page_jobs)
                print(f"   ✅ Extracted {len(page_jobs)} jobs (total: {len(jobs)})")
                
                if page < num_pages - 1 and len(jobs) < max_jobs:
                    delay = random.uniform(4, 7)  # Longer delay for LinkedIn
                    time.sleep(delay)
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        finally:
            self.jobs_scraped.extend(jobs)
        
        print(f"\n   ✅ Total scraped: {len(jobs)} jobs\n")
        return jobs
    
    def _build_url(self, job_title: str, location: str, start: int) -> str:
        """Build LinkedIn jobs URL"""
        # Get location code if available
        location_code = self.location_codes.get(location, '')
        
        params = {
            'keywords': job_title,
            'location': location,
            'start': start,
            'sortBy': 'DD'  # Sort by date (most recent)
        }
        
        if location_code:
            params['geoId'] = location_code
        
        query = urllib.parse.urlencode(params)
        return f"{self.base_url}/jobs/search?{query}"
    
    def _handle_see_more_button(self):
        """Click 'See more jobs' button if present"""
        try:
            see_more = self.driver.find_element(By.CSS_SELECTOR, "button.infinite-scroller__show-more-button")
            see_more.click()
            time.sleep(2)
        except:
            pass
    
    def _extract_jobs_from_page(self, default_location: str) -> List[Dict]:
        """Extract jobs from current page"""
        jobs = []
        
        try:
            # Wait for job cards
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.job-search-card, li.jobs-search-results__list-item")))
            
            # Find all job cards
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.job-search-card, li.jobs-search-results__list-item")
            
            for card in job_cards:
                job = self._parse_job_card(card, default_location)
                if job:
                    jobs.append(job)
        
        except TimeoutException:
            print(f"      ⚠️  Timeout waiting for job cards")
        except Exception as e:
            print(f"      ⚠️  Error: {e}")
        
        return jobs
    
    def _parse_job_card(self, card, default_location: str) -> Dict:
        """Parse individual job card"""
        try:
            # Extract title
            try:
                title_elem = card.find_element(By.CSS_SELECTOR, "h3.base-search-card__title, a.job-card-list__title")
                job_title = title_elem.text.strip()
            except:
                return None
            
            if not job_title:
                return None
            
            # Extract company
            try:
                company_elem = card.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle, a.job-card-container__company-name")
                company = company_elem.text.strip()
            except:
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, "a.hidden-nested-link")
                    company = company_elem.text.strip()
                except:
                    company = "Unknown"
            
            # Extract location
            try:
                loc_elem = card.find_element(By.CSS_SELECTOR, "span.job-search-card__location, span.job-card-container__metadata-item")
                job_location = loc_elem.text.strip()
            except:
                job_location = default_location
            
            # Extract job URL
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, "a.base-card__full-link, a.job-card-list__title")
                job_url = link_elem.get_attribute("href")
                # Clean up LinkedIn tracking parameters
                if '?' in job_url:
                    job_url = job_url.split('?')[0]
            except:
                job_url = ""
            
            # Extract description snippet (if available)
            try:
                desc_elem = card.find_element(By.CSS_SELECTOR, "p.job-search-card__snippet, div.job-card-list__snippet")
                description = desc_elem.text.strip()
            except:
                # LinkedIn often doesn't show snippets in search results
                description = f"Position: {job_title} at {company}. Location: {job_location}. View full details on LinkedIn."
            
            # Generate job ID
            job_id = self._generate_job_id(job_title, company, job_location)
            
            # Categorize
            category = self._categorize_job(job_title, description)
            
            job = {
                'job_id': job_id,
                'job_title': job_title,
                'company_name': company,
                'location_city': job_location,
                'location_country': self.location_country,
                'job_category': category,
                'job_description': description,
                'job_url': job_url,
                'source': f'linkedin_{self.country}'
            }
            
            return job
        
        except Exception as e:
            return None
    
    def _generate_job_id(self, title: str, company: str, location: str) -> str:
        """Generate unique job ID"""
        content = f"linkedin_{title}_{company}_{location}".lower()
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _categorize_job(self, title: str, description: str) -> str:
        """Categorize job"""
        text = (title + " " + description).lower()
        
        if any(kw in text for kw in ['fintech', 'blockchain', 'crypto', 'payment', 'digital banking']):
            return 'fintech'
        
        if any(kw in text for kw in ['data analyst', 'business analyst', 'analytics', 'data science', 'bi analyst']):
            return 'analytics_data'
        
        if any(kw in text for kw in ['risk', 'compliance', 'audit', 'regulatory', 'aml', 'kyc']):
            return 'risk_compliance'
        
        return 'traditional_finance'
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("✅ Browser closed")
    
    def __del__(self):
        """Cleanup"""
        self.close()


# Test
if __name__ == "__main__":
    print("🧪 Testing LinkedIn Scraper...\n")
    
    scraper = LinkedInSeleniumScraper(country="in", headless=True)
    
    jobs = scraper.scrape_jobs(
        job_title="Financial Analyst",
        location="Mumbai",
        num_pages=2,
        max_jobs=50
    )
    
    scraper.close()
    
    print("\n" + "="*60)
    print(f"🎉 SCRAPING COMPLETE: {len(jobs)} jobs")
    print("="*60)
    
    if len(jobs) > 0:
        print("\n📊 Sample Jobs:\n")
        for i, job in enumerate(jobs[:3], 1):
            print(f"   {i}. {job['job_title']}")
            print(f"      Company: {job['company_name']}")
            print(f"      Location: {job['location_city']}")
            print(f"      Category: {job['job_category']}")
            print(f"      Description: {job['job_description'][:100]}...")
            print(f"      URL: {job['job_url'][:50]}...\n")
        
        print(f"📈 Statistics:")
        print(f"   Total: {len(jobs)}")
        print(f"   Companies: {len(set(j['company_name'] for j in jobs))}")
        print(f"   Categories: {set(j['job_category'] for j in jobs)}")
