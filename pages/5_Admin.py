"""
Admin Page - Schema Management & Diagnostics.

Features:
- Database connection status and configuration
- Available schemas with table statistics
- Schema comparison (side-by-side row counts)
- Cache management

Use Cases:
- Verify database connectivity
- Inspect schema contents before analysis
- Compare experiment data across schemas
- Clear cached data for fresh queries
"""

import sys
from pathlib import Path

import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components import render_sidebar
from db import (
    check_table_exists,
    get_available_schemas,
    get_db_url,
    get_engine,
    run_scalar,
)

# ==============================================================================
# Page Configuration
# ==============================================================================

st.set_page_config(
    page_title="Admin | Mnemoverse",
    page_icon="⚙️",
    layout="wide"
)

# ==============================================================================
# Sidebar & Header
# ==============================================================================

schema = render_sidebar()

st.title("⚙️ Admin")
st.info(
    "🛠️ **System Management:** Check database health, inspect schemas, "
    "and manage cached data. For developers and debugging."
)
st.divider()

# ==============================================================================
# Connection Info
# ==============================================================================

st.subheader("🔌 Connection Status")
st.caption("Database connectivity and configuration details.")

db_url = get_db_url()
engine = get_engine()

if db_url and engine:
    # Mask credentials for display
    if '@' in db_url:
        masked = db_url.split('@')[1]
        st.success(f"✅ Connected to: `...@{masked}`")
    else:
        st.success("✅ Connected to database")
else:
    st.error("❌ Database not connected")
    st.code("""
# Add to .streamlit/secrets.toml:
DATABASE_URL = "postgresql://user:pass@host/db?sslmode=require"
    """, language="toml")
    st.info("💡 You can also set DATABASE_URL as an environment variable")

st.divider()

# ==============================================================================
# Available Schemas
# ==============================================================================

st.subheader("📁 Available Schemas")

schemas = get_available_schemas()

if not schemas:
    st.warning("No KDM schemas found in database.")
    st.info("Create a schema with: `db_schema_manager.py create kdm_exp_001`")
else:
    st.caption(f"Found **{len(schemas)}** schemas")
    
    # Define tables to check
    TABLES = [
        'state_atoms',
        'process_atoms',
        'hebbian_edges',
        'feedback_events',
        'adaline_state',
        'experiment_runs'
    ]
    
    for s in schemas:
        with st.expander(f"📂 Schema: `{s}`", expanded=(s == schema)):
            col1, col2 = st.columns(2)
            
            for i, table in enumerate(TABLES):
                target_col = col1 if i % 2 == 0 else col2
                
                with target_col:
                    exists = check_table_exists(s, table)
                    if exists:
                        count = run_scalar(
                            f"SELECT COUNT(*) FROM {s}.{table}", s
                        ) or 0
                        st.text(f"✅ {table}: {count:,} rows")
                    else:
                        st.text(f"❌ {table}: not found")

st.divider()

# ==============================================================================
# Schema Comparison
# ==============================================================================

st.subheader("⚖️ Schema Comparison")

if len(schemas) >= 2:
    col1, col2 = st.columns(2)
    
    with col1:
        schema_a = st.selectbox(
            "Schema A",
            schemas,
            key="cmp_a",
            help="First schema to compare"
        )
    
    with col2:
        default_idx = min(1, len(schemas) - 1)
        schema_b = st.selectbox(
            "Schema B",
            schemas,
            index=default_idx,
            key="cmp_b",
            help="Second schema to compare"
        )
    
    if schema_a and schema_b:
        comparison = []
        compare_tables = [
            'state_atoms',
            'process_atoms',
            'hebbian_edges',
            'feedback_events'
        ]
        
        for table in compare_tables:
            count_a = run_scalar(
                f"SELECT COUNT(*) FROM {schema_a}.{table}", schema_a
            ) or 0
            count_b = run_scalar(
                f"SELECT COUNT(*) FROM {schema_b}.{table}", schema_b
            ) or 0
            
            diff = count_b - count_a
            diff_str = f"+{diff}" if diff > 0 else str(diff)
            
            comparison.append({
                'Table': table,
                schema_a: f"{count_a:,}",
                schema_b: f"{count_b:,}",
                'Diff': diff_str
            })
        
        st.dataframe(
            comparison,
            use_container_width=True,
            hide_index=True
        )
else:
    st.info("📊 Need at least 2 schemas for comparison.")

st.divider()

# ==============================================================================
# Cache Management
# ==============================================================================

st.subheader("🧹 Cache Management")

col1, col2 = st.columns([1, 3])

with col1:
    if st.button("🗑️ Clear All Cache", type="primary"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("✅ Cache cleared successfully")
        st.rerun()

with col2:
    st.caption(
        "Clears both data cache (`@st.cache_data`) and resource cache "
        "(`@st.cache_resource` including DB connections). "
        "Use when data seems stale."
    )

st.divider()

# ==============================================================================
# Footer
# ==============================================================================

st.caption("**Mnemoverse Dashboard** v0.3")
st.caption("Data source: Neon PostgreSQL with pgvector")
