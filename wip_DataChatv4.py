# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 21:33:32 2026

@author: DELL
"""
###python -m streamlit run wip_DataChatv3.py
# -*- coding: utf-8 -*-

import os
import io
import ast
import re
import html
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
df = pd.read_csv(BASE_DIR / "datainfo.csv")
#path = 'F:\\DataChat\\chatbot'
#os.chdir(path)
#os.getcwd()

import pandas as pd
import streamlit as st
from openai import OpenAI

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    LongTable,
    TableStyle
)


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NexaData AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. CONFIGURATION
# ============================================================
#input_file = "F:\\DataChat\\chatbot"
#FILE_PATH = input_file+"\\"+"datainfo.csv"

###  ngrok token
##   ngrok config add-authtoken <your-ngrok-token>  
###  C:\Users\DELL\AppData\Local\ngrok\ngrok.yml 

###ngrok token
###ngrok http 80 --url https://spookily-clapper-squeeze.ngrok-free.dev

#API_KEY = "will add here locally"

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

st.set_page_config(
    page_title="NexaData AI",
    page_icon="🧠",
    layout="wide"
)


st.image("NexaData AI_ Ask_Analyze_Discover.png", width=500)


def ask_general_question(question):
    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions=(
            "You are NexaData AI, a helpful general-purpose "
            "assistant. Answer clearly and accurately. "
            "Help with Python, AI, data science, programming, "
            "and general knowledge. Do not analyze the CSV "
            "unless the user explicitly asks about it."
        ),
        input=question,
        max_output_tokens=1000
    )

    return response.output_text

tab1, tab2 = st.tabs([
    "💬 General Questions",
    "📊 Data-Specific Questions"
])
with tab1:
    st.subheader("Ask NexaData AI")
    st.caption("Have a question? Ask away! I'm here to help with whatever you need.")

    general_question = st.text_area(
        "",
        placeholder="Ask a general question...",
        height=100,
        key="general_question",
        label_visibility="collapsed"
    )

    if st.button("Ask AI", key="general_btn"):
        if general_question.strip():
            try:
                with st.spinner("NexaData AI is thinking..."):
                    answer = ask_general_question(
                        general_question.strip()
                    )

                st.markdown("### Answer")
                st.write(answer)

            except Exception as e:
                st.error(f"API request failed: {e}")
        else:
            st.warning("Please enter a question.")

# ============================================================
# 3. LOAD DATA
# ============================================================
with tab2:
    @st.cache_data
    def load_data(path):
    
        return pd.read_csv(
            path,
            header=0,
            low_memory=False
        )
    
    
    try:
    
        df = df
    
    except Exception as e:
    
        st.error(
            f"Unable to load CSV file:\n\n{e}"
        )
    
        st.stop()
    
    
    # ============================================================
    # 4. SESSION STATE
    # ============================================================
    
    if "history" not in st.session_state:
    
        st.session_state.history = []
    
    
    if "current" not in st.session_state:
    
        st.session_state.current = None
    
    
    # ============================================================
    # 5. ASK AI FOR PANDAS EXPRESSION
    # ============================================================
    
    def ask_dataframe(question):
    
        metadata = {
            "rows": len(df),
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict()
        }
    
        prompt = f"""
    You are an expert Python Pandas data analyst.
    
    DataFrame metadata:
    {metadata}
    
    User question:
    {question}
    
    Generate exactly ONE Python Pandas expression that answers
    the user's question.
    
    Rules:
    - Use the DataFrame named df.
    - Use only existing columns.
    - Do not create sample data.
    - Do not import anything.
    - Do not read files.
    - Do not write files.
    - Do not modify df.
    - Do not use inplace operations.
    - Return only the Python expression.
    - Do not return markdown.
    - Do not explain the expression.
    """
    
        response = client.responses.create(
            model="gpt-5.6-luna",
            input=prompt,
            max_output_tokens=500
        )
    
        return response.output_text.strip()
    
    
    # ============================================================
    # 6. CLEAN GENERATED CODE
    # ============================================================
    
    def clean_code(code):
    
        code = code.strip()
    
        if code.startswith("```python"):
    
            code = code[len("```python"):].strip()
    
        elif code.startswith("```"):
    
            code = code[3:].strip()
    
        if code.endswith("```"):
    
            code = code[:-3].strip()
    
        return code
    
    
    # ============================================================
    # 7. VALIDATE GENERATED CODE
    # ============================================================
    
    def validate_code(code):
    
        tree = ast.parse(
            code,
            mode="eval"
        )
    
        blocked_names = {
            "eval",
            "exec",
            "open",
            "compile",
            "__import__",
            "globals",
            "locals",
            "getattr",
            "setattr",
            "delattr",
            "input",
            "breakpoint"
        }
    
        blocked_methods = {
            "to_csv",
            "to_excel",
            "to_pickle",
            "to_sql",
            "to_json",
            "to_parquet",
            "to_clipboard",
            "to_hdf",
            "to_feather",
            "to_stata"
        }
    
        for node in ast.walk(tree):
    
            if isinstance(node, ast.Name):
    
                if node.id.startswith("_"):
    
                    raise ValueError(
                        "Private names are not allowed."
                    )
    
                if node.id in blocked_names:
    
                    raise ValueError(
                        f"Unsafe operation detected: {node.id}"
                    )
    
            if isinstance(node, ast.Attribute):
    
                if node.attr.startswith("_"):
    
                    raise ValueError(
                        "Private attributes are not allowed."
                    )
    
                if node.attr in blocked_methods:
    
                    raise ValueError(
                        f"File-writing operation is not allowed: "
                        f"{node.attr}"
                    )
    
            if isinstance(node, ast.NamedExpr):
    
                raise ValueError(
                    "Assignments are not allowed."
                )
    
        return code
    
    
    # ============================================================
    # 8. EXECUTE GENERATED EXPRESSION
    # ============================================================
    
    def execute_query(code):
    
        validate_code(code)
    
        # Work on a copy so the original DataFrame is protected.
        working_df = df.copy()
    
        return eval(
            code,
            {
                "__builtins__": {}
            },
            {
                "df": working_df,
                "pd": pd
            }
        )
    
    
    # ============================================================
    # 9. CONVERT RESULT TO DATAFRAME
    #
    # This is important for groupby results.
    #
    # Example:
    #
    # df.groupby("religion")["income"].describe()
    #
    # normally gives religion as an INDEX.
    #
    # reset_index() converts religion back into a column.
    # ============================================================
    
    def result_to_df(result):
    
        if isinstance(
            result,
            pd.DataFrame
        ):
    
            result = result.copy()
    
            if (
                result.index.name is not None
                or isinstance(result.index, pd.MultiIndex)
            ):
    
                result = result.reset_index()
    
            return result
    
    
        if isinstance(
            result,
            pd.Series
        ):
    
            result = result.copy()
    
            return result.reset_index(
                name="Value"
            )
    
    
        return pd.DataFrame(
            {
                "Result": [result]
            }
        )
    
    
    # ============================================================
    # 10. FIND COLUMNS USED IN GENERATED CODE
    # ============================================================
    
    def find_columns_in_code(code):
    
        found = []
    
        patterns = [
    
            r"df\s*\[\s*['\"]([^'\"]+)['\"]\s*\]",
    
            r"groupby\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
    
            r"get\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"
    
        ]
    
        for pattern in patterns:
    
            matches = re.findall(
                pattern,
                code
            )
    
            for match in matches:
    
                if match in df.columns:
    
                    found.append(match)
    
    
        # Remove duplicates while keeping order
        return list(
            dict.fromkeys(found)
        )
    
    
    # ============================================================
    # 11. FIND GROUPBY COLUMNS
    # ============================================================
    
    def find_groupby_columns(code):
    
        pattern = (
            r"groupby\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"
        )
    
        matches = re.findall(
            pattern,
            code
        )
    
        return [
            x
            for x in matches
            if x in df.columns
        ]
    
    
    # ============================================================
    # 12. GENERATE MEANINGFUL FILE TITLE
    # ============================================================
    
    def generate_filename_title(
        question,
        code
    ):
    
        question_lower = question.lower()
        code_lower = code.lower()
    
        columns = find_columns_in_code(
            code
        )
    
        group_columns = find_groupby_columns(
            code
        )
    
    
        # --------------------------------------------------------
        # Helper
        # --------------------------------------------------------
    
        def pretty_column(column):
    
            if not column:
    
                return None
    
            name = str(column)
    
            name = name.replace(
                "_",
                " "
            )
    
            name = re.sub(
                r"\s+",
                " ",
                name
            ).strip()
    
            return name.title().replace(
                " ",
                "_"
            )
    
    
        # --------------------------------------------------------
        # Special dataset questions
        # --------------------------------------------------------
    
        if (
            "shape" in question_lower
            or "shape" in code_lower
        ):
    
            return "Dataset_Shape"
    
    
        if (
            "file details" in question_lower
            or "dataset details" in question_lower
            or "file information" in question_lower
        ):
    
            return "Dataset_Details"
    
    
        if (
            "all columns" in question_lower
            or "column names" in question_lower
        ):
    
            return "All_Columns"
    
    
        if (
            "total records" in question_lower
            or "total number of records" in question_lower
            or code_lower.startswith("len(df)")
        ):
    
            return "Total_Record_Count"
    
    
        # --------------------------------------------------------
        # Group column
        # --------------------------------------------------------
    
        group_name = None
    
        if group_columns:
    
            group_name = pretty_column(
                group_columns[0]
            )
    
    
        # --------------------------------------------------------
        # Metric column
        # --------------------------------------------------------
    
        metric_columns = [
            col
            for col in columns
            if col not in group_columns
        ]
    
        metric = (
            metric_columns[0]
            if metric_columns
            else None
        )
    
        metric_name = pretty_column(
            metric
        )
    
    
        # --------------------------------------------------------
        # BLANK / MISSING
        # --------------------------------------------------------
    
        if (
            "isna" in code_lower
            or "isnull" in code_lower
            or "blank" in question_lower
            or "missing" in question_lower
        ):
    
            if metric_name:
    
                return (
                    f"Blank_{metric_name}_Count"
                )
    
            return "Blank_Value_Count"
    
    
        # --------------------------------------------------------
        # DUPLICATES
        # --------------------------------------------------------
    
        if (
            "duplicated" in code_lower
            or "duplicate" in question_lower
        ):
    
            if metric_name:
    
                return (
                    f"Duplicate_{metric_name}_Count"
                )
    
            return "Duplicate_Record_Count"
    
    
        # --------------------------------------------------------
        # STATISTICS
        # --------------------------------------------------------
    
        if (
            ".describe()" in code_lower
            or "statistics" in question_lower
            or "stats" in question_lower
            or "statistical" in question_lower
        ):
    
            if group_name and metric_name:
    
                return (
                    f"{group_name}_Wise_"
                    f"{metric_name}_Statistics"
                )
    
            if metric_name:
    
                return (
                    f"{metric_name}_Statistics"
                )
    
            if group_name:
    
                return (
                    f"{group_name}_Wise_Statistics"
                )
    
            return "Dataset_Statistics"
    
    
        # --------------------------------------------------------
        # TOTAL / SUM
        # --------------------------------------------------------
    
        if (
            ".sum()" in code_lower
            or "total" in question_lower
        ):
    
            if group_name and metric_name:
    
                return (
                    f"{group_name}_Wise_Total_"
                    f"{metric_name}"
                )
    
            if metric_name:
    
                return (
                    f"Total_{metric_name}"
                )
    
            if group_name:
    
                return (
                    f"{group_name}_Wise_Total"
                )
    
    
        # --------------------------------------------------------
        # AVERAGE / MEAN
        # --------------------------------------------------------
    
        if (
            ".mean()" in code_lower
            or "average" in question_lower
            or "avg" in question_lower
        ):
    
            if group_name and metric_name:
    
                return (
                    f"{group_name}_Wise_Average_"
                    f"{metric_name}"
                )
    
            if metric_name:
    
                return (
                    f"Average_{metric_name}"
                )
    
            if group_name:
    
                return (
                    f"{group_name}_Wise_Average"
                )
    
    
        # --------------------------------------------------------
        # COUNT
        # --------------------------------------------------------
    
        if (
            ".count()" in code_lower
            or ".size()" in code_lower
            or "count" in question_lower
            or "how many" in question_lower
            or "number of" in question_lower
        ):
    
            if group_name and metric_name:
    
                return (
                    f"{group_name}_Wise_"
                    f"{metric_name}_Count"
                )
    
            if group_name:
    
                return (
                    f"{group_name}_Wise_Count"
                )
    
            if metric_name:
    
                return (
                    f"{metric_name}_Count"
                )
    
            return "Record_Count"
    
    
        # --------------------------------------------------------
        # UNIQUE
        # --------------------------------------------------------
    
        if (
            "nunique" in code_lower
            or "unique" in question_lower
        ):
    
            if metric_name:
    
                return (
                    f"Unique_{metric_name}_Count"
                )
    
            return "Unique_Value_Count"
    
    
        # --------------------------------------------------------
        # GROUPBY FALLBACK
        # --------------------------------------------------------
    
        if group_name and metric_name:
    
            return (
                f"{group_name}_Wise_"
                f"{metric_name}_Analysis"
            )
    
    
        if group_name:
    
            return (
                f"{group_name}_Wise_Analysis"
            )
    
    
        if metric_name:
    
            return (
                f"{metric_name}_Analysis"
            )
    
    
        # --------------------------------------------------------
        # GENERAL FALLBACK
        # --------------------------------------------------------
    
        return "AI_Data_Analysis_Result"
    
    
    # ============================================================
    # 13. CLEAN WINDOWS FILENAME
    # ============================================================
    
    def safe_filename(name):
    
        name = re.sub(
            r'[<>:"/\\|?*]',
            "",
            name
        )
    
        name = re.sub(
            r"\s+",
            "_",
            name
        )
    
        name = re.sub(
            r"_+",
            "_",
            name
        )
    
        name = name.strip(
            " ._"
        )
    
        if not name:
    
            name = "AI_Data_Analysis_Result"
    
        return name[:100]
    
    
    # ============================================================
    # 14. GENERATE PDF
    # ============================================================
    
    def generate_pdf(
        question,
        code,
        result
    ):
    
        buffer = io.BytesIO()
    
        document = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=30,
            rightMargin=30,
            topMargin=30,
            bottomMargin=30
        )
    
        styles = getSampleStyleSheet()
    
        elements = []
    
    
        # --------------------------------------------------------
        # TITLE
        # --------------------------------------------------------
    
        elements.append(
            Paragraph(
                "AI Data Analyst Report",
                styles["Title"]
            )
        )
    
        elements.append(
            Spacer(1, 20)
        )
    
    
        # --------------------------------------------------------
        # QUESTION
        # --------------------------------------------------------
    
        elements.append(
            Paragraph(
                "Question",
                styles["Heading2"]
            )
        )
    
        elements.append(
            Paragraph(
                html.escape(
                    str(question)
                ),
                styles["Normal"]
            )
        )
    
        elements.append(
            Spacer(1, 15)
        )
    
    
        # --------------------------------------------------------
        # GENERATED CODE
        # --------------------------------------------------------
    
        elements.append(
            Paragraph(
                "Generated Pandas Expression",
                styles["Heading2"]
            )
        )
    
        elements.append(
            Paragraph(
                html.escape(
                    str(code)
                ),
                styles["Normal"]
            )
        )
    
        elements.append(
            Spacer(1, 15)
        )
    
    
        # --------------------------------------------------------
        # RESULT
        # --------------------------------------------------------
    
        elements.append(
            Paragraph(
                "Result",
                styles["Heading2"]
            )
        )
    
    
        result_df = result_to_df(
            result
        )
    
    
        # PDF preview only
        pdf_df = result_df.head(50)
    
        # Keep PDF readable
        pdf_df = pdf_df.iloc[:, :10]
    
    
        if len(pdf_df.columns) > 0:
    
            data = []
    
    
            # Header
            data.append(
                [
                    Paragraph(
                        html.escape(
                            str(column)
                        ),
                        styles["Normal"]
                    )
                    for column in pdf_df.columns
                ]
            )
    
    
            # Rows
            for row in pdf_df.itertuples(
                index=False,
                name=None
            ):
    
                data.append(
                    [
                        Paragraph(
                            html.escape(
                                str(value)
                            ),
                            styles["Normal"]
                        )
                        for value in row
                    ]
                )
    
    
            column_count = len(
                pdf_df.columns
            )
    
    
            available_width = (
                landscape(A4)[0] - 60
            )
    
    
            column_width = (
                available_width /
                column_count
            )
    
    
            table = LongTable(
                data,
                colWidths=[
                    column_width
                ] * column_count,
                repeatRows=1
            )
    
    
            table.setStyle(
                TableStyle([
    
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey
                    ),
    
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.grey
                    ),
    
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),
    
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        8
                    ),
    
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    )
    
                ])
            )
    
    
            elements.append(
                table
            )
    
    
        elements.append(
            Spacer(1, 15)
        )
    
    
        elements.append(
            Paragraph(
                f"PDF preview: "
                f"{len(pdf_df):,} rows and "
                f"{len(pdf_df.columns):,} columns.",
                styles["Normal"]
            )
        )
    
    
        document.build(
            elements
        )
    
    
        buffer.seek(0)
    
        return buffer.getvalue()
    
    
    # ============================================================
    # 15. GENERATE EXCEL
    # ============================================================
    
    def generate_excel(result):
    
        buffer = io.BytesIO()
    
        result_df = result_to_df(
            result
        )
    
        result_df.to_excel(
            buffer,
            index=False,
            engine="openpyxl",
            sheet_name="Result"
        )
    
        buffer.seek(0)
    
        return buffer.getvalue()
    
    
    # ============================================================
    # 16. SIDEBAR - QUESTION HISTORY
    # ============================================================
    
    with st.sidebar:
    
        st.header(
            "🕘 Question History"
        )
    
    
        history = (
            st.session_state.history
        )
    
    
        st.caption(
            f"Questions asked: {len(history)}"
        )
    
    
        st.divider()
    
    
        # --------------------------------------------------------
        # HISTORY
        # --------------------------------------------------------
    
        for i in range(
            len(history) - 1,
            -1,
            -1
        ):
    
            item = history[i]
    
            question_text = (
                item["question"]
            )
    
    
            if len(question_text) > 45:
    
                display_text = (
                    question_text[:45]
                    + "..."
                )
    
            else:
    
                display_text = question_text
    
    
            if st.button(
                f"🔹 {display_text}",
                key=f"history_{i}",
                use_container_width=True
            ):
    
                st.session_state.current = (
                    item
                )
    
                st.rerun()
    
    
        # --------------------------------------------------------
        # CLEAR HISTORY
        # --------------------------------------------------------
    
        st.divider()
    
    
        if st.button(
            "🗑️ Clear History",
            use_container_width=True
        ):
    
            st.session_state.history = []
    
            st.session_state.current = None
    
            st.rerun()
    
    
    # ============================================================
    # 17. MAIN PAGE
    # ============================================================
    # st.set_page_config(
    #     page_title="NexaData AI",
    #     page_icon="🧠",
    #     layout="wide"
    # )
    
    
    # st.image("NexaData AI_ Ask_Analyze_Discover.png", width=500)
    
    #st.title("NexaData AI")
    #st.caption("Ask. Analyze. Discover.")
    
    
    ##st.title("NexaData AI")
    ##st.caption("Ask. Analyze. Discover.")
    
    ##st.write(
    ##    "Ask questions about your CSV dataset "
    ##    "using natural language."
    ##)
    
    
    
    # ============================================================
    # DATASET INFORMATION
    # ============================================================
    
    # col1, col2 = st.columns(2)
    
    
    # with col1:
    
    #     st.metric(
    #         "Total Rows",
    #         f"{len(df):,}"
    #     )
    
    
    # with col2:
    
    #     st.metric(
    #         "Total Columns",
    #         f"{len(df.columns):,}"
    #     )
    
    
    # ============================================================
    # QUESTION INPUT
    # ============================================================
    
    st.subheader("Ask NexaData AI")
    #st.caption("What would you like to discover from your data?")
    
    question = st.text_area(
        "",
        placeholder="e.g., What is the total income by nationality?",
        height=60,
        label_visibility="collapsed"
    )
    
    
    # ============================================================
    # ASK QUESTION
    # ============================================================
    
    if st.button(
        "🔍 Ask Question",
        type="primary"
    ):
    
        if not question.strip():
    
            st.warning(
                "Please enter a question."
            )
    
        else:
    
            with st.spinner(
                "Analyzing your data..."
            ):
    
                try:
    
                    # Generate Pandas expression
                    code = ask_dataframe(
                        question
                    )
    
    
                    # Clean generated expression
                    code = clean_code(
                        code
                    )
    
    
                    # Execute expression
                    result = execute_query(
                        code
                    )
    
    
                    # Create history item
                    item = {
                        "question": question,
                        "code": code,
                        "result": result
                    }
    
    
                    # Save history
                    st.session_state.history.append(
                        item
                    )
    
    
                    # Current result
                    st.session_state.current = (
                        item
                    )
    
    
                    st.success(
                        "Question answered successfully!"
                    )
    
    
                except Exception as e:
    
                    st.error(
                        f"Could not process the question:\n\n{e}"
                    )
    
    
    # ============================================================
    # 18. DISPLAY CURRENT RESULT
    # ============================================================
    
    current = (
        st.session_state.current
    )
    
    
    if current is not None:
    
        st.divider()
    
    
        # ========================================================
        # QUESTION
        # ========================================================
    
        st.subheader(
            "❓ Question"
        )
    
        st.write(
            current["question"]
        )
    
    
        # ========================================================
        # GENERATED PANDAS CODE
        # ========================================================
    
        st.subheader(
            "🐍 Generated Pandas Expression"
        )
    
        st.code(
            current["code"],
            language="python"
        )
    
    
        # ========================================================
        # ANSWER
        # ========================================================
    
        st.subheader(
            "✅ Answer"
        )
    
    
        result = current["result"]
    
    
        if isinstance(
            result,
            (pd.DataFrame, pd.Series)
        ):
    
            display_result = result_to_df(
                result
            )
    
            st.dataframe(
                display_result,
                use_container_width=True
            )
    
        else:
    
            st.success(
                str(result)
            )
    
    
        # ========================================================
        # DOWNLOAD SECTION
        # ========================================================
    
        st.divider()
    
    
        st.subheader(
            "📥 Download Result"
        )
    
    
        # --------------------------------------------------------
        # Meaningful filename
        # --------------------------------------------------------
    
        file_title = generate_filename_title(
            current["question"],
            current["code"]
        )
    
    
        file_title = safe_filename(
            file_title
        )
    
    
        pdf_filename = (
            f"{file_title}.pdf"
        )
    
        excel_filename = (
            f"{file_title}.xlsx"
        )
    
    
        # --------------------------------------------------------
        # Generate PDF and Excel
        # --------------------------------------------------------
    
        try:
    
            pdf_data = generate_pdf(
                current["question"],
                current["code"],
                result
            )
    
    
            excel_data = generate_excel(
                result
            )
    
    
            # ----------------------------------------------------
            # Show filenames
            # ----------------------------------------------------
    
            st.caption(
                f"Generated files: "
                f"`{pdf_filename}`  |  "
                f"`{excel_filename}`"
            )
    
    
            # ----------------------------------------------------
            # Download buttons
            # ----------------------------------------------------
    
            col1, col2 = st.columns(2)
    
    
            # PDF
            with col1:
    
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_data,
                    file_name=pdf_filename,
                    mime="application/pdf",
                    use_container_width=True
                )
    
    
            # Excel
            with col2:
    
                st.download_button(
                    label="📊 Download Excel",
                    data=excel_data,
                    file_name=excel_filename,
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    use_container_width=True
                )
    
    
        except Exception as e:
    
            st.error(
                f"Could not generate download files:\n\n{e}"
            )
