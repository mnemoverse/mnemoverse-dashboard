"""
Database connection and query utilities.
Handles schema selection, connection pooling, error handling.
"""

import os
import streamlit as st
import pandas as pd
from typing import Optional, List, Any
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


def get_db_url() -> Optional[str]:
    """Get DATABASE_URL from Streamlit secrets or environment."""
    # Try Streamlit secrets first
    try:
        if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
            return st.secrets['DATABASE_URL']
    except Exception:
        pass  # No secrets file - that's ok, try env
    
    return os.getenv('DATABASE_URL')


@st.cache_resource
def get_engine():
    """Create SQLAlchemy engine with connection recovery."""
    db_url = get_db_url()
    if not db_url:
        return None
    
    return create_engine(
        db_url,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=3,
        max_overflow=5,
    )


def get_available_schemas() -> List[str]:
    """Get list of KDM schemas from database."""
    engine = get_engine()
    if not engine:
        return []
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name LIKE 'kdm%'
                ORDER BY schema_name
            """))
            schemas = [row[0] for row in result]
            return schemas if schemas else []
    except SQLAlchemyError as e:
        st.error(f"Failed to fetch schemas: {e}")
        return []


def run_query(query: str, schema: str) -> pd.DataFrame:
    """
    Execute query with schema substitution.
    Returns empty DataFrame on error (with error logged).
    """
    engine = get_engine()
    if not engine:
        st.error("Database not connected. Set DATABASE_URL.")
        return pd.DataFrame()
    
    # Replace {schema} placeholder
    query = query.replace('{schema}', schema)
    
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query), conn)
    except SQLAlchemyError as e:
        error_msg = str(e)
        # Clean up error message
        if "relation" in error_msg and "does not exist" in error_msg:
            st.warning(f"Table not found in schema '{schema}'. Run migrations first.")
        elif "SSL" in error_msg or "connection" in error_msg.lower():
            st.cache_resource.clear()
            st.error("Connection lost. Please refresh.")
        else:
            st.error(f"Query error: {error_msg[:200]}")
        return pd.DataFrame()


def run_scalar(query: str, schema: str) -> Any:
    """Execute query and return single value. Returns None on error."""
    engine = get_engine()
    if not engine:
        return None
    
    query = query.replace('{schema}', schema)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query)).scalar()
            return result
    except SQLAlchemyError:
        return None


def check_table_exists(schema: str, table: str) -> bool:
    """Check if a table exists in the schema."""
    engine = get_engine()
    if not engine:
        return False
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = :schema AND table_name = :table
                )
            """), {"schema": schema, "table": table})
            return result.scalar() or False
    except SQLAlchemyError:
        return False


def check_table_exists(schema: str, table: str) -> bool:
    """Check if a table exists in schema."""
    query = f"""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = '{schema}' AND table_name = '{table}'
        )
    """
    result = run_scalar(query, schema)
    return bool(result)
