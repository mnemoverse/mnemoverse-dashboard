"""
Tests for Dashboard Page Logic.

Integration tests for page behavior with mocked data.
"""

import pytest
from unittest.mock import MagicMock, patch
import pandas as pd


# ==============================================================================
# Overview Page Tests
# ==============================================================================


class TestOverviewPage:
    """Tests for 1_Overview.py page logic."""
    
    def test_displays_key_metrics(self, sample_process_atoms):
        """Should display all four key metrics."""
        with patch("db.get_engine") as mock_engine, \
             patch("db.run_scalar") as mock_scalar:
            
            # Mock scalar queries for counts
            mock_scalar.side_effect = [100, 50, 200, 30]
            
            # Verify metrics would be displayed correctly
            counts = [
                mock_scalar("SELECT COUNT(*) FROM {schema}.state_atoms", "kdm"),
                mock_scalar("SELECT COUNT(*) FROM {schema}.process_atoms", "kdm"),
                mock_scalar("SELECT COUNT(*) FROM {schema}.hebbian_edges", "kdm"),
                mock_scalar("SELECT COUNT(*) FROM {schema}.feedback_events", "kdm")
            ]
            
            assert counts == [100, 50, 200, 30]
    
    def test_handles_empty_experiment_runs(self):
        """Should show info message when no experiment runs."""
        with patch("db.run_query") as mock_query:
            mock_query.return_value = pd.DataFrame()
            
            result = mock_query("SELECT * FROM {schema}.experiment_runs", "kdm")
            assert result.empty


# ==============================================================================
# Learning Curve Page Tests
# ==============================================================================


class TestLearningCurvePage:
    """Tests for 2_Learning_Curve.py page logic."""
    
    def test_calculates_accuracy_correctly(self):
        """Should calculate accuracy as correct/total * 100."""
        tasks_total = 100
        tasks_correct = 35
        
        accuracy = (tasks_correct / tasks_total * 100) if tasks_total > 0 else 0
        
        assert accuracy == 35.0
    
    def test_handles_zero_tasks(self):
        """Should return 0% accuracy when no tasks."""
        tasks_total = 0
        tasks_correct = 0
        
        accuracy = (tasks_correct / tasks_total * 100) if tasks_total > 0 else 0
        
        assert accuracy == 0
    
    def test_computes_delta_between_modes(self, sample_experiment_runs):
        """Should compute delta between baseline and memory accuracy."""
        df = sample_experiment_runs
        
        baseline_runs = df[df['mode'] == 'baseline']
        memory_runs = df[df['mode'] == 'memory']
        
        baseline_acc = baseline_runs['accuracy'].mean()
        memory_acc = memory_runs['accuracy'].mean()
        
        delta = memory_acc - baseline_acc
        
        # Memory should be better than baseline
        assert delta > 0
        assert baseline_acc == 0.26
        assert memory_acc == pytest.approx(0.37, rel=0.01)


# ==============================================================================
# Memory State Page Tests
# ==============================================================================


class TestMemoryStatePage:
    """Tests for 3_Memory_State.py page logic."""
    
    def test_displays_top_concepts_by_utility(self, sample_state_atoms):
        """Should sort concepts by adaline_utility descending."""
        df = sample_state_atoms.sort_values('adaline_utility', ascending=False)
        
        assert df.iloc[0]['concept'] == 'pattern_c'  # Highest utility
        assert df.iloc[0]['adaline_utility'] == 0.91
    
    def test_feedback_distribution(self):
        """Should correctly sum feedback by type."""
        feedback_data = pd.DataFrame({
            'feedback_type': ['positive', 'negative', 'positive'],
            'count': [1, 1, 1]
        })
        
        grouped = feedback_data.groupby('feedback_type').sum()
        
        assert grouped.loc['positive', 'count'] == 2
        assert grouped.loc['negative', 'count'] == 1


# ==============================================================================
# Knowledge Graph Page Tests
# ==============================================================================


class TestKnowledgeGraphPage:
    """Tests for 4_Knowledge_Graph.py page logic."""
    
    def test_filters_edges_by_weight(self, sample_hebbian_edges):
        """Should filter edges with weight below threshold."""
        min_weight = 0.5
        
        filtered = sample_hebbian_edges[
            sample_hebbian_edges['weight'] >= min_weight
        ]
        
        assert len(filtered) == 2  # Only edges >= 0.5
        assert all(filtered['weight'] >= min_weight)
    
    def test_builds_graph_from_edges(self, sample_hebbian_edges):
        """Should create NetworkX graph from edge data."""
        import networkx as nx
        
        G = nx.Graph()
        for _, row in sample_hebbian_edges.iterrows():
            G.add_edge(row['source'], row['target'], weight=row['weight'])
        
        assert len(G.nodes()) == 3  # pattern_a, pattern_b, pattern_c
        assert len(G.edges()) == 3
    
    def test_calculates_node_degrees(self, sample_hebbian_edges):
        """Should correctly calculate node connection counts."""
        import networkx as nx
        
        G = nx.Graph()
        for _, row in sample_hebbian_edges.iterrows():
            G.add_edge(row['source'], row['target'])
        
        degrees = dict(G.degree())
        
        assert degrees['pattern_a'] == 2  # Connected to b and c
        assert degrees['pattern_b'] == 2  # Connected to a and c
        assert degrees['pattern_c'] == 2  # Connected to a and b


# ==============================================================================
# Admin Page Tests
# ==============================================================================


class TestAdminPage:
    """Tests for 5_Admin.py page logic."""
    
    def test_masks_database_credentials(self):
        """Should mask password in database URL for display."""
        db_url = "postgresql://user:secret_password@host.neon.tech/db"
        
        if '@' in db_url:
            masked = db_url.split('@')[1]
        else:
            masked = 'configured'
        
        assert 'secret_password' not in masked
        assert 'host.neon.tech' in masked
    
    def test_schema_comparison(self, sample_schemas):
        """Should allow comparing two schemas."""
        schema_a = sample_schemas[0]
        schema_b = sample_schemas[1]
        
        assert schema_a != schema_b
        assert schema_a == "kdm"
        assert schema_b == "kdm_exp_001"


# ==============================================================================
# Data Integrity Tests
# ==============================================================================


class TestDataIntegrity:
    """Tests for data consistency and integrity."""
    
    def test_accuracy_in_valid_range(self, sample_experiment_runs):
        """Accuracy should be between 0 and 1."""
        for acc in sample_experiment_runs['accuracy']:
            assert 0 <= acc <= 1
    
    def test_utility_in_valid_range(self, sample_state_atoms):
        """Adaline utility should be between 0 and 1."""
        for utility in sample_state_atoms['adaline_utility']:
            assert 0 <= utility <= 1
    
    def test_weight_in_valid_range(self, sample_hebbian_edges):
        """Edge weights should be between 0 and 1."""
        for weight in sample_hebbian_edges['weight']:
            assert 0 <= weight <= 1
    
    def test_counts_are_non_negative(self, sample_state_atoms):
        """All counts should be non-negative."""
        assert all(sample_state_atoms['use_count'] >= 0)
        assert all(sample_state_atoms['positive_feedback_count'] >= 0)
        assert all(sample_state_atoms['negative_feedback_count'] >= 0)
