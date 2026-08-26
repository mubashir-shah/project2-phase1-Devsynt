import pandas as pd
from typing import Dict

class AnalysisAgent:
    """Generates key insights from cleaned data"""
    
    def __init__(self):
        self.name = "AnalysisAgent"
    
    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        Perform EDA and generate insights
        """
        print(f"\n{'='*50}")
        print(f"ANALYSIS AGENT: Starting data analysis")
        print(f"{'='*50}")
        
        insights = {}
        
        # 1. Total Sales
        total_sales = df['Sales'].sum()
        insights['total_sales'] = total_sales
        print(f"\n1. TOTAL SALES: ${total_sales:,.2f}")
        
        # 2. Best-Selling Products (by quantity)
        top_products = df.groupby('Product')['Quantity'].sum().sort_values(ascending=False).head(5)
        insights['top_products'] = top_products.to_dict()
        print(f"\n2. TOP 5 PRODUCTS (by quantity):")
        for product, qty in top_products.items():
            print(f"   - {product}: {qty} units")
        
        # 3. Sales by Region
        sales_by_region = df.groupby('Region')['Sales'].sum().sort_values(ascending=False)
        insights['sales_by_region'] = sales_by_region.to_dict()
        print(f"\n3. SALES BY REGION:")
        for region, sales in sales_by_region.items():
            print(f"   - {region}: ${sales:,.2f}")
        
        # 4. Sales by Category
        sales_by_category = df.groupby('Category')['Sales'].sum().sort_values(ascending=False)
        insights['sales_by_category'] = sales_by_category.to_dict()
        print(f"\n4. SALES BY CATEGORY:")
        for category, sales in sales_by_category.items():
            print(f"   - {category}: ${sales:,.2f}")
        
        # 5. Summary Statistics
        summary_stats = {
            'total_records': len(df),
            'total_quantity': df['Quantity'].sum(),
            'avg_transaction_value': df['Sales'].mean(),
            'max_sale': df['Sales'].max(),
            'min_sale': df['Sales'].min(),
            'date_range': f"{df['Date'].min()} to {df['Date'].max()}"
        }
        insights['summary_statistics'] = summary_stats
        print(f"\n5. SUMMARY STATISTICS:")
        print(f"   - Total Transactions: {summary_stats['total_records']}")
        print(f"   - Total Quantity Sold: {summary_stats['total_quantity']} units")
        print(f"   - Avg Transaction Value: ${summary_stats['avg_transaction_value']:,.2f}")
        print(f"   - Max Sale: ${summary_stats['max_sale']:,.2f}")
        print(f"   - Min Sale: ${summary_stats['min_sale']:,.2f}")
        print(f"   - Date Range: {summary_stats['date_range']}")
        
        print(f"\n✓ Analysis complete!")
        
        return insights
