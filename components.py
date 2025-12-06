"""
Shared UI Components for Mnemoverse Dashboard.

Components:
- render_sidebar: Schema selector with connection status
- page_header: Consistent page header with schema indicator
- info_tooltip: Help icon with documentation popup
"""

import streamlit as st

from db import get_available_schemas, get_engine, run_scalar

# ==============================================================================
# Session State Keys
# ==============================================================================

SESSION_SCHEMA = "current_schema"

# ==============================================================================
# Sidebar Component
# ==============================================================================


def render_sidebar() -> str | None:
    """
    Render sidebar with schema selector and connection status.
    
    Features:
    - Schema dropdown (persisted in session state)
    - Connection status indicator
    - Quick stats for selected schema
    - Refresh button to clear cache
    
    Returns:
        Selected schema name or None if not connected/selected.
    """
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
        st.sidebar.warning("No KDM schemas found")
        return None
    
    # Initialize session state
    if SESSION_SCHEMA not in st.session_state:
        st.session_state[SESSION_SCHEMA] = schemas[0]
    
    # Find current index (handle deleted schemas)
    current = st.session_state[SESSION_SCHEMA]
    current_idx = schemas.index(current) if current in schemas else 0
    
    selected = st.sidebar.selectbox(
        "Select schema:",
        schemas,
        index=current_idx,
        key="schema_selector",
        help="Choose experiment schema to analyze"
    )
    
    # Update session state
    st.session_state[SESSION_SCHEMA] = selected
    
    # Quick stats
    if selected:
        _render_sidebar_stats(selected)
    
    st.sidebar.divider()
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    return selected


def _render_sidebar_stats(schema: str) -> None:
    """Render quick stats in sidebar for selected schema."""
    atoms = run_scalar("SELECT COUNT(*) FROM {schema}.process_atoms", schema)
    feedback = run_scalar("SELECT COUNT(*) FROM {schema}.feedback_events", schema)
    
    if atoms is not None:
        st.sidebar.caption(f"📊 Atoms: {atoms} | Feedback: {feedback or 0}")


# ==============================================================================
# Page Header Component
# ==============================================================================


def page_header(title: str, schema: str | None = None) -> None:
    """
    Render consistent page header with schema indicator.
    
    Args:
        title: Page title (displayed as h1)
        schema: Schema name to display (optional)
    """
    st.title(title)
    
    if schema:
        st.caption(f"Schema: `{schema}`")
    
    st.divider()


# ==============================================================================
# Info Tooltip Component (for metric explanations)
# ==============================================================================


def info_tooltip(text: str) -> None:
    """
    Render info icon (ℹ️) with help popup.
    
    Use this next to metrics to explain what they mean
    and where the data comes from.
    
    Args:
        text: Markdown text to display in popup
        
    Example:
        >>> col1, col2 = st.columns([4, 1])
        >>> with col1:
        ...     st.metric("Accuracy", "42%")
        >>> with col2:
        ...     info_tooltip("**Accuracy** = correct / total tasks")
    """
    with st.popover("ℹ️"):
        st.markdown(text)
