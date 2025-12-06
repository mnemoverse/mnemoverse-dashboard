"""
Mnemoverse Dashboard v0.3
=========================
Analytics dashboard for KDMemory (Knowledge Delta Memory) experiments.

Purpose:
    Visualize and analyze ARC-AGI experiment results with cognitive memory.
    Track learning curves, memory state, and knowledge graph evolution.

Data Source:
    Neon PostgreSQL with pgvector
    Schemas: kdm_* (isolated experiment environments)

Pages:
    1. Overview - Quick stats and last experiment summary
    2. Learning Curve - Accuracy vs memory size (key hypothesis)
    3. Memory State - Adaline learning, concept utilities
    4. Knowledge Graph - Hebbian network visualization
    5. Admin - Schema management, diagnostics
    6. Tools - External integrations (W&B, Phoenix, Neon)

Deploy:
    Streamlit Cloud: https://share.streamlit.io
    Local: streamlit run streamlit_app.py
"""

import streamlit as st

# Configure app - this sets the browser tab title and sidebar name
st.set_page_config(
    page_title="Mnemoverse Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main page just redirects to Home
# The "streamlit app" in sidebar will show as page_title from set_page_config
st.switch_page("pages/0_🏠_Home.py")
