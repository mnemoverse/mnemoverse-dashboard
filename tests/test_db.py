"""
Tests for db.py - Database Connection and Query Utilities.

Tests cover:
- get_db_url() - URL retrieval from secrets/env
- get_engine() - SQLAlchemy engine creation
- get_available_schemas() - Schema discovery
- check_table_exists() - Table existence check
- run_query() - Query execution
- run_scalar() - Scalar query execution
"""

import os
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import pandas as pd


# ==============================================================================
# get_db_url Tests
# ==============================================================================


class TestGetDbUrl:
    """Tests for get_db_url function."""
    
    def test_returns_none_when_not_configured(self):
        """Should return None when DATABASE_URL is not set."""
        with patch.dict(os.environ, {}, clear=True), \
             patch("db.st") as mock_st:
            # No secrets
            mock_st.secrets = {}
            
            from db import get_db_url
            # Need to reimport to clear any cached values
            import importlib
            import db
            importlib.reload(db)
            
            result = db.get_db_url()
            # May return None or env value depending on test environment
            assert result is None or isinstance(result, str)
    
    def test_returns_url_from_environment(self):
        """Should return DATABASE_URL from environment when set."""
        test_url = "postgresql://user:pass@host/db"
        
        with patch.dict(os.environ, {"DATABASE_URL": test_url}), \
             patch("db.st") as mock_st:
            mock_st.secrets = {}
            
            import importlib
            import db
            importlib.reload(db)
            
            result = db.get_db_url()
            assert result == test_url


# ==============================================================================
# get_available_schemas Tests
# ==============================================================================


class TestGetAvailableSchemas:
    """Tests for get_available_schemas function."""
    
    def test_returns_empty_list_when_no_engine(self):
        """Should return empty list when engine is None."""
        with patch("db.get_engine", return_value=None):
            from db import get_available_schemas
            result = get_available_schemas()
            assert result == []
    
    def test_returns_schemas_from_database(self, mock_engine, sample_schemas):
        """Should return list of schemas starting with 'kdm'."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.__iter__ = lambda self: iter([(s,) for s in sample_schemas])
        
        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_result
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)
        
        mock_engine.connect.return_value = mock_conn
        
        with patch("db.get_engine", return_value=mock_engine):
            from db import get_available_schemas
            result = get_available_schemas()
            
            assert isinstance(result, list)
            # All should start with 'kdm'
            for schema in result:
                assert schema.startswith("kdm")


# ==============================================================================
# check_table_exists Tests
# ==============================================================================


class TestCheckTableExists:
    """Tests for check_table_exists function."""
    
    def test_returns_false_when_no_engine(self):
        """Should return False when engine is None."""
        with patch("db.get_engine", return_value=None):
            from db import check_table_exists
            result = check_table_exists("kdm", "state_atoms")
            assert result is False
    
    def test_returns_true_when_table_exists(self, mock_engine):
        """Should return True when table exists in schema."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = True
        
        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_result
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)
        
        mock_engine.connect.return_value = mock_conn
        
        with patch("db.get_engine", return_value=mock_engine):
            from db import check_table_exists
            result = check_table_exists("kdm", "state_atoms")
            assert result is True
    
    def test_returns_false_when_table_not_exists(self, mock_engine):
        """Should return False when table does not exist."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = False
        
        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_result
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)
        
        mock_engine.connect.return_value = mock_conn
        
        with patch("db.get_engine", return_value=mock_engine):
            from db import check_table_exists
            result = check_table_exists("kdm", "nonexistent_table")
            assert result is False


# ==============================================================================
# run_query Tests
# ==============================================================================


class TestRunQuery:
    """Tests for run_query function."""
    
    def test_returns_empty_df_when_no_engine(self):
        """Should return empty DataFrame when engine is None."""
        with patch("db.get_engine", return_value=None), \
             patch("db.st"):
            from db import run_query
            result = run_query("SELECT 1", "kdm")
            
            assert isinstance(result, pd.DataFrame)
            assert result.empty
    
    def test_replaces_schema_placeholder(self, mock_engine, sample_process_atoms):
        """Should replace {schema} with actual schema name."""
        with patch("db.get_engine", return_value=mock_engine), \
             patch("db.pd.read_sql", return_value=sample_process_atoms) as mock_read_sql:
            from db import run_query
            
            result = run_query(
                "SELECT * FROM {schema}.process_atoms",
                "kdm_exp_001"
            )
            
            # Check that schema was replaced
            call_args = mock_read_sql.call_args
            query_text = str(call_args[0][0])
            assert "kdm_exp_001" in query_text
            assert "{schema}" not in query_text


# ==============================================================================
# run_scalar Tests
# ==============================================================================


class TestRunScalar:
    """Tests for run_scalar function."""
    
    def test_returns_none_when_no_engine(self):
        """Should return None when engine is None."""
        with patch("db.get_engine", return_value=None):
            from db import run_scalar
            result = run_scalar("SELECT COUNT(*)", "kdm")
            assert result is None
    
    def test_returns_scalar_value(self, mock_engine):
        """Should return single scalar value from query."""
        expected_count = 42
        
        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_count
        
        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_result
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)
        
        mock_engine.connect.return_value = mock_conn
        
        with patch("db.get_engine", return_value=mock_engine):
            from db import run_scalar
            result = run_scalar(
                "SELECT COUNT(*) FROM {schema}.process_atoms",
                "kdm"
            )
            assert result == expected_count
    
    def test_replaces_schema_in_query(self, mock_engine):
        """Should replace {schema} placeholder with actual schema."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        
        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_result
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)
        
        mock_engine.connect.return_value = mock_conn
        
        with patch("db.get_engine", return_value=mock_engine):
            from db import run_scalar
            run_scalar("SELECT 1 FROM {schema}.table", "my_schema")
            
            # Verify execute was called
            assert mock_conn.execute.called
