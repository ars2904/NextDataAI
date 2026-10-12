"""Data ingestion and schema profiling module for NexaData AI."""
import io
from pathlib import Path
from typing import Union, Tuple, Dict, Any, Optional
import pandas as pd
from core.config import DEFAULT_DATA_PATH


def load_dataset(source: Optional[Union[str, Path, io.BytesIO, Any]] = None) -> Tuple[pd.DataFrame, str]:
    """
    Load a dataset from a file path, file-like object, or fallback to the default datainfo.csv.
    
    Returns:
        Tuple[pd.DataFrame, str]: The loaded DataFrame and the source filename/identifier.
    """
    if source is None:
        source = DEFAULT_DATA_PATH

    filename = "default_dataset.csv"
    
    if isinstance(source, (str, Path)):
        path = Path(source)
        filename = path.name
        suffix = path.suffix.lower()
        if suffix == ".csv":
            df = pd.read_csv(path, low_memory=False)
        elif suffix in [".xlsx", ".xls"]:
            df = pd.read_excel(path)
        elif suffix == ".parquet":
            df = pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    else:
        # File-like object (e.g. Streamlit UploadedFile)
        filename = getattr(source, "name", "uploaded_file.csv")
        suffix = Path(filename).suffix.lower()
        if suffix == ".csv":
            df = pd.read_csv(source, low_memory=False)
        elif suffix in [".xlsx", ".xls"]:
            df = pd.read_excel(source)
        elif suffix == ".parquet":
            df = pd.read_parquet(source)
        else:
            # Fallback attempt as CSV
            df = pd.read_csv(source, low_memory=False)

    # Clean whitespace from column names for robust querying
    df.columns = [str(c).strip() for c in df.columns]
    return df, filename


def get_dataset_profile(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate rich metadata and statistical profile of the DataFrame
    used both for user exploration and feeding context to the AI model.
    """
    total_rows = len(df)
    total_cols = len(df.columns)
    
    # Categorize columns
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime"]).columns.tolist()
    categorical_cols = [c for c in df.columns if c not in numeric_cols and c not in datetime_cols]
    
    missing_summary = df.isnull().sum().to_dict()
    dtypes_summary = df.dtypes.astype(str).to_dict()
    
    # Sample unique values for categorical columns (up to 5 per column) for AI context
    sample_values = {}
    for col in df.columns:
        uniques = df[col].dropna().unique()
        if len(uniques) > 0:
            sample_values[col] = [str(v) for v in uniques[:5]]
            
    memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

    return {
        "rows": total_rows,
        "columns": list(df.columns),
        "column_count": total_cols,
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "datetime_columns": datetime_cols,
        "dtypes": dtypes_summary,
        "missing_values": missing_summary,
        "sample_values": sample_values,
        "memory_mb": round(memory_mb, 2),
    }
