"""NexaData AI - Advanced Autonomous Data Analyst Platform."""
import os
import streamlit as st
import pandas as pd
from openai import OpenAI

from core.config import (
    APP_TITLE,
    APP_SUBTITLE,
    APP_ICON,
    DEFAULT_DATA_PATH,
    LOGO_PATH,
    DEFAULT_MODEL,
    get_openai_api_key
)
from connectors.loader import load_dataset, get_dataset_profile
from engine.query_engine import run_analytical_query
from visualizer.charts import create_chart, auto_detect_chart_type, figure_to_image_bytes
from reporting.pdf_generator import generate_executive_pdf
from reporting.excel_generator import generate_executive_excel


# 1. Page Configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Session State Initialization
if "history" not in st.session_state:
    st.session_state.history = []
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "df" not in st.session_state:
    st.session_state.df = None
if "dataset_name" not in st.session_state:
    st.session_state.dataset_name = "datainfo.csv"


# 3. Sidebar Configuration
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)
    else:
        st.title(f"{APP_ICON} {APP_TITLE}")
    
    st.caption(APP_SUBTITLE)
    st.divider()

    # API Key Configuration
    default_key = get_openai_api_key()
    api_key = st.text_input(
        "🔑 OpenAI API Key",
        value=default_key,
        type="password",
        help="Enter your OpenAI API key or configure it in .streamlit/secrets.toml"
    )

    # Model Selection
    selected_model = st.selectbox(
        "🧠 AI Model",
        options=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        index=0
    )

    st.divider()

    # Data Source Selection
    st.subheader("📁 Data Source")
    use_default = st.checkbox("Use default dataset (datainfo.csv)", value=True)
    uploaded_file = None

    if not use_default:
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel file",
            type=["csv", "xlsx", "xls", "parquet"]
        )

    # Load dataset
    try:
        if use_default or uploaded_file is None:
            if st.session_state.df is None or st.session_state.dataset_name != "datainfo.csv":
                df, fname = load_dataset(DEFAULT_DATA_PATH)
                st.session_state.df = df
                st.session_state.dataset_name = fname
        else:
            df, fname = load_dataset(uploaded_file)
            st.session_state.df = df
            st.session_state.dataset_name = fname
    except Exception as e:
        st.error(f"Error loading dataset: {e}")

    df = st.session_state.df
    dataset_name = st.session_state.dataset_name

    if df is not None:
        profile = get_dataset_profile(df)
        st.caption(f"**Loaded:** `{dataset_name}`")
        col_s1, col_s2 = st.columns(2)
        col_s1.metric("Rows", f"{profile['rows']:,}")
        col_s2.metric("Columns", f"{profile['column_count']:,}")

    # Query History
    st.divider()
    st.subheader("🕘 Query History")
    if st.session_state.history:
        for idx, item in enumerate(reversed(st.session_state.history)):
            q_label = item["question"]
            if len(q_label) > 35:
                q_label = q_label[:35] + "..."
            if st.button(f"🔹 {q_label}", key=f"hist_{idx}", use_container_width=True):
                st.session_state.current_result = item
                st.rerun()

        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history = []
            st.session_state.current_result = None
            st.rerun()
    else:
        st.caption("No queries asked yet.")


# 4. Main Page Tabs
tab_analyst, tab_explorer, tab_general = st.tabs([
    "🤖 AI Data Analyst",
    "📊 Data Explorer & Schema",
    "💬 General Assistant"
])

