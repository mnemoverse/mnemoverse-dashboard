"""
Shared components: sidebar with schema selector, common layout.
"""

import streamlit as st
from db import get_engine, get_available_schemas, run_scalar


def render_sidebar():
    """Render sidebar with schema selector and connection status."""
    
    st.sidebar.title("Mnemoverse Dashboard")
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
    
    # Persist schema selection in session_state
    if "current_schema" not in st.session_state:
        st.session_state.current_schema = schemas[0]
    
    # Find current index
    current_idx = 0
    if st.session_state.current_schema in schemas:
        current_idx = schemas.index(st.session_state.current_schema)
    
    selected = st.sidebar.selectbox(
        "Select schema:",
        schemas,
        index=current_idx,
        key="schema_selector"
    )
    
    # Update session state when selection changes
    st.session_state.current_schema = selected
    
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
    st.title(title)
    st.caption(f"Schema: `{schema}`")
    st.divider()
