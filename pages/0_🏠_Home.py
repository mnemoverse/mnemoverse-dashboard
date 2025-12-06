"""
Home Page - Welcome to Mnemoverse Dashboard.

Landing page with quick navigation and system overview.
"""

import streamlit as st

# ==============================================================================
# Page Configuration
# ==============================================================================

st.set_page_config(
    page_title="Home | Mnemoverse",
    page_icon="🏠",
    layout="wide"
)

# ==============================================================================
# Welcome Section
# ==============================================================================

st.title("🧠 Mnemoverse Dashboard")

st.markdown("""
### Welcome to the Cognitive Memory Analytics Dashboard!

This dashboard helps you understand how AI learns from experience by visualizing:

| Page | What You'll Find |
|------|------------------|
| 📊 **Overview** | Quick snapshot of memory size and recent experiments |
| 📈 **Learning Curve** | Does accuracy improve as memory grows? The key hypothesis! |
| 🧠 **Memory State** | Inside the learning algorithm (Adaline neural network) |
| 🕸️ **Knowledge Graph** | Visual map of concept connections |
| ⚙️ **Admin** | Database health and schema management |
| 🔧 **Tools** | Links to external monitoring tools |

---

### 🚀 Quick Start

1. **Select a schema** in the sidebar (e.g., `kdm`)
2. **Go to Overview** to see current memory state
3. **Check Learning Curve** to see if memory is helping

---
""")

# Quick stats
col1, col2, col3 = st.columns(3)

with col1:
    st.info("💡 **Tip:** Hover over `?` icons for explanations of metrics")

with col2:
    st.info("🔄 **Refresh:** Use sidebar button to reload data")

with col3:
    st.info("📊 **Schema:** Each schema is an isolated experiment")

st.divider()

# Navigation buttons
st.subheader("🧭 Quick Navigation")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📊 Overview", use_container_width=True):
        st.switch_page("pages/1_Overview.py")

with col2:
    if st.button("📈 Learning Curve", use_container_width=True):
        st.switch_page("pages/2_Learning_Curve.py")

with col3:
    if st.button("🧠 Memory State", use_container_width=True):
        st.switch_page("pages/3_Memory_State.py")

with col4:
    if st.button("🕸️ Knowledge Graph", use_container_width=True):
        st.switch_page("pages/4_Knowledge_Graph.py")
