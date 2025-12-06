"""
Overview Page - Quick Stats & Last Experiment Summary.

Metrics displayed:
- State Atoms: Persistent concepts learned from successful solutions
- Process Atoms: Individual solution attempts (successful and failed)
- Hebbian Edges: Co-activation links between concepts
- Feedback Events: Positive/negative learning signals

Data Sources:
- {schema}.state_atoms - Concept storage
- {schema}.process_atoms - Solution attempts
- {schema}.hebbian_edges - Knowledge graph
- {schema}.experiment_runs - Experiment metadata
"""

import sys
from pathlib import Path

import streamlit as st

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from components import page_header, render_sidebar
from db import run_query, run_scalar
from metric_definitions import (
    HELP_FEEDBACK_EVENTS,
    HELP_HEBBIAN_EDGES,
    HELP_PROCESS_ATOMS,
    HELP_STATE_ATOMS,
)

# ==============================================================================
# Page Configuration
# ==============================================================================

st.set_page_config(
    page_title="Overview | Mnemoverse",
    page_icon="📊",
    layout="wide"
)

# ==============================================================================
# Sidebar & Header
# ==============================================================================

schema = render_sidebar()

if not schema:
    st.warning("Select a schema to view data.")
    st.stop()

page_header("📊 Overview", schema)

# Welcome message
st.info(
    "👋 **Welcome!** This page shows a snapshot of the current experiment. "
    "Use the metrics below to quickly assess memory size and learning progress."
)

# ==============================================================================
# Key Metrics Row
# ==============================================================================

st.subheader("📈 Key Metrics")
st.caption(
    "Core memory components. Hover over `?` for explanations."
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    count = run_scalar("SELECT COUNT(*) FROM {schema}.state_atoms", schema)
    st.metric("State Atoms", count or 0, help=HELP_STATE_ATOMS)

with col2:
    count = run_scalar("SELECT COUNT(*) FROM {schema}.process_atoms", schema)
    st.metric("Process Atoms", count or 0, help=HELP_PROCESS_ATOMS)

with col3:
    count = run_scalar("SELECT COUNT(*) FROM {schema}.hebbian_edges", schema)
    st.metric("Hebbian Edges", count or 0, help=HELP_HEBBIAN_EDGES)

with col4:
    count = run_scalar("SELECT COUNT(*) FROM {schema}.feedback_events", schema)
    st.metric("Feedback Events", count or 0, help=HELP_FEEDBACK_EVENTS)

st.divider()

# ==============================================================================
# Last Experiment Run
# ==============================================================================

st.subheader("🧪 Last Experiment Run")
st.caption(
    "Most recent experiment. Compare baseline vs memory mode on the Learning Curve page."
)

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
    st.info("No experiment runs found. Run an experiment to see results here.")
else:
    row = last_run.iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Run Name", row['run_name'] or "N/A")
    
    with col2:
        mode = row['mode'] or "N/A"
        mode_emoji = "🧠" if mode == "memory" else "📝"
        st.metric("Mode", f"{mode_emoji} {mode}")
    
    with col3:
        correct = row['tasks_correct'] or 0
        total = row['tasks_total'] or 0
        st.metric("Tasks", f"{correct} / {total}")
    
    with col4:
        acc = row['accuracy']
        st.metric(
            "Accuracy",
            f"{acc:.1%}" if acc else "N/A",
            help="Percentage of tasks solved correctly"
        )
    
    # Timestamps
    if row['started_at']:
        started = row['started_at']
        completed = row['completed_at']
        if completed:
            duration = completed - started
            st.caption(f"⏱️ Started: {started} | Duration: {duration}")
        else:
            st.caption(f"⏱️ Started: {started} | Status: Running...")

st.divider()

# ==============================================================================
# Recent Process Atoms
# ==============================================================================

st.subheader("📝 Recent Process Atoms")

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
    st.info("No process atoms yet. Run an experiment to populate memory.")
else:
    st.dataframe(
        recent,
        use_container_width=True,
        hide_index=True,
        column_config={
            "concept": st.column_config.TextColumn(
                "Concept",
                help="Task or pattern identifier"
            ),
            "query_preview": st.column_config.TextColumn(
                "Query",
                help="Solution attempt (truncated)"
            ),
            "is_successful": st.column_config.CheckboxColumn(
                "Success",
                help="Did this attempt solve the task?"
            ),
            "created_at": st.column_config.DatetimeColumn(
                "Created",
                help="When this attempt was recorded"
            )
        }
    )
