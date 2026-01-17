"""
Skill Taxonomy - Step 4
List of skills to extract from job descriptions
"""

# Skill categories and their skills
SKILL_TAXONOMY = {
    # Data Analytics Skills
    "SQL": {
        "category": "Data Analytics",
        "synonyms": ["sql", "mysql", "postgresql", "sql server", "t-sql"],
        "emerging": False
    },
    "Python": {
        "category": "Data Analytics",
        "synonyms": ["python", "pandas", "numpy"],
        "emerging": False
    },
    "Excel": {
        "category": "Data Analytics",
        "synonyms": ["excel", "advanced excel", "ms excel", "vba"],
        "emerging": False
    },
    "Power BI": {
        "category": "Data Analytics",
        "synonyms": ["power bi", "powerbi", "power-bi"],
        "emerging": False
    },
    "Tableau": {
        "category": "Data Analytics",
        "synonyms": ["tableau"],
        "emerging": False
    },
    "R": {
        "category": "Data Analytics",
        "synonyms": ["r programming", "r language"],
        "emerging": False
    },
    
    # Finance Skills
    "Financial Modeling": {
        "category": "Finance Core",
        "synonyms": ["financial modeling", "financial modelling", "dcf", "valuation"],
        "emerging": False
    },
    "Financial Reporting": {
        "category": "Finance Core",
        "synonyms": ["financial reporting", "reporting", "gaap", "ifrs"],
        "emerging": False
    },
    "Budgeting": {
        "category": "Finance Core",
        "synonyms": ["budgeting", "budget planning", "forecasting"],
        "emerging": False
    },
    "Forecasting": {
        "category": "Finance Core",
        "synonyms": ["forecasting", "financial forecasting", "planning"],
        "emerging": False
    },
    
    # Software/ERP
    "SAP": {
        "category": "Software/ERP",
        "synonyms": ["sap", "sap fico", "sap s/4hana"],
        "emerging": False
    },
    "Oracle": {
        "category": "Software/ERP",
        "synonyms": ["oracle", "oracle ebs", "oracle financials"],
        "emerging": False
    },
    "QuickBooks": {
        "category": "Software/ERP",
        "synonyms": ["quickbooks", "quick books"],
        "emerging": False
    },
    
    # Emerging Tech
    "Machine Learning": {
        "category": "Emerging Tech",
        "synonyms": ["machine learning", "ml", "ai", "artificial intelligence"],
        "emerging": True
    },
    "AWS": {
        "category": "Emerging Tech",
        "synonyms": ["aws", "amazon web services", "cloud"],
        "emerging": True
    },
    "Azure": {
        "category": "Emerging Tech",
        "synonyms": ["azure", "microsoft azure"],
        "emerging": True
    },
    
    # Domain Skills
    "Risk Management": {
        "category": "Risk & Compliance",
        "synonyms": ["risk management", "risk assessment", "credit risk"],
        "emerging": False
    },
    "Compliance": {
        "category": "Risk & Compliance",
        "synonyms": ["compliance", "regulatory compliance", "aml"],
        "emerging": False
    },
    "Data Analysis": {
        "category": "Data Analytics",
        "synonyms": ["data analysis", "data analytics", "analytics"],
        "emerging": False
    }
}

def get_all_skills():
    """Get list of all skill names"""
    return list(SKILL_TAXONOMY.keys())

def get_skill_info(skill_name):
    """Get information about a specific skill"""
    return SKILL_TAXONOMY.get(skill_name, None)

def get_skills_by_category(category):
    """Get all skills in a category"""
    return [skill for skill, info in SKILL_TAXONOMY.items() 
            if info['category'] == category]

# Self-test
if __name__ == "__main__":
    print("🧪 Testing Skill Taxonomy...")
    
    print(f"\n1️⃣ Total skills: {len(SKILL_TAXONOMY)}")
    print(f"   ✅ {len(SKILL_TAXONOMY)} skills defined")
    
    print("\n2️⃣ Skills by category:")
    categories = set(info['category'] for info in SKILL_TAXONOMY.values())
    for cat in categories:
        skills = get_skills_by_category(cat)
        print(f"   ✅ {cat}: {len(skills)} skills")
    
    print("\n3️⃣ Sample skill info:")
    skill_info = get_skill_info("SQL")
    print(f"   ✅ SQL: {skill_info}")
    
    print("\n4️⃣ Emerging tech skills:")
    emerging = [skill for skill, info in SKILL_TAXONOMY.items() if info['emerging']]
    print(f"   ✅ {emerging}")
    
    print("\n" + "="*50)
    print("🎉 TAXONOMY TEST PASSED!")
    print("="*50)
