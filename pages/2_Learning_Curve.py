"""
Learning Curve Page - Main Experiment Analysis.

This is the KEY page for validating the memory hypothesis:
"Does accuracy improve as memory grows?"

Charts:
1. Accuracy vs Memory Size - Cumulative accuracy over tasks
2. Baseline vs Memory - Compare modes side-by-side
3. Task Timeline - Success distribution over time

Metrics:
- Tasks Solved: Total attempts with task_id
- Correct: Attempts where is_successful=true
- Accuracy: correct / total * 100%
- Memory Size: Number of process atoms stored

Data Sources:
- {schema}.process_atoms - Individual solution attempts
- {schema}.experiment_runs - Run metadata with mode (baseline/memory)
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components import info_tooltip, page_header, render_sidebar
from db import run_query, run_scalar
from metric_definitions import (
    METRIC_ACCURACY,
    METRIC_BASELINE,
    METRIC_CORRECT,
    METRIC_DELTA,
    METRIC_MEMORY_MODE,
    METRIC_MEMORY_SIZE,
    METRIC_TASKS_SOLVED,
)

# ==============================================================================
# Page Configuration
# ==============================================================================

st.set_page_config(
    page_title="Learning Curve | Mnemoverse",
    page_icon="📈",
    layout="wide"
)

# ==============================================================================
# Sidebar & Header
# ==============================================================================

schema = render_sidebar()

if not schema:
    st.warning("Select a schema to view data.")
    st.stop()

page_header("📈 Learning Curve", schema)

# ==============================================================================
# Key Metrics Row
# ==============================================================================

# Header with info
header_col, info_col = st.columns([10, 1])
with header_col:
    st.subheader("📊 Experiment Metrics")
with info_col:
    with st.popover("ℹ️"):
        st.markdown("""
        **Key Experiment Metrics**
        
        These metrics track progress of the current experiment:
        - Tasks Solved: Total attempts
        - Correct: Successful solutions
        - Accuracy: Success rate (%)
        - Memory Size: Knowledge accumulated
        """)

col1, col2, col3, col4 = st.columns(4)

# Query metrics
tasks_total = run_scalar("""
    SELECT COUNT(*) FROM {schema}.process_atoms WHERE task_id IS NOT NULL
""", schema) or 0

tasks_correct = run_scalar("""
    SELECT COUNT(*) FROM {schema}.process_atoms 
    WHERE task_id IS NOT NULL AND is_successful = true
""", schema) or 0

memory_size = run_scalar(
    "SELECT COUNT(*) FROM {schema}.process_atoms", schema
) or 0

accuracy = (tasks_correct / tasks_total * 100) if tasks_total > 0 else 0

with col1:
    m_col, i_col = st.columns([4, 1])
    with m_col:
        st.metric("Tasks Solved", tasks_total)
    with i_col:
        info_tooltip(METRIC_TASKS_SOLVED)

with col2:
    m_col, i_col = st.columns([4, 1])
    with m_col:
        st.metric("Correct", tasks_correct)
    with i_col:
        info_tooltip(METRIC_CORRECT)

with col3:
    m_col, i_col = st.columns([4, 1])
    with m_col:
        st.metric("Accuracy", f"{accuracy:.1f}%")
    with i_col:
        info_tooltip(METRIC_ACCURACY)

with col4:
    m_col, i_col = st.columns([4, 1])
    with m_col:
        st.metric("Memory Size", memory_size)
    with i_col:
        info_tooltip(METRIC_MEMORY_SIZE)

st.divider()

# ==============================================================================
# Learning Curve Chart - The Key Hypothesis Visualization
# ==============================================================================

st.subheader("📊 Accuracy vs Memory Size")
st.caption("**Key Hypothesis**: Accuracy should increase as memory grows")

learning_data = run_query("""
    WITH ordered_tasks AS (
        SELECT 
            task_id,
            is_successful,
            created_at,
            ROW_NUMBER() OVER (ORDER BY created_at) as task_num
        FROM {schema}.process_atoms
        WHERE task_id IS NOT NULL
        ORDER BY created_at
    ),
    cumulative AS (
        SELECT 
            task_num,
            task_num as memory_size,
            SUM(CASE WHEN is_successful THEN 1 ELSE 0 END) 
                OVER (ORDER BY task_num) as correct_so_far,
            (SUM(CASE WHEN is_successful THEN 1 ELSE 0 END) 
                OVER (ORDER BY task_num))::float / task_num * 100 as accuracy
        FROM ordered_tasks
    )
    SELECT task_num, memory_size, accuracy
    FROM cumulative
    ORDER BY task_num
