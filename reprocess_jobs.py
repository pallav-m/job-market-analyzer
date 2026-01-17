"""
Reprocess Jobs - Use context-aware extractor on existing jobs
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database import JobMarketDatabase
from src.nlp.context_aware_extractor import ContextAwareSkillExtractor
import config

def reprocess_all_jobs():
    """Reprocess all jobs with new extractor"""
    print("🔄 Reprocessing jobs with context-aware extractor...\n")
    
    db = JobMarketDatabase(config.DB_PATH)
    extractor = ContextAwareSkillExtractor()
    
    # Clear old extracted skills
    print("1️⃣ Clearing old skill extractions...")
    cursor = db.conn.cursor()
    cursor.execute("DELETE FROM extracted_skills")
    db.conn.commit()
    print("   ✅ Cleared old skills\n")
    
    # Reset processed flag
    print("2️⃣ Resetting processed flags...")
    cursor.execute("UPDATE job_postings SET processed = 0")
    db.conn.commit()
    print("   ✅ Reset flags\n")
    
    # Get all jobs
    print("3️⃣ Fetching jobs...")
    jobs = db.get_unprocessed_jobs(limit=1000)
    print(f"   ✅ Found {len(jobs)} jobs to process\n")
    
    if len(jobs) == 0:
        print("   ℹ️  No jobs to process!")
        db.close()
        return
    
    # Process each job
    print("4️⃣ Extracting skills with context awareness...")
    total_skills = 0
    required_count = 0
    preferred_count = 0
    with_experience = 0
    
    for i, job in enumerate(jobs, 1):
        # Extract skills
        skills = extractor.extract_skills(
            job['job_description'], 
            job['job_title']
        )
        
        # Count metadata
        for skill in skills:
            if skill['requirement_level'] == 'required':
                required_count += 1
            elif skill['requirement_level'] == 'preferred':
                preferred_count += 1
            if skill['experience_years'] > 0:
                with_experience += 1
        
        # Insert into database
        if skills:
            count = db.insert_extracted_skills(job['job_id'], skills)
            total_skills += count
        
        # Mark as processed
        db.mark_job_processed(job['job_id'])
        
        # Progress
        if i % 10 == 0:
            print(f"   ✅ Processed {i}/{len(jobs)} jobs...")
    
    print(f"   ✅ Completed processing {len(jobs)} jobs\n")
    
    # Summary
    print("5️⃣ Processing Summary:")
    print(f"   ✅ Total skills extracted: {total_skills}")
    print(f"   ✅ Average skills per job: {total_skills/len(jobs):.1f}")
    print(f"   ✅ Required skills: {required_count} ({100*required_count/total_skills:.1f}%)")
    print(f"   ✅ Preferred skills: {preferred_count} ({100*preferred_count/total_skills:.1f}%)")
    print(f"   ✅ Skills with experience level: {with_experience}\n")
    
    # Get updated stats
    stats = db.get_stats()
    print("6️⃣ Database Statistics:")
    print(f"   ✅ Total jobs: {stats['total_jobs']}")
    print(f"   ✅ Processed jobs: {stats['processed_jobs']}")
    print(f"   ✅ Unique skills: {stats['unique_skills']}\n")
    
    db.close()
    
    print("="*50)
    print("🎉 REPROCESSING COMPLETE!")
    print("="*50)

if __name__ == "__main__":
    reprocess_all_jobs()
