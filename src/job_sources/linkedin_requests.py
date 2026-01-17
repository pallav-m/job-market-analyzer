"""
LinkedIn Requests-Based Scraper - Better Performance
Uses requests + BeautifulSoup instead of Selenium for faster, more reliable scraping
Outputs to existing database schema
"""

import sys
from pathlib import Path
import time
import random
import hashlib

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import quote
from datetime import datetime

class LinkedInRequestsScraper:
    """
    Enhanced LinkedIn scraper using requests (faster than Selenium)
    Compatible with existing database schema
    """
    
    def __init__(self, country: str = "in", headless: bool = True):
        """
        Initialize scraper
        
        Args:
            country: 'in' for India, 'com' for USA, 'uk' for UK
            headless: Included for compatibility (not used in requests)
        """
        self.country = country
        self.base_url = "https://www.linkedin.com"
        
        # Set location country for database
        if country == "in":
            self.location_country = "India"
        elif country == "uk":
            self.location_country = "UK"
        else:
            self.location_country = "USA"
        
        # Headers to mimic browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        self.jobs_scraped = []
    
    def scrape_jobs(self, job_title: str, location: str, num_pages: int = 3, max_jobs: int = 75) -> List[Dict]:
        """
        Scrape jobs from LinkedIn using requests
        
        Args:
            job_title: Job title to search
            location: Location name
            num_pages: Number of pages (25 jobs per page)
            max_jobs: Maximum jobs to collect
            
        Returns:
            List of job dictionaries matching existing schema
        """
        print(f"🔍 Scraping LinkedIn (requests): '{job_title}' in '{location}'")
        print(f"   Target: {num_pages} pages, max {max_jobs} jobs\n")
        
        jobs = []
        
        try:
            for page in range(num_pages):
                if len(jobs) >= max_jobs:
                    print(f"   ✅ Reached target of {max_jobs} jobs\n")
                    break
                
                start = page * 25
                
                # Get job cards from search page
                url = self._build_search_url(job_title, location, start)
                
                print(f"   📄 Page {page + 1}/{num_pages}...")
                
                soup = self._get_with_retry(url)
                
                if not soup:
                    print(f"   ⚠️  Failed to load page, stopping...")
                    break
                
                page_jobs = self._extract_job_cards(soup, location)
                
                if len(page_jobs) == 0:
                    print(f"   ⚠️  No jobs found, stopping...")
                    break
                
                # Fetch full descriptions for each job
                jobs_with_desc = self._fetch_descriptions(page_jobs, max_jobs - len(jobs))
                
                jobs.extend(jobs_with_desc)
                print(f"   ✅ Extracted {len(jobs_with_desc)} jobs (total: {len(jobs)})")
                
                if page < num_pages - 1 and len(jobs) < max_jobs:
                    delay = random.uniform(3, 6)
                    time.sleep(delay)
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        finally:
            self.jobs_scraped.extend(jobs)
        
        print(f"\n   ✅ Total scraped: {len(jobs)} jobs\n")
        return jobs
    
    def _build_search_url(self, job_title: str, location: str, start: int) -> str:
        """Build LinkedIn job search URL"""
        keywords = quote(job_title)
        loc = quote(location)
        
        # Different domain for UK
        if self.country == "uk":
            domain = "https://uk.linkedin.com"
        else:
            domain = self.base_url
        
        url = f"{domain}/jobs-guest/jobs/api/seeMoreJobPostings/search"
        url += f"?keywords={keywords}&location={loc}&start={start}&sortBy=DD"
        
        return url
    
    def _get_with_retry(self, url: str, retries: int = 3, delay: int = 2) -> BeautifulSoup:
        """Get URL with retries"""
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            
            except requests.exceptions.Timeout:
                print(f"      ⚠️  Timeout (attempt {attempt + 1}/{retries}), retrying...")
                time.sleep(delay)
            
            except Exception as e:
                print(f"      ⚠️  Error: {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
        
        return None
    
    def _extract_job_cards(self, soup: BeautifulSoup, default_location: str) -> List[Dict]:
        """Extract job cards from search results page"""
        jobs = []
        
        try:
            divs = soup.find_all('div', class_='base-search-card__info')
            
            if not divs:
                # Try alternative selectors
                divs = soup.find_all('div', class_='job-search-card')
            
            for item in divs:
                job = self._parse_job_card(item, default_location)
                if job:
                    jobs.append(job)
        
        except Exception as e:
            print(f"      ⚠️  Error extracting cards: {e}")
        
        return jobs
    
    def _parse_job_card(self, item, default_location: str) -> Dict:
        """Parse individual job card"""
        try:
            # Extract title
            title_elem = item.find('h3')
            if not title_elem:
                return None
            
            title = title_elem.text.strip()
            
            # Extract company
            company_elem = item.find('a', class_='hidden-nested-link')
            if not company_elem:
                company_elem = item.find('h4', class_='base-search-card__subtitle')
            
            company = company_elem.text.strip().replace('\n', ' ') if company_elem else 'Unknown'
            
            # Extract location
            location_elem = item.find('span', class_='job-search-card__location')
            location = location_elem.text.strip() if location_elem else default_location
            
            # Extract job URL and ID
            parent_div = item.parent
            if parent_div and parent_div.has_attr('data-entity-urn'):
                entity_urn = parent_div['data-entity-urn']
                job_posting_id = entity_urn.split(':')[-1]
                job_url = f'https://www.linkedin.com/jobs/view/{job_posting_id}/'
            else:
                # Try to find link
                link = item.find('a', class_='base-card__full-link')
                if link and link.has_attr('href'):
                    job_url = link['href']
                else:
                    return None
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'job_url': job_url,
                'job_description': ''  # Will be filled later
            }
        
        except Exception as e:
            return None
    
    def _fetch_descriptions(self, job_cards: List[Dict], max_jobs: int) -> List[Dict]:
        """Fetch full job descriptions for each job card"""
        jobs_with_desc = []
        
        for i, job_card in enumerate(job_cards[:max_jobs], 1):
            try:
                print(f"      [{i}/{min(len(job_cards), max_jobs)}] Fetching: {job_card['title'][:40]}...")
                
                # Fetch job detail page
                soup = self._get_with_retry(job_card['job_url'])
                
                if not soup:
                    print(f"         ⚠️  Failed to fetch description")
                    continue
                
                # Extract description
                description = self._extract_description(soup)
                
                if not description or len(description) < 100:
                    print(f"         ⚠️  Description too short ({len(description)} chars)")
                    description = f"Position: {job_card['title']} at {job_card['company']}. Location: {job_card['location']}."
                else:
                    print(f"         ✅ Got {len(description)} chars")
                
                # Convert to schema format
                job = self._to_schema_format(job_card, description)
                jobs_with_desc.append(job)
                
                # Delay between requests
                time.sleep(random.uniform(1, 2))
            
            except Exception as e:
                print(f"         ⚠️  Error: {e}")
                continue
        
        return jobs_with_desc
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract job description from job detail page"""
        try:
            # Find description div
            div = soup.find('div', class_='description__text description__text--rich')
            
            if not div:
                # Try alternative selectors
                div = soup.find('div', class_='show-more-less-html__markup')
            
            if not div:
                return ""
            
            # Remove unwanted elements
            for element in div.find_all(['span', 'a']):
                element.decompose()
            
            # Replace bullet points
            for ul in div.find_all('ul'):
                for li in ul.find_all('li'):
                    li.insert(0, '- ')
            
            # Get text
            text = div.get_text(separator='\n').strip()
            
            # Clean up
            text = text.replace('\n\n', '\n')
            text = text.replace('::marker', '-')
            text = text.replace('-\n', '- ')
            text = text.replace('Show less', '').replace('Show more', '')
            text = text.strip()
            
            return text
        
        except Exception as e:
            return ""
    
    def _to_schema_format(self, job_card: Dict, description: str) -> Dict:
        """Convert to existing database schema format"""
        job_id = self._generate_job_id(
            job_card['title'],
            job_card['company'],
            job_card['location']
        )
        
        category = self._categorize_job(job_card['title'], description)
        
        return {
            'job_id': job_id,
            'job_title': job_card['title'],
            'company_name': job_card['company'],
            'location_city': job_card['location'],
            'location_country': self.location_country,
            'job_category': category,
            'job_description': description,
            'job_url': job_card['job_url'],
            'source': f'linkedin_requests_{self.country}'
        }
    
    def _generate_job_id(self, title: str, company: str, location: str) -> str:
        """Generate unique job ID"""
        content = f"linkedin_{title}_{company}_{location}".lower()
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _categorize_job(self, title: str, description: str) -> str:
        """Categorize job based on title and description"""
        text = (title + " " + description).lower()
        
        if any(kw in text for kw in ['fintech', 'blockchain', 'crypto', 'payment', 'digital banking']):
            return 'fintech'
        
        if any(kw in text for kw in ['data analyst', 'business analyst', 'analytics', 'data science', 'bi analyst']):
            return 'analytics_data'
        
        if any(kw in text for kw in ['risk', 'compliance', 'audit', 'regulatory', 'aml', 'kyc']):
            return 'risk_compliance'
        
        return 'traditional_finance'
    
    def close(self):
        """Close method for compatibility (not needed for requests)"""
        pass


# Test
if __name__ == "__main__":
    print("🧪 Testing LinkedIn Requests Scraper...\n")
    
    scraper = LinkedInRequestsScraper(country="in")
    
    jobs = scraper.scrape_jobs(
        job_title="Financial Analyst",
        location="Mumbai",
        num_pages=2,
        max_jobs=20
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
            print(f"      Description: {len(job['job_description'])} chars")
            print(f"      URL: {job['job_url'][:50]}...\n")
        
        print(f"📈 Statistics:")
        print(f"   Total: {len(jobs)}")
        print(f"   Avg description length: {sum(len(j['job_description']) for j in jobs) / len(jobs):.0f} chars")
        print(f"   Companies: {len(set(j['company_name'] for j in jobs))}")
