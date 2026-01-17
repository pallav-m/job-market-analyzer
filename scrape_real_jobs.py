# """
# Real Jobs Scraper - Production Run
# Scrapes 500+ jobs across categories and locations
# """

# import sys
# from pathlib import Path

# project_root = Path(__file__).parent
# sys.path.insert(0, str(project_root))

# from src.job_sources.indeed_selenium import IndeedSeleniumScraper
# from src.database import JobMarketDatabase
# import config
# import time

# class JobScraperOrchestrator:
#     """Orchestrate scraping across multiple searches"""
    
#     def __init__(self):
#         self.db = JobMarketDatabase(config.DB_PATH)
#         self.total_scraped = 0
#         self.total_inserted = 0
    
#     def scrape_all(self, target_jobs: int = 500):
#         """
#         Scrape jobs across multiple searches
        
#         Args:
#             target_jobs: Target number of jobs to collect
#         """
#         print("\n" + "="*60)
#         print(f"  REAL JOB SCRAPING - TARGET: {target_jobs} JOBS")
#         print("="*60 + "\n")
        
#         # Define search configurations
#         searches = self._get_search_configs()
        
#         print(f"📋 Configured {len(searches)} search queries\n")
        
#         for i, search in enumerate(searches, 1):
#             if self.total_scraped >= target_jobs:
#                 print(f"\n✅ Reached target of {target_jobs} jobs!\n")
#                 break
            
#             print(f"{'='*60}")
#             print(f"Search {i}/{len(searches)}: {search['title']} in {search['location']} ({search['country']})")
#             print(f"{'='*60}\n")
            
#             # Calculate how many more jobs we need
#             remaining = target_jobs - self.total_scraped
#             jobs_to_scrape = min(search['max_jobs'], remaining)
#             pages = (jobs_to_scrape + 9) // 10  # 10 jobs per page
            
#             # Scrape
#             jobs = self._scrape_search(
#                 country=search['country'],
#                 job_title=search['title'],
#                 location=search['location'],
#                 num_pages=pages,
#                 max_jobs=jobs_to_scrape
#             )
            
#             # Save to database
#             inserted = self._save_jobs(jobs)
            
#             self.total_scraped += len(jobs)
#             self.total_inserted += inserted
            
#             print(f"\n   Progress: {self.total_scraped}/{target_jobs} jobs scraped, {self.total_inserted} inserted\n")
            
#             # Delay between searches
#             if i < len(searches):
#                 print("   ⏳ Waiting 10 seconds before next search...")
#                 time.sleep(10)
        
#         # Final summary
#         self._print_summary()
    
#     def _get_search_configs(self) -> list:
#         """Define search configurations"""
#         return [
#             # India searches
#             {'country': 'in', 'title': 'Financial Analyst', 'location': 'Mumbai', 'max_jobs': 50},
#             {'country': 'in', 'title': 'Data Analyst', 'location': 'Bangalore', 'max_jobs': 50},
#             {'country': 'in', 'title': 'Business Analyst', 'location': 'Mumbai', 'max_jobs': 50},
#             {'country': 'in', 'title': 'Risk Analyst', 'location': 'Mumbai', 'max_jobs': 40},
#             {'country': 'in', 'title': 'Compliance Officer', 'location': 'Delhi', 'max_jobs': 40},
#             {'country': 'in', 'title': 'Financial Modeler', 'location': 'Mumbai', 'max_jobs': 30},
#             {'country': 'in', 'title': 'Treasury Analyst', 'location': 'Mumbai', 'max_jobs': 30},
            
#             # USA searches
#             {'country': 'com', 'title': 'Financial Analyst', 'location': 'New York', 'max_jobs': 50},
#             {'country': 'com', 'title': 'Data Analyst', 'location': 'San Francisco', 'max_jobs': 40},
#             {'country': 'com', 'title': 'Risk Manager', 'location': 'New York', 'max_jobs': 40},
            
