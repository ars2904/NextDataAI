"""NexaData AI - Official Dual-Mode Streamlit Application.
Seamlessly deployable to Streamlit Community Cloud.
"""
import os
import sys
from pathlib import Path
import streamlit as st
from openai import OpenAI

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from rag.engine import knowledge_base

# 1. Page Configuration
ICON_PATH = BASE_DIR / "frontend" / "icon.png"
LOGO_PATH = BASE_DIR / "frontend" / "logo_dark.png"
FALLBACK_LOGO = BASE_DIR / "NexaData AI_ Ask_Analyze_Discover.png"

st.set_page_config(
    page_title="NexaData AI - Ask. Analyze. Discover.",
    page_icon=str(ICON_PATH) if ICON_PATH.exists() else "🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Modern Dark Styling (Matching High-Fidelity Mockup)
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background: radial-gradient(circle at 50% 10%, rgba(14, 165, 233, 0.08) 0%, #050814 70%);
        color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Header branding */
    .brand-hero-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 10px 0 20px;
    }
    
    /* Custom Cards */
    .stCard {
        background-color: #0B1326;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    /* Source Citations */
    .source-box {
        background: rgba(2, 132, 199, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 10px;
        font-size: 13px;
    }
    
    .disclaimer-box {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 10px;
        font-size: 12px;
        color: #94A3B8;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        justify-content: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 24px;
        padding: 8px 20px;
        background-color: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #94A3B8;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #0284C7 !important;
        color: #FFFFFF !important;
        border-color: #0284C7 !important;
        font-weight: 600;
        box-shadow: 0 0 15px rgba(2, 132, 199, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# 3. Retrieve API Key
api_key = None
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
elif os.getenv("OPENAI_API_KEY"):
    api_key = os.getenv("OPENAI_API_KEY")

with st.sidebar:
    st.subheader("⚙️ Settings")
    if not api_key:
        api_key = st.text_input("OpenAI API Key", type="password", help="Enter key or save in Streamlit Secrets")
    st.markdown("---")
    st.markdown("**NexaData AI** - Enterprise Intelligence")
    st.caption("PDF RAG Grounded + General Multi-Mode Chat")
    if st.button("🗑️ Clear Current Chat"):
        st.session_state.company_messages = []
        st.session_state.general_messages = []
        st.rerun()

client = OpenAI(api_key=api_key) if api_key else None

# 4. Initialize Session State
if "company_messages" not in st.session_state:
    st.session_state.company_messages = []
if "general_messages" not in st.session_state:
    st.session_state.general_messages = []

# 5. Header / Brand Banner
col_l, col_c, col_r = st.columns([1, 2, 1])
with col_c:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)
    elif FALLBACK_LOGO.exists():
        st.image(str(FALLBACK_LOGO), use_container_width=True)
    else:
        st.title("🧠 NexaData AI")
        st.caption("Ask. Analyze. Discover.")

# 6. Mode Switcher Tabs
tab_company, tab_general = st.tabs([
    "📄 Company Questions (PDF Grounded)",
    "💬 General Questions"
])

# Helper function to generate AI response
def generate_response(prompt: str, mode: str):
    if not client:
        return "⚠️ OpenAI API key is missing. Please add it in Streamlit Cloud Secrets (OPENAI_API_KEY) or in the sidebar.", []

    if mode == "company":
        # Grounded RAG Retrieval
        retrieval = knowledge_base.retrieve(prompt, top_k=3)
        context = retrieval["context"]
        sources = retrieval["sources"]

        system_instruction = (
            "You are NexaData AI, the official company intelligence assistant for NexaData.\n"
            "Your tagline is 'Ask. Analyze. Discover.'\n"
            "Answer the user's question clearly, professionally, and accurately using ONLY the official company documents provided below.\n"
            "If the documents do not contain the answer, politely state: 'Based on official NexaData documents, this information is not available.'\n\n"
            f"OFFICIAL DOCUMENTS CONTEXT:\n{context}"
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content, sources
    else:
        # General Open AI
        system_instruction = (
            "You are NexaData AI, a helpful, highly knowledgeable general-purpose AI assistant.\n"
            "Answer questions clearly, thoroughly, and accurately regarding Python, data science, machine learning, and general topics."
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content, []

# =========================================================================
# TAB 1: COMPANY QUESTIONS (PDF RAG)
# =========================================================================
with tab_company:
    st.caption("🛡️ Grounded in official NexaData company documents & policies.")

    # Quick prompt pills
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("📌 What is NexaData?", key="p1"):
        st.session_state.preset_company = "What is NexaData and what solutions do you offer?"
    if c2.button("🚀 Enterprise Solutions", key="p2"):
        st.session_state.preset_company = "What are your enterprise solutions and pricing plans?"
    if c3.button("🔒 Data Security", key="p3"):
        st.session_state.preset_company = "What are your data privacy and security policies?"
    if c4.button("⚡ How It Works", key="p4"):
        st.session_state.preset_company = "How does the AI query pipeline work?"

    # Render History
    for msg in st.session_state.company_messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else str(ICON_PATH)):
            st.markdown(msg["content"])
            if msg.get("sources"):
                s = msg["sources"][0]
                st.markdown(
                    f"""<div class="source-box">
                    📄 <b>Source:</b> Based on official NexaData documents (<code>{s.get('document', 'Knowledge Base')}</code> - Page {s.get('page', 1)})
                    </div>""",
                    unsafe_allow_html=True
                )

    # Input
    user_query = st.chat_input("Ask anything about NexaData's official documents...")
    if "preset_company" in st.session_state:
        user_query = st.session_state.pop("preset_company")

    if user_query:
        st.session_state.company_messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant", avatar=str(ICON_PATH)):
            with st.spinner("Searching NexaData documents..."):
                reply, sources = generate_response(user_query, mode="company")
                st.markdown(reply)
                if sources:
                    st.markdown(
                        f"""<div class="source-box">
                        📄 <b>Source:</b> Based on official NexaData documents (<code>{sources[0].get('document', 'Knowledge Base')}</code> - Page {sources[0].get('page', 1)})
                        </div>""",
                        unsafe_allow_html=True
                    )
        st.session_state.company_messages.append({
            "role": "assistant",
            "content": reply,
            "sources": sources
        })

# =========================================================================
# TAB 2: GENERAL QUESTIONS
# =========================================================================
with tab_general:
    st.caption("💬 General open AI assistant for programming, data science, and analysis.")

    # Render History
    for msg in st.session_state.general_messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else str(ICON_PATH)):
            st.markdown(msg["content"])
            if msg.get("is_general"):
                st.markdown(
                    """<div class="disclaimer-box">
                    ℹ️ <i>This is a general AI answer, not specific to NexaData's documents. For verified company information, please use Company Questions mode.</i>
                    </div>""",
                    unsafe_allow_html=True
                )

    user_gen = st.chat_input("Ask a general question...", key="gen_input")
    if user_gen:
        st.session_state.general_messages.append({"role": "user", "content": user_gen})
        with st.chat_message("user"):
            st.markdown(user_gen)

        with st.chat_message("assistant", avatar=str(ICON_PATH)):
            with st.spinner("NexaData AI is thinking..."):
                reply, _ = generate_response(user_gen, mode="general")
                st.markdown(reply)
                st.markdown(
                    """<div class="disclaimer-box">
                    ℹ️ <i>This is a general AI answer, not specific to NexaData's documents. For verified company information, please use Company Questions mode.</i>
                    </div>""",
                    unsafe_allow_html=True
                )
        st.session_state.general_messages.append({
            "role": "assistant",
            "content": reply,
            "is_general": True
        })
