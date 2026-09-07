import pandas as pd
from typing import Dict, Tuple, Optional


class CleanAgent:
    """
    Production-grade generic data cleaning agent.

    Handles:
    - Missing values
    - Duplicate records
    - Numeric data type conversion
    - Date/datetime detection
    - Categorical values
    - Unexpected or malformed data
    """

    def __init__(self):
        self.name = "CleanAgent"

    def clean(
        self,
        csv_path: str,
        config: Optional[Dict] = None
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Clean any CSV dataset using generic rules.

        Args:
            csv_path: Path to the CSV file.
            config: Optional domain configuration from DomainConfigAgent.

        Returns:
            Tuple containing:
            - cleaned DataFrame
            - cleaning report
        """

        print(f"\n{'=' * 60}")
        print("CLEAN AGENT: Starting data cleaning")
        print(f"{'=' * 60}")

        # ---------------------------------------------------------
        # STEP 1: LOAD DATA
        # ---------------------------------------------------------
        try:
            df = pd.read_csv(csv_path)

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Dataset not found: {csv_path}"
            )

        except pd.errors.EmptyDataError:
            raise ValueError(
                "Dataset is empty."
            )

        except Exception as e:
            raise ValueError(
                f"Unable to read dataset: {e}"
            )

        if df.empty:
            raise ValueError(
                "Dataset contains no records."
            )

        # ---------------------------------------------------------
        # STEP 2: NORMALIZE COLUMN NAMES
        # ---------------------------------------------------------
        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
        )

        original_columns = list(df.columns)

        # ---------------------------------------------------------
        # BEFORE-CLEANING REPORT
        # ---------------------------------------------------------
        original_records = len(df)
        original_missing = int(
            df.isnull().sum().sum()
        )
        original_duplicates = int(
            df.duplicated().sum()
        )

        print("\nBEFORE CLEANING:")
        print(f"  - Total records: {original_records}")
        print(f"  - Columns: {len(df.columns)}")
        print(f"  - Missing values: {original_missing}")
        print(f"  - Duplicates: {original_duplicates}")

        # ---------------------------------------------------------
        # STEP 3: REMOVE DUPLICATES
        # ---------------------------------------------------------
        df = df.drop_duplicates()

        duplicates_removed = (
            original_records - len(df)
        )

        # ---------------------------------------------------------
        # STEP 4: DETECT AND FIX DATA TYPES
        # ---------------------------------------------------------
        numeric_columns = []
        datetime_columns = []
        categorical_columns = []

        for column in df.columns:

            # Skip completely empty columns
            if df[column].isna().all():
                continue

            # -----------------------------------------------------
            # Already numeric
            # -----------------------------------------------------
            if pd.api.types.is_numeric_dtype(
                df[column]
            ):
                numeric_columns.append(column)
                continue

            # -----------------------------------------------------
            # Try numeric conversion
            # -----------------------------------------------------
            numeric_candidate = pd.to_numeric(
                df[column],
                errors="coerce"
            )

            numeric_ratio = (
                numeric_candidate.notna().mean()
            )

            if numeric_ratio >= 0.80:
                df[column] = numeric_candidate
                numeric_columns.append(column)
                continue

            # -----------------------------------------------------
            # Try datetime conversion
            # -----------------------------------------------------
            try:
                datetime_candidate = pd.to_datetime(
                    df[column],
                    errors="coerce",
                    format="mixed"
                )

            except (TypeError, ValueError):
                datetime_candidate = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )

            datetime_ratio = (
                datetime_candidate.notna().mean()
            )

            if datetime_ratio >= 0.80:
                df[column] = datetime_candidate
                datetime_columns.append(column)
                continue

            # -----------------------------------------------------
            # Otherwise categorical/text
            # -----------------------------------------------------
            df[column] = (
                df[column]
                .astype(str)
                .str.strip()
            )

            categorical_columns.append(column)

        # ---------------------------------------------------------
        # STEP 5: HANDLE MISSING VALUES
        # ---------------------------------------------------------
        missing_before_handling = int(
            df.isnull().sum().sum()
        )

        missing_values_filled = 0
        rows_removed_for_missing = 0

        for column in list(df.columns):

            missing_count = int(
                df[column].isnull().sum()
            )

            if missing_count == 0:
                continue

            # -----------------------------------------------------
            # Numeric → median
            # -----------------------------------------------------
            if column in numeric_columns:

                median_value = df[column].median()

                if pd.notna(median_value):

                    df[column] = df[column].fillna(
                        median_value
                    )

                    missing_values_filled += (
                        missing_count
                    )

                else:

                    df = df.drop(
                        columns=[column]
                    )

            # -----------------------------------------------------
            # Datetime → remove invalid/missing dates
            # -----------------------------------------------------
            elif column in datetime_columns:

                before = len(df)

                df = df.dropna(
                    subset=[column]
                )

                rows_removed_for_missing += (
                    before - len(df)
                )

            # -----------------------------------------------------
            # Categorical/Text → Unknown
            # -----------------------------------------------------
            else:

                df[column] = df[column].fillna(
                    "Unknown"
                )

                missing_values_filled += (
                    missing_count
                )

        # ---------------------------------------------------------
        # STEP 6: REMOVE COMPLETELY EMPTY COLUMNS
        # ---------------------------------------------------------
        empty_columns = [
            column
            for column in df.columns
            if df[column].isnull().all()
        ]

        if empty_columns:

            df = df.drop(
                columns=empty_columns
            )

        # ---------------------------------------------------------
        # STEP 7: RESET INDEX
        # ---------------------------------------------------------
        df = df.reset_index(
            drop=True
        )

        # ---------------------------------------------------------
        # AFTER-CLEANING REPORT
        # ---------------------------------------------------------
        final_records = len(df)

        final_missing = int(
            df.isnull().sum().sum()
        )

        print("\nAFTER CLEANING:")
        print(f"  - Total records: {final_records}")
        print(f"  - Missing values: {final_missing}")
        print(
            f"  - Duplicates: "
            f"{df.duplicated().sum()}"
        )

        print("\nDETECTED DATA TYPES:")
        print(
            f"  - Numeric: "
            f"{numeric_columns}"
        )

        print(
            f"  - Datetime: "
            f"{datetime_columns}"
        )

        print(
            f"  - Categorical: "
            f"{categorical_columns}"
        )

        # ---------------------------------------------------------
        # CREATE CLEANING REPORT
        # ---------------------------------------------------------
        report = {
            "agent": self.name,
            "status": "success",
            "original_records": original_records,
            "cleaned_records": final_records,
            "duplicates_removed": duplicates_removed,
            "missing_values_before": original_missing,
            "missing_values_handled": missing_values_filled,
            "rows_removed_for_missing": (
                rows_removed_for_missing
            ),
            "missing_values_after": final_missing,
            "numeric_columns": numeric_columns,
            "datetime_columns": datetime_columns,
            "categorical_columns": categorical_columns,
            "columns_before": original_columns,
            "columns_after": list(df.columns),
            "empty_columns_removed": empty_columns,
            "data_types_fixed": True
        }

        print("\n✓ Cleaning complete!")

        return df, report