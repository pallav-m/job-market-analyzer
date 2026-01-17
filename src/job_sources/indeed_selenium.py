"""
Indeed Selenium Scraper - Production Version
Scrapes real job postings using browser automation
"""

import sys
from pathlib import Path
import time
import random
import re

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

class IndeedSeleniumScraper:
    """Production-ready Indeed scraper using Selenium"""
    
    def __init__(self, country: str = "in", headless: bool = True):
        """
        Initialize scraper
        
        Args:
            country: 'in' for India, 'com' for USA, 'co.uk' for UK
            headless: Run browser in background (True) or visible (False)
        """
        self.country = country
        self.headless = headless
        
        # Set base URL
        if country == "in":
            self.base_url = "https://in.indeed.com"
            self.location_country = "India"
        elif country == "com":
            self.base_url = "https://www.indeed.com"
            self.location_country = "USA"
        elif country == "co.uk":
            self.base_url = "https://uk.indeed.com"
            self.location_country = "UK"
        else:
            self.base_url = "https://www.indeed.com"
            self.location_country = "USA"
        
        self.driver = None
        self.wait = None
        self.jobs_scraped = []
    
    def _init_driver(self):
        """Initialize Chrome driver"""
        if self.driver is not None:
            return
        
        print("🌐 Starting Chrome browser...")
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set user agent
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
        print("✅ Browser ready\n")
    
    def scrape_jobs(self, job_title: str, location: str, num_pages: int = 5, max_jobs: int = 100) -> List[Dict]:
        """
        Scrape jobs from Indeed
        
        Args:
            job_title: Job title to search (e.g., "Financial Analyst")
            location: Location (e.g., "Mumbai", "New York")
            num_pages: Number of pages to scrape (10 jobs per page)
            max_jobs: Maximum number of jobs to collect
            
        Returns:
            List of job dictionaries
        """
        self._init_driver()
        
        print(f"🔍 Scraping Indeed.{self.country}: '{job_title}' in '{location}'")
        print(f"   Target: {num_pages} pages, max {max_jobs} jobs\n")
        
        jobs = []
        
        try:
            for page in range(num_pages):
                if len(jobs) >= max_jobs:
                    print(f"   ✅ Reached target of {max_jobs} jobs\n")
                    break
                
                start = page * 10
                url = self._build_url(job_title, location, start)
                
                print(f"   📄 Page {page + 1}/{num_pages}...")
                
                # Navigate to page
                self.driver.get(url)
                time.sleep(random.uniform(2, 4))  # Random delay
                
                # Extract jobs from page
                page_jobs = self._extract_jobs_from_page(location)
                
                if len(page_jobs) == 0:
                    print(f"   ⚠️  No jobs found on page {page + 1}, stopping...")
                    break
                
                jobs.extend(page_jobs)
                print(f"   ✅ Extracted {len(page_jobs)} jobs (total: {len(jobs)})")
                
                # Random delay between pages
                if page < num_pages - 1:
                    delay = random.uniform(3, 6)
                    time.sleep(delay)
        
        except Exception as e:
            print(f"   ❌ Error during scraping: {e}")
        
        finally:
            self.jobs_scraped.extend(jobs)
        
        print(f"\n   ✅ Total scraped: {len(jobs)} jobs\n")
        return jobs
    
    def _build_url(self, job_title: str, location: str, start: int) -> str:
        """Build Indeed search URL"""
        params = {
            'q': job_title,
            'l': location,
            'start': start,
            'sort': 'date'
        }
        query = urllib.parse.urlencode(params)
        return f"{self.base_url}/jobs?{query}"
    
    def _extract_jobs_from_page(self, default_location: str) -> List[Dict]:
        """Extract all jobs from current page"""
        jobs = []
        
        try:
            # Wait for job cards to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.job_seen_beacon, td.resultContent")))
            
            # Find all job cards
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.job_seen_beacon, td.resultContent")
            
            for card in job_cards:
                job = self._parse_job_card(card, default_location)
                if job:
                    jobs.append(job)
        
        except TimeoutException:
            print(f"      ⚠️  Timeout waiting for job cards")
        except Exception as e:
            print(f"      ⚠️  Error extracting jobs: {e}")
        
        return jobs
    
    def _parse_job_card(self, card, default_location: str) -> Dict:
        """Parse individual job card"""
        try:
            # Extract title
            try:
                title_elem = card.find_element(By.CSS_SELECTOR, "h2.jobTitle span")
                job_title = title_elem.text.strip()
            except:
                title_elem = card.find_element(By.CSS_SELECTOR, "h2.jobTitle")
                job_title = title_elem.text.strip()
            
            if not job_title:
                return None
            
            # Extract company
            try:
                company_elem = card.find_element(By.CSS_SELECTOR, "span.companyName")
                company = company_elem.text.strip()
            except:
                company = "Unknown"
            
            # Extract location
            try:
                loc_elem = card.find_element(By.CSS_SELECTOR, "div.companyLocation")
                job_location = loc_elem.text.strip()
            except:
                job_location = default_location
            
            # Extract snippet (short description)
            try:
                snippet_elem = card.find_element(By.CSS_SELECTOR, "div.job-snippet")
                description = snippet_elem.text.strip()
            except:
                description = ""
            
            # Extract job URL
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
                job_url = link_elem.get_attribute("href")
            except:
                job_url = ""
            
            # Generate job ID
            job_id = self._generate_job_id(job_title, company, job_location)
            
            # Categorize job (simple heuristic)
            category = self._categorize_job(job_title, description)
            
            # Build job dictionary
            job = {
                'job_id': job_id,
                'job_title': job_title,
                'company_name': company,
                'location_city': job_location,
                'location_country': self.location_country,
                'job_category': category,
                'job_description': description,
                'job_url': job_url,
                'source': f'indeed_{self.country}'
            }
            
            return job
        
        except Exception as e:
            # Skip job if parsing fails
            return None
    
    def _generate_job_id(self, title: str, company: str, location: str) -> str:
        """Generate unique job ID"""
        content = f"indeed_{title}_{company}_{location}".lower()
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _categorize_job(self, title: str, description: str) -> str:
        """Categorize job based on title and description"""
        text = (title + " " + description).lower()
        
        # Fintech keywords
        if any(kw in text for kw in ['fintech', 'blockchain', 'crypto', 'payment', 'digital bank']):
            return 'fintech'
        
        # Analytics/Data keywords
        if any(kw in text for kw in ['data analyst', 'business analyst', 'analytics', 'data science']):
            return 'analytics_data'
        
        # Risk/Compliance keywords
        if any(kw in text for kw in ['risk', 'compliance', 'audit', 'regulatory']):
            return 'risk_compliance'
        
        # Default to traditional finance
        return 'traditional_finance'
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("✅ Browser closed")
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.close()

    def _fetch_full_description(self, job_url: str) -> str:
        """
        Fetch full job description from job detail page
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Full job description or empty string if failed
        """
        try:
            # Navigate to job detail page
            self.driver.get(job_url)
            time.sleep(random.uniform(1, 2))
            
            # Wait for job description to load
            desc_elem = self.wait.until(
                EC.presence_of_element_located((By.ID, "jobDescriptionText"))
            )
            
            # Get full description text
            full_description = desc_elem.text.strip()
            
            return full_description
        
        except TimeoutException:
            # Try alternative selector
            try:
                desc_elem = self.driver.find_element(By.CLASS_NAME, "jobsearch-jobDescriptionText")
                return desc_elem.text.strip()
            except:
                return ""
        
        except Exception as e:
            return ""



