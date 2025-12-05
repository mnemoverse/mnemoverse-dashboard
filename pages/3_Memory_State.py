"""
Memory State Page
Shows current state of memory system.

- Top concepts by Adaline utility
- Feedback distribution
- Adaline learning progress
- Recent insights quality
"""

import streamlit as st
import plotly.express as px
import sys
sys.path.insert(0, str(__file__).replace('pages/3_Memory_State.py', ''))

from db import run_query, run_scalar
from components import render_sidebar, page_header

st.set_page_config(page_title="Memory State | Mnemoverse", page_icon="🧠", layout="wide")

# Sidebar
schema = render_sidebar()

if not schema:
    st.warning("Select a schema to view data.")
    st.stop()

# Header
page_header("Memory State", schema)

# Adaline State
st.subheader("Adaline Learning")

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
    st.info("Adaline state not persisted yet. Run experiment with feedback to populate.")
else:
    col1, col2, col3 = st.columns(3)
    
    row = adaline.iloc[0]
    with col1:
        st.metric("Updates", int(row['update_count']) if row['update_count'] else 0)
    with col2:
        st.metric("Avg Error", f"{row['avg_error']:.4f}" if row['avg_error'] else "N/A")
    with col3:
        st.metric("Learning Rate", f"{row['learning_rate']:.4f}" if row['learning_rate'] else "N/A")
    
    if row['updated_at']:
        st.caption(f"Last updated: {row['updated_at']}")

st.divider()

# Feedback Distribution
st.subheader("Feedback Distribution")

feedback = run_query("""
    SELECT 
        feedback_type,
        COUNT(*) as count
    FROM {schema}.feedback_events
    GROUP BY feedback_type
""", schema)

if feedback.empty:
    st.info("No feedback events yet.")
else:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        for _, row in feedback.iterrows():
            st.metric(row['feedback_type'].capitalize(), row['count'])
    
    with col2:
        fig = px.pie(
            feedback,
            values='count',
            names='feedback_type',
            color='feedback_type',
            color_discrete_map={'positive': 'green', 'negative': 'red'}
        )
        fig.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# Top Concepts by Utility
st.subheader("Top Concepts by Adaline Utility")

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
    st.info("No state atoms with utility scores yet.")
else:
    st.dataframe(
        top_concepts,
        use_container_width=True,
        hide_index=True,
        column_config={
            "concept": "Concept",
            "adaline_utility": st.column_config.ProgressColumn(
                "Utility",
                format="%.3f",
                min_value=0,
                max_value=1,
            ),
            "use_count": "Uses",
            "positive_feedback_count": "Positive",
            "negative_feedback_count": "Negative"
        }
    )

st.divider()

# Recent Insights Quality
st.subheader("Recent Insights")

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
    st.info("No insights recorded yet.")
else:
    st.dataframe(
        insights,
        use_container_width=True,
        hide_index=True,
        column_config={
            "concept": "Concept",
            "insight_preview": "Insight",
            "is_successful": st.column_config.CheckboxColumn("Helped"),
            "feedback_score": st.column_config.NumberColumn(
                "Score",
                format="%.2f"
            ),
            "created_at": "Created"
        }
    )
