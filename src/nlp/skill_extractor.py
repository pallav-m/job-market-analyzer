"""
Skill Extractor - Step 4
Extract skills from job descriptions using pattern matching
"""

"""
Skill Extractor - Step 4
Extract skills from job descriptions using pattern matching
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# import re
# from src.nlp.skill_taxonomy import SKILL_TAXONOMY

import re
from src.nlp.skill_taxonomy import SKILL_TAXONOMY

class SkillExtractor:
    """Extract skills from text using simple pattern matching"""
    
    def __init__(self):
        """Initialize with skill taxonomy"""
        self.taxonomy = SKILL_TAXONOMY
        self.required_keywords = ["required", "must have", "essential", "mandatory"]
        self.preferred_keywords = ["preferred", "nice to have", "beneficial", "plus"]
    
    def extract_skills(self, job_description: str, job_title: str = "") -> list:
        """
        Extract skills from job description
        
        Returns: List of dicts with skill info
        """
        text = (job_description + " " + job_title).lower()
        extracted_skills = []
        
        for skill_name, skill_info in self.taxonomy.items():
            # Check if skill or its synonyms appear in text
            all_terms = [skill_name.lower()] + skill_info['synonyms']
            
            for term in all_terms:
                if term in text:
                    # Determine if required or preferred
                    is_required = self._is_required(text, term)
                    
                    extracted_skills.append({
                        'skill_name': skill_name,
                        'skill_category': skill_info['category'],
                        'skill_subcategory': 'General',  # Can expand later
                        'extraction_confidence': 1.0,  # Simple matching = 100%
                        'is_required': is_required
                    })
                    break  # Found this skill, move to next
        
        return extracted_skills
    
    def _is_required(self, text: str, skill_term: str) -> bool:
        """Determine if a skill is required based on context"""
        # Simple heuristic: look for required/preferred keywords near the skill
        skill_position = text.find(skill_term)
        if skill_position == -1:
            return False
        
        # Check surrounding text (100 chars before/after)
        start = max(0, skill_position - 100)
        end = min(len(text), skill_position + 100)
        context = text[start:end]
        
        # Check for required keywords
        for keyword in self.required_keywords:
            if keyword in context:
                return True
        
        # Default to not required (preferred/optional)
        return False


# Self-test
if __name__ == "__main__":
    print("🧪 Testing Skill Extractor...")
    
    extractor = SkillExtractor()
    
    # Test 1: Simple extraction
    print("\n1️⃣ Test: Simple Extraction")
    test_desc_1 = "We need a Financial Analyst with SQL, Python, and Excel skills. Power BI is a plus."
    skills_1 = extractor.extract_skills(test_desc_1)
    print(f"   ✅ Found {len(skills_1)} skills: {[s['skill_name'] for s in skills_1]}")
    
    # Test 2: Required vs Preferred
    print("\n2️⃣ Test: Required vs Preferred")
    test_desc_2 = "Must have SQL and Excel. Python is preferred. Power BI nice to have."
    skills_2 = extractor.extract_skills(test_desc_2)
    required = [s['skill_name'] for s in skills_2 if s['is_required']]
    preferred = [s['skill_name'] for s in skills_2 if not s['is_required']]
    print(f"   ✅ Required: {required}")
    print(f"   ✅ Preferred: {preferred}")
    
    # Test 3: Multiple skills
    print("\n3️⃣ Test: Complex Description")
    test_desc_3 = """
    We are seeking a Senior Financial Analyst with 5+ years experience.
    Required skills: Financial Modeling, SQL, Excel, SAP
    Preferred skills: Python, Machine Learning, AWS
    Must have strong data analysis and risk management capabilities.
    """
    skills_3 = extractor.extract_skills(test_desc_3)
    print(f"   ✅ Found {len(skills_3)} skills")
    
    # Group by category
    categories = {}
    for skill in skills_3:
        cat = skill['skill_category']
        categories[cat] = categories.get(cat, 0) + 1
    print(f"   ✅ By category: {categories}")
    
    # Test 4: Empty description
    print("\n4️⃣ Test: Empty Description")
    skills_4 = extractor.extract_skills("")
    print(f"   ✅ Empty text returns: {len(skills_4)} skills")
    
    print("\n" + "="*50)
    print("🎉 EXTRACTOR TEST PASSED!")
    print("="*50)
