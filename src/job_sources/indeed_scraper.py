"""
Indeed Scraper - Enhanced Version
Better anti-detection measures
"""

import sys
from pathlib import Path
import random
import time

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.job_sources.base_scraper import BaseScraper
import urllib.parse
from typing import List, Dict, Optional

class IndeedScraper(BaseScraper):
    """Scraper for Indeed job board with anti-detection"""
    
    # Rotate user agents
    USER_AGENTS = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    def __init__(self, country: str = "in"):
        """Initialize Indeed scraper with enhanced headers"""
        super().__init__(source_name="indeed", rate_limit=3.0)  # Slower rate
        
        self.country = country
        if country == "in":
            self.base_url = "https://in.indeed.com"
        elif country == "com":
            self.base_url = "https://www.indeed.com"
        elif country == "co.uk":
            self.base_url = "https://uk.indeed.com"
        else:
            self.base_url = "https://www.indeed.com"
        
        # Enhanced session headers
        self._update_session_headers()
    
    def _update_session_headers(self):
        """Update session with better headers"""
        self.session.headers.update({
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
    
    def _fetch_page(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Enhanced fetch with better delays"""
        for attempt in range(max_retries):
            try:
                # Rotate user agent
                self.session.headers['User-Agent'] = random.choice(self.USER_AGENTS)
                
                # Random delay (3-6 seconds)
                delay = self.rate_limit + random.uniform(1, 3)
                print(f"   ⏳ Waiting {delay:.1f}s...")
                time.sleep(delay)
                
                response = self.session.get(url, timeout=15, allow_redirects=True)
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 403:
                    print(f"   ⚠️  403 Forbidden - Indeed blocking scraper (attempt {attempt+1})")
                    if attempt < max_retries - 1:
                        wait = (attempt + 1) * 15  # 15, 30, 45 seconds
                        print(f"   ⏳ Backing off for {wait}s...")
                        time.sleep(wait)
                elif response.status_code == 429:
                    wait = (attempt + 1) * 20
                    print(f"   ⚠️  Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"   ⚠️  Status {response.status_code}")
                    
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(10)
        
        return None
    
    # ... rest of the methods stay the same as before ...
    def scrape_jobs(self, job_title: str, location: str, num_pages: int = 3) -> List[Dict]:
        """Scrape jobs from Indeed"""
        print(f"\n🔍 Scraping Indeed.{self.country}: '{job_title}' in '{location}'")
        
        jobs = []
        
        for page in range(num_pages):
            start = page * 10
            url = self._build_search_url(job_title, location, start)
            
            print(f"   📄 Page {page + 1}/{num_pages}...")
            
            html = self._fetch_page(url)
            if not html:
                print(f"   ⚠️  Failed to fetch page {page + 1}")
                continue
            
            page_jobs = self._parse_search_page(html, location)
            jobs.extend(page_jobs)
            
            print(f"   ✅ Found {len(page_jobs)} jobs on page {page + 1}")
            
            if len(page_jobs) == 0:
                print(f"   ℹ️  No more jobs found, stopping...")
                break
        
        self.jobs_scraped.extend(jobs)
        print(f"   ✅ Total jobs scraped: {len(jobs)}\n")
        
        return jobs
    
    def _build_search_url(self, job_title: str, location: str, start: int = 0) -> str:
        """Build Indeed search URL"""
        params = {
            'q': job_title,
            'l': location,
            'start': start,
            'sort': 'date'
        }
        query_string = urllib.parse.urlencode(params)
        return f"{self.base_url}/jobs?{query_string}"
    
    def _parse_search_page(self, html: str, location: str) -> List[Dict]:
        """Parse job listings from search results page"""
        soup = self._parse_html(html)
        jobs = []
        
        job_cards = soup.find_all('div', class_='job_seen_beacon') or \
                    soup.find_all('div', class_='cardOutline') or \
                    soup.find_all('td', class_='resultContent')
        
        for card in job_cards:
            job = self._parse_job_card(card, location)
            if job:
                jobs.append(job)
        
        return jobs
    
    def _parse_job_card(self, card_element, location: str) -> Optional[Dict]:
        """Parse individual job card"""
        try:
            title_elem = card_element.find('h2', class_='jobTitle') or \
                        card_element.find('a', class_='jcs-JobTitle')
            
            if not title_elem:
                return None
            
            job_title = self._clean_text(title_elem.get_text())
            
            company_elem = card_element.find('span', class_='companyName')
            company_name = self._clean_text(company_elem.get_text()) if company_elem else "Unknown"
            
            location_elem = card_element.find('div', class_='companyLocation')
            job_location = self._clean_text(location_elem.get_text()) if location_elem else location
            
            job_link = title_elem.find('a') if title_elem.name != 'a' else title_elem
            job_url = f"{self.base_url}{job_link['href']}" if job_link and 'href' in job_link.attrs else ""
            
            snippet_elem = card_element.find('div', class_='job-snippet')
            job_description = self._clean_text(snippet_elem.get_text()) if snippet_elem else ""
            
            job_id = self._generate_job_id(job_title, company_name, job_location)
            country = self._map_country_code(self.country)
            
            job = {
                'job_id': job_id,
                'job_title': job_title,
                'company_name': company_name,
                'location_city': job_location,
                'location_country': country,
                'job_category': 'unknown',
                'job_description': job_description,
                'job_url': job_url,
                'source': f'indeed_{self.country}'
            }
            
            return job
            
        except Exception as e:
            print(f"   ⚠️  Error parsing job card: {e}")
            return None
    
    def _map_country_code(self, code: str) -> str:
        """Map country code to full name"""
        mapping = {'in': 'India', 'com': 'USA', 'co.uk': 'UK'}
        return mapping.get(code, 'Unknown')


# Self-test
if __name__ == "__main__":
    print("🧪 Testing Enhanced Indeed Scraper...\n")
    
    scraper = IndeedScraper(country="in")
    
    print("⚠️  Note: Indeed may still block. This is normal.")
    print("    If 403 persists, we'll use alternative methods.\n")
    
    jobs = scraper.scrape_jobs("Financial Analyst", "Mumbai", num_pages=1)
    
    print("\n" + "="*50)
    print(f"🎉 SCRAPER TEST: {len(jobs)} jobs scraped")
    print("="*50)
    
    if len(jobs) == 0:
        print("\n⚠️  Indeed is blocking. Next steps:")
        print("   1. Use Selenium (browser automation)")
        print("   2. Try alternative sources")
        print("   3. Use mock data for now, real data later")
