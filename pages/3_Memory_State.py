"""
Memory State Page - Adaline Learning & Concept Analysis.

This page shows the internal state of the memory system:
- Adaline perceptron learning state (weights, error, learning rate)
- Feedback distribution (positive vs negative signals)
- Concept utilities (which concepts are most valuable)
- Recent insights quality

Key Concepts:
- Adaline: Adaptive Linear Neuron for utility prediction
- Utility: How useful a concept is for solving tasks (0-1)
- Feedback: Learning signals from task success/failure

Data Sources:
- {schema}.adaline_state - Perceptron state snapshots
- {schema}.feedback_events - Learning signals
- {schema}.state_atoms - Concept utilities and usage
- {schema}.process_atoms - Solution attempts with feedback
"""

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components import page_header, render_sidebar
from db import run_query, run_scalar
from metric_definitions import (
    HELP_ADALINE_UPDATES,
    HELP_AVG_ERROR,
    HELP_LEARNING_RATE,
)

# ==============================================================================
# Page Configuration
# ==============================================================================

st.set_page_config(
    page_title="Memory State | Mnemoverse",
    page_icon="🧠",
    layout="wide"
)

# ==============================================================================
# Sidebar & Header
# ==============================================================================

schema = render_sidebar()

if not schema:
    st.warning("Select a schema to view data.")
    st.stop()

page_header("🧠 Memory State", schema)

# Page intro
st.info(
    "🧠 **Inside the Memory:** See how the system learns which concepts are useful. "
    "Adaline is a neural network that predicts concept value based on feedback."
)

# ==============================================================================
# Adaline Learning State
# ==============================================================================

st.subheader("🎓 Adaline Learning")
st.caption(
    "Adaptive Linear Neuron — learns from feedback to predict which concepts will help solve tasks."
)

adaline = run_query("""
    SELECT 
        name,
        update_count,
        avg_error,
        learning_rate,
        updated_at
    FROM {schema}.adaline_state
    ORDER BY updated_at DESC
    LIMIT 5
""", schema)

if adaline.empty:
    st.info(
        "📭 Adaline state not persisted yet. "
        "Run an experiment with feedback to populate."
    )
else:
    row = adaline.iloc[0]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        updates = int(row['update_count']) if row['update_count'] else 0
        st.metric("Updates", updates, help=HELP_ADALINE_UPDATES)
    
    with col2:
        avg_error = row['avg_error']
        st.metric("Avg Error", f"{avg_error:.4f}" if avg_error else "N/A", help=HELP_AVG_ERROR)
    
    with col3:
        lr = row['learning_rate']
        st.metric("Learning Rate", f"{lr:.4f}" if lr else "N/A", help=HELP_LEARNING_RATE)
    
    if row['updated_at']:
        st.caption(f"⏱️ Last updated: {row['updated_at']}")

st.divider()

# ==============================================================================
# Feedback Distribution
# ==============================================================================

st.subheader("📊 Feedback Distribution")

feedback = run_query("""
    SELECT 
        feedback_type,
        COUNT(*) as count
    FROM {schema}.feedback_events
    GROUP BY feedback_type
""", schema)

if feedback.empty:
    st.info("📭 No feedback events yet. Complete tasks to generate feedback.")
else:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        for _, row in feedback.iterrows():
            fb_type = row['feedback_type']
            count = row['count']
            emoji = "✅" if fb_type == 'positive' else "❌"
            st.metric(
                f"{emoji} {fb_type.capitalize()}",
                count,
                help=f"Number of {fb_type} feedback events"
            )
    
    with col2:
        fig = px.pie(
            feedback,
            values='count',
            names='feedback_type',
            color='feedback_type',
            color_discrete_map={
                'positive': '#2ecc71',
                'negative': '#e74c3c'
            }
        )
        fig.update_layout(
            height=250,
            margin=dict(t=0, b=0, l=0, r=0),
            showlegend=True
        )
        fig.update_traces(
            hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>'
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==============================================================================
# Top Concepts by Adaline Utility
# ==============================================================================

st.subheader("🏆 Top Concepts by Utility")
st.caption("Concepts ranked by their predicted usefulness for solving tasks")

top_concepts = run_query("""
    SELECT 
        concept,
        adaline_utility,
        use_count,
        positive_feedback_count,
        negative_feedback_count
    FROM {schema}.state_atoms
    WHERE adaline_utility IS NOT NULL
    ORDER BY adaline_utility DESC
    LIMIT 15
""", schema)

if top_concepts.empty:
    st.info("📭 No state atoms with utility scores yet.")
else:
    st.dataframe(
        top_concepts,
        use_container_width=True,
        hide_index=True,
        column_config={
            "concept": st.column_config.TextColumn(
                "Concept",
                help="Pattern or task identifier"
            ),
            "adaline_utility": st.column_config.ProgressColumn(
                "Utility",
                format="%.3f",
                min_value=0,
                max_value=1,
                help="Predicted usefulness (0-1, higher is better)"
            ),
            "use_count": st.column_config.NumberColumn(
                "Uses",
                help="Times this concept was retrieved"
            ),
            "positive_feedback_count": st.column_config.NumberColumn(
                "✅ Positive",
                help="Positive feedback count"
            ),
            "negative_feedback_count": st.column_config.NumberColumn(
                "❌ Negative",
                help="Negative feedback count"
            )
        }
    )

st.divider()

# ==============================================================================
# Recent Insights
# ==============================================================================

st.subheader("💡 Recent Insights")
st.caption("Latest solution attempts and their quality")

insights = run_query("""
    SELECT 
        concept,
        LEFT(response, 100) as insight_preview,
        is_successful,
        feedback_score,
        created_at
    FROM {schema}.process_atoms
    WHERE response IS NOT NULL
    ORDER BY created_at DESC
    LIMIT 15
""", schema)

if insights.empty:
    st.info("📭 No insights recorded yet.")
else:
    st.dataframe(
        insights,
        use_container_width=True,
        hide_index=True,
        column_config={
            "concept": st.column_config.TextColumn(
                "Concept",
                help="Task or pattern identifier"
            ),
            "insight_preview": st.column_config.TextColumn(
                "Insight",
                help="Solution attempt (truncated)"
            ),
            "is_successful": st.column_config.CheckboxColumn(
                "Helped",
                help="Did this insight help solve the task?"
            ),
            "feedback_score": st.column_config.NumberColumn(
                "Score",
                format="%.2f",
                help="Quality score from feedback (-1 to 1)"
            ),
            "created_at": st.column_config.DatetimeColumn(
                "Created",
                help="When this insight was generated"
            )
        }
    )
