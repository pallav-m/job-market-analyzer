"""
Database Upgrade - Add new columns for context-aware extraction
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import sqlite3
import config

def upgrade_database():
    """Add new columns to existing database"""
    print("🔧 Upgrading database schema...\n")
    
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(extracted_skills)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Add new columns if they don't exist
    new_columns = {
        'skill_subcategory': 'TEXT DEFAULT "General"',
        'extraction_confidence': 'FLOAT DEFAULT 1.0',
        'requirement_level': 'TEXT DEFAULT "optional"',
        'experience_years': 'INTEGER DEFAULT 0',
        'context_snippet': 'TEXT'
    }
    
    for col_name, col_type in new_columns.items():
        if col_name not in columns:
            try:
                cursor.execute(f'ALTER TABLE extracted_skills ADD COLUMN {col_name} {col_type}')
                print(f"   ✅ Added column: {col_name}")
            except Exception as e:
                print(f"   ⚠️  Column {col_name} may already exist: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database upgrade complete!")

if __name__ == "__main__":
    upgrade_database()
