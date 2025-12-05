"""
Overview Page
Quick stats and last experiment summary.
"""

import streamlit as st
import sys
sys.path.insert(0, str(__file__).replace('pages/1_Overview.py', ''))

from db import run_query, run_scalar
from components import render_sidebar

st.set_page_config(page_title="Overview | Mnemoverse", page_icon="📊", layout="wide")

# Header first
st.title("Overview")

# Sidebar
schema = render_sidebar()

if not schema:
    st.warning("Select a schema to view data.")
    st.stop()

# Schema info under title
st.caption(f"Schema: `{schema}`")
st.divider()

# Key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    count = run_scalar("SELECT COUNT(*) FROM {schema}.state_atoms", schema)
    st.metric("State Atoms", count if count else 0)

with col2:
    count = run_scalar("SELECT COUNT(*) FROM {schema}.process_atoms", schema)
    st.metric("Process Atoms", count if count else 0)

with col3:
    count = run_scalar("SELECT COUNT(*) FROM {schema}.hebbian_edges", schema)
    st.metric("Hebbian Edges", count if count else 0)

with col4:
    count = run_scalar("SELECT COUNT(*) FROM {schema}.feedback_events", schema)
    st.metric("Feedback Events", count if count else 0)

st.divider()

# Last experiment run
st.subheader("Last Experiment Run")

last_run = run_query("""
    SELECT 
        run_name,
        model,
        mode,
        tasks_total,
        tasks_correct,
        accuracy,
        started_at,
        completed_at
    FROM {schema}.experiment_runs
    ORDER BY started_at DESC
    LIMIT 1
""", schema)

if last_run.empty:
    st.info("No experiment runs found in this schema.")
else:
    row = last_run.iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Run", row['run_name'] or "N/A")
    with col2:
        st.metric("Mode", row['mode'] or "N/A")
    with col3:
        tasks = f"{row['tasks_correct'] or 0} / {row['tasks_total'] or 0}"
        st.metric("Tasks", tasks)
    with col4:
        acc = row['accuracy']
        st.metric("Accuracy", f"{acc:.1%}" if acc else "N/A")
    
    if row['started_at']:
        st.caption(f"Started: {row['started_at']}")

st.divider()

# Recent activity
st.subheader("Recent Process Atoms")

recent = run_query("""
    SELECT 
        concept,
        LEFT(query, 80) as query_preview,
        is_successful,
        created_at
    FROM {schema}.process_atoms
    ORDER BY created_at DESC
    LIMIT 10
""", schema)

if recent.empty:
    st.info("No process atoms yet. Run an experiment to populate.")
else:
    st.dataframe(
        recent,
        use_container_width=True,
        hide_index=True,
        column_config={
            "concept": "Concept",
            "query_preview": "Query",
            "is_successful": st.column_config.CheckboxColumn("Success"),
            "created_at": "Created"
        }
    )
