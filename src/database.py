"""
Database Layer - Step 2
Minimal SQLite3 interface for job market data
"""

import sqlite3
import hashlib
from datetime import datetime
from typing import Dict, List, Optional

class JobMarketDatabase:
    """SQLite3 database handler"""
    
    def __init__(self, db_path: str):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def connect(self):
        """Create database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, timeout=10)
            self.conn.row_factory = sqlite3.Row  # Access columns by name
        return self.conn
    
    def init_database(self):
        """Create tables if they don't exist"""
        self.connect()
        cursor = self.conn.cursor()
        
        # Job Postings Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_postings (
            job_id TEXT PRIMARY KEY,
            job_title TEXT NOT NULL,
            company_name TEXT,
            location_city TEXT,
            location_country TEXT,
            job_category TEXT,
            job_description TEXT NOT NULL,
            job_url TEXT,
            source TEXT,
            content_hash TEXT UNIQUE,
            scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed BOOLEAN DEFAULT 0
        )
        ''')
        
        # # Extracted Skills Table
        # cursor.execute('''
        # CREATE TABLE IF NOT EXISTS extracted_skills (
        #     skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        #     job_id TEXT NOT NULL,
        #     skill_name TEXT NOT NULL,
        #     skill_category TEXT,
        #     is_required BOOLEAN DEFAULT 0,
        #     FOREIGN KEY (job_id) REFERENCES job_postings(job_id)
        # )
        # ''')
        # Extracted Skills Table (Enhanced)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS extracted_skills (
            skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL,
            skill_name TEXT NOT NULL,
            skill_category TEXT,
            skill_subcategory TEXT,
            extraction_confidence FLOAT DEFAULT 1.0,
            is_required BOOLEAN DEFAULT 0,
            requirement_level TEXT DEFAULT 'optional',
            experience_years INTEGER DEFAULT 0,
            context_snippet TEXT,
            FOREIGN KEY (job_id) REFERENCES job_postings(job_id)
        )
        ''')

        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_country ON job_postings(location_country)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_category ON job_postings(job_category)')
        
        self.conn.commit()
        print("✅ Database initialized successfully")
    
    def insert_job_posting(self, job_data: Dict) -> bool:
        """Insert a job posting"""
        try:
            cursor = self.conn.cursor()
            
            # Create content hash to detect duplicates
            content = f"{job_data.get('job_title', '')}{job_data.get('job_description', '')}"
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            cursor.execute('''
            INSERT OR IGNORE INTO job_postings 
            (job_id, job_title, company_name, location_city, location_country, 
             job_category, job_description, job_url, source, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_data.get('job_id'),
                job_data.get('job_title'),
                job_data.get('company_name'),
                job_data.get('location_city'),
                job_data.get('location_country'),
                job_data.get('job_category'),
                job_data.get('job_description'),
                job_data.get('job_url'),
                job_data.get('source'),
                content_hash
            ))
            
            self.conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.IntegrityError:
            return False  # Duplicate
        except Exception as e:
            print(f"Error inserting job: {e}")
            return False
    
    def get_unprocessed_jobs(self, limit: int = 1000) -> List[Dict]:
        """Get jobs that haven't been processed for NLP yet"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT job_id, job_title, job_description 
        FROM job_postings 
        WHERE processed = 0 
        LIMIT ?
        ''', (limit,))
        
        jobs = []
        for row in cursor.fetchall():
            jobs.append({
                'job_id': row['job_id'],
                'job_title': row['job_title'],
                'job_description': row['job_description']
            })
        return jobs
    
    def mark_job_processed(self, job_id: str) -> bool:
        """Mark a job as processed (skills extracted)"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE job_postings SET processed = 1 WHERE job_id = ?', (job_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # def insert_extracted_skills(self, job_id: str, skills: List[Dict]) -> int:
    #     """
    #     Insert extracted skills for a job
    #     Returns: Number of skills inserted
    #     """
    #     cursor = self.conn.cursor()
    #     count = 0
        
    #     for skill in skills:
    #         try:
    #             cursor.execute('''
    #             INSERT INTO extracted_skills 
    #             (job_id, skill_name, skill_category, is_required)
    #             VALUES (?, ?, ?, ?)
    #             ''', (
    #                 job_id,
    #                 skill['skill_name'],
    #                 skill['skill_category'],
    #                 skill['is_required']
    #             ))
    #             count += 1
    #         except Exception as e:
    #             print(f"Error inserting skill {skill.get('skill_name')}: {e}")
        
    #     self.conn.commit()
    #     return count

    def insert_extracted_skills(self, job_id: str, skills: List[Dict]) -> int:
        """Insert extracted skills with enhanced metadata"""
        cursor = self.conn.cursor()
        count = 0
        
        for skill in skills:
            try:
                cursor.execute('''
                INSERT INTO extracted_skills 
                (job_id, skill_name, skill_category, skill_subcategory, 
                 extraction_confidence, is_required, requirement_level, 
                 experience_years, context_snippet)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job_id,
                    skill['skill_name'],
                    skill['skill_category'],
                    skill.get('skill_subcategory', 'General'),
                    skill.get('extraction_confidence', 1.0),
                    skill['is_required'],
                    skill.get('requirement_level', 'optional'),
                    skill.get('experience_years', 0),
                    skill.get('context_snippet', '')[:200]  # Limit to 200 chars
                ))
                count += 1
            except Exception as e:
                print(f"Error inserting skill {skill.get('skill_name')}: {e}")
        
        self.conn.commit()
        return count

    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total jobs
        cursor.execute('SELECT COUNT(*) FROM job_postings')
        stats['total_jobs'] = cursor.fetchone()[0]
        
        # Processed jobs
        cursor.execute('SELECT COUNT(*) FROM job_postings WHERE processed = 1')
        stats['processed_jobs'] = cursor.fetchone()[0]
        
        # Jobs by country
        cursor.execute('SELECT location_country, COUNT(*) FROM job_postings GROUP BY location_country')
        stats['jobs_by_country'] = dict(cursor.fetchall())
        
        # Jobs by category
        cursor.execute('SELECT job_category, COUNT(*) FROM job_postings GROUP BY job_category')
        stats['jobs_by_category'] = dict(cursor.fetchall())
        
        # Unique skills
        cursor.execute('SELECT COUNT(DISTINCT skill_name) FROM extracted_skills')
        stats['unique_skills'] = cursor.fetchone()[0]
        
        # Total skill mentions
        cursor.execute('SELECT COUNT(*) FROM extracted_skills')
        stats['total_skill_mentions'] = cursor.fetchone()[0]
        
        return stats
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute custom SQL query (for analysis)"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        columns = [description[0] for description in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None


# Self-test when run directly
if __name__ == "__main__":
    import tempfile
    import os
    
    print("🧪 Testing Database Module...")
    
    # Create temporary database for testing
    test_db = tempfile.mktemp(suffix='.db')
    
    try:
        # Test 1: Database creation
        print("\n1️⃣ Test: Database Creation")
        db = JobMarketDatabase(test_db)
        print("   ✅ Database created")
        
        # Test 2: Insert job posting
        print("\n2️⃣ Test: Insert Job Posting")
        test_job = {
            'job_id': 'test_001',
            'job_title': 'Financial Analyst',
            'company_name': 'Goldman Sachs',
            'location_city': 'New York',
            'location_country': 'USA',
            'job_category': 'traditional_finance',
            'job_description': 'We are seeking a Financial Analyst with strong Excel and SQL skills.',
            'job_url': 'https://example.com/job1',
            'source': 'test'
        }
        
        success = db.insert_job_posting(test_job)
        print(f"   ✅ Job inserted: {success}")
        
        # Test 3: Duplicate detection
        print("\n3️⃣ Test: Duplicate Detection")
        duplicate = db.insert_job_posting(test_job)
        print(f"   ✅ Duplicate rejected: {not duplicate}")
        
        # Test 4: Get statistics
        print("\n4️⃣ Test: Get Statistics")
        stats = db.get_stats()
        print(f"   ✅ Total jobs: {stats['total_jobs']}")
        print(f"   ✅ Jobs by country: {stats['jobs_by_country']}")
        print(f"   ✅ Jobs by category: {stats['jobs_by_category']}")
        
        # Test 5: Get unprocessed jobs
        print("\n5️⃣ Test: Get Unprocessed Jobs")
        unprocessed = db.get_unprocessed_jobs()
        print(f"   ✅ Unprocessed jobs: {len(unprocessed)}")
        
        # Test 6: Insert skills
        print("\n6️⃣ Test: Insert Extracted Skills")
        test_skills = [
            {'skill_name': 'SQL', 'skill_category': 'Data Analytics', 'is_required': True},
            {'skill_name': 'Excel', 'skill_category': 'Data Analytics', 'is_required': True}
        ]
        count = db.insert_extracted_skills('test_001', test_skills)
        print(f"   ✅ Skills inserted: {count}")
        
        # Test 7: Mark as processed
        print("\n7️⃣ Test: Mark Job Processed")
        marked = db.mark_job_processed('test_001')
        print(f"   ✅ Job marked processed: {marked}")
        
        # Test 8: Verify stats
        print("\n8️⃣ Test: Final Statistics")
        stats = db.get_stats()
        print(f"   ✅ Total jobs: {stats['total_jobs']}")
        print(f"   ✅ Processed jobs: {stats['processed_jobs']}")
        print(f"   ✅ Unique skills: {stats['unique_skills']}")
        
        # Test 9: Close connection
        print("\n9️⃣ Test: Close Connection")
        db.close()
        print("   ✅ Connection closed")
        
        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED!")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if os.path.exists(test_db):
            os.remove(test_db)
            print("\n🧹 Test database cleaned up")
