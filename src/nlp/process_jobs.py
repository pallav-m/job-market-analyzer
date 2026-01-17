"""
Job Processor - Step 4
Process jobs from database and extract skills
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database import JobMarketDatabase
from src.nlp.skill_extractor import SkillExtractor
import config

def process_all_jobs():
    """Process all unprocessed jobs in database"""
    
    print("🔄 Starting Job Processing...\n")
    
    # Initialize
    db = JobMarketDatabase(config.DB_PATH)
    extractor = SkillExtractor()
    
    # Get unprocessed jobs
    print("1️⃣ Fetching unprocessed jobs...")
    jobs = db.get_unprocessed_jobs(limit=1000)
    print(f"   ✅ Found {len(jobs)} unprocessed jobs\n")
    
    if len(jobs) == 0:
        print("   ℹ️  No jobs to process!")
        db.close()
        return
    
    # Process each job
    print("2️⃣ Extracting skills from job descriptions...")
    total_skills = 0
    
    for i, job in enumerate(jobs, 1):
        # Extract skills
        skills = extractor.extract_skills(
            job['job_description'], 
            job['job_title']
        )
        
        # Insert skills into database
        if skills:
            count = db.insert_extracted_skills(job['job_id'], skills)
            total_skills += count
        
        # Mark job as processed
        db.mark_job_processed(job['job_id'])
        
        # Progress update
        if i % 10 == 0:
            print(f"   ✅ Processed {i}/{len(jobs)} jobs...")
    
    print(f"   ✅ Completed processing {len(jobs)} jobs\n")
    
    # Show summary
    print("3️⃣ Processing Summary:")
    print(f"   ✅ Jobs processed: {len(jobs)}")
    print(f"   ✅ Skills extracted: {total_skills}")
    print(f"   ✅ Avg skills per job: {total_skills/len(jobs):.1f}\n")
    
    # Get updated stats
    stats = db.get_stats()
    print("4️⃣ Database Statistics:")
    print(f"   ✅ Total jobs: {stats['total_jobs']}")
    print(f"   ✅ Processed jobs: {stats['processed_jobs']}")
    print(f"   ✅ Unique skills: {stats['unique_skills']}")
    print(f"   ✅ Total skill mentions: {stats['total_skill_mentions']}\n")
    
    db.close()
    
    print("="*50)
    print("🎉 PROCESSING COMPLETE!")
    print("="*50)

if __name__ == "__main__":
    process_all_jobs()
