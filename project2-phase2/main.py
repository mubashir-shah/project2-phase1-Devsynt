import os
import sys
from agents.orchestrator import OrchestratorAgent
from agents.visualization import VisualizationAgent

def main():
    csv_path = "data/retail_data.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV file not found at {csv_path}")
        sys.exit(1)
    
    # Run core pipeline (Orchestrator -> Clean -> Analysis)
    orchestrator = OrchestratorAgent()
    final_state = orchestrator.orchestrate(csv_path)
    
    # Save cleaned data
    final_state['cleaned_data'].to_csv('data/cleaned_data.csv', index=False)
    print(f"\n✓ Cleaned data saved: data/cleaned_data.csv")
    
    # Save insights as text
    insights = final_state['analysis_insights']
    with open('data/insights.txt', 'w') as f:
        f.write("RETAIL DATA ANALYSIS INSIGHTS\n")
        f.write("="*50 + "\n\n")
        f.write(f"Total Sales: ${insights['total_sales']:,.2f}\n\n")
        f.write("Top Products:\n")
        for product, qty in insights['top_products'].items():
            f.write(f"  - {product}: {qty} units\n")
        f.write("\nSales by Region:\n")
        for region, sales in insights['sales_by_region'].items():
            f.write(f"  - {region}: ${sales:,.2f}\n")
        f.write("\nSales by Category:\n")
        for category, sales in insights['sales_by_category'].items():
            f.write(f"  - {category}: ${sales:,.2f}\n")
        f.write("\nSummary Statistics:\n")
        for key, val in insights['summary_statistics'].items():
            f.write(f"  - {key}: {val}\n")
    
    print(f"✓ Insights saved: data/insights.txt")
    
    # Bonus: Run Visualization Agent
    viz_agent = VisualizationAgent()
    viz_result = viz_agent.visualize(final_state['cleaned_data'], insights, output_dir='assets')
    print(f"\n✓ Visualization complete: {viz_result['charts_created']} charts in {viz_result['location']}/")

if __name__ == "__main__":
    main()
