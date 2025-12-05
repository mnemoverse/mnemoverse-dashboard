"""
Mnemoverse Dashboard v0.2
=========================
Clean, professional dashboard for KDMemory experiments.

Focus: ARC-AGI experiment metrics from EXPERIMENT.md
Data: Neon PostgreSQL (kdm schema and experiment schemas)

Deploy: Streamlit Cloud
"""

import streamlit as st

st.set_page_config(page_title="Mnemoverse Dashboard", page_icon="📊", layout="wide")

# Redirect to first page immediately
st.switch_page("pages/1_Overview.py")
