import os
import sys

from agents.orchestrator import OrchestratorAgent
from agents.dashboard import DashboardAgent


def main():
    print("\n")
    print("=" * 70)
    print("PHASE 3 - DOMAIN-AWARE MULTI-AGENT ANALYTICS")
    print("=" * 70)

    # --------------------------------------------------------------
    # Dataset path
    # --------------------------------------------------------------

    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        csv_path = "data/retail_data.csv"

    print(f"\nDataset: {csv_path}")

    if not os.path.exists(csv_path):
        print(f"\n✗ Dataset not found: {csv_path}")

        print("\nUsage:")
        print("  python3 main.py data/retail_data.csv")

        return 1

    # --------------------------------------------------------------
    # Run Orchestrator
    # --------------------------------------------------------------

    print("\nStarting analytics pipeline...")

    orchestrator = OrchestratorAgent()

    try:
        result = orchestrator.orchestrate(csv_path)

    except Exception as e:
        print("\n✗ Orchestrator failed:")
        print(f"  {e}")

        return 1

    # --------------------------------------------------------------
    # Check pipeline result
    # --------------------------------------------------------------

    if not result.get("success", False):

        print("\n" + "=" * 70)
        print("PIPELINE FAILED")
        print("=" * 70)

        print(
            f"\nError: "
            f"{result.get('error', 'Unknown error')}"
        )

        return 1

    # --------------------------------------------------------------
    # Extract pipeline results
    # --------------------------------------------------------------

    domain_config = result.get(
        "domain_config",
        {}
    )

    analysis_insights = result.get(
        "analysis_insights",
        {}
    )

    domain = result.get(
        "domain",
        domain_config.get(
            "domain",
            "business analytics"
        )
    )

    # --------------------------------------------------------------
    # Extract cleaned dataframe
    # --------------------------------------------------------------

    cleaned_df = result.get(
        "cleaned_data"
    )

    if cleaned_df is None:

        print("\n✗ Dashboard generation failed:")
        print("  Cleaned dataset was not returned by orchestrator.")

        return 1

    # --------------------------------------------------------------
    # Generate Dynamic Dashboard
    # --------------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("DASHBOARD GENERATION")
    print("=" * 70)

    dashboard_agent = DashboardAgent(
        output_path="dashboard.html"
    )

    try:

        dashboard_agent.generate(
            df=cleaned_df,
            config=domain_config,
            insights=analysis_insights
        )

        dashboard_path = "dashboard.html"

    except Exception as e:

        print("\n✗ Dashboard generation failed:")
        print(f"  {e}")

        return 1

    # --------------------------------------------------------------
    # Final Result
    # --------------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("PHASE 3 PIPELINE COMPLETED")
    print("=" * 70)

    print("\n✓ Dataset processed successfully")

    print(
        f"✓ Domain detected: "
        f"{domain}"
    )

    print(
        f"✓ Primary metric: "
        f"{analysis_insights.get('primary_metric', 'N/A')}"
    )

    print(
        f"✓ Metrics detected: "
        f"{analysis_insights.get('metric_columns', [])}"
    )

    print(
        f"✓ Dimensions detected: "
        f"{analysis_insights.get('dimension_columns', [])}"
    )

    print(
        f"✓ Dashboard generated: "
        f"{dashboard_path}"
    )

    print("\n" + "=" * 70)
    print("Open dashboard.html in your browser.")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())