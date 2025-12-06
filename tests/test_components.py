"""
Tests for components.py - Shared UI Components.

Tests cover:
- render_sidebar() - Schema selector rendering
- page_header() - Page header rendering
- help_button() - Compact help tooltip rendering
"""

import pytest
from unittest.mock import MagicMock, patch


# ==============================================================================
# render_sidebar Tests
# ==============================================================================


class TestRenderSidebar:
    """Tests for render_sidebar function."""
    
    def test_returns_none_when_no_engine(self):
        """Should return None when database is not connected."""
        with patch("components.get_engine", return_value=None), \
             patch("components.st") as mock_st:
            mock_st.sidebar = MagicMock()
            mock_st.session_state = {}
            
            from components import render_sidebar
            result = render_sidebar()
            
            # Should show error in sidebar
            mock_st.sidebar.error.assert_called()
    
    def test_returns_none_when_no_schemas(self):
        """Should return None when no schemas found."""
        mock_engine = MagicMock()
        
        with patch("components.get_engine", return_value=mock_engine), \
             patch("components.get_available_schemas", return_value=[]), \
             patch("components.st") as mock_st:
            mock_st.sidebar = MagicMock()
            mock_st.session_state = {}
            
            from components import render_sidebar
            result = render_sidebar()
            
            # Should show warning
            mock_st.sidebar.warning.assert_called()
    
    def test_returns_selected_schema(self):
        """Should return the selected schema from dropdown."""
        mock_engine = MagicMock()
        schemas = ["kdm", "kdm_exp_001"]
        
        with patch("components.get_engine", return_value=mock_engine), \
             patch("components.get_available_schemas", return_value=schemas), \
             patch("components.run_scalar", return_value=42), \
             patch("components.st") as mock_st:
            mock_st.sidebar = MagicMock()
            mock_st.sidebar.selectbox.return_value = "kdm_exp_001"
            mock_st.sidebar.button.return_value = False
            mock_st.session_state = {"current_schema": "kdm"}
            
            from components import render_sidebar
            result = render_sidebar()
            
            assert result == "kdm_exp_001"


# ==============================================================================
# page_header Tests
# ==============================================================================


class TestPageHeader:
    """Tests for page_header function."""
    
    def test_renders_title(self):
        """Should render page title."""
        with patch("components.st") as mock_st:
            from components import page_header
            page_header("Test Page")
            
            mock_st.title.assert_called_once_with("Test Page")
            mock_st.divider.assert_called_once()
    
    def test_renders_schema_caption(self):
        """Should render schema caption when provided."""
        with patch("components.st") as mock_st:
            from components import page_header
            page_header("Test Page", schema="kdm_exp_001")
            
            mock_st.title.assert_called_once_with("Test Page")
            mock_st.caption.assert_called_once()
            
            # Check that schema is in the caption
            caption_text = mock_st.caption.call_args[0][0]
            assert "kdm_exp_001" in caption_text
    
    def test_no_caption_when_no_schema(self):
        """Should not render caption when schema is None."""
        with patch("components.st") as mock_st:
            from components import page_header
            page_header("Test Page", schema=None)
            
            mock_st.title.assert_called_once()
            mock_st.caption.assert_not_called()


# ==============================================================================
# help_button Tests
# ==============================================================================


class TestHelpButton:
    """Tests for help_button function."""
    
    def test_renders_popover_with_caption(self):
        """Should render ? popover with caption text."""
        with patch("components.st") as mock_st:
            mock_popover = MagicMock()
            mock_st.popover.return_value.__enter__ = MagicMock(return_value=mock_popover)
            mock_st.popover.return_value.__exit__ = MagicMock(return_value=None)
            
            from components import help_button
            help_button("Short help text")
            
            mock_st.popover.assert_called_once_with("?", help="Click for details")
            mock_st.caption.assert_called_once_with("Short help text")

