"""
Test Pipeline - Step 3
Test mock data generation + database insertion
"""

from src.database import JobMarketDatabase
from src.utils.mock_data_generator import MockJobGenerator
import config

def test_pipeline():
    """Test full pipeline: generate → insert → query"""
    
    print("🧪 Testing Full Pipeline...\n")
    
    # Initialize database
    print("1️⃣ Initialize Database")
    db = JobMarketDatabase(config.DB_PATH)
    print("   ✅ Database ready\n")
    
    # Initialize mock generator
    print("2️⃣ Initialize Mock Generator")
    generator = MockJobGenerator(config.JOB_CATEGORIES, config.GEOGRAPHIC_TARGETS)
    print("   ✅ Generator ready\n")
    
    # Generate jobs
    print("3️⃣ Generate 50 Mock Jobs")
    jobs = generator.generate_batch(50)
    print(f"   ✅ Generated {len(jobs)} jobs\n")
    
    # Insert into database
    print("4️⃣ Insert Jobs into Database")
    inserted = 0
    for job in jobs:
        if db.insert_job_posting(job):
            inserted += 1
    print(f"   ✅ Inserted {inserted}/{len(jobs)} jobs\n")
    
    # Get statistics
    print("5️⃣ Query Database Statistics")
    stats = db.get_stats()
    print(f"   ✅ Total jobs: {stats['total_jobs']}")
    print(f"   ✅ Jobs by country: {stats['jobs_by_country']}")
    print(f"   ✅ Jobs by category: {stats['jobs_by_category']}\n")
    
    # Close database
    db.close()
    
    print("="*50)
    print("🎉 PIPELINE TEST COMPLETE!")
    print("="*50)
    print(f"\n✅ Successfully generated and stored {inserted} jobs")
    print(f"✅ Database: {config.DB_PATH}")
    print(f"✅ Ready for Step 4: NLP Processing")

if __name__ == "__main__":
    test_pipeline()
