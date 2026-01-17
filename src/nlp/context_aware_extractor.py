# """
# Context-Aware Skill Extractor - Step 7.2
# Uses spaCy NLP for intelligent extraction
# """

# import sys
# from pathlib import Path
# import re

# project_root = Path(__file__).parent.parent.parent
# sys.path.insert(0, str(project_root))

# import spacy
# from spacy.matcher import PhraseMatcher
# from src.nlp.skill_taxonomy import SKILL_TAXONOMY

# class ContextAwareSkillExtractor:
#     """Context-aware skill extraction using spaCy"""
    
#     def __init__(self, model_name: str = "en_core_web_lg"):
#         """Initialize with spaCy model"""
#         print(f"🧠 Loading spaCy model: {model_name}...")
#         self.nlp = spacy.load(model_name)
#         self.taxonomy = SKILL_TAXONOMY
        
#         # Build phrase matcher for skills
#         self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
#         self._build_skill_patterns()
        
#         # Context keywords
#         self.required_patterns = [
#             "required", "must have", "must-have", "essential", "mandatory",
#             "need", "needs", "needed", "require", "requires"
#         ]
        
#         self.preferred_patterns = [
#             "preferred", "nice to have", "nice-to-have", "beneficial",
#             "plus", "bonus", "desirable", "advantageous", "ideal"
#         ]
        
#         self.experience_pattern = re.compile(r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience\s+)?(?:in\s+|with\s+)?', re.IGNORECASE)
        
#         print(f"✅ Loaded {len(self.taxonomy)} skills into matcher")
    
#     def _build_skill_patterns(self):
#         """Build phrase patterns for all skills and synonyms"""
#         for skill_name, skill_info in self.taxonomy.items():
#             # Add main skill name
#             patterns = [self.nlp(skill_name.lower())]
            
#             # Add synonyms
#             for synonym in skill_info['synonyms']:
#                 patterns.append(self.nlp(synonym.lower()))
            
#             # Add to matcher
#             self.matcher.add(skill_name, patterns)
    
#     def extract_skills(self, job_description: str, job_title: str = "") -> list:
#         """
#         Extract skills with context awareness
        
#         Returns: List of skill dictionaries with enhanced metadata
#         """
#         # Combine text
#         full_text = f"{job_title}. {job_description}"
        
#         # Process with spaCy
#         doc = self.nlp(full_text)
        
#         # Find skill matches
#         matches = self.matcher(doc)
        
#         extracted_skills = []
#         seen_skills = set()
        
#         for match_id, start, end in matches:
#             skill_name = self.nlp.vocab.strings[match_id]
            
#             # Skip if already extracted
#             if skill_name in seen_skills:
#                 continue
            
#             seen_skills.add(skill_name)
            
#             # Get the matched span
#             span = doc[start:end]
            
#             # Analyze context around the match
#             context = self._get_context(doc, start, end, window=20)
            
#             # Classify requirement level
#             requirement_level = self._classify_requirement(context)
            
#             # Extract experience level if mentioned
#             experience = self._extract_experience(context, skill_name)
            
#             # Calculate confidence score
#             confidence = self._calculate_confidence(span, context)
            
#             # Build skill dict
#             skill_dict = {
#                 'skill_name': skill_name,
#                 'skill_category': self.taxonomy[skill_name]['category'],
#                 'skill_subcategory': 'General',
#                 'extraction_confidence': confidence,
#                 'is_required': requirement_level == 'required',
#                 'requirement_level': requirement_level,  # required, preferred, optional
#                 'experience_years': experience,
#                 'context_snippet': context[:100]  # First 100 chars of context
#             }
            
#             extracted_skills.append(skill_dict)
        
#         return extracted_skills
    
#     # def _get_context(self, doc, start: int, end: int, window: int = 20) -> str:
#     #     """Get surrounding context for a match"""
#     #     context_start = max(0, start - window)
#     #     context_end = min(len(doc), end + window)
        
#     #     context_span = doc[context_start:context_end]
#     #     return context_span.text
#     def _get_context(self, doc, start: int, end: int, window: int = 30) -> str:
#         """Get surrounding context for a match (increased window)"""
#         context_start = max(0, start - window)
#         context_end = min(len(doc), end + window)
        
#         context_span = doc[context_start:context_end]
#         return context_span.text

    
#     # def _classify_requirement(self, context: str) -> str:
#     #     """
#     #     Classify if skill is required, preferred, or optional
        
#     #     Returns: 'required', 'preferred', or 'optional'
#     #     """
#     #     context_lower = context.lower()
        
