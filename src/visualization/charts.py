"""
Charts - Step 5
Generate visualizations using matplotlib
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
from src.analysis.analyzer import JobMarketAnalyzer
import config

class ChartGenerator:
    """Generate charts for job market analysis"""
    
    def __init__(self, output_dir: str):
        """Initialize with output directory"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.analyzer = JobMarketAnalyzer(config.DB_PATH)
    
    def generate_top_skills_chart(self, limit: int = 15):
        """Generate bar chart of top skills"""
        print("📊 Generating top skills chart...")
        
        skills = self.analyzer.get_top_skills(limit)
        
        skill_names = [s['skill_name'] for s in skills]
        counts = [s['mention_count'] for s in skills]
        
        plt.figure(figsize=(12, 8))
        plt.barh(skill_names, counts, color='steelblue')
        plt.xlabel('Number of Job Postings', fontsize=12)
        plt.ylabel('Skills', fontsize=12)
        plt.title(f'Top {limit} In-Demand Skills', fontsize=14, fontweight='bold')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        
        output_path = self.output_dir / 'top_skills.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✅ Saved: {output_path}")
        return str(output_path)
    
    def generate_ai_adoption_chart(self):
        """Generate bar chart of AI adoption by geography"""
        print("📊 Generating AI adoption chart...")
        
        adoption = self.analyzer.get_ai_adoption_by_geography()
        
        countries = [a['location_country'] for a in adoption]
        percentages = [a['ai_adoption_pct'] for a in adoption]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(countries, percentages, color=['#2ecc71', '#3498db', '#e74c3c'])
        plt.xlabel('Country', fontsize=12)
        plt.ylabel('AI/Tech Skills Adoption (%)', fontsize=12)
        plt.title('AI & Emerging Tech Adoption by Geography', fontsize=14, fontweight='bold')
        plt.ylim(0, 100)
        
        # Add percentage labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%',
                    ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        output_path = self.output_dir / 'ai_adoption.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✅ Saved: {output_path}")
        return str(output_path)
    
    def generate_skills_by_category_chart(self):
        """Generate stacked bar of skills by job category"""
        print("📊 Generating skills by category chart...")
        
        # Get top 5 skills overall
        top_skills = self.analyzer.get_top_skills(5)
        top_skill_names = [s['skill_name'] for s in top_skills]
        
        # Get skills by category
        category_data = self.analyzer.get_skills_by_category()
        
        # Organize data
        categories = list(set([d['job_category'] for d in category_data]))
        
        data = {skill: [0] * len(categories) for skill in top_skill_names}
        
        for row in category_data:
            if row['skill_name'] in top_skill_names:
                cat_idx = categories.index(row['job_category'])
                data[row['skill_name']][cat_idx] = row['count']
        
        # Create chart
        plt.figure(figsize=(12, 6))
        x = range(len(categories))
        width = 0.15
        
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        
        for i, (skill, counts) in enumerate(data.items()):
            offset = width * (i - 2)
            plt.bar([p + offset for p in x], counts, width, label=skill, color=colors[i])
        
        plt.xlabel('Job Category', fontsize=12)
        plt.ylabel('Skill Mentions', fontsize=12)
        plt.title('Top Skills by Job Category', fontsize=14, fontweight='bold')
        plt.xticks(x, categories, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        
        output_path = self.output_dir / 'skills_by_category.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✅ Saved: {output_path}")
        return str(output_path)
    
    def generate_all_charts(self):
        """Generate all charts"""
        print("\n🎨 Generating All Charts...\n")
        
        charts = []
        charts.append(self.generate_top_skills_chart())
        charts.append(self.generate_ai_adoption_chart())
        charts.append(self.generate_skills_by_category_chart())
        
        print(f"\n✅ Generated {len(charts)} charts")
        return charts
    
    def close(self):
        """Close analyzer connection"""
        self.analyzer.close()


# Self-test
if __name__ == "__main__":
    print("🧪 Testing Chart Generator...\n")
    
    generator = ChartGenerator(config.OUTPUTS_DIR)
    charts = generator.generate_all_charts()
    generator.close()
    
    print("\n" + "="*50)
    print("🎉 CHART GENERATION COMPLETE!")
    print("="*50)
    print(f"\nCheck {config.OUTPUTS_DIR} for generated charts")
