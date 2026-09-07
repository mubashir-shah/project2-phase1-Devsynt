import re
from pathlib import Path

import pandas as pd


class DomainConfigAgent:
    """
    Production-grade domain configuration agent.

    Responsibilities:
        1. Validate the dataset
        2. Detect dataset structure
        3. Detect the business domain
        4. Identify meaningful metrics
        5. Identify meaningful business dimensions
        6. Exclude technical identifier columns
        7. Define domain-specific success metrics
    """

    SUPPORTED_DOMAINS = [
        "e-commerce",
        "inventory",
        "restaurant sales",
        "subscription / saas",
        "retail sales",
        "general business analytics",
    ]

    # ============================================================
    # PUBLIC METHOD
    # ============================================================

    def configure(self, csv_path):
        """
        Analyze a CSV dataset and return a domain-aware configuration.
        """

        result = {
            "success": False,
            "agent": "DomainConfigAgent",
            "domain": "general business analytics",
            "dataset_profile": {},
            "metric_columns": [],
            "dimension_columns": [],
            "success_metrics": [],
        }

        try:
            path = Path(csv_path)

            if not path.exists():
                result["error"] = (
                    f"Dataset not found: {csv_path}"
                )
                return result

            if path.suffix.lower() != ".csv":
                result["error"] = (
                    "Only CSV datasets are supported."
                )
                return result

            df = pd.read_csv(path)

            if df is None or df.empty:
                result["error"] = (
                    "Dataset is empty."
                )
                return result

            # ----------------------------------------------------
            # Clean column names
            # ----------------------------------------------------

            df.columns = [
                str(column).strip()
                for column in df.columns
            ]

            # Remove unnamed CSV index columns
            unnamed_columns = [
                column
                for column in df.columns
                if str(column).lower().startswith("unnamed:")
            ]

            if unnamed_columns:
                df = df.drop(
                    columns=unnamed_columns,
                    errors="ignore"
                )

            if df.empty or len(df.columns) == 0:
                result["error"] = (
                    "Dataset contains no usable columns."
                )
                return result

            # ----------------------------------------------------
            # Detect column types
            # ----------------------------------------------------

            numeric_columns = self._detect_numeric_columns(df)

            datetime_columns = self._detect_datetime_columns(df)

            categorical_columns = [
                column
                for column in df.columns
                if column not in numeric_columns
                and column not in datetime_columns
            ]

            # ----------------------------------------------------
            # Detect domain
            # ----------------------------------------------------

            domain = self._detect_domain(
                df,
                numeric_columns,
                categorical_columns,
                datetime_columns
            )

            # ----------------------------------------------------
            # Select business metrics
            # ----------------------------------------------------

            metric_columns = self._select_metric_columns(
                df,
                numeric_columns,
                domain
            )

            # ----------------------------------------------------
            # Select business dimensions
            # ----------------------------------------------------

            dimension_columns = self._select_dimension_columns(
                df,
                categorical_columns,
                domain
            )

            # ----------------------------------------------------
            # Domain-specific success metrics
            # ----------------------------------------------------

            success_metrics = self._get_success_metrics(
                domain
            )

            # ----------------------------------------------------
            # Dataset profile
            # ----------------------------------------------------

            profile = {
                "rows": int(len(df)),
                "columns": int(len(df.columns)),
                "column_names": [
                    str(column)
                    for column in df.columns
                ],
                "numeric_columns": numeric_columns,
                "categorical_columns": categorical_columns,
                "datetime_columns": datetime_columns,
                "date_column": (
                    datetime_columns[0]
                    if datetime_columns
                    else None
                ),
            }

            result.update(
                {
                    "success": True,
                    "domain": domain,
                    "dataset_profile": profile,
                    "metric_columns": metric_columns,
                    "dimension_columns": dimension_columns,
                    "success_metrics": success_metrics,
                }
            )

            return result

        except Exception as exc:

            result["error"] = str(exc)

            return result

    # ============================================================
    # TYPE DETECTION
    # ============================================================

    def _detect_numeric_columns(self, df):

        numeric_columns = []

        for column in df.columns:

            series = df[column]

            # Already numeric
            if pd.api.types.is_numeric_dtype(series):
                numeric_columns.append(column)
                continue

            # Try numeric conversion
            converted = pd.to_numeric(
                series,
                errors="coerce"
            )

            non_empty = series.notna().sum()

            if non_empty == 0:
                continue

            numeric_ratio = (
                converted.notna().sum()
                / non_empty
            )

            if numeric_ratio >= 0.80:
                numeric_columns.append(column)

        return numeric_columns

    def _detect_datetime_columns(self, df):

        datetime_columns = []

        for column in df.columns:

            series = df[column]

            if pd.api.types.is_datetime64_any_dtype(
                series
            ):
                datetime_columns.append(column)
                continue

            try:
                converted = pd.to_datetime(
                    series,
                    errors="coerce",
                    format="mixed"
                )

                non_empty = series.notna().sum()

                if non_empty == 0:
                    continue

                datetime_ratio = (
                    converted.notna().sum()
                    / non_empty
                )

                if datetime_ratio >= 0.80:
                    datetime_columns.append(column)

            except Exception:
                continue

        return datetime_columns

    # ============================================================
    # DOMAIN DETECTION
    # ============================================================

    def _detect_domain(
        self,
        df,
        numeric_columns,
        categorical_columns,
        datetime_columns
    ):

        column_names = [
            str(column).lower()
            for column in df.columns
        ]

        text = " ".join(column_names)

        scores = {
            "e-commerce": 0,
            "inventory": 0,
            "restaurant sales": 0,
            "subscription / saas": 0,
            "retail sales": 0,
        }

        # --------------------------------------------------------
        # E-commerce
        # --------------------------------------------------------

        ecommerce_keywords = [
            "order",
            "customer",
            "payment",
            "shipping",
            "delivery",
            "discount",
            "cart",
            "online",
            "ecommerce",
            "e-commerce",
        ]

        for keyword in ecommerce_keywords:

            if keyword in text:
                scores["e-commerce"] += 2

        if self._has_column(
            df,
            ["orderid", "order_id"]
        ):
            scores["e-commerce"] += 5

        if self._has_column(
            df,
            ["customer", "customerid", "customer_id"]
        ):
            scores["e-commerce"] += 3

        # --------------------------------------------------------
        # Inventory
        # --------------------------------------------------------

        inventory_keywords = [
            "stock",
            "inventory",
            "warehouse",
            "reorder",
            "supplier",
            "unitsin",
            "unitsout",
            "stocklevel",
            "reorderlevel",
        ]

        for keyword in inventory_keywords:

            if keyword in text.replace("_", ""):
                scores["inventory"] += 3

        # --------------------------------------------------------
        # Restaurant
        # --------------------------------------------------------

        restaurant_keywords = [
            "restaurant",
            "menu",
            "dish",
            "food",
            "item",
            "table",
            "server",
            "waiter",
            "chef",
            "payment",
            "category",
        ]

        for keyword in restaurant_keywords:

            if keyword in text:
                scores["restaurant sales"] += 2

        # Strong restaurant structure
        has_item = self._has_column(
            df,
            ["item", "menuitem", "menu_item", "dish", "food"]
        )

        has_table_or_server = (
            self._has_column(
                df,
                ["table", "tablenumber", "table_number"]
            )
            or
            self._has_column(
                df,
                ["server", "waiter", "waitstaff"]
            )
        )

        has_payment = self._has_column(
            df,
            ["paymentmethod", "payment_method", "payment"]
        )

        if has_item:
            scores["restaurant sales"] += 5

        if has_table_or_server:
            scores["restaurant sales"] += 4

        if has_payment:
            scores["restaurant sales"] += 2

        if has_item and has_table_or_server:
            scores["restaurant sales"] += 5

        # --------------------------------------------------------
        # Subscription / SaaS
        # --------------------------------------------------------

        saas_keywords = [
            "subscription",
            "subscriber",
            "plan",
            "monthlyfee",
            "monthly_fee",
            "activeusers",
            "active_users",
            "churn",
            "churned",
            "mrr",
            "arr",
            "saas",
            "renewal",
        ]

        for keyword in saas_keywords:

            if keyword in text.replace("_", ""):
                scores["subscription / saas"] += 3

        if self._has_column(
            df,
            [
                "subscriptionid",
                "subscription_id"
            ]
        ):
            scores["subscription / saas"] += 6

        # --------------------------------------------------------
        # Retail
        # --------------------------------------------------------

        retail_keywords = [
            "product",
            "category",
            "region",
            "sales",
            "quantity",
            "unitprice",
            "unit_price",
            "revenue",
            "store",
            "branch",
        ]

        for keyword in retail_keywords:

            if keyword in text.replace("_", ""):
                scores["retail sales"] += 2

        if (
            self._has_column(
                df,
                ["product"]
            )
            and
            self._has_column(
                df,
                ["quantity"]
            )
        ):
            scores["retail sales"] += 5

        # --------------------------------------------------------
        # Structural signals
        # --------------------------------------------------------

        # Order + customer = e-commerce
        if (
            self._has_column(
                df,
                ["orderid", "order_id"]
            )
            and
            self._has_column(
                df,
                ["customer", "customerid", "customer_id"]
            )
        ):
            scores["e-commerce"] += 8

        # Product + quantity = retail
        if (
            self._has_column(
                df,
                ["product"]
            )
            and
            self._has_column(
                df,
                ["quantity", "qty", "units"]
            )
        ):
            scores["retail sales"] += 7

        # Inventory signals
        if (
            self._has_column(
                df,
                ["stocklevel", "stock_level", "stock"]
            )
            or
            self._has_column(
                df,
                ["reorderlevel", "reorder_level"]
            )
        ):
            scores["inventory"] += 8

        # Subscription signals
        if (
            self._has_column(
                df,
                [
                    "subscriptionid",
                    "subscription_id"
                ]
            )
            and
            self._has_column(
                df,
                ["plan"]
            )
        ):
            scores["subscription / saas"] += 8

        # --------------------------------------------------------
        # Special restaurant override
        # --------------------------------------------------------

        if has_item and has_table_or_server:
            restaurant_score = scores["restaurant sales"]

            ecommerce_score = scores["e-commerce"]

            if restaurant_score >= ecommerce_score:
                return "restaurant sales"

        # --------------------------------------------------------
        # Select highest score
        # --------------------------------------------------------

        best_domain = max(
            scores,
            key=scores.get
        )

        best_score = scores[best_domain]

        if best_score <= 0:
            return "general business analytics"

        return best_domain

    # ============================================================
    # METRIC SELECTION
    # ============================================================

    def _select_metric_columns(
        self,
        df,
        numeric_columns,
        domain
    ):

        selected = []

        for column in numeric_columns:

            name = self._normalize(column)

            # Ignore technical/index-like numeric fields
            if self._is_identifier_column(
                column,
                df
            ):
                continue

            metric_keywords = [
                "sales",
                "revenue",
                "amount",
                "total",
                "profit",
                "income",
                "price",
                "cost",
                "quantity",
                "qty",
                "unit",
                "units",
                "stock",
                "inventory",
                "users",
                "activeusers",
                "subscribers",
                "customers",
                "churn",
                "fee",
                "mrr",
                "arr",
                "discount",
                "rate",
                "margin",
                "spend",
                "expense",
                "value",
            ]

            if any(
                keyword in name
                for keyword in metric_keywords
            ):
                selected.append(column)

        # If nothing matched, use numeric columns
        if not selected:
            selected = [
                column
                for column in numeric_columns
                if not self._is_identifier_column(
                    column,
                    df
                )
            ]

        # Domain-specific ordering
        selected = self._prioritize_metrics(
            selected,
            domain
        )

        return selected

    def _prioritize_metrics(
        self,
        columns,
        domain
    ):

        priority = {
            "restaurant sales": [
                "totalamount",
                "sales",
                "revenue",
                "quantity",
                "unitprice",
            ],

            "e-commerce": [
                "totalamount",
                "amount",
                "sales",
                "revenue",
                "quantity",
                "discount",
                "unitprice",
            ],

            "retail sales": [
                "sales",
                "revenue",
                "amount",
                "quantity",
                "unitprice",
            ],

            "inventory": [
                "stocklevel",
                "stock",
                "unitsin",
                "unitsout",
                "quantity",
                "unitcost",
            ],

            "subscription / saas": [
                "mrr",
                "arr",
                "monthlyfee",
                "users",
                "activeusers",
                "subscribers",
                "churned",
                "churn",
            ],
        }

        keywords = priority.get(
            domain,
            []
        )

        ordered = []

        for keyword in keywords:

            for column in columns:

                normalized = self._normalize(
                    column
                )

                if (
                    keyword in normalized
                    and column not in ordered
                ):
                    ordered.append(column)

        for column in columns:

            if column not in ordered:
                ordered.append(column)

        return ordered

    # ============================================================
    # DIMENSION SELECTION
    # ============================================================

    def _select_dimension_columns(
        self,
        df,
        categorical_columns,
        domain
    ):

        dimensions = []

        for column in categorical_columns:

            if self._is_identifier_column(
                column,
                df
            ):
                continue

            if self._is_text_or_free_form_column(
                df[column]
            ):
                continue

            # Avoid extremely high-cardinality fields
            unique_count = df[column].nunique(
                dropna=True
            )

            row_count = max(
                len(df),
                1
            )

            unique_ratio = (
                unique_count / row_count
            )

            if unique_ratio > 0.80:
                continue

            dimensions.append(column)

        # --------------------------------------------------------
        # Domain-specific meaningful dimensions
        # --------------------------------------------------------

        preferred = {
            "restaurant sales": [
                "item",
                "menuitem",
                "menu_item",
                "dish",
                "category",
                "server",
                "waiter",
                "paymentmethod",
                "payment_method",
                "region",
            ],

            "e-commerce": [
                "product",
                "category",
                "customer",
                "region",
                "paymentmethod",
                "payment_method",
                "shippingmethod",
                "shipping_method",
            ],

            "inventory": [
                "product",
                "category",
                "warehouse",
                "location",
                "supplier",
            ],

            "subscription / saas": [
                "plan",
                "customer",
                "region",
                "segment",
            ],

            "retail sales": [
                "product",
                "category",
                "region",
                "store",
                "branch",
            ],
        }

        preferred_keywords = preferred.get(
            domain,
            []
        )

        ordered = []

        # First add preferred dimensions
        for keyword in preferred_keywords:

            for column in dimensions:

                normalized = self._normalize(
                    column
                )

                if (
                    keyword in normalized
                    and column not in ordered
                ):
                    ordered.append(column)

        # Then remaining valid dimensions
        for column in dimensions:

            if column not in ordered:
                ordered.append(column)

        return ordered

    # ============================================================
    # IDENTIFIER DETECTION
    # ============================================================

    def _is_identifier_column(
        self,
        column,
        df
    ):

        name = self._normalize(column)

        # Exact identifier names
        identifier_names = {
            "id",
            "orderid",
            "order_id",
            "transactionid",
            "transaction_id",
            "customerid",
            "customer_id",
            "userid",
            "user_id",
            "subscriptionid",
            "subscription_id",
            "invoiceid",
            "invoice_id",
            "productid",
            "product_id",
            "categoryid",
            "category_id",
            "employeeid",
            "employee_id",
            "supplierid",
            "supplier_id",
            "warehouseid",
            "warehouse_id",
            "recordid",
            "record_id",
        }

        if name in identifier_names:
            return True

        # ID suffix/prefix
        if name.endswith("id"):
            return True

        if name.startswith("id"):
            return True

        # UUID-like / code-like fields
        if any(
            token in name
            for token in [
                "uuid",
                "guid",
                "identifier",
                "transactionnumber",
                "ordernumber",
                "invoicenumber",
            ]
        ):
            return True

        # Very high-cardinality fields are usually identifiers
        try:

            unique_count = df[column].nunique(
                dropna=True
            )

            row_count = max(
                len(df),
                1
            )

            if (
                unique_count >= 20
                and unique_count / row_count >= 0.85
            ):
                return True

        except Exception:
            pass

        return False

    def _is_text_or_free_form_column(
        self,
        series
    ):

        if series.empty:
            return True

        values = series.dropna().astype(str)

        if values.empty:
            return True

        avg_length = values.str.len().mean()

        # Long descriptions/comments should not be dimensions
        if avg_length > 40:
            return True

        return False

    # ============================================================
    # SUCCESS METRICS
    # ============================================================

    def _get_success_metrics(
        self,
        domain
    ):

        metrics = {

            "restaurant sales": [
                "total restaurant revenue",
                "total items sold",
                "top menu items",
                "sales by category",
                "sales by server",
                "sales by payment method",
            ],

            "e-commerce": [
                "total revenue",
                "total orders or units",
                "top products",
                "sales by category",
                "customer performance",
            ],

            "inventory": [
                "total inventory",
                "total units",
                "inventory by product",
                "inventory by location",
                "inventory by supplier",
            ],

            "subscription / saas": [
                "active customers or subscribers",
                "churn rate",
                "performance by plan",
            ],

            "retail sales": [
                "total sales",
                "total quantity",
                "top products",
                "sales by category",
                "sales by region",
            ],

            "general business analytics": [
                "primary business metric",
                "top performing dimensions",
                "time-based performance",
            ],
        }

        return metrics.get(
            domain,
            metrics["general business analytics"]
        )

    # ============================================================
    # HELPERS
    # ============================================================

    def _has_column(
        self,
        df,
        names
    ):

        normalized_columns = {
            self._normalize(column)
            for column in df.columns
        }

        for name in names:

            if self._normalize(name) in normalized_columns:
                return True

        return False

    def _normalize(self, value):

        text = str(value).strip().lower()

        return re.sub(
            r"[^a-z0-9]",
            "",
            text
        )