#     #     # Check for required keywords
#     #     for pattern in self.required_patterns:
#     #         if pattern in context_lower:
#     #             return 'required'
        
#     #     # Check for preferred keywords
#     #     for pattern in self.preferred_patterns:
#     #         if pattern in context_lower:
#     #             return 'preferred'
        
#     #     # Default to optional if no clear signal
#     #     return 'optional'

#     def _classify_requirement(self, context: str) -> str:
#         """
#         Improved classification with better pattern matching
        
#         Returns: 'required', 'preferred', or 'optional'
#         """
#         context_lower = context.lower()
        
#         # Strongest signals first - explicit required indicators
#         strong_required = [
#             'required skills:', 'must have', 'must-have', 'essential', 
#             'mandatory', 'required:', 'requirements:', 'necessary'
#         ]
        
#         for pattern in strong_required:
#             if pattern in context_lower:
#                 return 'required'
        
#         # Check for "must" or "need" verbs near the skill
#         if re.search(r'\b(must|need|needs|needed|require|requires|required)\b', context_lower):
#             # Make sure it's not negated or in a "nice to have" section
#             if 'nice to have' not in context_lower and 'preferred' not in context_lower:
#                 return 'required'
        
#         # Preferred indicators
#         preferred_patterns = [
#             'nice to have:', 'preferred:', 'preferred skills:', 
#             'bonus:', 'plus:', 'advantageous', 'beneficial',
#             'nice-to-have', 'desirable', 'ideal'
#         ]
        
#         for pattern in preferred_patterns:
#             if pattern in context_lower:
#                 return 'preferred'
        
#         # Check for weak preference indicators
#         if any(word in context_lower for word in ['plus', 'bonus', 'ideal']):
#             return 'preferred'
        
#         # Default to optional if no clear signal
#         return 'optional'


    
#     def _extract_experience(self, context: str, skill_name: str) -> int:
#         """
#         Extract experience level for a skill
        
#         Returns: Number of years, or 0 if not mentioned
#         """
#         # Look for patterns like "5+ years of Python" or "3 years SQL experience"
#         matches = self.experience_pattern.findall(context)
        
#         if matches:
#             # Return the first number found
#             try:
#                 return int(matches[0])
#             except:
#                 pass
        
#         return 0
    
#     def _calculate_confidence(self, span, context: str) -> float:
#         """
#         Calculate confidence score for extraction
        
#         Factors:
#         - Exact match vs fuzzy match
#         - Context clarity
#         - Surrounding keywords
#         """
#         confidence = 0.7  # Base confidence
        
#         # Boost if in a clear "skills" section
#         context_lower = context.lower()
#         if any(keyword in context_lower for keyword in ['skills:', 'requirements:', 'qualifications:']):
#             confidence += 0.15
        
#         # Boost if requirement level is clear
#         if any(pattern in context_lower for pattern in self.required_patterns + self.preferred_patterns):
#             confidence += 0.10
        
#         # Boost if part of a list structure
#         if any(char in context for char in ['•', '-', '*', '·']):
#             confidence += 0.05
        
#         return min(1.0, confidence)


# # Self-test
# if __name__ == "__main__":
#     print("🧪 Testing Context-Aware Skill Extractor...\n")
    
#     extractor = ContextAwareSkillExtractor()
    
#     # Test 1: Simple extraction
#     print("1️⃣ Test: Basic Extraction")
#     test_desc_1 = """
#     We are seeking a Financial Analyst.
#     Required Skills: SQL, Python, Excel
#     Nice to have: Power BI, Tableau
#     """
#     skills_1 = extractor.extract_skills(test_desc_1)
#     print(f"   ✅ Found {len(skills_1)} skills")
    
#     for skill in skills_1:
#         print(f"      - {skill['skill_name']}: {skill['requirement_level']} (confidence: {skill['extraction_confidence']:.2f})")
    
#     # Test 2: Experience extraction
#     print("\n2️⃣ Test: Experience Extraction")
#     test_desc_2 = """
#     Must have 5+ years of SQL experience.
#     Python with 3 years experience required.
#     Excel is preferred.
#     """
#     skills_2 = extractor.extract_skills(test_desc_2)
#     print(f"   ✅ Found {len(skills_2)} skills")
    
#     for skill in skills_2:
#         exp_text = f", {skill['experience_years']}+ years" if skill['experience_years'] > 0 else ""
#         print(f"      - {skill['skill_name']}: {skill['requirement_level']}{exp_text}")
    
#     # Test 3: Context awareness
#     print("\n3️⃣ Test: Context Awareness")
#     test_desc_3 = """
#     Key Requirements:
#     • Must have strong SQL and data analysis skills
#     • Python is a plus but not required
#     • Financial modeling experience essential
    
