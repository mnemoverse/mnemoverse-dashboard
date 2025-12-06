"""
Database Connection & Query Utilities for Mnemoverse Dashboard.

Handles:
- Database connection via DATABASE_URL (secrets or env)
- Schema selection for multi-experiment isolation
- Connection pooling with auto-recovery
- Safe query execution with error handling
"""

import os
from typing import Any

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# ==============================================================================
# Connection Management
# ==============================================================================


def get_db_url() -> str | None:
    """
    Get DATABASE_URL from Streamlit secrets or environment.
    
    Priority:
    1. Streamlit secrets (.streamlit/secrets.toml)
    2. Environment variable
    
    Returns:
        Database URL string or None if not configured.
    """
    # Try Streamlit secrets first
    try:
        if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
            return st.secrets['DATABASE_URL']
    except Exception:
        pass  # Secrets file missing - fallback to env
    
    return os.getenv('DATABASE_URL')


@st.cache_resource
def get_engine():
    """
    Create SQLAlchemy engine with connection recovery.
    
    Configuration:
    - pool_pre_ping: Validates connections before use
    - pool_recycle: Refreshes connections every 5 minutes
    - pool_size: Maintains 3 persistent connections
    - max_overflow: Allows 5 additional connections under load
    
    Returns:
        SQLAlchemy Engine or None if DATABASE_URL not configured.
    """
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


# ==============================================================================
# Schema Discovery
# ==============================================================================


def get_available_schemas() -> list[str]:
    """
    Get list of KDM experiment schemas from database.
    
    Filters schemas starting with 'kdm' prefix.
    
    Returns:
        List of schema names sorted alphabetically.
    """
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
            return [row[0] for row in result]
    except SQLAlchemyError as e:
        st.error(f"Failed to fetch schemas: {e}")
        return []


def check_table_exists(schema: str, table: str) -> bool:
    """
    Check if a table exists in the specified schema.
    
    Uses parameterized query for SQL injection protection.
    
    Args:
        schema: Database schema name
        table: Table name to check
        
    Returns:
        True if table exists, False otherwise.
    """
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


# ==============================================================================
# Query Execution
# ==============================================================================


def run_query(query: str, schema: str) -> pd.DataFrame:
    """
    Execute query with schema substitution.
    
    Replaces {schema} placeholder in query with actual schema name.
    Returns empty DataFrame on error (errors are displayed to user).
    
    Args:
        query: SQL query with {schema} placeholder
        schema: Target schema name
        
    Returns:
        Query results as DataFrame, or empty DataFrame on error.
    """
    engine = get_engine()
    if not engine:
        st.error("Database not connected. Set DATABASE_URL.")
        return pd.DataFrame()
    
    # Replace schema placeholder
    query = query.replace('{schema}', schema)
    
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query), conn)
    except SQLAlchemyError as e:
        _handle_query_error(e, schema)
        return pd.DataFrame()


def run_scalar(query: str, schema: str) -> Any:
    """
    Execute query and return single scalar value.
    
    Args:
        query: SQL query with {schema} placeholder
        schema: Target schema name
        
    Returns:
        Single value from query, or None on error.
    """
    engine = get_engine()
    if not engine:
        return None
    
    query = query.replace('{schema}', schema)
    
    try:
        with engine.connect() as conn:
            return conn.execute(text(query)).scalar()
    except SQLAlchemyError:
        return None


# ==============================================================================
# Error Handling
# ==============================================================================


def _handle_query_error(error: SQLAlchemyError, schema: str) -> None:
    """
    Handle query errors with user-friendly messages.
    
    Categorizes errors and shows appropriate messages:
    - Missing table: Suggests running migrations
    - Connection lost: Clears cache and suggests refresh
    - Other: Shows truncated error message
    """
    error_msg = str(error)
    
    if "relation" in error_msg and "does not exist" in error_msg:
        st.warning(f"Table not found in schema '{schema}'. Run migrations first.")
    elif "SSL" in error_msg or "connection" in error_msg.lower():
        st.cache_resource.clear()
        st.error("Connection lost. Please refresh the page.")
    else:
        st.error(f"Query error: {error_msg[:200]}")
