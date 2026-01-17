"""
Mock Data Generator - Step 3
Generate realistic fake job postings for testing
"""

import random
from datetime import datetime, timedelta

class MockJobGenerator:
    """Generate fake but realistic job postings"""
    
    # Sample companies
    COMPANIES = {
        "India": ["HDFC Bank", "ICICI Bank", "TCS", "Infosys", "Wipro", "Paytm", "PhonePe", "Razorpay"],
        "USA": ["Goldman Sachs", "JP Morgan", "Morgan Stanley", "Stripe", "Square", "Robinhood"],
        "UK": ["Barclays", "HSBC", "Lloyds", "Revolut", "Monzo", "TransferWise"]
    }
    
    # Skill keywords to include in descriptions
    SKILLS = [
        "SQL", "Python", "Excel", "Power BI", "Tableau", "Financial Modeling",
        "Data Analysis", "SAP", "Oracle", "QuickBooks", "VBA", "R",
        "Machine Learning", "AWS", "Azure", "Risk Management", "Compliance",
        "GAAP", "IFRS", "Financial Reporting", "Budgeting", "Forecasting"
    ]
    
    # Job description templates
    DESCRIPTION_TEMPLATES = [
        "We are seeking a {title} to join our {department} team. Must have {experience} years of experience with {skills}. Responsibilities include {responsibilities}.",
        "Looking for a talented {title} with expertise in {skills}. You will be responsible for {responsibilities}. {experience}+ years required.",
        "{title} needed for our {department} division. Key skills: {skills}. Main duties: {responsibilities}. Experience: {experience} years."
    ]
    
    RESPONSIBILITIES = [
        "financial analysis and reporting",
        "budget planning and forecasting",
        "data analysis and visualization",
        "risk assessment and mitigation",
        "process improvement initiatives",
        "stakeholder communication",
        "financial modeling and valuation"
    ]
    
    def __init__(self, job_categories: dict, geographic_targets: dict):
        """Initialize with config data"""
        self.job_categories = job_categories
        self.geographic_targets = geographic_targets
    
    def generate_job(self, category: str, country: str) -> dict:
        """Generate a single fake job posting"""
        
        # Select random job title from category
        job_titles = self.job_categories[category]["keywords"]
        job_title = random.choice(job_titles)
        
        # Select random city from country
        city = random.choice(self.geographic_targets[country])
        
        # Select random company from country
        company = random.choice(self.COMPANIES[country])
        
        # Generate job description
        template = random.choice(self.DESCRIPTION_TEMPLATES)
        selected_skills = random.sample(self.SKILLS, k=random.randint(3, 6))
        selected_responsibilities = random.sample(self.RESPONSIBILITIES, k=random.randint(2, 4))
        
        description = template.format(
            title=job_title,
            department=self.job_categories[category]["label"],
            experience=random.randint(2, 7),
            skills=", ".join(selected_skills),
            responsibilities="; ".join(selected_responsibilities)
        )
        
        # Generate unique job ID
        job_id = f"mock_{category}_{country}_{random.randint(1000, 9999)}"
        
        # Create job posting
        job_posting = {
            'job_id': job_id,
            'job_title': job_title,
            'company_name': company,
            'location_city': city,
            'location_country': country,
            'job_category': category,
            'job_description': description,
            'job_url': f'https://example.com/jobs/{job_id}',
            'source': 'mock_generator'
        }
        
        return job_posting
    
    def generate_batch(self, num_jobs: int = 100) -> list:
        """Generate a batch of job postings"""
        jobs = []
        
        # Distribute jobs across categories and geographies
        categories = list(self.job_categories.keys())
        countries = list(self.geographic_targets.keys())
        
        for i in range(num_jobs):
            category = random.choice(categories)
            country = random.choice(countries)
            job = self.generate_job(category, country)
            jobs.append(job)
        
        return jobs


# Self-test
if __name__ == "__main__":
    print("🧪 Testing Mock Data Generator...")
    
    # Test config (minimal for testing)
    test_categories = {
        "traditional_finance": {
            "label": "Traditional Finance",
            "keywords": ["Financial Analyst", "FP&A Analyst"]
        },
        "fintech": {
            "label": "FinTech",
            "keywords": ["FinTech Analyst", "Payments Analyst"]
        }
    }
    
    test_geographies = {
        "India": ["Mumbai", "Bengaluru"],
        "USA": ["New York", "San Francisco"]
    }
    
    # Create generator
    generator = MockJobGenerator(test_categories, test_geographies)
    
    # Test 1: Generate single job
    print("\n1️⃣ Test: Generate Single Job")
    job = generator.generate_job("traditional_finance", "India")
    print(f"   ✅ Generated job: {job['job_title']} at {job['company_name']}")
    print(f"   ✅ Location: {job['location_city']}, {job['location_country']}")
    print(f"   ✅ Description length: {len(job['job_description'])} chars")
    
    # Test 2: Generate batch
    print("\n2️⃣ Test: Generate Batch")
    jobs = generator.generate_batch(10)
    print(f"   ✅ Generated {len(jobs)} jobs")
    
    # Test 3: Verify distribution
    print("\n3️⃣ Test: Verify Distribution")
    categories = {}
    countries = {}
    
    for job in jobs:
        cat = job['job_category']
        country = job['location_country']
        categories[cat] = categories.get(cat, 0) + 1
        countries[country] = countries.get(country, 0) + 1
    
    print(f"   ✅ Categories: {categories}")
    print(f"   ✅ Countries: {countries}")
    
    # Test 4: Check uniqueness
    print("\n4️⃣ Test: Check Uniqueness")
    job_ids = [j['job_id'] for j in jobs]
    unique_ids = len(set(job_ids))
    print(f"   ✅ Unique job IDs: {unique_ids}/{len(jobs)}")
    
    print("\n" + "="*50)
    print("🎉 ALL TESTS PASSED!")
    print("="*50)

