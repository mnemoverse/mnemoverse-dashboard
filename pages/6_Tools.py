"""
Tools & Integrations
Links to external observability tools with setup instructions.
"""

import streamlit as st

st.set_page_config(page_title="Tools | Mnemoverse", page_icon="🔧", layout="wide")

st.title("Tools & Integrations")
st.caption("External observability and experiment tracking tools")
st.divider()

# === W&B ===
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("Weights & Biases")
    st.markdown("""
    **Primary experiment tracking.** Every `run_experiment.py` run logs here automatically.
    
    **What you get:**
    - Accuracy curves (baseline vs memory)
    - Latency metrics per task
    - Memory size growth
    - Run comparison & filtering
    - Artifacts (configs, results)
    
    **Project:** `arc-kdm-experiments`
    """)
with col2:
    st.link_button("Open W&B", "https://wandb.ai/mnemoverse/arc-kdm-experiments", use_container_width=True)
    st.caption("Login: mnemoverse org")

st.divider()

# === Phoenix ===
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("Phoenix (Arize)")
    st.markdown("""
    **LLM Tracing & Observability.** See every LLM call with latency, tokens, errors.
    
    **What you get:**
    - Trace waterfall (full request breakdown)
    - P50/P95 latency per endpoint
    - Token usage analytics
    - Error tracking & debugging
    
    **Project:** `cognitive-kdm` (needs activation)
    
    **Status:** Configured but not sending traces yet. Run experiment with `PHOENIX_ENABLED=true`.
    """)
with col2:
    st.link_button("Open Phoenix", "https://app.phoenix.arize.com", use_container_width=True)
    st.caption("Login: Arize account")

st.divider()

# === LangSmith ===
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("LangSmith")
    st.markdown("""
    **LangChain native tracing.** If using LangChain, traces go here automatically.
    
    **What you get:**
    - Chain execution traces
    - Prompt/completion pairs
    - Token costs
    - Playground for testing
    
    **Status:** Configured via `LANGSMITH_API_KEY` in `.env`
    """)
with col2:
    st.link_button("Open LangSmith", "https://smith.langchain.com", use_container_width=True)
    st.caption("Login: LangChain account")

st.divider()

# === Weave ===
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("Weave (W&B)")
    st.markdown("""
    **LLM-specific tracing in W&B.** Part of Weights & Biases.
    
    **What you get:**
    - LLM call traces
    - Integrated with W&B runs
    - Model versioning
    
    **Status:** Available via `weave.init()` in LLMClient
    """)
with col2:
    st.link_button("Open Weave", "https://wandb.ai/home", use_container_width=True)
    st.caption("Look for 'Weave' tab")

st.divider()

# === Neon PostgreSQL ===
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("Neon PostgreSQL")
    st.markdown("""
    **Primary database.** All experiment data stored here.
    
    **Schemas:**
    - `kdm_default` - main experiments
    - `kdm_exp_*` - isolated experiments
    
    **Tables:**
    - `state_atoms` - long-term memories
    - `process_atoms` - working memories  
    - `hebbian_edges` - associations
    - `adaline_state` - learning weights
    - `feedback_events` - user feedback
    - `experiment_runs` - run metadata
    """)
with col2:
    st.link_button("Open Neon Console", "https://console.neon.tech", use_container_width=True)
    st.caption("Project: neondb")

st.divider()

# === Quick Setup ===
st.subheader("Quick Setup")

with st.expander("Enable Phoenix Tracing"):
    st.code("""
# In .env:
PHOENIX_ENABLED=true
PHOENIX_API_KEY=<your-key>
PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com/v1/traces
PHOENIX_PROJECT_NAME=cognitive-kdm

# In code:
from cognitive_kdm.core.tracing import MemoryTracer
tracer = MemoryTracer(enabled=True, use_phoenix=True)
    """, language="bash")

with st.expander("Run Experiment with Full Tracing"):
    st.code("""
# PowerShell
$env:KDM_SCHEMA='kdm_exp_002'
$env:PHOENIX_ENABLED='true'
.\\.venv\\Scripts\\python.exe experiments/arc-agi/run_experiment.py --main --max-tasks 10

# Check results:
# - W&B: https://wandb.ai/mnemoverse/arc-kdm-experiments  
# - Phoenix: https://app.phoenix.arize.com
# - Dashboard: This tool (Overview, Learning Curve pages)
    """, language="powershell")

with st.expander("Create New Isolated Experiment"):
    st.code("""
# Create schema
.\\.venv\\Scripts\\python.exe experiments/arc-agi/db_schema_manager.py create kdm_exp_003

# Run with isolation
$env:KDM_SCHEMA='kdm_exp_003'
.\\.venv\\Scripts\\python.exe experiments/arc-agi/run_experiment.py --main

# View in Dashboard: select schema in sidebar
    """, language="powershell")

st.divider()

# === Architecture ===
st.subheader("Data Flow")
st.markdown("""
```
run_experiment.py
    │
    ├──► W&B (metrics, configs, artifacts)
    │
    ├──► Phoenix (LLM traces, latency)
    │
    ├──► PostgreSQL (atoms, edges, feedback)
    │
    └──► This Dashboard (aggregated view)
```
""")

st.caption("Mnemoverse Dashboard v0.2 • Gateway to all tools")