# -------------------------------------------------------------
# TAB 1: AI DATA ANALYST
# -------------------------------------------------------------
with tab_analyst:
    st.subheader("Ask NexaData AI")
    st.caption("Ask questions about your data in plain English. NexaData AI translates them into high-performance SQL, runs the numbers, creates visualizations, and compiles executive reports.")

    # Example chips
    st.markdown("**Quick Prompts:**")
    prompt_cols = st.columns(3)
    sample_q = ""
    if prompt_cols[0].button("💰 Income by nationality", use_container_width=True):
        sample_q = "What is the average and total income by nationality?"
    if prompt_cols[1].button("🏙️ Top cities by population", use_container_width=True):
        sample_q = "Show the top 5 cities by total number of records"
    if prompt_cols[2].button("💼 Job distribution & age", use_container_width=True):
        sample_q = "What is the average age and employee count for each job?"

    question_input = st.text_area(
        "Enter your question:",
        value=sample_q,
        placeholder="e.g., What is the average income by city and married status?",
        height=75,
        label_visibility="collapsed"
    )

    col_btn1, col_btn2 = st.columns([1, 5])
    ask_clicked = col_btn1.button("🔍 Ask Question", type="primary", use_container_width=True)

    if ask_clicked:
        if not api_key:
            st.error("Please provide an OpenAI API key in the sidebar.")
        elif not question_input.strip():
            st.warning("Please type a question.")
        else:
            with st.spinner("Analyzing dataset with DuckDB & AI..."):
                try:
                    client = OpenAI(api_key=api_key)
                    query_result = run_analytical_query(
                        question=question_input.strip(),
                        df=df,
                        profile=profile,
                        client=client,
                        model=selected_model
                    )

                    if query_result["success"]:
                        result_item = {
                            "question": question_input.strip(),
                            "query": query_result["query"],
                            "result_df": query_result["result"],
                            "attempts": query_result["attempts"]
                        }
                        st.session_state.history.append(result_item)
                        st.session_state.current_result = result_item
                        st.success("Analysis complete!")
                    else:
                        st.error(f"Analysis failed: {query_result['error']}")
                except Exception as e:
                    st.error(f"Execution error: {e}")

    # Display Current Result
    curr = st.session_state.current_result
    if curr is not None:
        st.divider()
        st.markdown(f"### ❓ **Question:** {curr['question']}")
        
        # Executed Query Expander
        with st.expander("🛠️ View Executed DuckDB SQL Query", expanded=False):
            st.code(curr["query"], language="sql")

        res_df = curr["result_df"]

        if res_df is not None and len(res_df) > 0:
            # Layout: Left side Tabular findings, Right side Visualizations
            col_data, col_viz = st.columns([1, 1])

            with col_data:
                st.markdown("#### 📋 Data Findings")
                st.caption(f"Returned **{len(res_df):,}** records")
                st.dataframe(res_df, use_container_width=True, height=380)

            with col_viz:
                st.markdown("#### 📈 Interactive Visualization")
                # Auto chart type
                default_type, auto_x, auto_y = auto_detect_chart_type(res_df)
                
                chart_selector_col, _ = st.columns([2, 1])
                chart_type = chart_selector_col.selectbox(
                    "Chart Type",
                    options=["bar", "pie", "line", "scatter"],
                    index=["bar", "pie", "line", "scatter"].index(default_type) if default_type in ["bar", "pie", "line", "scatter"] else 0,
                    key="chart_type_selector"
                )

                fig = create_chart(
                    df=res_df,
                    chart_type=chart_type,
                    x_col=auto_x,
                    y_col=auto_y,
                    title=curr["question"][:50]
                )
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Chart not available for this data shape.")

            # -------------------------------------------------------------
            # DOWNLOAD CENTER (PDF & EXCEL)
            # -------------------------------------------------------------
            st.divider()
            st.subheader("📥 Export & Download Executive Reports")
            st.caption("Generate client-ready PDF and Excel reports with embedded formatting and metadata.")

            col_pdf, col_xlsx = st.columns(2)

            with col_pdf:
                # Generate PDF with optional chart image
                chart_img_bytes = figure_to_image_bytes(fig) if fig else None
                try:
                    pdf_bytes = generate_executive_pdf(
                        question=curr["question"],
                        query=curr["query"],
                        df_result=res_df,
                        dataset_name=dataset_name,
                        chart_image_bytes=chart_img_bytes
                    )
                    safe_name = curr["question"][:30].strip().replace(" ", "_").replace("?", "")
                    st.download_button(
                        label="📄 Download Executive PDF Report",
                        data=pdf_bytes,
                        file_name=f"{safe_name}_Report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error compiling PDF: {e}")

            with col_xlsx:
                try:
                    excel_bytes = generate_executive_excel(
                        question=curr["question"],
                        query=curr["query"],
                        df_result=res_df,
                        dataset_name=dataset_name
                    )
                    safe_name = curr["question"][:30].strip().replace(" ", "_").replace("?", "")
                    st.download_button(
                        label="📊 Download Styled Excel Workbook",
                        data=excel_bytes,
                        file_name=f"{safe_name}_Analysis.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error compiling Excel: {e}")


# -------------------------------------------------------------
# TAB 2: DATA EXPLORER & SCHEMA
# -------------------------------------------------------------
with tab_explorer:
    st.subheader("Dataset Profiler & Schema Inspector")
    if df is not None:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Records", f"{profile['rows']:,}")
        m2.metric("Total Columns", f"{profile['column_count']:,}")
        m3.metric("Numeric Columns", len(profile['numeric_columns']))
        m4.metric("Memory Footprint", f"{profile['memory_mb']} MB")

        st.divider()
        st.markdown("#### Sample Records (Top 10)")
        st.dataframe(df.head(10), use_container_width=True)

        st.divider()
        st.markdown("#### Column Schema & Completeness")
        schema_rows = []
        for col in profile["columns"]:
            schema_rows.append({
                "Column Name": col,
                "Data Type": profile["dtypes"].get(col, ""),
                "Missing Values": profile["missing_values"].get(col, 0),
                "Completeness": f"{(1 - (profile['missing_values'].get(col, 0) / profile['rows'])) * 100:.1f}%",
                "Sample Unique Values": ", ".join(profile["sample_values"].get(col, [])[:4])
            })
        st.dataframe(pd.DataFrame(schema_rows), use_container_width=True)


# -------------------------------------------------------------
# TAB 3: GENERAL ASSISTANT
# -------------------------------------------------------------
with tab_general:
    st.subheader("NexaData AI General Assistant")
    st.caption("Ask general questions about Python, data analysis, statistics, or AI concepts.")

    gen_q = st.text_area("Ask any question:", placeholder="e.g., Explain the difference between DuckDB and Pandas.")
    if st.button("Ask Assistant", type="secondary"):
        if not api_key:
            st.error("Please enter an OpenAI API key in the sidebar.")
        elif not gen_q.strip():
            st.warning("Please type a question.")
        else:
            with st.spinner("Thinking..."):
                try:
                    client = OpenAI(api_key=api_key)
                    resp = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {"role": "system", "content": "You are NexaData AI, an expert AI and data science assistant. Provide clear, concise, and helpful answers."},
                            {"role": "user", "content": gen_q.strip()}
                        ],
                        max_tokens=800
                    )
                    st.markdown("### Answer")
                    st.write(resp.choices[0].message.content)
                except Exception as e:
                    st.error(f"API request failed: {e}")
