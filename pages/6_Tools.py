"""
Tools & Integrations
Links to external observability tools.
"""

import streamlit as st

st.set_page_config(page_title="Tools | Mnemoverse", page_icon="🔧", layout="wide")

st.title("Tools & Integrations")
st.divider()

# === Neon PostgreSQL ===
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("🗄️ Neon PostgreSQL")
    st.markdown("""
    **Primary database** — все данные экспериментов.
    
    **Schemas:** `kdm_*` — изолированные эксперименты  
    **Tables:** `state_atoms`, `process_atoms`, `hebbian_edges`, `experiment_runs`
    """)
with col2:
    st.link_button("Open Neon", "https://console.neon.tech", use_container_width=True)

st.divider()

# === W&B ===
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("📊 Weights & Biases")
    st.markdown("""
    **Experiment tracking** — метрики, артефакты, сравнение runs.
    
    **Project:** `arc-kdm-experiments`  
    **Features:** accuracy curves, latency, run comparison
    """)
with col2:
    st.link_button("Open W&B", "https://wandb.ai/mnemoverse/arc-kdm-experiments", use_container_width=True)

st.divider()

# === Phoenix ===
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("🔥 Phoenix (Arize)")
    st.markdown("""
    **LLM Tracing** — трейсы всех LLM вызовов.
    
    **Project:** `cognitive-kdm`  
    **Features:** latency, tokens, error tracking
    """)
with col2:
    st.link_button("Open Phoenix", "https://app.phoenix.arize.com", use_container_width=True)

st.divider()

# === GitHub ===
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("🐙 GitHub")
    st.markdown("""
    **Source code** — cognitive-kdm repository.
    
    **Branches:** `main`, `develop`  
    **CI:** GitHub Actions
    """)
with col2:
    st.link_button("Open GitHub", "https://github.com/mnemoverse/cognitive-kdm", use_container_width=True)

st.divider()

# === Quick Commands ===
st.subheader("⚡ Quick Commands")

with st.expander("Run Experiment"):
    st.code("""
cd cognitive-kdm
$env:KDM_SCHEMA='kdm_exp_001'
.\\.venv\\Scripts\\python.exe experiments/arc-agi/run_experiment.py --main --max-tasks 10
    """, language="powershell")

with st.expander("Create New Schema"):
    st.code("""
.\\.venv\\Scripts\\python.exe experiments/arc-agi/db_schema_manager.py create kdm_exp_002
    """, language="powershell")

st.divider()
st.caption("Mnemoverse Dashboard v0.2")
