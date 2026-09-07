import pandas as pd
from typing import Dict

from agents.domain_config import DomainConfigAgent
from agents.clean import CleanAgent
from agents.analysis import AnalysisAgent


class OrchestratorAgent:
    """
    Production-grade orchestrator for the Phase 3
    domain-aware multi-agent analytics pipeline.

    Pipeline:
        DomainConfigAgent
              ↓
        CleanAgent
              ↓
        AnalysisAgent
              ↓
        DashboardAgent
    """

    def __init__(self):
        self.name = "OrchestratorAgent"

        self.domain_config_agent = DomainConfigAgent()
        self.clean_agent = CleanAgent()
        self.analysis_agent = AnalysisAgent()

    def orchestrate(self, csv_path: str) -> Dict:
        print("\n")
        print("=" * 70)
        print("ORCHESTRATOR AGENT: Starting Phase 3 Pipeline")
        print("=" * 70)

        pipeline_state = {
            "success": False,
            "status": "started",
            "dataset_path": csv_path,
            "domain_config": None,
            "domain": None,
            "raw_data": None,
            "cleaned_data": None,
            "clean_report": None,
            "analysis_insights": None,
            "error": None,
        }

        # ==============================================================
        # STEP 1: DOMAIN CONFIGURATION
        # ==============================================================

        print("\n[1/3] DOMAIN CONFIGURATION")

        try:
            domain_config = self.domain_config_agent.configure(csv_path)

            if not domain_config.get("success", False):
                error_message = domain_config.get(
                    "error",
                    "Domain configuration failed."
                )

                pipeline_state["status"] = "failed"
                pipeline_state["error"] = error_message

                print(f"\n✗ Domain configuration failed: {error_message}")

                return pipeline_state

            pipeline_state["domain_config"] = domain_config
            pipeline_state["domain"] = domain_config.get(
                "domain",
                "unknown"
            )

            print(
                f"\n✓ Domain configured: "
                f"{pipeline_state['domain']}"
            )

        except FileNotFoundError as e:
            pipeline_state["status"] = "failed"
            pipeline_state["error"] = str(e)

            print(f"\n✗ Error: {e}")

            return pipeline_state

        except Exception as e:
            pipeline_state["status"] = "failed"
            pipeline_state["error"] = (
                f"Domain configuration error: {e}"
            )

            print(
                f"\n✗ Domain configuration error: {e}"
            )

            return pipeline_state

        # ==============================================================
        # STEP 2: DATA CLEANING
        # ==============================================================

        print("\n[2/3] DATA CLEANING")

        try:
            raw_df = pd.read_csv(csv_path)

            if raw_df.empty:
                raise ValueError(
                    "Input dataset contains no records."
                )

            pipeline_state["raw_data"] = raw_df

            print(
                f"  Raw records: {len(raw_df)}"
            )

            cleaned_df, clean_report = self.clean_agent.clean(
                csv_path,
                pipeline_state["domain_config"]
            )

            if cleaned_df is None or cleaned_df.empty:
                raise ValueError(
                    "Cleaning produced an empty dataset."
                )

            pipeline_state["cleaned_data"] = cleaned_df
            pipeline_state["clean_report"] = clean_report

            print("\n✓ Cleaning completed")
            print(
                f"  Cleaned records: {len(cleaned_df)}"
            )

        except FileNotFoundError as e:
            pipeline_state["status"] = "failed"
            pipeline_state["error"] = str(e)

            print(f"\n✗ Error: {e}")

            return pipeline_state

        except pd.errors.EmptyDataError:
            pipeline_state["status"] = "failed"
            pipeline_state["error"] = (
                "Input CSV file is empty."
            )

            print(
                "\n✗ Error: Input CSV file is empty."
            )

            return pipeline_state

        except Exception as e:
            pipeline_state["status"] = "failed"
            pipeline_state["error"] = (
                f"Data cleaning error: {e}"
            )

            print(
                f"\n✗ Data cleaning error: {e}"
            )

            return pipeline_state

        # ==============================================================
        # STEP 3: DOMAIN-AWARE ANALYSIS
        # ==============================================================

        print("\n[3/3] DOMAIN-AWARE ANALYSIS")

        try:
            analysis_insights = self.analysis_agent.analyze(
                cleaned_df,
                pipeline_state["domain_config"]
            )

            if analysis_insights.get("status") != "success":
                raise ValueError(
                    analysis_insights.get(
                        "error",
                        "Analysis failed."
                    )
                )

            pipeline_state["analysis_insights"] = (
                analysis_insights
            )

            print("\n✓ Analysis completed")

        except Exception as e:
            pipeline_state["status"] = "failed"
            pipeline_state["error"] = (
                f"Analysis error: {e}"
            )

            print(
                f"\n✗ Analysis error: {e}"
            )

            return pipeline_state

        # ==============================================================
        # PIPELINE COMPLETED
        # ==============================================================

        pipeline_state["success"] = True
        pipeline_state["status"] = "completed"

        print("\n")
        print("=" * 70)
        print("ORCHESTRATOR: Pipeline completed successfully")
        print("=" * 70)

        self._print_pipeline_summary(pipeline_state)

        return pipeline_state

    # ==================================================================
    # PIPELINE SUMMARY
    # ==================================================================

    def _print_pipeline_summary(self, state: Dict):
        domain = state.get(
            "domain",
            "Unknown"
        )

        raw_data = state.get(
            "raw_data"
        )

        cleaned_data = state.get(
            "cleaned_data"
        )

        clean_report = state.get(
            "clean_report",
            {}
        )

        analysis = state.get(
            "analysis_insights",
            {}
        )

        print("\nPIPELINE SUMMARY:")

        print(
            f"  - Domain: {domain}"
        )

        if raw_data is not None:
            print(
                f"  - Raw records: {len(raw_data)}"
            )

        if cleaned_data is not None:
            print(
                f"  - Cleaned records: {len(cleaned_data)}"
            )

        if clean_report:
            print(
                f"  - Duplicates removed: "
                f"{clean_report.get('duplicates_removed', 0)}"
            )

            print(
                f"  - Missing values handled: "
                f"{clean_report.get('missing_values_handled', 0)}"
            )

        if analysis:
            print(
                f"  - Primary metric: "
                f"{analysis.get('primary_metric', 'N/A')}"
            )

            print(
                f"  - Metrics detected: "
                f"{analysis.get('metric_columns', [])}"
            )

            print(
                f"  - Dimensions detected: "
                f"{analysis.get('dimension_columns', [])}"
            )

            time_trend = analysis.get(
                "time_trend",
                {}
            )

            if time_trend:
                print(
                    f"  - Time periods: "
                    f"{len(time_trend)}"
                )

        print(
            f"  - Status: "
            f"{state.get('status')}"
        )