"""
Learning Curve Page
MAIN page for experiment analysis.

Shows:
- Accuracy vs Memory Size (the key hypothesis chart)
- Baseline vs Memory comparison
- Task completion timeline
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
sys.path.insert(0, str(__file__).replace('pages/2_Learning_Curve.py', ''))

from db import run_query, run_scalar
from components import render_sidebar

st.set_page_config(page_title="Learning Curve | Mnemoverse", page_icon="📈", layout="wide")

# Header first
st.title("Learning Curve")

# Sidebar
schema = render_sidebar()

if not schema:
    st.warning("Select a schema to view data.")
    st.stop()

st.caption(f"Schema: `{schema}`")
st.divider()

# Key experiment metrics
col1, col2, col3, col4 = st.columns(4)

# Total tasks solved
tasks_total = run_scalar("""
    SELECT COUNT(*) FROM {schema}.process_atoms WHERE task_id IS NOT NULL
""", schema)

# Tasks correct (is_successful = true)
tasks_correct = run_scalar("""
    SELECT COUNT(*) FROM {schema}.process_atoms 
    WHERE task_id IS NOT NULL AND is_successful = true
""", schema)

# Memory size (process atoms)
memory_size = run_scalar("SELECT COUNT(*) FROM {schema}.process_atoms", schema)

# Calculate accuracy
accuracy = (tasks_correct / tasks_total * 100) if tasks_total and tasks_total > 0 else 0

with col1:
    st.metric("Tasks Solved", tasks_total or 0)

with col2:
    st.metric("Correct", tasks_correct or 0)

with col3:
    st.metric("Accuracy", f"{accuracy:.1f}%")

with col4:
    st.metric("Memory Size", memory_size or 0)

st.divider()

# Learning Curve Chart - Accuracy vs Memory Size
st.subheader("Accuracy vs Memory Size")

# Get cumulative accuracy over time
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
            SUM(CASE WHEN is_successful THEN 1 ELSE 0 END) OVER (ORDER BY task_num) as correct_so_far,
            (SUM(CASE WHEN is_successful THEN 1 ELSE 0 END) OVER (ORDER BY task_num))::float / task_num * 100 as accuracy
        FROM ordered_tasks
    )
    SELECT task_num, memory_size, accuracy
    FROM cumulative
    ORDER BY task_num
""", schema)

if learning_data.empty:
    st.info("No task data yet. Run an experiment to see the learning curve.")
else:
    fig = px.line(
        learning_data,
        x='memory_size',
        y='accuracy',
        title='Cumulative Accuracy Over Tasks',
        labels={'memory_size': 'Tasks Completed', 'accuracy': 'Accuracy (%)'}
    )
    fig.update_traces(line=dict(width=2))
    fig.update_layout(
        height=400,
        xaxis_title="Memory Size (tasks completed)",
        yaxis_title="Accuracy (%)",
        yaxis_range=[0, 100]
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Experiment runs comparison
st.subheader("Experiment Runs Comparison")

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
    st.info("No experiment runs recorded yet.")
else:
    # Baseline vs Memory comparison
    baseline_runs = runs[runs['mode'] == 'baseline']
    memory_runs = runs[runs['mode'] == 'memory']
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not baseline_runs.empty:
            baseline_acc = baseline_runs['accuracy'].mean()
            st.metric("Baseline Accuracy (avg)", f"{baseline_acc:.1%}" if baseline_acc else "N/A")
        else:
            st.metric("Baseline Accuracy", "No baseline runs")
    
    with col2:
        if not memory_runs.empty:
            memory_acc = memory_runs['accuracy'].mean()
            st.metric("Memory Accuracy (avg)", f"{memory_acc:.1%}" if memory_acc else "N/A")
            
            # Delta
            if not baseline_runs.empty and baseline_acc:
                delta = memory_acc - baseline_acc
                st.caption(f"Delta: {delta:+.1%}")
        else:
            st.metric("Memory Accuracy", "No memory runs")
    
    st.divider()
    
    # Runs table
    st.dataframe(
        runs,
        use_container_width=True,
        hide_index=True,
        column_config={
            "run_name": "Run",
            "mode": "Mode",
            "tasks_total": "Total",
            "tasks_correct": "Correct",
            "accuracy": st.column_config.ProgressColumn(
                "Accuracy",
                format="%.1f%%",
                min_value=0,
                max_value=1,
            ),
            "started_at": "Started"
        }
    )

st.divider()

# Task success timeline
st.subheader("Task Success Timeline")

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
    st.info("No timeline data available.")
else:
    timeline['accuracy'] = timeline['correct'] / timeline['total'] * 100
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=timeline['date'],
        y=timeline['total'],
        name='Total Tasks',
        marker_color='lightgray'
    ))
    fig.add_trace(go.Bar(
        x=timeline['date'],
        y=timeline['correct'],
        name='Correct',
        marker_color='green'
    ))
    fig.update_layout(
        barmode='overlay',
        height=300,
        xaxis_title="Date",
        yaxis_title="Tasks"
    )
    st.plotly_chart(fig, use_container_width=True)
