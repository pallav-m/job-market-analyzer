"""
Test New Insights - Query enhanced skill data
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database import JobMarketDatabase
import config

def show_new_insights():
    """Display insights from context-aware extraction"""
    
    db = JobMarketDatabase(config.DB_PATH)
    
    print("\n" + "="*60)
    print("  NEW INSIGHTS: Context-Aware Extraction Results")
    print("="*60 + "\n")
    
    # 1. Skills by requirement level
    print("1️⃣ Skills by Requirement Level:\n")
    query1 = '''
    SELECT 
        requirement_level,
        COUNT(*) as count,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM extracted_skills), 1) as percentage
    FROM extracted_skills
    GROUP BY requirement_level
    ORDER BY count DESC
    '''
    results1 = db.execute_query(query1)
    for row in results1:
        print(f"   {row['requirement_level'].upper():12} {row['count']:4} mentions ({row['percentage']}%)")
    
    # 2. Top required skills
    print("\n2️⃣ Top 10 REQUIRED Skills:\n")
    query2 = '''
    SELECT 
        skill_name,
        COUNT(*) as mentions,
        ROUND(AVG(extraction_confidence), 2) as avg_confidence
    FROM extracted_skills
    WHERE requirement_level = 'required'
    GROUP BY skill_name
    ORDER BY mentions DESC
    LIMIT 10
    '''
    results2 = db.execute_query(query2)
    for i, row in enumerate(results2, 1):
        print(f"   {i:2}. {row['skill_name']:20} {row['mentions']:3} mentions (confidence: {row['avg_confidence']})")
    
    # 3. Skills with experience requirements
    print("\n3️⃣ Skills with Experience Requirements:\n")
    query3 = '''
    SELECT 
        skill_name,
        ROUND(AVG(experience_years), 1) as avg_years,
        COUNT(*) as mentions
    FROM extracted_skills
    WHERE experience_years > 0
    GROUP BY skill_name
    ORDER BY avg_years DESC, mentions DESC
    '''
    results3 = db.execute_query(query3)
    if results3:
        for row in results3:
            print(f"   {row['skill_name']:20} {row['avg_years']} years avg ({row['mentions']} mentions)")
    else:
        print("   (No experience requirements detected)")
    
    # 4. Confidence distribution
    print("\n4️⃣ Extraction Confidence Distribution:\n")
    query4 = '''
    SELECT 
        CASE 
            WHEN extraction_confidence >= 0.9 THEN 'High (0.9-1.0)'
            WHEN extraction_confidence >= 0.8 THEN 'Medium (0.8-0.9)'
            ELSE 'Low (<0.8)'
        END as confidence_range,
        COUNT(*) as count
    FROM extracted_skills
    GROUP BY confidence_range
    ORDER BY confidence_range DESC
    '''
    results4 = db.execute_query(query4)
    for row in results4:
        print(f"   {row['confidence_range']:20} {row['count']} extractions")
    
    # 5. Requirement level by skill category
    print("\n5️⃣ Requirement Distribution by Skill Category:\n")
    query5 = '''
    SELECT 
        skill_category,
        SUM(CASE WHEN requirement_level = 'required' THEN 1 ELSE 0 END) as required_count,
        SUM(CASE WHEN requirement_level = 'preferred' THEN 1 ELSE 0 END) as preferred_count,
        COUNT(*) as total
    FROM extracted_skills
    GROUP BY skill_category
    ORDER BY total DESC
    '''
    results5 = db.execute_query(query5)
    for row in results5:
        req_pct = round(100 * row['required_count'] / row['total'], 1) if row['total'] > 0 else 0
        print(f"   {row['skill_category']:25} Required: {row['required_count']:3} ({req_pct}%)  |  Preferred: {row['preferred_count']:3}")
    
    db.close()
    
    print("\n" + "="*60)
    print("🎉 Context-aware extraction provides much richer insights!")
    print("="*60 + "\n")

if __name__ == "__main__":
    show_new_insights()