""", schema)

if learning_data.empty:
    st.info("📭 No task data yet. Run an experiment to see the learning curve.")
else:
    fig = px.line(
        learning_data,
        x='memory_size',
        y='accuracy',
        labels={
            'memory_size': 'Tasks Completed',
            'accuracy': 'Cumulative Accuracy (%)'
        }
    )
    
    fig.update_traces(
        line=dict(width=2, color='#1f77b4'),
        hovertemplate='<b>Task %{x}</b><br>Accuracy: %{y:.1f}%<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Memory Size (tasks completed)",
        yaxis_title="Accuracy (%)",
        yaxis_range=[0, 100],
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==============================================================================
# Baseline vs Memory Comparison
# ==============================================================================

st.subheader("⚖️ Baseline vs Memory Comparison")

runs = run_query("""
    SELECT 
        run_name,
        mode,
        tasks_total,
        tasks_correct,
        accuracy,
        started_at
    FROM {schema}.experiment_runs
    ORDER BY started_at DESC
    LIMIT 20
""", schema)

if runs.empty:
    st.info("📭 No experiment runs recorded yet.")
else:
    # Split by mode
    baseline_runs = runs[runs['mode'] == 'baseline']
    memory_runs = runs[runs['mode'] == 'memory']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not baseline_runs.empty:
            baseline_acc = baseline_runs['accuracy'].mean()
            st.metric(
                "📝 Baseline (avg)",
                f"{baseline_acc:.1%}" if pd.notna(baseline_acc) else "N/A",
                help="Average accuracy without memory assistance"
            )
        else:
            st.metric("📝 Baseline", "No runs")
    
    with col2:
        if not memory_runs.empty:
            memory_acc = memory_runs['accuracy'].mean()
            st.metric(
                "🧠 Memory (avg)",
                f"{memory_acc:.1%}" if pd.notna(memory_acc) else "N/A",
                help="Average accuracy with memory assistance"
            )
        else:
            st.metric("🧠 Memory", "No runs")
    
    with col3:
        if not baseline_runs.empty and not memory_runs.empty:
            baseline_acc = baseline_runs['accuracy'].mean()
            memory_acc = memory_runs['accuracy'].mean()
            if pd.notna(baseline_acc) and pd.notna(memory_acc):
                delta = memory_acc - baseline_acc
                delta_pct = delta * 100
                st.metric(
                    "📊 Delta",
                    f"{delta:+.1%}",
                    delta=f"{delta_pct:+.1f}pp",
                    help="Memory improvement over baseline"
                )
            else:
                st.metric("📊 Delta", "N/A")
        else:
            st.metric("📊 Delta", "Need both modes")
    
    st.divider()
    
    # Runs table
    st.caption("Recent Experiment Runs")
    st.dataframe(
        runs,
        use_container_width=True,
        hide_index=True,
        column_config={
            "run_name": st.column_config.TextColumn("Run Name"),
            "mode": st.column_config.TextColumn(
                "Mode",
                help="baseline=no memory, memory=with KDMemory"
            ),
            "tasks_total": st.column_config.NumberColumn("Total"),
            "tasks_correct": st.column_config.NumberColumn("Correct"),
            "accuracy": st.column_config.ProgressColumn(
                "Accuracy",
                format="%.1f%%",
                min_value=0,
                max_value=1,
            ),
            "started_at": st.column_config.DatetimeColumn("Started")
        }
    )

st.divider()

# ==============================================================================
# Task Success Timeline
# ==============================================================================

st.subheader("📅 Task Success Timeline")

timeline = run_query("""
    SELECT 
        DATE(created_at) as date,
        COUNT(*) as total,
        SUM(CASE WHEN is_successful THEN 1 ELSE 0 END) as correct
    FROM {schema}.process_atoms
    WHERE task_id IS NOT NULL
    GROUP BY DATE(created_at)
    ORDER BY date
""", schema)

if timeline.empty:
    st.info("📭 No timeline data available.")
else:
    timeline['accuracy'] = timeline['correct'] / timeline['total'] * 100
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=timeline['date'],
        y=timeline['total'],
        name='Total Tasks',
        marker_color='lightgray',
        hovertemplate='<b>%{x}</b><br>Total: %{y}<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=timeline['date'],
        y=timeline['correct'],
        name='Correct',
        marker_color='#2ecc71',
        hovertemplate='<b>%{x}</b><br>Correct: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        barmode='overlay',
        height=300,
        xaxis_title="Date",
        yaxis_title="Tasks",
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
