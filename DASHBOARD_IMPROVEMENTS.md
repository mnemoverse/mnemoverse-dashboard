# 🌌 Mnemoverse Dashboard - Enterprise Improvement Plan

## 📊 Current State Analysis

### ✅ What Works Well
1. **Professional Styling** - Gradient headers, dark theme, good color palette
2. **Core Features** - Overview, Memory Graph, Experiments, Concepts, Settings
3. **Hebbian Network Visualization** - Weighted layout, filtering, stats
4. **Database Integration** - Neon PostgreSQL with connection pooling
5. **Responsive Layout** - Sidebar navigation, metric cards

### ⚠️ Issues Found
1. **Deprecation Warnings** - `use_container_width` → `width='stretch'`
2. **Hard-coded Schema** - Only `kdm` schema, no multi-schema support
3. **No Error Boundaries** - Queries can fail silently
4. **Auto-refresh Implementation** - Blocking `time.sleep()` is wrong
5. **Missing Features** - No learning curve, no Adaline stats, no real-time updates

---

## 🎯 Enterprise Improvement Roadmap

### Phase 1: Code Quality & Stability (1-2 hours)

#### 1.1 Fix Deprecation Warnings
```python
# OLD:
st.dataframe(df, use_container_width=True)

# NEW:  
st.dataframe(df, width='stretch')
```

#### 1.2 Add Multi-Schema Support
```python
# Sidebar schema selector
available_schemas = get_available_schemas()  # ['kdm', 'kdm_big_run_400', ...]
selected_schema = st.sidebar.selectbox("Schema", available_schemas)
```

#### 1.3 Proper Error Handling
```python
@st.cache_data(ttl=60)
def safe_query(query: str, schema: str) -> pd.DataFrame:
    try:
        return execute_query(query.replace('{schema}', schema))
    except Exception as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()
```

#### 1.4 Fix Auto-Refresh (use st.fragment or st.rerun with timer)
```python
# Use Streamlit's native auto-rerun
if auto_refresh:
    st_autorefresh(interval=60000, limit=None)  # 60 seconds
```

---

### Phase 2: New Business Features (2-3 hours)

#### 2.1 📈 Learning Curve Page
**Purpose:** Visualize how memory improves accuracy over tasks

```
Metrics:
- Accuracy progression (task 1 → task N)
- Adaline prediction curve
- Memory retrieval success rate
- Feedback events over time
```

#### 2.2 🧬 Adaline Analytics
**Purpose:** Show learning algorithm behavior

```
Metrics:
- Current prediction value
- Learning rate (eta)
- Update history
- Positive/negative feedback ratio
```

#### 2.3 📊 Experiment Comparison
**Purpose:** Compare multiple runs side-by-side

```
Features:
- Select 2+ experiments
- Overlay accuracy curves
- Delta comparison table
- Best/worst task breakdown
```

#### 2.4 🔔 Real-time Updates (WebSocket)
**Purpose:** Live dashboard without manual refresh

```
Implementation:
- Poll database every 5s
- Update metrics in-place
- Animated transitions
```

---

### Phase 3: Enterprise Polish (1-2 hours)

#### 3.1 🎨 Design System Consistency
```css
/* Color tokens */
--color-primary: #667eea;
--color-success: #22c55e;
--color-warning: #f59e0b;
--color-error: #ef4444;
--color-bg-dark: #0f172a;
--color-bg-card: #1e293b;
```

#### 3.2 📱 Mobile Responsiveness
- Collapsible sidebar
- Stacked metrics on mobile
- Touch-friendly controls

#### 3.3 🔐 Authentication Ready
```python
# Placeholder for future auth
def require_auth():
    if 'authenticated' not in st.session_state:
        st.warning("Please log in")
        st.stop()
```

#### 3.4 📤 Export Capabilities
- Download CSV/Excel
- Export charts as PNG
- Share dashboard links

---

### Phase 4: Integration Enhancements (1 hour)

#### 4.1 🔗 W&B Integration
```python
# Fetch runs from W&B API
import wandb
runs = wandb.Api().runs("mnemoverse/arc-kdm-experiments")
```

#### 4.2 🔥 Phoenix Tracing Link
- Deep links to specific traces
- Latency overlay on experiment view

#### 4.3 📧 Alerts & Notifications
- Slack webhook on accuracy drop
- Email digest of daily stats

---

## 📋 Implementation Priority

| Priority | Feature | Effort | Impact |
|----------|---------|--------|--------|
| 🔴 P0 | Fix deprecations | 30min | Stability |
| 🔴 P0 | Multi-schema support | 1hr | Usability |
| 🟠 P1 | Learning Curve page | 2hr | Business value |
| 🟠 P1 | Adaline analytics | 1hr | Insight |
| 🟡 P2 | Experiment comparison | 2hr | Analysis |
| 🟡 P2 | Export capabilities | 1hr | Convenience |
| 🟢 P3 | Real-time updates | 2hr | Polish |
| 🟢 P3 | W&B integration | 1hr | Integration |

---

## 🏗️ Proposed File Structure

```
mnemoverse-dashboard/
├── streamlit_app.py          # Main entry point (clean, imports pages)
├── config.py                 # Settings, constants, color tokens
├── database.py               # All DB functions, schema handling
├── components/
│   ├── sidebar.py            # Sidebar with schema selector
│   ├── header.py             # Main header component
│   ├── metrics.py            # Metric card components
│   └── charts.py             # All Plotly chart functions
├── pages/
│   ├── 1_Overview.py
│   ├── 2_Learning_Curve.py   # NEW
│   ├── 3_Memory_Graph.py
│   ├── 4_Experiments.py
│   ├── 5_Concepts.py
│   ├── 6_Adaline.py          # NEW
│   └── 7_Settings.py
├── utils/
│   ├── formatting.py         # Number/date formatting
│   └── caching.py            # Cache utilities
└── assets/
    └── styles.css            # External CSS (optional)
```

---

## ✅ Quick Wins (Do Now)

1. **Fix `use_container_width`** → replace with `width='stretch'`
2. **Add schema selector** to sidebar
3. **Remove blocking auto-refresh** 
4. **Add loading states** for slow queries
5. **Clean up temp files** (streamlit_app_a71e164.py, etc.)

---

## 🎯 Success Metrics

- [ ] Zero deprecation warnings
- [ ] Multi-schema support working
- [ ] Learning curve shows Adaline progression
- [ ] All external tool links verified
- [ ] Mobile-friendly layout
- [ ] < 3s initial load time
- [ ] Automated tests for critical queries

---

*Created: 2025-12-05*
*Author: Arch Smart*
*Status: PLANNING*
