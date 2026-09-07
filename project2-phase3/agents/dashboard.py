import json
import math
import html
from pathlib import Path

import pandas as pd


class DashboardAgent:
    """
    Production-grade dynamic dashboard generator.

    The dashboard is domain-agnostic and uses the output of:
        DomainConfigAgent
        CleanAgent
        AnalysisAgent

    It dynamically adapts to:
        - Dataset domain
        - Numeric metrics
        - Categorical dimensions
        - Datetime columns
        - Primary business metric
        - Analysis results
    """

    def __init__(self, output_path="dashboard.html"):
        self.output_path = Path(output_path)

    # ============================================================
    # PUBLIC METHOD
    # ============================================================

    def generate(self, df, config=None, insights=None):
        """
        Generate a complete HTML dashboard.

        Parameters
        ----------
        df : pandas.DataFrame
            Cleaned dataset.

        config : dict
            Output from DomainConfigAgent.

        insights : dict
            Output from AnalysisAgent.

        Returns
        -------
        str
            Generated HTML.
        """

        config = config or {}
        insights = insights or {}

        if df is None:
            df = pd.DataFrame()

        domain = config.get(
            "domain",
            "General Business Analytics"
        )

        profile = config.get(
            "dataset_profile",
            {}
        )

        metric_columns = self._valid_columns(
            df,
            config.get("metric_columns", [])
        )

        dimension_columns = self._valid_columns(
            df,
            config.get("dimension_columns", [])
        )

        datetime_columns = self._valid_columns(
            df,
            profile.get("datetime_columns", [])
        )

        primary_metric = self._get_primary_metric(
            df,
            insights,
            metric_columns
        )

        kpis = self._build_kpis(
            df,
            primary_metric,
            metric_columns,
            dimension_columns
        )

        trend = self._build_trend(
            df,
            insights,
            primary_metric,
            datetime_columns
        )

        dimensions = self._build_dimension_charts(
            df,
            insights,
            primary_metric,
            dimension_columns
        )

        key_insights = self._build_insights(
            df,
            insights,
            primary_metric,
            dimension_columns
        )

        overview = self._build_overview(
            df,
            config,
            metric_columns,
            dimension_columns,
            datetime_columns
        )

        html_content = self._render_html(
            domain=domain,
            primary_metric=primary_metric,
            kpis=kpis,
            trend=trend,
            dimensions=dimensions,
            key_insights=key_insights,
            overview=overview,
        )

        self.output_path.write_text(
            html_content,
            encoding="utf-8"
        )

        return html_content

    # ============================================================
    # COLUMN HELPERS
    # ============================================================

    def _valid_columns(self, df, columns):
        if not isinstance(columns, list):
            return []

        return [
            column
            for column in columns
            if column in df.columns
        ]

    def _friendly_label(self, value):
        if value is None:
            return "Metric"

        text = str(value).replace("_", " ").strip()

        if not text:
            return "Metric"

        return text.title()

    def _format_number(self, value):
        if value is None:
            return "0"

        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return str(value)

        if math.isnan(numeric) or math.isinf(numeric):
            return "0"

        if numeric.is_integer():
            return f"{int(numeric):,}"

        if abs(numeric) >= 1_000_000:
            return f"{numeric:,.2f}"

        if abs(numeric) >= 1_000:
            return f"{numeric:,.2f}"

        return f"{numeric:,.2f}"

    def _format_compact(self, value):
        if value is None:
            return "0"

        try:
            value = float(value)
        except (TypeError, ValueError):
            return str(value)

        if math.isnan(value) or math.isinf(value):
            return "0"

        if abs(value) >= 1_000_000_000:
            return f"{value / 1_000_000_000:.1f}B"

        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"

        if abs(value) >= 1_000:
            return f"{value / 1_000:.1f}K"

        if value.is_integer():
            return f"{int(value):,}"

        return f"{value:,.2f}"

    def _safe_json(self, value):
        return json.dumps(
            value,
            ensure_ascii=False
        ).replace("</", "<\\/")

    # ============================================================
    # PRIMARY METRIC
    # ============================================================

    def _get_primary_metric(
        self,
        df,
        insights,
        metric_columns
    ):
        primary = insights.get("primary_metric")

        if primary in df.columns:
            return primary

        priority_words = [
            "sales",
            "revenue",
            "amount",
            "profit",
            "income",
            "value",
            "total",
            "mrr",
            "arr",
            "gmv",
            "price",
            "cost",
            "spend",
            "expense",
            "stock",
            "quantity",
            "units",
            "orders",
            "customers",
            "subscribers",
        ]

        for word in priority_words:
            for column in metric_columns:
                if word in str(column).lower():
                    return column

        if metric_columns:
            return metric_columns[0]

        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_columns:
            return numeric_columns[0]

        return None

    # ============================================================
    # KPI BUILDER
    # ============================================================

    def _build_kpis(
        self,
        df,
        primary_metric,
        metric_columns,
        dimension_columns
    ):
        kpis = []

        used_metrics = set()

        # --------------------------------------------------------
        # Primary metric
        # --------------------------------------------------------

        if primary_metric and primary_metric in df.columns:

            value = self._semantic_metric_value(
                df,
                primary_metric
            )

            label = self._semantic_metric_label(
                primary_metric
            )

            kpis.append(
                {
                    "label": label,
                    "value": self._format_number(value),
                    "raw_value": value,
                    "type": "primary",
                    "icon": "↗",
                }
            )

            used_metrics.add(primary_metric)

        # --------------------------------------------------------
        # Additional numeric metrics
        # --------------------------------------------------------

        for column in metric_columns:

            if column in used_metrics:
                continue

            if len(kpis) >= 3:
                break

            value = self._semantic_metric_value(
                df,
                column
            )

            label = self._semantic_metric_label(
                column
            )

            kpis.append(
                {
                    "label": label,
                    "value": self._format_number(value),
                    "raw_value": value,
                    "type": "metric",
                    "icon": "•",
                }
            )

            used_metrics.add(column)

        # --------------------------------------------------------
        # Top dimension
        # --------------------------------------------------------

        if len(kpis) < 4 and dimension_columns:

            dimension = dimension_columns[0]

            top_value = self._top_dimension_value(
                df,
                dimension,
                primary_metric
            )

            if top_value:
                kpis.append(
                    {
                        "label": "Top " + self._friendly_label(
                            dimension
                        ),
                        "value": str(top_value[0]),
                        "raw_value": top_value[1],
                        "type": "dimension",
                        "icon": "★",
                    }
                )

        # --------------------------------------------------------
        # Dataset size fallback
        # --------------------------------------------------------

        while len(kpis) < 4:

            kpis.append(
                {
                    "label": "Records",
                    "value": self._format_number(
                        len(df)
                    ),
                    "raw_value": len(df),
                    "type": "dataset",
                    "icon": "▦",
                }
            )

        return kpis[:4]

    def _semantic_metric_value(self, df, column):

        if column not in df.columns:
            return 0

        series = pd.to_numeric(
            df[column],
            errors="coerce"
        ).dropna()

        if series.empty:
            return 0

        name = str(column).lower()

        average_keywords = [
            "price",
            "cost",
            "rate",
            "margin",
            "percentage",
            "percent",
            "discount",
            "average",
            "avg",
        ]

        total_keywords = [
            "sales",
            "revenue",
            "amount",
            "profit",
            "income",
            "total",
            "quantity",
            "qty",
            "units",
            "unit",
            "stock",
            "inventory",
            "orders",
            "customers",
            "subscribers",
            "users",
            "spend",
            "expense",
            "mrr",
            "arr",
            "gmv",
        ]

        for keyword in average_keywords:
            if keyword in name:
                return float(series.mean())

        for keyword in total_keywords:
            if keyword in name:
                return float(series.sum())

        return float(series.sum())

    def _semantic_metric_label(self, column):

        name = str(column).lower()

        if any(
            keyword in name
            for keyword in [
                "sales",
                "revenue",
                "amount",
                "profit",
                "income",
                "gmv",
                "mrr",
                "arr",
            ]
        ):
            return self._friendly_label(column)

        if any(
            keyword in name
            for keyword in [
                "price",
                "cost",
                "rate",
                "margin",
                "percentage",
                "percent",
                "discount",
                "average",
                "avg",
            ]
        ):
            return "Avg " + self._friendly_label(column)

        if any(
            keyword in name
            for keyword in [
                "quantity",
                "qty",
                "units",
                "stock",
                "inventory",
            ]
        ):
            return "Total " + self._friendly_label(column)

        return self._friendly_label(column)

    # ============================================================
    # TOP DIMENSION
    # ============================================================

    def _top_dimension_value(
        self,
        df,
        dimension,
        primary_metric
    ):
        if dimension not in df.columns:
            return None

        if df.empty:
            return None

        working = df.copy()

        if primary_metric in working.columns:
            working[primary_metric] = pd.to_numeric(
                working[primary_metric],
                errors="coerce"
            )

            grouped = (
                working
                .dropna(subset=[primary_metric])
                .groupby(dimension)[primary_metric]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            if not grouped.empty:
                value = grouped.index[0]
                amount = grouped.iloc[0]

                return (
                    value,
                    float(amount)
                )

        counts = (
            working[dimension]
            .astype(str)
            .value_counts()
        )

        if counts.empty:
            return None

        value = counts.index[0]

        return (
            value,
            float(counts.iloc[0])
        )

    # ============================================================
    # TREND
    # ============================================================

    def _build_trend(
        self,
        df,
        insights,
        primary_metric,
        datetime_columns
    ):

        trend = {
            "available": False,
            "labels": [],
            "values": [],
            "title": "Performance Trend",
            "metric": self._friendly_label(
                primary_metric
            ),
        }

        if primary_metric not in df.columns:
            return trend

        date_column = None

        if datetime_columns:
            date_column = datetime_columns[0]

        if date_column is None:
            for column in df.columns:

                if pd.api.types.is_datetime64_any_dtype(
                    df[column]
                ):
                    date_column = column
                    break

        if date_column is None:
            return trend

        working = df.copy()

        working[date_column] = pd.to_datetime(
            working[date_column],
            errors="coerce"
        )

        working[primary_metric] = pd.to_numeric(
            working[primary_metric],
            errors="coerce"
        )

        working = working.dropna(
            subset=[
                date_column,
                primary_metric
            ]
        )

        if working.empty:
            return trend

        grouped = (
            working
            .groupby(
                working[date_column].dt.to_period("M")
            )[primary_metric]
            .sum()
            .sort_index()
        )

        if grouped.empty:
            return trend

        labels = [
            str(period)
            for period in grouped.index
        ]

        values = [
            float(value)
            for value in grouped.values
        ]

        trend["available"] = True
        trend["labels"] = labels
        trend["values"] = values

        return trend

    # ============================================================
    # DIMENSION CHARTS
    # ============================================================

    def _build_dimension_charts(
        self,
        df,
        insights,
        primary_metric,
        dimension_columns
    ):

        charts = []

        for dimension in dimension_columns[:4]:

            if dimension not in df.columns:
                continue

            grouped = self._group_dimension(
                df,
                dimension,
                primary_metric
            )

            if not grouped:
                continue

            charts.append(
                {
                    "dimension": dimension,
                    "title": self._dimension_title(
                        dimension_columns,
                        dimension_columns.index(
                            dimension
                        ),
                        primary_metric
                    ),
                    "labels": [
                        item[0]
                        for item in grouped
                    ],
                    "values": [
                        item[1]
                        for item in grouped
                    ],
                }
            )

        return charts

    def _group_dimension(
        self,
        df,
        dimension,
        primary_metric
    ):

        working = df.copy()

        if primary_metric in working.columns:

            working[primary_metric] = pd.to_numeric(
                working[primary_metric],
                errors="coerce"
            )

            grouped = (
                working
                .dropna(subset=[primary_metric])
                .groupby(dimension)[primary_metric]
                .sum()
                .sort_values(
                    ascending=False
                )
                .head(8)
            )

            return [
                (
                    str(index),
                    float(value)
                )
                for index, value in grouped.items()
            ]

        counts = (
            working[dimension]
            .astype(str)
            .value_counts()
            .head(8)
        )

        return [
            (
                str(index),
                float(value)
            )
            for index, value in counts.items()
        ]

    def _dimension_title(
        self,
        dimensions,
        index,
        primary_metric
    ):

        if index >= len(dimensions):
            return "Category Breakdown"

        dimension = dimensions[index]

        metric_label = self._friendly_label(
            primary_metric or "Metric"
        )

        dimension_label = self._friendly_label(
            dimension
        )

        return (
            f"{metric_label} by "
            f"{dimension_label}"
        )

    # ============================================================
    # INSIGHTS
    # ============================================================

    def _build_insights(
        self,
        df,
        insights,
        primary_metric,
        dimension_columns
    ):

        results = []

        # --------------------------------------------------------
        # Primary metric
        # --------------------------------------------------------

        if primary_metric in df.columns:

            value = self._semantic_metric_value(
                df,
                primary_metric
            )

            metric_label = self._friendly_label(
                primary_metric
            )

            results.append(
                {
                    "title": "Primary Metric",
                    "description": (
                        f"{metric_label} is "
                        f"{self._format_number(value)} "
                        f"across {len(df):,} records."
                    ),
                }
            )

        # --------------------------------------------------------
        # Top dimensions
        # --------------------------------------------------------

        for dimension in dimension_columns[:3]:

            top = self._top_dimension_value(
                df,
                dimension,
                primary_metric
            )

            if not top:
                continue

            value = top[0]
            amount = top[1]

            results.append(
                {
                    "title": (
                        "Top "
                        + self._friendly_label(
                            dimension
                        )
                    ),
                    "description": (
                        f"{value} leads "
                        f"{self._friendly_label(dimension)} "
                        f"with {self._format_number(amount)} "
                        f"in {self._friendly_label(primary_metric)}."
                    ),
                }
            )

        # --------------------------------------------------------
        # Time coverage
        # --------------------------------------------------------

        date_columns = []

        for column in df.columns:

            if pd.api.types.is_datetime64_any_dtype(
                df[column]
            ):
                date_columns.append(column)

        if date_columns:

            date_column = date_columns[0]

            dates = pd.to_datetime(
                df[date_column],
                errors="coerce"
            ).dropna()

            if not dates.empty:

                start = dates.min().strftime(
                    "%b %Y"
                )

                end = dates.max().strftime(
                    "%b %Y"
                )

                results.append(
                    {
                        "title": "Time Coverage",
                        "description": (
                            f"Data spans from {start} "
                            f"to {end}."
                        ),
                    }
                )

        if not results:

            results.append(
                {
                    "title": "Dataset Overview",
                    "description": (
                        f"The dataset contains "
                        f"{len(df):,} records ready "
                        f"for analysis."
                    ),
                }
            )

        return results[:4]

    # ============================================================
    # OVERVIEW
    # ============================================================

    def _build_overview(
        self,
        df,
        config,
        metric_columns,
        dimension_columns,
        datetime_columns
    ):

        return {
            "records": len(df),
            "columns": len(df.columns),
            "metrics": metric_columns,
            "dimensions": dimension_columns,
            "datetime": datetime_columns,
            "domain": config.get(
                "domain",
                "General Business Analytics"
            ),
        }

    # ============================================================
    # HTML RENDER
    # ============================================================

    def _render_html(
        self,
        domain,
        primary_metric,
        kpis,
        trend,
        dimensions,
        key_insights,
        overview
    ):
        """Render a premium, restrained business-intelligence dashboard."""

        domain_title = self._friendly_label(domain)
        primary_label = self._friendly_label(primary_metric or "Metric")
        kpi_html = self._render_kpis(kpis)
        dimension_html = self._render_dimension_cards(dimensions)
        insights_html = self._render_insights(key_insights)
        trend_section = self._render_trend(trend)
        overview_html = self._render_overview(overview)

        subtitle = (
            f"A dynamic view of {domain_title.lower()} performance, built from the detected "
            "dataset structure and business measures."
        )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#0a111d">
    <title>{html.escape(domain_title)} · Analytics Studio</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ box-sizing: border-box; }}
        html {{ scroll-behavior: smooth; }}
        :root {{
            --bg: #0a111d;
            --panel: #101a2a;
            --panel-2: #0d1725;
            --panel-3: #142238;
            --border: #24344c;
            --border-soft: rgba(160, 181, 208, .10);
            --text: #f5f7fb;
            --muted: #8c9bb0;
            --subtle: #5f7087;
            --blue: #4f7cff;
            --blue-soft: rgba(79,124,255,.12);
            --teal: #28c1ae;
            --amber: #e9ae55;
            --rose: #e5758a;
            --shadow: 0 20px 50px rgba(0,0,0,.18);
            --radius: 20px;
        }}
        body {{
            margin: 0;
            min-height: 100vh;
            background: var(--bg);
            color: var(--text);
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
        }}
        body::before {{
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background:
                radial-gradient(circle at 82% 4%, rgba(79,124,255,.10), transparent 25%),
                radial-gradient(circle at 5% 42%, rgba(40,193,174,.045), transparent 24%);
            z-index: -2;
        }}
        body::after {{
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            opacity: .028;
            background-image:
                linear-gradient(rgba(255,255,255,.7) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,.7) 1px, transparent 1px);
            background-size: 46px 46px;
            mask-image: linear-gradient(to bottom, #000 0%, transparent 72%);
            z-index: -1;
        }}
        .page {{ width: min(1480px, calc(100% - 56px)); margin: 0 auto; padding: 22px 0 52px; }}

        .topbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
            padding: 11px 12px 11px 14px;
            margin-bottom: 32px;
            border: 1px solid var(--border-soft);
            border-radius: 16px;
            background: rgba(12,20,33,.76);
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 28px rgba(0,0,0,.10);
            animation: fadeDown .55s ease both;
        }}
        .brand {{ display: flex; align-items: center; gap: 11px; min-width: 0; }}
        .brand-mark {{
            width: 34px; height: 34px; display: grid; place-items: center;
            border-radius: 10px;
            background: #1a2941;
            border: 1px solid #2b4264;
            color: #a9c0ff;
            font-weight: 850;
            font-size: 14px;
        }}
        .brand-name {{ font-size: 12px; font-weight: 800; letter-spacing: .11em; text-transform: uppercase; }}
        .brand-meta {{ color: var(--subtle); font-size: 10px; margin-top: 1px; }}
        .topbar-right {{ display: flex; align-items: center; gap: 8px; }}
        .pill {{ display: inline-flex; align-items: center; gap: 7px; padding: 7px 10px; border: 1px solid #22324a; border-radius: 999px; background: #0d1725; color: #aebbd0; font-size: 10px; font-weight: 750; letter-spacing: .04em; }}
        .domain-pill {{ max-width: 250px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #a9bfff; border-color: rgba(79,124,255,.22); background: rgba(79,124,255,.06); }}
        .pill-dot {{ width: 6px; height: 6px; border-radius: 50%; background: var(--teal); box-shadow: 0 0 0 4px rgba(40,193,174,.10); }}

        .hero {{ display: grid; grid-template-columns: minmax(0,1fr) 300px; gap: 28px; align-items: end; padding: 0 3px; margin-bottom: 30px; animation: fadeUp .65s .05s ease both; }}
        .eyebrow {{ display: flex; align-items: center; gap: 9px; margin-bottom: 11px; color: #8797ad; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: .14em; }}
        .eyebrow-line {{ width: 31px; height: 2px; background: var(--blue); opacity: .85; border-radius: 2px; }}
        h1 {{ margin: 0; max-width: 920px; font-size: clamp(38px, 5vw, 64px); line-height: 1.02; letter-spacing: -.06em; font-weight: 830; }}
        .hero-title-accent {{ color: #b6c7e5; }}
        .subtitle {{ max-width: 790px; margin: 13px 0 0; color: #7f8ea4; font-size: 13px; }}
        .hero-side {{ display: grid; gap: 9px; }}
        .hero-stat {{ padding: 14px 16px; border: 1px solid var(--border-soft); border-radius: 16px; background: linear-gradient(145deg, rgba(18,30,48,.94), rgba(13,22,36,.94)); }}
        .hero-stat-label {{ color: var(--subtle); font-size: 9px; font-weight: 800; text-transform: uppercase; letter-spacing: .12em; }}
        .hero-stat-value {{ margin-top: 3px; color: #e8eef8; font-size: 17px; font-weight: 780; overflow-wrap: anywhere; }}

        .section-title {{ display: flex; justify-content: space-between; align-items: end; gap: 16px; margin: 28px 2px 12px; }}
        .section-title h2 {{ margin: 0; color: #becadd; font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: .13em; }}
        .section-note {{ color: #56667e; font-size: 10px; }}

        .kpi-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 13px; }}
        .kpi {{
            --accent: var(--blue);
            position: relative;
            min-height: 150px;
            overflow: hidden;
            padding: 19px 20px;
            border: 1px solid var(--border);
            border-radius: 19px;
            background: linear-gradient(145deg, rgba(17,28,45,.98), rgba(12,21,34,.98));
            box-shadow: 0 14px 34px rgba(0,0,0,.14);
            transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease;
            animation: fadeUp .55s ease both;
        }}
        .kpi:nth-child(2) {{ animation-delay: .05s; }}
        .kpi:nth-child(3) {{ animation-delay: .10s; }}
        .kpi:nth-child(4) {{ animation-delay: .15s; }}
        .kpi::before {{ content: ""; position: absolute; left: 20px; right: 20px; top: 0; height: 2px; border-radius: 0 0 2px 2px; background: var(--accent); opacity: .86; }}
        .kpi::after {{ content: ""; position: absolute; right: -52px; bottom: -60px; width: 126px; height: 126px; border-radius: 50%; border: 1px solid rgba(255,255,255,.035); box-shadow: 0 0 0 16px rgba(255,255,255,.010), 0 0 0 33px rgba(255,255,255,.006); }}
        .kpi:hover {{ transform: translateY(-4px); border-color: #344865; box-shadow: 0 22px 42px rgba(0,0,0,.20); }}
        .kpi-head {{ display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 27px; }}
        .kpi-label {{ color: #8f9db2; font-size: 9px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }}
        .kpi-icon {{ width: 29px; height: 29px; display: grid; place-items: center; border-radius: 9px; border: 1px solid rgba(255,255,255,.07); background: rgba(255,255,255,.025); color: var(--accent); font-size: 11px; font-weight: 800; }}
        .kpi-value {{ position: relative; z-index: 1; color: #f1f5fb; font-size: clamp(28px,3vw,38px); font-weight: 820; letter-spacing: -.045em; line-height: 1; overflow-wrap: anywhere; }}

        .section {{ margin-top: 18px; }}
        .card {{
            overflow: hidden;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            background: linear-gradient(145deg, rgba(16,26,42,.98), rgba(12,20,33,.98));
            box-shadow: var(--shadow);
            animation: fadeUp .62s .16s ease both;
        }}
        .card-head {{ display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 21px 23px 11px; }}
        .card-title {{ display: flex; align-items: center; gap: 9px; color: #e6edf7; font-size: 15px; font-weight: 780; letter-spacing: -.01em; }}
        .card-title::before {{ content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--blue); box-shadow: 0 0 0 5px rgba(79,124,255,.06); }}
        .card-subtitle {{ margin-top: 4px; color: #6e7e95; font-size: 10px; }}
        .trend-meta {{ display: inline-flex; align-items: center; gap: 8px; color: #708097; font-size: 9px; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; }}
        .legend-line {{ width: 19px; height: 2px; background: var(--blue); border-radius: 2px; }}
        .chart-wrap {{ height: 365px; padding: 8px 19px 21px; }}
        .chart-wrap canvas {{ width: 100% !important; height: 100% !important; }}

        .two-column {{ display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 16px; }}
        .dimension-card {{ min-height: 395px; }}
        .dimension-title {{ display: flex; align-items: center; gap: 9px; }}
        .dimension-index {{ display: inline-grid; place-items: center; width: 25px; height: 25px; border-radius: 8px; color: #a8bbf3; background: rgba(79,124,255,.06); border: 1px solid rgba(79,124,255,.18); font-size: 9px; font-weight: 850; }}

        .insights {{ display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: 10px; padding: 0 19px 21px; }}
        .insight {{ position: relative; min-height: 91px; overflow: hidden; padding: 16px 18px 15px 20px; border: 1px solid #223149; border-radius: 15px; background: #0d1725; transition: transform .2s ease, border-color .2s ease, background .2s ease; }}
        .insight::before {{ content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: var(--blue); }}
        .insight:nth-child(2)::before {{ background: var(--teal); }}
        .insight:nth-child(3)::before {{ background: var(--amber); }}
        .insight:nth-child(4)::before {{ background: var(--rose); }}
        .insight:hover {{ transform: translateY(-2px); border-color: #31435f; background: #101b2b; }}
        .insight-title {{ color: #c1cede; font-size: 9px; font-weight: 850; text-transform: uppercase; letter-spacing: .12em; margin-bottom: 7px; }}
        .insight-text {{ color: #8e9caf; font-size: 11px; line-height: 1.66; }}

        .overview-grid {{ display: grid; grid-template-columns: repeat(5,minmax(0,1fr)); gap: 9px; padding: 0 19px 21px; }}
        .overview-item {{ min-height: 82px; padding: 14px 15px; border: 1px solid #223149; border-radius: 14px; background: #0d1725; }}
        .overview-label {{ margin-bottom: 8px; color: #61718a; font-size: 8px; font-weight: 850; text-transform: uppercase; letter-spacing: .11em; }}
        .overview-value {{ color: #d3deed; font-size: 11px; font-weight: 700; line-height: 1.5; overflow-wrap: anywhere; }}

        .empty {{ min-height: 235px; display: grid; place-items: center; padding: 30px; text-align: center; color: #738299; font-size: 11px; }}
        .footer {{ display: flex; justify-content: space-between; gap: 18px; padding: 19px 2px 0; color: #53637a; font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: .09em; }}

        @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(13px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes fadeDown {{ from {{ opacity: 0; transform: translateY(-7px); }} to {{ opacity: 1; transform: translateY(0); }} }}

        @media (max-width: 1100px) {{
            .kpi-grid {{ grid-template-columns: repeat(2,minmax(0,1fr)); }}
            .overview-grid {{ grid-template-columns: repeat(3,minmax(0,1fr)); }}
            .hero {{ grid-template-columns: 1fr; }}
            .hero-side {{ grid-template-columns: repeat(2,minmax(0,1fr)); }}
        }}
        @media (max-width: 780px) {{
            .page {{ width: min(100% - 26px, 1480px); padding-top: 14px; }}
            .topbar-right {{ display: none; }}
            .two-column, .insights {{ grid-template-columns: 1fr; }}
            .overview-grid {{ grid-template-columns: repeat(2,minmax(0,1fr)); }}
            .hero-side {{ grid-template-columns: 1fr; }}
            h1 {{ font-size: clamp(34px,10vw,48px); }}
        }}
        @media (max-width: 520px) {{
            .kpi-grid, .overview-grid {{ grid-template-columns: 1fr; }}
            .chart-wrap {{ height: 295px; padding: 7px 9px 17px; }}
            .card-head {{ padding: 17px 17px 10px; }}
            .insights, .overview-grid {{ padding-left: 13px; padding-right: 13px; }}
            .footer {{ flex-direction: column; }}
        }}
    </style>
</head>
<body>
<div class="page">
    <div class="topbar">
        <div class="brand">
            <div class="brand-mark">A</div>
            <div>
                <div class="brand-name">Analytics Studio</div>
                <div class="brand-meta">Dynamic multi-agent business intelligence</div>
            </div>
        </div>
        <div class="topbar-right">
            <div class="pill domain-pill" title="{html.escape(domain_title)}">{html.escape(domain_title)}</div>
            <div class="pill"><span class="pill-dot"></span> Analysis ready</div>
        </div>
    </div>

    <header class="hero">
        <div>
            <div class="eyebrow"><span class="eyebrow-line"></span> BUSINESS INTELLIGENCE / DATASET VIEW</div>
            <h1>{html.escape(domain_title)} <span class="hero-title-accent">Analytics</span></h1>
            <p class="subtitle">{html.escape(subtitle)}</p>
        </div>
        <div class="hero-side">
            <div class="hero-stat">
                <div class="hero-stat-label">Primary measure</div>
                <div class="hero-stat-value">{html.escape(primary_label)}</div>
            </div>
            <div class="hero-stat">
                <div class="hero-stat-label">Dataset size</div>
                <div class="hero-stat-value">{self._format_number(overview.get("records", 0))} records</div>
            </div>
        </div>
    </header>

    <div class="section-title">
        <h2>Executive snapshot</h2>
        <div class="section-note">Key measures selected automatically for this domain</div>
    </div>
    <section class="kpi-grid">
        {kpi_html}
    </section>

    <div class="section-title">
        <h2>Trend & performance</h2>
        <div class="section-note">Time-aware performance view</div>
    </div>
    <section class="section">
        {trend_section}
    </section>

    <div class="section-title">
        <h2>Business breakdowns</h2>
        <div class="section-note">Top contributors across detected dimensions</div>
    </div>
    <section class="section">
        <div class="two-column">
            {dimension_html}
        </div>
    </section>

    <div class="section-title">
        <h2>Analyst notes</h2>
        <div class="section-note">Automatically derived observations</div>
    </div>
    <section class="section">
        <div class="card">
            <div class="card-head">
                <div>
                    <div class="card-title">Key insights</div>
                    <div class="card-subtitle">The strongest signals surfaced from the current analysis</div>
                </div>
            </div>
            {insights_html}
        </div>
    </section>

    <div class="section-title">
        <h2>Dataset profile</h2>
        <div class="section-note">Structure detected by the production pipeline</div>
    </div>
    <section class="section">
        <div class="card">
            <div class="card-head">
                <div>
                    <div class="card-title">Data overview</div>
                    <div class="card-subtitle">Columns and fields used to assemble the dashboard</div>
                </div>
            </div>
            {overview_html}
        </div>
    </section>

    <footer class="footer">
        <span>Dynamic Multi-Agent Analytics Pipeline</span>
        <span>Domain → Clean → Analyze → Dashboard</span>
    </footer>
</div>

<script>
    Chart.defaults.font.family = 'Inter, ui-sans-serif, system-ui, sans-serif';
    Chart.defaults.color = '#738198';

    const gridColor = 'rgba(134,151,178,.085)';
    const blue = '#4f7cff';
    const teal = '#28c1ae';
    const amber = '#e9ae55';
    const rose = '#e5758a';
    const palette = [blue, teal, amber, rose, '#8c86ff', '#4aa5f5'];

    function chartTooltip() {{
        return {{
            enabled: true,
            backgroundColor: '#0a111d',
            borderColor: '#2c3d57',
            borderWidth: 1,
            titleColor: '#f3f6fb',
            bodyColor: '#b3c0d2',
            titleFont: {{ size: 11, weight: '700' }},
            bodyFont: {{ size: 11 }},
            padding: 11,
            displayColors: false,
            cornerRadius: 9,
            caretPadding: 8
        }};
    }}

    function shortenLabel(value, max) {{
        const text = String(value);
        return text.length > max ? text.slice(0, max - 1) + '…' : text;
    }}

    function createLineChart(elementId, labels, values) {{
        const canvas = document.getElementById(elementId);
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const fill = ctx.createLinearGradient(0, 0, 0, 330);
        fill.addColorStop(0, 'rgba(79,124,255,.23)');
        fill.addColorStop(.58, 'rgba(79,124,255,.075)');
        fill.addColorStop(1, 'rgba(79,124,255,0)');
        new Chart(canvas, {{
            type: 'line',
            data: {{
                labels,
                datasets: [{{
                    data: values,
                    borderColor: blue,
                    backgroundColor: fill,
                    borderWidth: 2.4,
                    pointRadius: 3,
                    pointHoverRadius: 6,
                    pointBorderWidth: 2,
                    pointBorderColor: '#0d1725',
                    pointBackgroundColor: blue,
                    tension: .34,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{ mode: 'index', intersect: false }},
                animation: {{ duration: 1050, easing: 'easeOutQuart' }},
                plugins: {{ legend: {{ display: false }}, tooltip: chartTooltip() }},
                scales: {{
                    x: {{
                        grid: {{ display: false }},
                        border: {{ display: false }},
                        ticks: {{ color: '#607089', font: {{ size: 10 }} }}
                    }},
                    y: {{
                        beginAtZero: true,
                        grid: {{ color: gridColor }},
                        border: {{ display: false }},
                        ticks: {{
                            color: '#607089',
                            font: {{ size: 10 }},
                            padding: 7,
                            callback: function(value) {{ return Number(value).toLocaleString(); }}
                        }}
                    }}
                }}
            }}
        }});
    }}

    function createBarChart(elementId, labels, values, color) {{
        const canvas = document.getElementById(elementId);
        if (!canvas) return;
        new Chart(canvas, {{
            type: 'bar',
            data: {{
                labels: labels.map(function(value) {{ return shortenLabel(value, 15); }}),
                datasets: [{{
                    data: values,
                    backgroundColor: color,
                    borderColor: color,
                    borderWidth: 0,
                    borderRadius: 6,
                    borderSkipped: false,
                    maxBarThickness: 40,
                    hoverBackgroundColor: color
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                animation: {{ duration: 900, easing: 'easeOutQuart' }},
                plugins: {{ legend: {{ display: false }}, tooltip: chartTooltip() }},
                scales: {{
                    x: {{
                        grid: {{ display: false }},
                        border: {{ display: false }},
                        ticks: {{ color: '#607089', font: {{ size: 10 }}, maxRotation: 24, minRotation: 0, autoSkip: false }}
                    }},
                    y: {{
                        beginAtZero: true,
                        grid: {{ color: gridColor }},
                        border: {{ display: false }},
                        ticks: {{
                            color: '#607089',
                            font: {{ size: 10 }},
                            padding: 7,
                            callback: function(value) {{ return Number(value).toLocaleString(); }}
                        }}
                    }}
                }}
            }}
        }});
    }}

    const trendLabels = {self._safe_json(trend.get('labels', []))};
    const trendValues = {self._safe_json(trend.get('values', []))};
    createLineChart('trendChart', trendLabels, trendValues);

    const dimensionCharts = {self._safe_json(dimensions)};
    dimensionCharts.forEach(function(chart, index) {{
        createBarChart('dimensionChart' + index, chart.labels, chart.values, palette[index % palette.length]);
    }});
</script>
</body>
</html>
"""

    # ============================================================
    # HTML COMPONENTS
    # ============================================================

    def _render_kpis(self, kpis):
        accents = ['#4f7cff', '#28c1ae', '#e9ae55', '#e5758a']
        cards = []
        for index, kpi in enumerate(kpis):
            label = html.escape(str(kpi.get('label', 'Metric')))
            value = html.escape(str(kpi.get('value', '0')))
            icon = html.escape(str(kpi.get('icon', '•')))
            accent = accents[index % len(accents)]
            cards.append(
                f"""<div class="kpi" style="--accent:{accent}">
                    <div class="kpi-head">
                        <div class="kpi-label">{label}</div>
                        <div class="kpi-icon">{icon}</div>
                    </div>
                    <div class="kpi-value">{value}</div>
                </div>"""
            )
        return '\n'.join(cards)

    def _render_trend(self, trend):
        if not trend.get('available'):
            return '<div class="card"><div class="card-head"><div><div class="card-title">Performance trend</div><div class="card-subtitle">No valid time-series field was detected for this dataset</div></div></div><div class="empty">Time-based trend visualization is not available for the current dataset.</div></div>'
        title = html.escape(str(trend.get('metric', 'Performance')))
        return f"""<div class="card trend-card">
            <div class="card-head">
                <div>
                    <div class="card-title">{title} trend</div>
                    <div class="card-subtitle">Monthly movement of the selected primary measure</div>
                </div>
                <div class="trend-meta"><span class="legend-line"></span>{title}</div>
            </div>
            <div class="chart-wrap"><canvas id="trendChart"></canvas></div>
        </div>"""

    def _render_dimension_cards(self, dimensions):
        if not dimensions:
            return '<div class="card"><div class="empty">No categorical dimensions were detected for this dataset.</div></div>'
        cards = []
        for index, chart in enumerate(dimensions):
            title = html.escape(str(chart.get('title', 'Category Breakdown')))
            dimension = html.escape(self._friendly_label(chart.get('dimension', 'Category')))
            cards.append(
                f"""<div class="card dimension-card">
                    <div class="card-head">
                        <div>
                            <div class="card-title"><span class="dimension-index">{index + 1:02d}</span>{title}</div>
                            <div class="card-subtitle">Top {dimension} contributors · ranked by the primary measure</div>
                        </div>
                    </div>
                    <div class="chart-wrap"><canvas id="dimensionChart{index}"></canvas></div>
                </div>"""
            )
        return '\n'.join(cards)

    def _render_insights(self, insights):
        if not insights:
            return '<div class="empty">No additional insights were generated.</div>'
        cards = []
        for item in insights:
            title = html.escape(str(item.get('title', 'Insight')))
            description = html.escape(str(item.get('description', '')))
            cards.append(
                f"""<div class="insight">
                    <div class="insight-title">{title}</div>
                    <div class="insight-text">{description}</div>
                </div>"""
            )
        return '<div class="insights">' + '\n'.join(cards) + '</div>'

    def _render_overview(self, overview):
        metrics = overview.get('metrics', [])
        dimensions = overview.get('dimensions', [])
        datetime_columns = overview.get('datetime', [])
        items = [
            ('Records', self._format_number(overview.get('records', 0))),
            ('Columns', self._format_number(overview.get('columns', 0))),
            ('Metrics', ', '.join(self._friendly_label(x) for x in metrics) or 'None'),
            ('Dimensions', ', '.join(self._friendly_label(x) for x in dimensions) or 'None'),
            ('Time Field', ', '.join(self._friendly_label(x) for x in datetime_columns) or 'None'),
        ]
        cards = []
        for label, value in items:
            cards.append(
                f"""<div class="overview-item">
                    <div class="overview-label">{html.escape(label)}</div>
                    <div class="overview-value">{html.escape(str(value))}</div>
                </div>"""
            )
        return '<div class="overview-grid">' + '\n'.join(cards) + '</div>'


# ================================================================
# BACKWARD COMPATIBILITY
# ================================================================

def generate_dashboard(
    df,
    config=None,
    insights=None,
    output_path="dashboard.html"
):
    """Convenience function for existing pipeline code."""
    agent = DashboardAgent(output_path=output_path)
    return agent.generate(df=df, config=config, insights=insights)