#             # UK searches
#             {'country': 'co.uk', 'title': 'Financial Analyst', 'location': 'London', 'max_jobs': 50},
#             {'country': 'co.uk', 'title': 'Data Analyst', 'location': 'London', 'max_jobs': 40},
#             {'country': 'co.uk', 'title': 'Compliance Analyst', 'location': 'London', 'max_jobs': 40},
#         ]
    
#     def _scrape_search(self, country: str, job_title: str, location: str, 
#                        num_pages: int, max_jobs: int) -> list:
#         """Scrape a single search"""
#         scraper = IndeedSeleniumScraper(country=country, headless=True)
        
#         try:
#             jobs = scraper.scrape_jobs(
#                 job_title=job_title,
#                 location=location,
#                 num_pages=num_pages,
#                 max_jobs=max_jobs
#             )
#         except Exception as e:
#             print(f"   ❌ Error during scraping: {e}")
#             jobs = []
#         finally:
#             scraper.close()
        
#         return jobs
    
#     def _save_jobs(self, jobs: list) -> int:
#         """Save jobs to database"""
#         if len(jobs) == 0:
#             return 0
        
#         print(f"\n   💾 Saving {len(jobs)} jobs to database...")
        
#         inserted = 0
#         duplicates = 0
        
#         for job in jobs:
#             success = self.db.insert_job_posting(job)
#             if success:
#                 inserted += 1
#             else:
#                 duplicates += 1
        
#         print(f"   ✅ Inserted: {inserted} | Duplicates skipped: {duplicates}")
        
#         return inserted
    
#     def _print_summary(self):
#         """Print final summary"""
#         print("\n" + "="*60)
#         print("  SCRAPING COMPLETE - SUMMARY")
#         print("="*60 + "\n")
        
#         stats = self.db.get_stats()
        
#         print(f"📊 Scraping Results:")
#         print(f"   Total jobs scraped: {self.total_scraped}")
#         print(f"   New jobs inserted: {self.total_inserted}")
#         print(f"   Duplicates skipped: {self.total_scraped - self.total_inserted}\n")
        
#         print(f"📊 Database Statistics:")
#         print(f"   Total jobs in DB: {stats['total_jobs']}")
#         print(f"   Jobs by country: {stats['jobs_by_country']}")
#         print(f"   Jobs by category: {stats['jobs_by_category']}\n")
        
#         print("="*60)
#         print("🎉 Ready for NLP processing!")
#         print("="*60)
#         print(f"\nNext step: python reprocess_jobs.py\n")
    
#     def close(self):
#         """Close database connection"""
#         self.db.close()


# def main():
#     """Main execution"""
#     orchestrator = JobScraperOrchestrator()
    
#     try:
#         # Scrape 500 jobs (adjust as needed)
#         orchestrator.scrape_all(target_jobs=600)
#     finally:
#         orchestrator.close()


# if __name__ == "__main__":
#     main()


