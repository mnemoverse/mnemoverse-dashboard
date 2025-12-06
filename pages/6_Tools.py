"""
Tools & Integrations Page - External Observability Links.

Quick access to all external tools used in the Mnemoverse ecosystem:
- Neon PostgreSQL: Database console
- Weights & Biases: Experiment tracking
- Phoenix (Arize): LLM tracing
- GitHub: Source code repository

Also provides quick command references for common operations.
"""

import streamlit as st

# ==============================================================================
# Page Configuration
# ==============================================================================

st.set_page_config(
    page_title="Tools | Mnemoverse",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 Tools & Integrations")
st.info(
    "🚀 **External Tools:** Quick links to databases, experiment tracking, "
    "and LLM tracing. Everything you need to monitor and debug."
)
st.divider()

# ==============================================================================
# Neon PostgreSQL
# ==============================================================================

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("🗄️ Neon PostgreSQL")
    st.markdown("""
    **Primary database** for all experiment data.
    
    | Feature | Description |
    |---------|-------------|
    | **Schemas** | `kdm_*` — Isolated experiment environments |
    | **Tables** | `state_atoms`, `process_atoms`, `hebbian_edges`, `experiment_runs` |
    | **Extension** | pgvector for embedding similarity search |
    """)

with col2:
    st.link_button(
        "🔗 Open Neon Console",
        "https://console.neon.tech",
        use_container_width=True
    )

st.divider()

# ==============================================================================
# Weights & Biases
# ==============================================================================

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📊 Weights & Biases")
    st.markdown("""
    **Experiment tracking** — metrics, artifacts, run comparison.
    
    | Feature | Description |
    |---------|-------------|
    | **Project** | `arc-kdm-experiments` |
    | **Metrics** | Accuracy curves, latency, memory usage |
    | **Artifacts** | Baseline results, model outputs |
    """)

with col2:
    st.link_button(
        "🔗 Open W&B Dashboard",
        "https://wandb.ai/mnemoverse/arc-kdm-experiments",
        use_container_width=True
    )

st.divider()

# ==============================================================================
# Phoenix (Arize)
# ==============================================================================

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("🔥 Phoenix (Arize)")
    st.markdown("""
    **LLM Tracing** — detailed traces of all LLM calls.
    
    | Feature | Description |
    |---------|-------------|
    | **Project** | `cognitive-kdm` |
    | **Metrics** | Latency, token usage, error rates |
    | **Traces** | Full request/response pairs |
    """)

with col2:
    st.link_button(
        "🔗 Open Phoenix",
        "https://app.phoenix.arize.com",
        use_container_width=True
    )

st.divider()

# ==============================================================================
# GitHub
# ==============================================================================

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("🐙 GitHub Repository")
    st.markdown("""
    **Source code** for cognitive-kdm and related projects.
    
    | Feature | Description |
    |---------|-------------|
    | **Main repo** | `cognitive-kdm` |
    | **Branches** | `main` (stable), `develop` (active) |
    | **CI/CD** | GitHub Actions for testing |
    """)

with col2:
    st.link_button(
        "🔗 Open GitHub",
        "https://github.com/mnemoverse/cognitive-kdm",
        use_container_width=True
    )

st.divider()

# ==============================================================================
# Quick Commands
# ==============================================================================

st.subheader("⚡ Quick Commands")
st.caption("Copy-paste commands for common operations")

with st.expander("🧪 Run Experiment", expanded=False):
    st.markdown("Run a memory experiment on ARC-AGI tasks:")
    st.code("""
cd cognitive-kdm
$env:KDM_SCHEMA='kdm_exp_001'
.\\.venv\\Scripts\\python.exe experiments/arc-agi/run_experiment.py \\
    --main --max-tasks 100 --passes 3 --attempts 5
    """, language="powershell")

with st.expander("📁 Create New Schema", expanded=False):
    st.markdown("Create an isolated schema for a new experiment:")
    st.code("""
.\\.venv\\Scripts\\python.exe experiments/arc-agi/db_schema_manager.py \\
    create kdm_exp_002
    """, language="powershell")

with st.expander("🔄 Reset Schema", expanded=False):
    st.markdown("⚠️ **Destructive** — Drops all tables in schema:")
    st.code("""
.\\.venv\\Scripts\\python.exe experiments/arc-agi/db_schema_manager.py \\
    drop kdm_exp_002 --confirm
    """, language="powershell")

with st.expander("📊 Run Dashboard Locally", expanded=False):
    st.markdown("Start the dashboard on localhost:")
    st.code("""
cd mnemoverse-dashboard
streamlit run streamlit_app.py --server.port 8501
    """, language="powershell")

st.divider()

# ==============================================================================
# Footer
# ==============================================================================

st.caption("**Mnemoverse Dashboard** v0.3")
st.caption("Part of the Cognitive KDM ecosystem")
