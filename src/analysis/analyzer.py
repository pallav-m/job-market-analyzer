"""
Analyzer - Step 5
Query and analyze extracted data
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database import JobMarketDatabase
import config

class JobMarketAnalyzer:
    """Analyze job market data"""
    
    def __init__(self, db_path: str):
        """Initialize with database"""
        self.db = JobMarketDatabase(db_path)
    
    def get_top_skills(self, limit: int = 20) -> list:
        """Get top N skills by frequency"""
        query = '''
        SELECT 
            skill_name, 
            skill_category,
            COUNT(*) as mention_count,
            SUM(CASE WHEN is_required = 1 THEN 1 ELSE 0 END) as required_count,
            ROUND(100.0 * SUM(CASE WHEN is_required = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as required_pct
        FROM extracted_skills
        GROUP BY skill_name
        ORDER BY mention_count DESC
        LIMIT ?
        '''
        return self.db.execute_query(query, (limit,))
    
    def get_skills_by_geography(self) -> list:
        """Get skill distribution by country"""
        query = '''
        SELECT 
            jp.location_country,
            es.skill_name,
            COUNT(*) as count
        FROM extracted_skills es
        JOIN job_postings jp ON es.job_id = jp.job_id
        GROUP BY jp.location_country, es.skill_name
        ORDER BY jp.location_country, count DESC
        '''
        return self.db.execute_query(query)
    
    def get_skills_by_category(self) -> list:
        """Get skill distribution by job category"""
        query = '''
        SELECT 
            jp.job_category,
            es.skill_name,
            COUNT(*) as count
        FROM extracted_skills es
        JOIN job_postings jp ON es.job_id = jp.job_id
        GROUP BY jp.job_category, es.skill_name
        ORDER BY jp.job_category, count DESC
        '''
        return self.db.execute_query(query)
    
    def get_ai_adoption_by_geography(self) -> list:
        """Calculate % of jobs with AI/ML skills by geography"""
        query = '''
        SELECT 
            location_country,
            COUNT(DISTINCT jp.job_id) as total_jobs,
            COUNT(DISTINCT CASE 
                WHEN es.skill_name IN ('Machine Learning', 'AWS', 'Azure', 'Python') 
                THEN jp.job_id 
            END) as ai_jobs,
            ROUND(100.0 * COUNT(DISTINCT CASE 
                WHEN es.skill_name IN ('Machine Learning', 'AWS', 'Azure', 'Python') 
                THEN jp.job_id 
            END) / COUNT(DISTINCT jp.job_id), 1) as ai_adoption_pct
        FROM job_postings jp
        LEFT JOIN extracted_skills es ON jp.job_id = es.job_id
        GROUP BY location_country
        ORDER BY ai_adoption_pct DESC
        '''
        return self.db.execute_query(query)
    
    def get_summary_stats(self) -> dict:
        """Get overall summary statistics"""
        stats = self.db.get_stats()
        
        # Add additional calculations
        if stats['total_jobs'] > 0:
            stats['avg_skills_per_job'] = round(
                stats['total_skill_mentions'] / stats['total_jobs'], 1
            )
        else:
            stats['avg_skills_per_job'] = 0
        
        return stats
    
    def close(self):
        """Close database connection"""
        self.db.close()

    def get_skills_by_requirement_level(self) -> list:
        """Get skills grouped by requirement level"""
        query = '''
        SELECT 
            requirement_level,
            skill_name,
            COUNT(*) as count,
            AVG(extraction_confidence) as avg_confidence,
            AVG(experience_years) as avg_experience
        FROM extracted_skills
        WHERE requirement_level IS NOT NULL
        GROUP BY requirement_level, skill_name
        ORDER BY requirement_level, count DESC
        '''
        return self.db.execute_query(query)
    
    def get_skills_with_experience(self, min_years: int = 1) -> list:
        """Get skills that mention experience requirements"""
        query = '''
        SELECT 
            skill_name,
            AVG(experience_years) as avg_years,
            COUNT(*) as mention_count
        FROM extracted_skills
        WHERE experience_years >= ?
        GROUP BY skill_name
        ORDER BY mention_count DESC
        '''
        return self.db.execute_query(query, (min_years,))



# Self-test
if __name__ == "__main__":
    print("🧪 Testing Analyzer...\n")
    
    analyzer = JobMarketAnalyzer(config.DB_PATH)
    
    # Test 1: Top skills
    print("1️⃣ Top 10 Skills:")
    top_skills = analyzer.get_top_skills(10)
    for skill in top_skills:
        print(f"   {skill['skill_name']}: {skill['mention_count']} mentions ({skill['required_pct']}% required)")
    
    # Test 2: AI adoption
    print("\n2️⃣ AI/Tech Adoption by Geography:")
    ai_adoption = analyzer.get_ai_adoption_by_geography()
    for geo in ai_adoption:
        print(f"   {geo['location_country']}: {geo['ai_adoption_pct']}% ({geo['ai_jobs']}/{geo['total_jobs']} jobs)")
    
    # Test 3: Summary stats
    print("\n3️⃣ Summary Statistics:")
    stats = analyzer.get_summary_stats()
    print(f"   Total Jobs: {stats['total_jobs']}")
    print(f"   Processed Jobs: {stats['processed_jobs']}")
    print(f"   Unique Skills: {stats['unique_skills']}")
    print(f"   Avg Skills per Job: {stats['avg_skills_per_job']}")
    
    analyzer.close()
    
    print("\n" + "="*50)
    print("🎉 ANALYZER TEST PASSED!")
    print("="*50)
