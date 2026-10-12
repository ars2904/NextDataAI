"""Interactive Plotly visualization generator and auto-chart engine."""
from typing import Optional, Dict, Any, Tuple
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io


def auto_detect_chart_type(df: pd.DataFrame) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Intelligently infer the most appropriate chart type and axes based on DataFrame structure.
    
    Returns:
        Tuple[str, Optional[str], Optional[str]]: (chart_type, x_col, y_col)
    """
    if df is None or len(df) == 0:
        return "none", None, None
        
    cols = df.columns.tolist()
    if len(cols) == 1:
        # Single column
        if pd.api.types.is_numeric_dtype(df[cols[0]]):
            return "histogram", cols[0], None
        return "bar", cols[0], None

    numeric_cols = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
    categorical_cols = [c for c in cols if c not in numeric_cols]

    # Standard Aggregation: 1 categorical + 1 numeric (e.g. City vs Average Income)
    if len(categorical_cols) == 1 and len(numeric_cols) >= 1:
        cat_col = categorical_cols[0]
        num_col = numeric_cols[0]
        unique_count = df[cat_col].nunique()
        
        if 2 <= unique_count <= 6:
            return "pie", cat_col, num_col
        return "bar", cat_col, num_col

    # Multi-group Aggregation: 2 categorical + 1 numeric
    if len(categorical_cols) >= 2 and len(numeric_cols) >= 1:
        return "grouped_bar", categorical_cols[0], numeric_cols[0]

    # 2 numeric columns: Correlation / Scatter
    if len(numeric_cols) >= 2 and len(categorical_cols) == 0:
        return "scatter", numeric_cols[0], numeric_cols[1]

    # Default fallback: pick first column as X, first numeric as Y if exists
    x_col = cols[0]
    y_col = numeric_cols[0] if numeric_cols else (cols[1] if len(cols) > 1 else None)
    return "bar", x_col, y_col


def create_chart(
    df: pd.DataFrame,
    chart_type: Optional[str] = None,
    x_col: Optional[str] = None,
    y_col: Optional[str] = None,
    title: str = "Query Result Visualization"
) -> Optional[go.Figure]:
    """
    Generate an interactive Plotly figure with modern styling.
    """
    if df is None or len(df) == 0:
        return None

    # Auto-detect if not explicitly provided
    detected_type, detected_x, detected_y = auto_detect_chart_type(df)
    chart_type = chart_type or detected_type
    x_col = x_col or detected_x
    y_col = y_col or detected_y

    color_sequence = ["#2563EB", "#059669", "#D97706", "#DC2626", "#7C3AED", "#DB2777"]

    fig = None
    if chart_type == "bar" and x_col and y_col:
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            title=title,
            color_discrete_sequence=color_sequence,
            text_auto=True
        )
        fig.update_layout(xaxis_tickangle=-30)

    elif chart_type == "pie" and x_col and y_col:
        fig = px.pie(
            df,
            names=x_col,
            values=y_col,
            title=title,
            hole=0.4,
            color_discrete_sequence=color_sequence
        )

    elif chart_type == "line" and x_col and y_col:
        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            title=title,
            markers=True,
            color_discrete_sequence=color_sequence
        )

    elif chart_type == "scatter" and x_col and y_col:
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            title=title,
            color_discrete_sequence=color_sequence
        )

    elif chart_type == "histogram" and x_col:
        fig = px.histogram(
            df,
            x=x_col,
            title=title,
            color_discrete_sequence=color_sequence
        )

    if fig:
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=40, r=40, t=50, b=40),
            font=dict(family="Inter, Segoe UI, sans-serif", size=13),
            title=dict(font=dict(size=16, color="#1E293B"))
        )
    return fig


def figure_to_image_bytes(fig: go.Figure) -> Optional[bytes]:
    """
    Export a Plotly figure to static PNG bytes for PDF generation.
    Falls back gracefully if static image rendering is unavailable.
    """
    if fig is None:
        return None
    try:
        return fig.to_image(format="png", width=800, height=450, scale=2)
    except Exception:
        # If kaleido engine is not present, return None so PDF generator falls back cleanly
        return None
