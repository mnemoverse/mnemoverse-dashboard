"""
Admin Page
Schema management, connection info, diagnostics.
"""

import streamlit as st
import sys
sys.path.insert(0, str(__file__).replace('pages/5_Admin.py', ''))

from db import get_db_url, get_engine, get_available_schemas, run_query, run_scalar, check_table_exists
from components import render_sidebar, page_header

st.set_page_config(page_title="Admin | Mnemoverse", page_icon="⚙️", layout="wide")

# Sidebar
schema = render_sidebar()

# Header (no schema required for admin)
st.title("Admin")
st.divider()

# Connection Info
st.subheader("Connection")

db_url = get_db_url()
if db_url:
    # Mask password
    masked = db_url.split('@')[1] if '@' in db_url else 'configured'
    st.success(f"Connected to: ...@{masked}")
else:
    st.error("DATABASE_URL not configured")
    st.code("""
# Add to .streamlit/secrets.toml:
DATABASE_URL = "postgresql://user:pass@host/db?sslmode=require"
    """)

st.divider()

# Available Schemas
st.subheader("Available Schemas")

schemas = get_available_schemas()

if not schemas:
    st.warning("No KDM schemas found in database.")
else:
    for s in schemas:
        with st.expander(f"Schema: {s}"):
            # Table stats
            tables = ['state_atoms', 'process_atoms', 'hebbian_edges', 'feedback_events', 'adaline_state', 'experiment_runs']
            
            for table in tables:
                exists = check_table_exists(s, table)
                if exists:
                    count = run_scalar(f"SELECT COUNT(*) FROM {s}.{table}", s)
                    st.text(f"  {table}: {count or 0} rows")
                else:
                    st.text(f"  {table}: not found")

st.divider()

# Schema comparison
st.subheader("Schema Comparison")

if len(schemas) >= 2:
    col1, col2 = st.columns(2)
    
    with col1:
        schema_a = st.selectbox("Schema A", schemas, key="cmp_a")
    with col2:
        schema_b = st.selectbox("Schema B", schemas, index=min(1, len(schemas)-1), key="cmp_b")
    
    if schema_a and schema_b:
        comparison = []
        for table in ['state_atoms', 'process_atoms', 'hebbian_edges', 'feedback_events']:
            count_a = run_scalar(f"SELECT COUNT(*) FROM {schema_a}.{table}", schema_a) or 0
            count_b = run_scalar(f"SELECT COUNT(*) FROM {schema_b}.{table}", schema_b) or 0
            comparison.append({
                'table': table,
                schema_a: count_a,
                schema_b: count_b,
                'diff': count_b - count_a
            })
        
        st.dataframe(comparison, use_container_width=True, hide_index=True)
else:
    st.info("Need at least 2 schemas for comparison.")

st.divider()

# Cache management
st.subheader("Cache")

if st.button("Clear all cache", type="primary"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.success("Cache cleared")
    st.rerun()

st.divider()

# Version
st.caption("Mnemoverse Dashboard v0.2")
st.caption("Data source: Neon PostgreSQL")
