"""
Main Orchestrator - Complete POC Pipeline
"""

from src.analysis.analyzer import JobMarketAnalyzer
from src.visualization.charts import ChartGenerator
from src.reporting.report_generator import ReportGenerator
import config

def main():
    """Run complete analysis pipeline"""
    
    print("\n" + "="*60)
    print("  FINANCE JOB MARKET ANALYSIS - COMPLETE PIPELINE")
    print("="*60 + "\n")
    
    try:
        # Step 1: Analysis
        print("📊 STEP 1: Running Analysis...")
        analyzer = JobMarketAnalyzer(config.DB_PATH)
        stats = analyzer.get_summary_stats()
        print(f"   ✅ Analyzed {stats['total_jobs']} jobs")
        print(f"   ✅ Found {stats['unique_skills']} unique skills\n")
        analyzer.close()
        
        # Step 2: Visualization
        print("🎨 STEP 2: Generating Charts...")
        chart_gen = ChartGenerator(config.OUTPUTS_DIR)
        charts = chart_gen.generate_all_charts()
        chart_gen.close()
        print(f"   ✅ Generated {len(charts)} visualizations\n")
        
        # Step 3: Report
        print("📝 STEP 3: Generating Report...")
        report_path = config.OUTPUTS_DIR / "analysis_report.md"
        report_gen = ReportGenerator(report_path)
        report_gen.generate_report()
        report_gen.close()
        print(f"   ✅ Report saved\n")
        
        # Summary
        print("="*60)
        print("🎉 ANALYSIS COMPLETE!")
        print("="*60)
        print(f"\n📁 Outputs Location: {config.OUTPUTS_DIR}")
        print(f"\n   📊 Charts:")
        print(f"      - top_skills.png")
        print(f"      - ai_adoption.png")
        print(f"      - skills_by_category.png")
        print(f"\n   📝 Report:")
        print(f"      - analysis_report.md")
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