# Self-test
if __name__ == "__main__":
    print("🧪 Testing Indeed Selenium Scraper...\n")
    
    # Test with India Indeed (change to "com" for USA, "co.uk" for UK)
    scraper = IndeedSeleniumScraper(country="in", headless=True)
    
    # Scrape Financial Analyst jobs in Mumbai
    jobs = scraper.scrape_jobs(
        job_title="Financial Analyst",
        location="Mumbai",
        num_pages=2,  # Just 2 pages for testing (20 jobs)
        max_jobs=20
    )
    
    scraper.close()
    
    # Show results
    print("\n" + "="*60)
    print(f"🎉 SCRAPING COMPLETE: {len(jobs)} jobs")
    print("="*60)
    
    if len(jobs) > 0:
        print("\n📊 Sample Job:\n")
        sample = jobs[0]
        print(f"   Title: {sample['job_title']}")
        print(f"   Company: {sample['company_name']}")
        print(f"   Location: {sample['location_city']}")
        print(f"   Category: {sample['job_category']}")
        print(f"   Description: {sample['job_description'][:150]}...")
        print(f"   URL: {sample['job_url'][:60]}...")
        
        print(f"\n   Total jobs: {len(jobs)}")
        print(f"   Unique companies: {len(set(j['company_name'] for j in jobs))}")
        print(f"   Categories: {set(j['job_category'] for j in jobs)}")
