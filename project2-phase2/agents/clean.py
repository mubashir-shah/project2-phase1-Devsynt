import pandas as pd
from typing import Dict, Tuple

class CleanAgent:
    """Handles data cleaning - missing values, data types, duplicates"""
    
    def __init__(self):
        self.name = "CleanAgent"
    
    def clean(self, csv_path: str) -> Tuple[pd.DataFrame, Dict]:
        """
        Clean the raw retail dataset
        Returns: (cleaned_dataframe, cleaning_report)
        """
        # Load raw data
        df = pd.read_csv(csv_path)
        
        print(f"\n{'='*50}")
        print(f"CLEAN AGENT: Starting data cleaning")
        print(f"{'='*50}")
        
        # Report before cleaning
        print(f"\nBEFORE CLEANING:")
        print(f"  - Total records: {len(df)}")
        print(f"  - Missing values:\n{df.isnull().sum()}")
        print(f"  - Duplicates: {df.duplicated().sum()}")
        print(f"  - Data types:\n{df.dtypes}")
        
        # Store original state for reporting
        original_records = len(df)
        original_missing = df.isnull().sum().sum()
        
        # Step 1: Remove duplicates
        df = df.drop_duplicates()
        duplicates_removed = original_records - len(df)
        
        # Step 2: Handle missing values
        df = df.dropna()
        missing_handled = len(df)
        
        # Step 3: Fix data types
        df['Date'] = pd.to_datetime(df['Date'])
        df['Quantity'] = df['Quantity'].astype(int)
        df['UnitPrice'] = df['UnitPrice'].astype(float)
        df['Sales'] = df['Sales'].astype(float)
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Report after cleaning
        print(f"\nAFTER CLEANING:")
        print(f"  - Total records: {len(df)}")
        print(f"  - Missing values: {df.isnull().sum().sum()}")
        print(f"  - Duplicates: {df.duplicated().sum()}")
        print(f"  - Data types:\n{df.dtypes}")
        
        # Create report
        report = {
            'agent': self.name,
            'original_records': original_records,
            'cleaned_records': len(df),
            'duplicates_removed': duplicates_removed,
            'missing_rows_removed': original_records - len(df) - duplicates_removed,
            'data_types_fixed': True
        }
        
        print(f"\n✓ Cleaning complete!")
        
        return df, report