"""
Multi-Source Job Scraper - Indeed + LinkedIn
Scrapes from multiple sources and combines data
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.job_sources.indeed_selenium import IndeedSeleniumScraper
from src.job_sources.linkedin_selenium import LinkedInSeleniumScraper
from src.database import JobMarketDatabase
import config
import time

class MultiSourceJobScraper:
    """Orchestrate scraping from multiple sources"""
    
    def __init__(self):
        self.db = JobMarketDatabase(config.DB_PATH)
        self.total_scraped = 0
        self.total_inserted = 0
        self.stats_by_source = {}
    
    def scrape_all(self, target_jobs: int = 500):
        """
        Scrape jobs from multiple sources
        
        Args:
            target_jobs: Target total jobs across all sources
        """
        print("\n" + "="*60)
        print(f"  MULTI-SOURCE JOB SCRAPING")
        print(f"  Target: {target_jobs} jobs from Indeed + LinkedIn")
        print("="*60 + "\n")
        
        # Split target between sources (60% Indeed, 40% LinkedIn)
        indeed_target = int(target_jobs * 0.6)
        linkedin_target = target_jobs - indeed_target
        
        print(f"📊 Distribution:")
        print(f"   Indeed: {indeed_target} jobs")
        print(f"   LinkedIn: {linkedin_target} jobs\n")
        
        # Scrape from Indeed
        print("="*60)
        print("  SOURCE 1: INDEED")
        print("="*60 + "\n")
        
        indeed_searches = self._get_indeed_searches()
        indeed_jobs = self._scrape_source(
            source_name="indeed",
            searches=indeed_searches,
            target_jobs=indeed_target,
            scraper_class=IndeedSeleniumScraper
        )
        
        # Scrape from LinkedIn
        print("\n" + "="*60)
        print("  SOURCE 2: LINKEDIN")
        print("="*60 + "\n")
        
        linkedin_searches = self._get_linkedin_searches()
        linkedin_jobs = self._scrape_source(
            source_name="linkedin",
            searches=linkedin_searches,
            target_jobs=linkedin_target,
            scraper_class=LinkedInSeleniumScraper
        )
        
        # Final summary
        self._print_summary()
    
    def _get_indeed_searches(self) -> list:
        """Define Indeed search configurations"""
        return [
            # India
            {'country': 'in', 'title': 'Financial Analyst', 'location': 'Mumbai', 'max_jobs': 60},
            {'country': 'in', 'title': 'Data Analyst', 'location': 'Bangalore', 'max_jobs': 50},
            {'country': 'in', 'title': 'Business Analyst', 'location': 'Mumbai', 'max_jobs': 50},
            {'country': 'in', 'title': 'Risk Analyst', 'location': 'Mumbai', 'max_jobs': 40},
            {'country': 'in', 'title': 'Compliance Officer', 'location': 'Delhi', 'max_jobs': 40},
            
            # USA
            {'country': 'com', 'title': 'Financial Analyst', 'location': 'New York', 'max_jobs': 50},
            {'country': 'com', 'title': 'Data Analyst', 'location': 'San Francisco', 'max_jobs': 40},
            
            # UK
            {'country': 'co.uk', 'title': 'Financial Analyst', 'location': 'London', 'max_jobs': 50},
            {'country': 'co.uk', 'title': 'Data Analyst', 'location': 'London', 'max_jobs': 40},
        ]
    
    def _get_linkedin_searches(self) -> list:
        """Define LinkedIn search configurations"""
        return [
            # India
            {'country': 'in', 'title': 'Financial Analyst', 'location': 'Mumbai', 'max_jobs': 50},
            {'country': 'in', 'title': 'Data Analyst', 'location': 'Bangalore', 'max_jobs': 50},
            {'country': 'in', 'title': 'Risk Manager', 'location': 'Mumbai', 'max_jobs': 40},
            
            # USA
            {'country': 'com', 'title': 'Financial Analyst', 'location': 'New York', 'max_jobs': 40},
            {'country': 'com', 'title': 'Business Analyst', 'location': 'San Francisco', 'max_jobs': 40},
        ]
    
    def _scrape_source(self, source_name: str, searches: list, target_jobs: int, scraper_class) -> list:
        """Scrape from a single source"""
        all_jobs = []
        
        for i, search in enumerate(searches, 1):
            if len(all_jobs) >= target_jobs:
                print(f"\n✅ Reached {source_name} target of {target_jobs} jobs!\n")
                break
            
            print(f"{'-'*60}")
            print(f"{source_name.upper()} Search {i}/{len(searches)}: {search['title']} in {search['location']}")
            print(f"{'-'*60}\n")
            
            # Calculate how many more needed
            remaining = target_jobs - len(all_jobs)
            jobs_to_scrape = min(search['max_jobs'], remaining)
            
            # Determine pages based on source
            if source_name == 'linkedin':
                pages = (jobs_to_scrape + 24) // 25  # 25 jobs per page
            else:
                pages = (jobs_to_scrape + 9) // 10  # 10 jobs per page
            
            # Scrape
            scraper = scraper_class(country=search['country'], headless=True)
            
            try:
                jobs = scraper.scrape_jobs(
                    job_title=search['title'],
                    location=search['location'],
                    num_pages=pages,
                    max_jobs=jobs_to_scrape
                )
            except Exception as e:
                print(f"   ❌ Error: {e}")
                jobs = []
            finally:
                scraper.close()
            
            # Save to database
            inserted = self._save_jobs(jobs)
            
            all_jobs.extend(jobs)
            self.total_scraped += len(jobs)
            self.total_inserted += inserted
            
            # Track by source
            if source_name not in self.stats_by_source:
                self.stats_by_source[source_name] = {'scraped': 0, 'inserted': 0}
            self.stats_by_source[source_name]['scraped'] += len(jobs)
            self.stats_by_source[source_name]['inserted'] += inserted
            
            print(f"\n   Progress: {len(all_jobs)}/{target_jobs} jobs from {source_name}")
            print(f"   Overall: {self.total_scraped} total scraped, {self.total_inserted} inserted\n")
            
            # Delay between searches
            if i < len(searches) and len(all_jobs) < target_jobs:
                print("   ⏳ Waiting 10 seconds before next search...")
                time.sleep(10)
        
        return all_jobs
    
    def _save_jobs(self, jobs: list) -> int:
        """Save jobs to database"""
        if len(jobs) == 0:
            return 0
        
        print(f"   💾 Saving {len(jobs)} jobs to database...")
        
        inserted = 0
        duplicates = 0
        
        for job in jobs:
            success = self.db.insert_job_posting(job)
            if success:
                inserted += 1
            else:
                duplicates += 1
        
        print(f"   ✅ Inserted: {inserted} | Duplicates: {duplicates}")
        
        return inserted
    
    def _print_summary(self):
        """Print final summary"""
        print("\n" + "="*60)
        print("  SCRAPING COMPLETE - FINAL SUMMARY")
        print("="*60 + "\n")
        
        print(f"📊 Scraping Results by Source:")
        for source, stats in self.stats_by_source.items():
            print(f"   {source.upper()}:")
            print(f"      Scraped: {stats['scraped']}")
            print(f"      Inserted: {stats['inserted']}")
            print(f"      Duplicates: {stats['scraped'] - stats['inserted']}")
        
        print(f"\n📊 Overall Totals:")
        print(f"   Total scraped: {self.total_scraped}")
        print(f"   Total inserted: {self.total_inserted}")
        print(f"   Duplicates: {self.total_scraped - self.total_inserted}\n")
        
        # Database stats
        db_stats = self.db.get_stats()
        
        print(f"📊 Database Statistics:")
        print(f"   Total jobs: {db_stats['total_jobs']}")
        print(f"   By country: {db_stats['jobs_by_country']}")
        print(f"   By category: {db_stats['jobs_by_category']}\n")
        
        # Source distribution in database
        print(f"📊 Jobs by Source in Database:")
        source_query = '''
        SELECT source, COUNT(*) as count 
        FROM job_postings 
        GROUP BY source 
        ORDER BY count DESC
        '''
        sources = self.db.execute_query(source_query)
        for row in sources:
            print(f"   {row['source']}: {row['count']} jobs")
        
        print("\n" + "="*60)
        print("🎉 Ready for NLP processing!")
        print("="*60)
        print(f"\nNext steps:")
        print(f"1. python reprocess_jobs.py  (extract skills)")
        print(f"2. python main.py            (generate report)\n")
    
    def close(self):
        """Close database"""
        self.db.close()


def main():
    """Main execution"""
    scraper = MultiSourceJobScraper()
    
    try:
        # Scrape 500 jobs total (300 Indeed + 200 LinkedIn)
        scraper.scrape_all(target_jobs=1000)
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
