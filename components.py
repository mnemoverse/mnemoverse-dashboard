"""
Shared components: sidebar with schema selector, common layout.
"""

import streamlit as st
from db import get_engine, get_available_schemas, run_scalar


def render_sidebar():
    """Render sidebar with schema selector and connection status."""
    
    st.sidebar.title("Mnemoverse")
    st.sidebar.caption("Dashboard v0.2")
    st.sidebar.divider()
    
    # Connection status
    engine = get_engine()
    if engine:
        st.sidebar.success("Connected ✓")
    else:
        st.sidebar.error("Not connected ✗")
        st.sidebar.info("Set DATABASE_URL in secrets or env")
        return None
    
    # Schema selector
    st.sidebar.subheader("Schema")
    schemas = get_available_schemas()
    
    if not schemas:
        st.sidebar.warning("No kdm schemas found")
        return None
    
    selected = st.sidebar.selectbox(
        "Select schema:",
        schemas,
        index=0,
        key="selected_schema"
    )
    
    # Quick stats for selected schema
    if selected:
        atoms = run_scalar("SELECT COUNT(*) FROM {schema}.process_atoms", selected)
        feedback = run_scalar("SELECT COUNT(*) FROM {schema}.feedback_events", selected)
        
        if atoms is not None:
            st.sidebar.caption(f"Atoms: {atoms} | Feedback: {feedback or 0}")
    
    st.sidebar.divider()
    
    # Refresh button
    if st.sidebar.button("Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    return selected


def page_header(title: str, schema: str):
    """Render page header with title and schema indicator."""
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(title)
    with col2:
        st.caption(f"Schema: `{schema}`")
    st.divider()
