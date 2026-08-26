import pandas as pd
from typing import Dict, Any
from agents.clean import CleanAgent
from agents.analysis import AnalysisAgent

class OrchestratorAgent:
    """
    Manager agent that orchestrates the workflow
    Routes data: Raw CSV -> Clean Agent -> Analysis Agent
    """
    
    def __init__(self):
        self.name = "OrchestratorAgent"
        self.clean_agent = CleanAgent()
        self.analysis_agent = AnalysisAgent()
        self.state = {}
    
    def orchestrate(self, csv_path: str) -> Dict[str, Any]:
        """
        Main orchestration function
        Coordinates the data pipeline
        """
        print(f"\n{'='*60}")
        print(f"ORCHESTRATOR AGENT: Starting multi-agent pipeline")
        print(f"{'='*60}")
        print(f"\nInput CSV: {csv_path}")
        
        # Step 1: Raw data loading
        print(f"\n[STEP 1] Loading raw data...")
        raw_df = pd.read_csv(csv_path)
        self.state['raw_data'] = raw_df
        self.state['raw_record_count'] = len(raw_df)
        print(f"✓ Raw data loaded: {len(raw_df)} records")
        
        # Step 2: Route to Clean Agent
        print(f"\n[STEP 2] Routing to CLEAN AGENT...")
        cleaned_df, clean_report = self.clean_agent.clean(csv_path)
        self.state['cleaned_data'] = cleaned_df
        self.state['clean_report'] = clean_report
        print(f"✓ Data cleaned: {len(cleaned_df)} records after cleaning")
        
        # Step 3: Route to Analysis Agent
        print(f"\n[STEP 3] Routing to ANALYSIS AGENT...")
        insights = self.analysis_agent.analyze(cleaned_df)
        self.state['analysis_insights'] = insights
        print(f"✓ Analysis complete")
        
        # Final summary
        print(f"\n{'='*60}")
        print(f"ORCHESTRATOR: Pipeline execution complete!")
        print(f"{'='*60}")
        print(f"\nPipeline Summary:")
        print(f"  - Raw records: {self.state['raw_record_count']}")
        print(f"  - Cleaned records: {len(cleaned_df)}")
        print(f"  - Records removed: {self.state['raw_record_count'] - len(cleaned_df)}")
        print(f"  - Total sales: ${insights['total_sales']:,.2f}")
        
        return self.state
