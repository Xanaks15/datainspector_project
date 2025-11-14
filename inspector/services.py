"""
Data profiling services used by the inspector API.

The DataProfile class encapsulates methods for loading a CSV file and
computing summary statistics, missing values, data types, unique
counts, histograms, duplicates and column names. Each method returns
plain Python structures that can be serialized to JSON by Django REST
Framework without additional processing.

The class is deliberately stateless beyond loading the file: every
method reloads the dataset to ensure that the most up-to-date data is
analyzed. This design makes the service resilient to file changes
between requests and eliminates the need for caching or database
storage of intermediary results.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Tuple
import pandas as pd


class DataProfile:
    """Encapsulates data analysis on a CSV file."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def _load_dataframe(self) -> pd.DataFrame:
        """Load the dataset from disk into a pandas DataFrame."""
        # Use low_memory=False to ensure correct type inference on large files
        return pd.read_csv(self.file_path, low_memory=False)

    def summary(self) -> Dict[str, Any]:
        """Compute basic summary statistics of the dataset."""
        df = self._load_dataframe()
        rows, cols = df.shape
        memory_bytes = df.memory_usage(deep=True).sum()
        missing_total = df.isna().sum().sum()
        missing_pct = (missing_total / (rows * cols) * 100) if rows and cols else 0
        duplicate_rows = int(df.duplicated().sum())
        return {
            'rows': int(rows),
            'columns': int(cols),
            'memory_bytes': int(memory_bytes),
            'missing_total': int(missing_total),
            'missing_pct': float(missing_pct),
            'duplicate_rows': duplicate_rows,
        }

    def missing(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return missing value counts by column."""
        df = self._load_dataframe()
        miss = df.isna().sum()
        result: List[Dict[str, Any]] = []
        for col, count in miss.items():
            result.append({
                'column': col,
                'missing': int(count),
                'missing_pct': float((count / len(df)) * 100) if len(df) else 0,
            })
        return {'missing_by_column': result}

    def dtypes(self) -> Dict[str, List[Dict[str, str]]]:
        """Return inferred data types for each column."""
        df = self._load_dataframe()
        result: List[Dict[str, str]] = []
        for col, dtype in df.dtypes.items():
            # Use pandas.api.types.infer_dtype for a more human-friendly type
            inferred = pd.api.types.infer_dtype(df[col], skipna=True)
            result.append({
                'column': col,
                'dtype': str(dtype),
                'inferred': inferred,
            })
        return {'dtypes': result}

    def nunique(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return number of unique values by column."""
        df = self._load_dataframe()
        unique_counts = df.nunique(dropna=False)
        result: List[Dict[str, Any]] = []
        for col, count in unique_counts.items():
            result.append({
                'column': col,
                'unique': int(count),
            })
        return {'nunique': result}

    def outlier_table(self):
        df = self._load_dataframe()   # ✔ CORRECTO
        numeric = df.select_dtypes(include="number")

        results = []
        for col in numeric.columns:
            series = numeric[col].dropna()

            if len(series) == 0:
                continue

            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            mask = (series < lower) | (series > upper)
            outliers_count = mask.sum()
            pct = (outliers_count / len(series)) * 100

            results.append({
                "column": col,
                "outliers": int(outliers_count),
                "pct": round(pct, 2)
            })

        return {"outliers": results}


    def duplicates(self, sample_size: int = 5) -> Dict[str, Any]:
        """Return a sample of duplicated rows and their count."""
        df = self._load_dataframe()
        duplicated_mask = df.duplicated(keep=False)
        duplicates_df = df[duplicated_mask]
        count = int(duplicates_df.shape[0])
        # Take a sample of up to `sample_size` duplicates to send to the client
        sample = duplicates_df.head(sample_size).to_dict(orient='records')
        return {
            'count': count,
            'duplicates_sample': sample,
        }

    def columns(self) -> Dict[str, List[str]]:
        """Return a list of column names in the dataset."""
        df = self._load_dataframe()
        return {'columns': df.columns.tolist()}