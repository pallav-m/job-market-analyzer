"""
Configuration for Finance Job Market POC
Step 2 - Minimal Version
"""

from pathlib import Path

# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
LOGS_DIR = OUTPUTS_DIR / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, OUTPUTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DB_PATH = str(DATA_DIR / "job_postings.db")
DB_TYPE = "sqlite3"
DB_TIMEOUT = 10  # seconds

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate configuration"""
    assert PROJECT_ROOT.exists(), "Project root not found"
    assert DATA_DIR.exists(), "Data directory not created"
    assert OUTPUTS_DIR.exists(), "Outputs directory not created"
    print("✅ Configuration validated successfully")
    print(f"   Database path: {DB_PATH}")
    print(f"   Data directory: {DATA_DIR}")
    print(f"   Output directory: {OUTPUTS_DIR}")
    return True


# ============================================================================
# JOB CATEGORIES
# ============================================================================

JOB_CATEGORIES = {
    "traditional_finance": {
        "label": "Traditional Finance",
        "keywords": ["Financial Analyst", "FP&A Analyst", "Finance Manager", "Accounting Analyst"]
    },
    "analytics_data": {
        "label": "Finance + Analytics",
        "keywords": ["Finance Data Analyst", "Business Analyst Finance", "Analytics Manager"]
    },
    "risk_compliance": {
        "label": "Risk & Compliance",
        "keywords": ["Risk Analyst", "Credit Risk Analyst", "Compliance Analyst"]
    },
    "fintech": {
        "label": "FinTech",
        "keywords": ["FinTech Analyst", "Payments Analyst", "Lending Analyst"]
    }
}

# ============================================================================
# GEOGRAPHIC TARGETS
# ============================================================================

GEOGRAPHIC_TARGETS = {
    "India": ["Mumbai", "Bengaluru", "Pune", "Chennai", "Hyderabad"],
    "USA": ["New York", "San Francisco", "Chicago", "Boston"],
    "UK": ["London", "Manchester", "Edinburgh"]
}


if __name__ == "__main__":
    validate_config()
