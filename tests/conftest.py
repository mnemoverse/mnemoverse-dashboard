"""
Pytest Configuration and Fixtures for Dashboard Tests.

Provides mock database connections and test data.
"""

import pytest
from unittest.mock import MagicMock, patch
import pandas as pd


# ==============================================================================
# Mock Database Fixtures
# ==============================================================================


@pytest.fixture
def mock_engine():
    """Create a mock SQLAlchemy engine."""
    engine = MagicMock()
    engine.connect.return_value.__enter__ = MagicMock()
    engine.connect.return_value.__exit__ = MagicMock()
    return engine


@pytest.fixture
def mock_db_url():
    """Sample database URL for testing."""
    return "postgresql://test:pass@localhost:5432/testdb?sslmode=require"


@pytest.fixture
def sample_schemas():
    """Sample schema list for testing."""
    return ["kdm", "kdm_exp_001", "kdm_exp_002", "kdm_clean"]


@pytest.fixture
def sample_process_atoms():
    """Sample process atoms DataFrame."""
    return pd.DataFrame({
        "id": [1, 2, 3],
        "concept": ["pattern_a", "pattern_b", "pattern_c"],
        "query": ["How to solve?", "Apply transform", "Grid rotation"],
        "response": ["Solution A", "Solution B", "Solution C"],
        "is_successful": [True, False, True],
        "task_id": ["task_001", "task_002", "task_003"],
        "created_at": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
    })


@pytest.fixture
def sample_state_atoms():
    """Sample state atoms DataFrame."""
    return pd.DataFrame({
        "id": [1, 2, 3],
        "concept": ["pattern_a", "pattern_b", "pattern_c"],
        "adaline_utility": [0.85, 0.72, 0.91],
        "use_count": [10, 5, 15],
        "positive_feedback_count": [8, 3, 12],
        "negative_feedback_count": [2, 2, 3]
    })


@pytest.fixture
def sample_hebbian_edges():
    """Sample hebbian edges DataFrame."""
    return pd.DataFrame({
        "source": ["pattern_a", "pattern_a", "pattern_b"],
        "target": ["pattern_b", "pattern_c", "pattern_c"],
        "weight": [0.75, 0.45, 0.60],
        "co_activation_count": [15, 8, 12]
    })


@pytest.fixture
def sample_experiment_runs():
    """Sample experiment runs DataFrame."""
    return pd.DataFrame({
        "run_name": ["baseline_001", "memory_001", "memory_002"],
        "mode": ["baseline", "memory", "memory"],
        "model": ["qwen3-80b", "qwen3-80b", "qwen3-80b"],
        "tasks_total": [100, 100, 200],
        "tasks_correct": [26, 35, 78],
        "accuracy": [0.26, 0.35, 0.39],
        "started_at": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
        "completed_at": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
    })


# ==============================================================================
# Streamlit Mock Fixtures
# ==============================================================================


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit module for testing."""
    with patch("streamlit.cache_data", lambda f: f), \
         patch("streamlit.cache_resource", lambda f: f), \
         patch("streamlit.error"), \
         patch("streamlit.warning"), \
         patch("streamlit.success"), \
         patch("streamlit.info"):
        yield


@pytest.fixture
def mock_secrets(mock_db_url):
    """Mock Streamlit secrets."""
    secrets = MagicMock()
    secrets.__contains__ = lambda self, key: key == "DATABASE_URL"
    secrets.__getitem__ = lambda self, key: mock_db_url if key == "DATABASE_URL" else None
    return secrets