#     Nice to have:
#     • Machine Learning knowledge
#     • AWS or Azure experience
#     """
#     skills_3 = extractor.extract_skills(test_desc_3)
#     print(f"   ✅ Found {len(skills_3)} skills")
    
#     required = [s for s in skills_3 if s['requirement_level'] == 'required']
#     preferred = [s for s in skills_3 if s['requirement_level'] == 'preferred']
#     optional = [s for s in skills_3 if s['requirement_level'] == 'optional']
    
#     print(f"      Required: {[s['skill_name'] for s in required]}")
#     print(f"      Preferred: {[s['skill_name'] for s in preferred]}")
#     print(f"      Optional: {[s['skill_name'] for s in optional]}")
    
#     print("\n" + "="*50)
#     print("🎉 CONTEXT-AWARE EXTRACTOR WORKING!")
#     print("="*50)



"""
Context-Aware Skill Extractor - Fixed Version
Robust section detection and classification
"""

import sys
from pathlib import Path
import re

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import spacy
from spacy.matcher import PhraseMatcher
from src.nlp.skill_taxonomy import SKILL_TAXONOMY

class ContextAwareSkillExtractor:
    """Context-aware skill extraction with robust section detection"""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize with spaCy model"""
        print(f"🧠 Loading spaCy model: {model_name}...")
        try:
            self.nlp = spacy.load(model_name)
        except:
            print(f"   ⚠️  {model_name} not found, using en_core_web_sm...")
            self.nlp = spacy.load("en_core_web_sm")
        
        self.taxonomy = SKILL_TAXONOMY
        
        # Build phrase matcher
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        self._build_skill_patterns()
        
        # Regex patterns
        self.experience_pattern = re.compile(
            r'(\d+)\+?\s*(?:years?|yrs?)',
            re.IGNORECASE
        )
        
        print(f"✅ Loaded {len(self.taxonomy)} skills into matcher")
    
    def _build_skill_patterns(self):
        """Build phrase patterns for skills"""
        for skill_name, skill_info in self.taxonomy.items():
            patterns = [self.nlp(skill_name.lower())]
            for synonym in skill_info['synonyms']:
                patterns.append(self.nlp(synonym.lower()))
            self.matcher.add(skill_name, patterns)
    
    def extract_skills(self, job_description: str, job_title: str = "") -> list:
        """Extract skills with section-aware classification"""
        full_text = f"{job_title}. {job_description}"
        
        # Split text into sections
        sections = self._split_into_sections(full_text)
        
        # Process with spaCy
        doc = self.nlp(full_text)
        matches = self.matcher(doc)
        
        extracted_skills = []
        seen_skills = set()
        
        for match_id, start, end in matches:
            skill_name = self.nlp.vocab.strings[match_id]
            
            if skill_name in seen_skills:
                continue
            seen_skills.add(skill_name)
            
            span = doc[start:end]
            
            # Get local context
            context = self._get_context(doc, start, end, window=40)
            
            # Find which section this skill is in
            skill_text = span.text
            section_type = self._find_section_for_skill(skill_text, sections)
            
            # Classify requirement level
            requirement_level = self._classify_requirement(context, section_type)
            
            # Extract experience
            experience = self._extract_experience(context)
            
            # Calculate confidence
            confidence = self._calculate_confidence(context, section_type)
            
            skill_dict = {
                'skill_name': skill_name,
                'skill_category': self.taxonomy[skill_name]['category'],
                'skill_subcategory': 'General',
                'extraction_confidence': confidence,
                'is_required': requirement_level == 'required',
                'requirement_level': requirement_level,
                'experience_years': experience,
                'context_snippet': context[:100]
            }
            
            extracted_skills.append(skill_dict)
        
        return extracted_skills
    
    def _split_into_sections(self, text: str) -> dict:
        """
        Split text into sections based on headers
        Returns: dict of {section_type: text_content}
        """
        sections = {'required': [], 'preferred': [], 'unknown': []}
        
        lines = text.split('\n')
        current_section = 'unknown'
        
        for line in lines:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            # Check for section headers
            if any(header in line_lower for header in [
                'required skills:', 'requirements:', 'must have:', 
                'key requirements:', 'essential skills:', 'mandatory skills:'
            ]):
                current_section = 'required'
                continue
            
            elif any(header in line_lower for header in [
                'nice to have:', 'preferred skills:', 'preferred:', 
                'bonus skills:', 'plus:', 'nice-to-have:', 'optional skills:'
            ]):
                current_section = 'preferred'
                continue
            
            # Add content to current section
            if line_stripped:
                sections[current_section].append(line_stripped)
        
        # Join sections back into text
        return {
            'required': ' '.join(sections['required']),
            'preferred': ' '.join(sections['preferred']),
            'unknown': ' '.join(sections['unknown'])
        }
    
    def _find_section_for_skill(self, skill_text: str, sections: dict) -> str:
        """Find which section contains this skill"""
        skill_lower = skill_text.lower()
        
        # Check required section
        if skill_lower in sections['required'].lower():
            return 'required'
        
        # Check preferred section
        if skill_lower in sections['preferred'].lower():
            return 'preferred'
        
        # Not found in any specific section
        return 'unknown'
    
    def _classify_requirement(self, context: str, section_type: str) -> str:
        """Classify requirement level"""
        # If we know the section, prioritize that
        if section_type == 'required':
            return 'required'
        elif section_type == 'preferred':
            return 'preferred'
        
        # Otherwise analyze local context
        context_lower = context.lower()
        
        # Check for strong required signals
        if any(word in context_lower for word in [
            'must have', 'must-have', 'required', 'essential', 
            'mandatory', 'need', 'necessary'
        ]):
            return 'required'
        
        # Check for preferred signals
        if any(word in context_lower for word in [
            'nice', 'preferred', 'plus', 'bonus', 'ideal', 'beneficial'
        ]):
            return 'preferred'
        
        return 'optional'
    
    def _get_context(self, doc, start: int, end: int, window: int = 40) -> str:
        """Get surrounding context"""
        context_start = max(0, start - window)
        context_end = min(len(doc), end + window)
        return doc[context_start:context_end].text
    
    def _extract_experience(self, context: str) -> int:
        """Extract experience years from context"""
        matches = self.experience_pattern.findall(context)
        if matches:
            try:
                return int(matches[0])
            except:
                pass
        return 0
    
    def _calculate_confidence(self, context: str, section_type: str) -> float:
        """Calculate extraction confidence"""
        confidence = 0.75
        
        # Boost if in a known section
        if section_type in ['required', 'preferred']:
            confidence += 0.15
        
        # Boost for structured content
        context_lower = context.lower()
        if any(kw in context_lower for kw in ['skills:', 'requirements:', 'qualifications:']):
            confidence += 0.05
        
        # Boost for list structures
        if any(char in context for char in ['•', '-', '*', '·']):
            confidence += 0.05
        
        return min(1.0, confidence)


# Self-test
if __name__ == "__main__":
    print("🧪 Testing Context-Aware Skill Extractor...\n")
    
    extractor = ContextAwareSkillExtractor()
    
    # Test 1
    print("1️⃣ Test: Section Detection")
    test_1 = """
    Required Skills: SQL, Python, Excel
    Nice to have: Power BI, Tableau
    """
    skills_1 = extractor.extract_skills(test_1)
    print(f"   ✅ Found {len(skills_1)} skills")
    for s in skills_1:
        print(f"      - {s['skill_name']}: {s['requirement_level']}")
    
    # Test 2
    print("\n2️⃣ Test: Experience Extraction")
    test_2 = """
    Requirements:
    - Must have 5+ years of SQL
    - Python with 3 years required
    - Excel preferred
    """
    skills_2 = extractor.extract_skills(test_2)
    print(f"   ✅ Found {len(skills_2)} skills")
    for s in skills_2:
        exp = f", {s['experience_years']}+ years" if s['experience_years'] > 0 else ""
        print(f"      - {s['skill_name']}: {s['requirement_level']}{exp}")
    
    # Test 3
    print("\n3️⃣ Test: Clear Sections")
    test_3 = """
    Key Requirements:
    • SQL
    • Data Analysis
    • Financial Modeling
    
    Nice to have:
    • Python
    • Machine Learning
    • AWS or Azure
    """
    skills_3 = extractor.extract_skills(test_3)
    print(f"   ✅ Found {len(skills_3)} skills")
    
    required = [s['skill_name'] for s in skills_3 if s['requirement_level'] == 'required']
    preferred = [s['skill_name'] for s in skills_3 if s['requirement_level'] == 'preferred']
    optional = [s['skill_name'] for s in skills_3 if s['requirement_level'] == 'optional']
    
    print(f"      Required ({len(required)}): {required}")
    print(f"      Preferred ({len(preferred)}): {preferred}")
    print(f"      Optional ({len(optional)}): {optional}")
    
    print("\n" + "="*50)
    print("🎉 EXTRACTOR READY!")
    print("="*50)
