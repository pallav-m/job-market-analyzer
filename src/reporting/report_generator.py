"""
Report Generator - Step 5
Generate markdown report with findings
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.analysis.analyzer import JobMarketAnalyzer
import config

class ReportGenerator:
    """Generate analysis report"""
    
    def __init__(self, output_path: str):
        """Initialize with output path"""
        self.output_path = Path(output_path)
        self.analyzer = JobMarketAnalyzer(config.DB_PATH)
    
    def generate_report(self):
        """Generate complete report"""
        print("📝 Generating Report...\n")
        
        # Get data
        stats = self.analyzer.get_summary_stats()
        top_skills = self.analyzer.get_top_skills(20)
        ai_adoption = self.analyzer.get_ai_adoption_by_geography()
        
        # Build report
        report = []
        report.append("# Finance/Fintech Job Market Analysis Report")
        report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("\n---\n")
        
        # Executive Summary
        report.append("## Executive Summary\n")
        report.append(f"- **Total Jobs Analyzed:** {stats['total_jobs']}")
        report.append(f"- **Unique Skills Identified:** {stats['unique_skills']}")
        report.append(f"- **Average Skills per Job:** {stats['avg_skills_per_job']}")
        report.append(f"- **Jobs Processed:** {stats['processed_jobs']}/{stats['total_jobs']}\n")
        
        # Geographic Distribution
        report.append("### Geographic Distribution\n")
        for country, count in stats['jobs_by_country'].items():
            pct = round(100 * count / stats['total_jobs'], 1)
            report.append(f"- **{country}:** {count} jobs ({pct}%)")
        report.append("\n")
        
        # Category Distribution
        report.append("### Job Category Distribution\n")
        for category, count in stats['jobs_by_category'].items():
            pct = round(100 * count / stats['total_jobs'], 1)
            report.append(f"- **{category}:** {count} jobs ({pct}%)")
        report.append("\n---\n")
        
        # Top Skills
        report.append("## Top In-Demand Skills\n")
        report.append("| Rank | Skill | Mentions | Category | Required % |")
        report.append("|------|-------|----------|----------|------------|")
        
        for i, skill in enumerate(top_skills, 1):
            report.append(f"| {i} | **{skill['skill_name']}** | {skill['mention_count']} | {skill['skill_category']} | {skill['required_pct']}% |")
        
        report.append("\n")
        
        # AI Adoption
        report.append("## AI & Emerging Tech Adoption\n")
        report.append("| Country | Total Jobs | AI/Tech Jobs | Adoption % |")
        report.append("|---------|------------|--------------|------------|")
        
        for geo in ai_adoption:
            report.append(f"| {geo['location_country']} | {geo['total_jobs']} | {geo['ai_jobs']} | {geo['ai_adoption_pct']}% |")
        
        report.append("\n")

        # NEW: Requirement Level Distribution
        report.append("## Skills by Requirement Level\n")
        
        req_query = '''
        SELECT 
            requirement_level,
            COUNT(*) as count,
            ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM extracted_skills), 1) as pct
        FROM extracted_skills
        GROUP BY requirement_level
        ORDER BY count DESC
        '''
        req_levels = self.analyzer.db.execute_query(req_query)
        
        report.append("| Level | Mentions | Percentage |")
        report.append("|-------|----------|------------|")
        for level in req_levels:
            report.append(f"| **{level['requirement_level'].title()}** | {level['count']} | {level['pct']}% |")
        
        report.append("\n")
        
        # NEW: Experience Requirements
        report.append("## Skills with Experience Requirements\n")
        
        exp_query = '''
        SELECT 
            skill_name, 
            ROUND(AVG(experience_years), 1) as avg_years, 
            COUNT(*) as mentions
        FROM extracted_skills
        WHERE experience_years > 0
        GROUP BY skill_name
        ORDER BY mentions DESC
        LIMIT 10
        '''
        exp_skills = self.analyzer.db.execute_query(exp_query)
        
        if exp_skills:
            report.append("| Skill | Avg Years Required | Mentions |")
            report.append("|-------|-------------------|----------|")
            for skill in exp_skills:
                report.append(f"| **{skill['skill_name']}** | {skill['avg_years']} years | {skill['mentions']} |")
        else:
            report.append("*No experience requirements detected in current dataset.*")
        
        report.append("\n")

        
        # Key Findings
        report.append("## Key Findings\n")
        
        # Find top skill
        if top_skills:
            top_skill = top_skills[0]
            report.append(f"1. **Most In-Demand Skill:** {top_skill['skill_name']} appears in {top_skill['mention_count']} job postings")
        
        # Calculate tech skills adoption
        tech_skills = ['SQL', 'Python', 'Power BI', 'Tableau', 'R']
        tech_count = sum(s['mention_count'] for s in top_skills if s['skill_name'] in tech_skills)
        report.append(f"2. **Tech Skills Prevalence:** {len([s for s in top_skills if s['skill_name'] in tech_skills])} of top 20 skills are technical")
        
        # AI adoption
        if ai_adoption:
            avg_ai = sum(g['ai_adoption_pct'] for g in ai_adoption) / len(ai_adoption)
            report.append(f"3. **AI/Emerging Tech:** Average {avg_ai:.1f}% of jobs require AI or cloud skills")
        
        report.append("\n---\n")
        
        # Recommendations
        report.append("## Recommendations\n")
        report.append("Based on this analysis:\n")
        report.append(f"1. **Priority Topic 1:** {top_skills[0]['skill_name']} - Highest demand with {top_skills[0]['mention_count']} mentions")
        report.append(f"2. **Priority Topic 2:** {top_skills[1]['skill_name']} - {top_skills[1]['mention_count']} mentions across categories")
        report.append(f"3. **Priority Topic 3:** {top_skills[2]['skill_name']} - {top_skills[2]['mention_count']} mentions")
        report.append("\n**Conclusion:** Strong demand for finance + analytics roles. Launch category is **recommended**.")

        # Source distribution
        report.append("### Data Sources\n")
        
        source_query = '''
        SELECT source, COUNT(*) as count
        FROM job_postings
        GROUP BY source
        ORDER BY count DESC
        '''
        sources = self.analyzer.db.execute_query(source_query)
        
        for row in sources:
            report.append(f"- **{row['source']}:** {row['count']} jobs")
        
        report.append("\n")

        
        report.append("\n---\n")
        report.append("*Report generated by Finance Job Market POC*")
        
        # Write to file
        with open(self.output_path, 'w') as f:
            f.write('\n'.join(report))
        
        print(f"✅ Report saved: {self.output_path}\n")
        
        return str(self.output_path)
    
    def close(self):
        """Close analyzer"""
        self.analyzer.close()


# Self-test
if __name__ == "__main__":
    print("🧪 Testing Report Generator...\n")
    
    output_file = config.OUTPUTS_DIR / "analysis_report.md"
    generator = ReportGenerator(output_file)
    report_path = generator.generate_report()
    generator.close()
    
    print("="*50)
    print("🎉 REPORT GENERATION COMPLETE!")
    print("="*50)
    print(f"\nReport available at: {report_path}")
