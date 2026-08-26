import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

class VisualizationAgent:
    """Bonus agent - creates charts from analysis insights"""
    
    def __init__(self):
        self.name = "VisualizationAgent"
    
    def visualize(self, df: pd.DataFrame, insights: dict, output_dir: str = "assets"):
        """
        Generate bar/line/pie charts from insights
        Saves charts as PNG images in assets/
        """
        print(f"\n{'='*50}")
        print(f"VISUALIZATION AGENT: Creating charts")
        print(f"{'='*50}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Chart 1: Sales by Region (Bar Chart)
        plt.figure(figsize=(8, 5))
        regions = list(insights['sales_by_region'].keys())
        sales = list(insights['sales_by_region'].values())
        plt.bar(regions, sales, color=['#3b82f6', '#8b5cf6', '#10b981', '#f97316'])
        plt.title('Sales by Region', fontsize=14, fontweight='bold')
        plt.xlabel('Region')
        plt.ylabel('Sales ($)')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/chart-sales-by-region.png', dpi=100)
        plt.close()
        print(f"✓ Chart saved: chart-sales-by-region.png")
        
        # Chart 2: Sales by Category (Pie Chart)
        plt.figure(figsize=(7, 7))
        categories = list(insights['sales_by_category'].keys())
        cat_sales = list(insights['sales_by_category'].values())
        plt.pie(cat_sales, labels=categories, autopct='%1.1f%%', 
                colors=['#3b82f6', '#8b5cf6', '#10b981'])
        plt.title('Sales by Category', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/chart-sales-by-category.png', dpi=100)
        plt.close()
        print(f"✓ Chart saved: chart-sales-by-category.png")
        
        # Chart 3: Top Products (Bar Chart)
        plt.figure(figsize=(8, 5))
        products = list(insights['top_products'].keys())
        qty = list(insights['top_products'].values())
        plt.barh(products, qty, color='#3b82f6')
        plt.title('Top 5 Products by Quantity Sold', fontsize=14, fontweight='bold')
        plt.xlabel('Units Sold')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/chart-top-products.png', dpi=100)
        plt.close()
        print(f"✓ Chart saved: chart-top-products.png")
        
        # Chart 4: Sales Trend Over Time (Line Chart)
        plt.figure(figsize=(10, 5))
        df_sorted = df.sort_values('Date')
        monthly_sales = df_sorted.groupby(df_sorted['Date'].dt.to_period('M'))['Sales'].sum()
        monthly_sales.index = monthly_sales.index.astype(str)
        plt.plot(monthly_sales.index, monthly_sales.values, marker='o', color='#8b5cf6', linewidth=2)
        plt.title('Monthly Sales Trend', fontsize=14, fontweight='bold')
        plt.xlabel('Month')
        plt.ylabel('Sales ($)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/chart-sales-trend.png', dpi=100)
        plt.close()
        print(f"✓ Chart saved: chart-sales-trend.png")
        
        print(f"\n✓ All charts generated successfully!")
        
        return {
            'charts_created': 4,
            'location': output_dir
        }
