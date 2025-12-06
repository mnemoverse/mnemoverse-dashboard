# Changelog

All notable changes to Mnemoverse Dashboard.

## [0.3.0] - 2024-12-06

### Added

- **Info tooltips (ℹ️)** for all metrics with detailed explanations
- **`metric_definitions.py`** - Centralized documentation for all metrics
- **Test suite** with pytest:
  - `tests/test_db.py` - Database utility tests
  - `tests/test_components.py` - Component tests  
  - `tests/test_pages.py` - Page logic tests
  - `tests/conftest.py` - Shared fixtures
- **`info_tooltip()`** component for help popovers

### Changed

- **Complete code cleanup** across all files:
  - Improved docstrings with data source documentation
  - Consistent code formatting and structure
  - Modern Python type hints (`str | None` instead of `Optional[str]`)
  - Organized imports (stdlib → third-party → local)
  - Section separators (`# ===`) for better navigation
  
- **`db.py`**:
  - Removed duplicate `check_table_exists` function
  - Added `_handle_query_error()` helper
  - Improved documentation for all functions
  
- **`components.py`**:
  - Extracted `_render_sidebar_stats()` helper
  - Added `SESSION_SCHEMA` constant
  - Added `info_tooltip()` function

- **All pages**:
  - Added subheaders with info buttons
  - Metrics now have ℹ️ tooltips with detailed explanations
  - Improved empty state messages with 📭 emoji
  - Better column layouts for metrics + tooltips

### Fixed

- Duplicate function definition in `db.py` (was overwriting parameterized version)
- Inconsistent path handling in page imports (now uses `pathlib.Path`)

## [0.2.0] - 2024-12-01

### Added

- Multi-schema support with schema selector
- 6 dashboard pages (Overview, Learning Curve, Memory State, Knowledge Graph, Admin, Tools)
- Connection pooling with auto-recovery
- Quick stats in sidebar
- Refresh button to clear cache

### Changed

- Migrated from single schema to multi-schema architecture
- Improved error handling for database queries

## [0.1.0] - 2024-11-15

### Added

- Initial dashboard implementation
- Basic metrics display
- Hebbian graph visualization
- Neon PostgreSQL integration
