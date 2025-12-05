"""
Mnemoverse Dashboard
====================
Unified monitoring dashboard for all Mnemoverse projects.

Data Sources (via Neon PostgreSQL):
- cognitive-kdm: Knowledge Delta Memory experiments
- research-agent: Research pipeline metrics  
- arch: Agent architecture stats

Deploy: https://share.streamlit.io
Repository: https://github.com/mnemoverse/mnemoverse-dashboard
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx

# ============================================
# Configuration
# ============================================

st.set_page_config(
    page_title="Mnemoverse Dashboard",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/mnemoverse',
        'Report a bug': 'https://github.com/mnemoverse/mnemoverse-dashboard/issues',
        'About': '# Mnemoverse\nUnified AI Memory & Research Platform'
    }
)

# Professional styling
st.markdown("""
<style>
    /* Header gradient */
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #fff, #a1c4fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.85;
        font-size: 1.1rem;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label {
        color: #a0a0a0 !important;
    }
    
    /* Cards */
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
    }
    .success-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
    }
    .warning-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
    }
    
    /* Status badges */
    .status-online {
        display: inline-block;
        padding: 6px 14px;
        background: linear-gradient(90deg, #11998e, #38ef7d);
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        color: white;
    }
    .status-offline {
        display: inline-block;
        padding: 6px 14px;
        background: linear-gradient(90deg, #eb3349, #f45c43);
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        color: white;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #888;
        border-top: 1px solid #333;
        margin-top: 3rem;
    }
    .footer a {
        color: #667eea;
        text-decoration: none;
    }
    .footer a:hover {
        text-decoration: underline;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(102, 126, 234, 0.1);
        border-radius: 8px;
        padding: 12px 24px;
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# Database Connection
# ============================================

def get_db_url() -> Optional[str]:
    """Get DATABASE_URL from Streamlit secrets or environment."""
    if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
        return st.secrets['DATABASE_URL']
    return os.getenv('DATABASE_URL')


@st.cache_resource
def get_engine():
    """Create cached database engine."""
    from sqlalchemy import create_engine
    db_url = get_db_url()
    if not db_url:
        return None
    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        with engine.connect() as conn:
            pass  # Test connection
        return engine
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None


def execute_query(query: str) -> pd.DataFrame:
    """Execute SQL query and return DataFrame."""
    engine = get_engine()
    if not engine:
        return pd.DataFrame()
    try:
        return pd.read_sql(query, engine)
    except Exception as e:
        st.warning(f"Query failed: {e}")
        return pd.DataFrame()


def execute_scalar(query: str) -> Any:
    """Execute SQL query and return scalar value."""
    engine = get_engine()
    if not engine:
        return 0
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            return conn.execute(text(query)).scalar() or 0
    except Exception:
        return 0


# ============================================
# Data Loading Functions
# ============================================

@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_kdm_stats() -> Dict[str, int]:
    """Load KDM memory statistics."""
    return {
        'state_atoms': execute_scalar("SELECT COUNT(*) FROM kdm.state_atoms"),
        'process_atoms': execute_scalar("SELECT COUNT(*) FROM kdm.process_atoms"),
        'hebbian_edges': execute_scalar("SELECT COUNT(*) FROM kdm.hebbian_edges"),
    }


@st.cache_data(ttl=60)
def load_hebbian_graph(min_weight: float = 0.0) -> pd.DataFrame:
    """Load Hebbian graph edges, optionally filtered by minimum weight."""
    query = f"""
        SELECT 
            s.concept as source,
            t.concept as target,
            e.weight,
            e.co_activation_count
        FROM kdm.hebbian_edges e
        JOIN kdm.state_atoms s ON e.source_id = s.id
        JOIN kdm.state_atoms t ON e.target_id = t.id
        WHERE e.weight >= {min_weight}
        ORDER BY e.weight DESC
    """
    return execute_query(query)


@st.cache_data(ttl=60)
def get_hebbian_stats() -> dict:
    """Get Hebbian graph statistics for slider defaults."""
    query = """
        SELECT 
            COUNT(*) as total_edges,
            MIN(weight) as min_weight,
            MAX(weight) as max_weight,
            AVG(weight) as avg_weight,
            PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY weight) as p25,
            PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY weight) as p50,
            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY weight) as p75
        FROM kdm.hebbian_edges
    """
    df = execute_query(query)
    if df.empty:
        return {'total_edges': 0, 'min_weight': 0, 'max_weight': 1, 'avg_weight': 0.5}
    return df.iloc[0].to_dict()


@st.cache_data(ttl=60)
def load_state_atoms(limit: int = 100) -> pd.DataFrame:
    """Load state atoms."""
    query = f"""
        SELECT 
            concept, domain, use_count, 
            gain_avg, utility_empirical,
            created_at, updated_at
        FROM kdm.state_atoms
        ORDER BY use_count DESC, created_at DESC
        LIMIT {limit}
    """
    return execute_query(query)


@st.cache_data(ttl=60)
def load_experiment_runs(limit: int = 50) -> pd.DataFrame:
    """Load experiment runs - adapted to actual schema."""
    # Actual schema: run_name, model, mode, tasks_total, tasks_correct, accuracy
    # Dashboard expects: run_id, experiment_name, baseline_accuracy, memory_accuracy, delta_accuracy, tasks_completed
    query = f"""
        SELECT 
            id::text as run_id, 
            run_name as experiment_name,
            CASE WHEN mode = 'baseline' THEN accuracy ELSE 0.0 END as baseline_accuracy,
            accuracy as memory_accuracy, 
            accuracy as delta_accuracy,
            tasks_correct as tasks_completed, 
            started_at as created_at
        FROM kdm.experiment_runs
        ORDER BY started_at DESC
        LIMIT {limit}
    """
    return execute_query(query)


@st.cache_data(ttl=60)
def load_daily_stats(days: int = 30) -> pd.DataFrame:
    """Load daily aggregated stats."""
    query = f"""
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as atoms_created
        FROM kdm.state_atoms
        WHERE created_at >= NOW() - INTERVAL '{days} days'
        GROUP BY DATE(created_at)
        ORDER BY date
    """
    return execute_query(query)


# ============================================
# Visualization Functions
# ============================================

def render_hebbian_network(df_edges: pd.DataFrame):
    """Render professional Hebbian network graph with clean dark theme."""
    if df_edges.empty:
        st.info("🔗 No Hebbian edges found. Run experiments to build the memory network.")
        return
    
    # Build graph with weights
    G = nx.Graph()
    for _, row in df_edges.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])
    
    # Weighted spring layout: stronger connections = closer nodes
    # We invert weight for 'distance' - higher weight = smaller distance
    max_weight = df_edges['weight'].max() if df_edges['weight'].max() > 0 else 1
    
    # Create distance dict: strong weight = small distance
    # distance = 1 / (weight + 0.1) normalized
    edge_distances = {}
    for _, row in df_edges.iterrows():
        # Invert: high weight → low distance (closer)
        dist = 1.0 / (row['weight'] / max_weight + 0.3)
        edge_distances[(row['source'], row['target'])] = dist
        edge_distances[(row['target'], row['source'])] = dist
    
    # Use Kamada-Kawai layout which respects edge weights as distances
    # Or spring layout with weight parameter
    try:
        # Kamada-Kawai gives better results for weighted graphs
        pos = nx.kamada_kawai_layout(G, weight='weight', scale=2.0)
    except:
        # Fallback to spring layout with inverted weights
        pos = nx.spring_layout(G, k=2.0, iterations=150, seed=42, weight='weight')
    
    # Edge traces - thin lines, weight = thickness
    edge_traces = []
    min_weight = df_edges['weight'].min() if df_edges['weight'].min() > 0 else 0.01
    
    for _, row in df_edges.iterrows():
        x0, y0 = pos[row['source']]
        x1, y1 = pos[row['target']]
        # Normalize weight to 0-1 range
        norm_weight = (row['weight'] - min_weight) / (max_weight - min_weight) if max_weight > min_weight else 0.5
        # Thin lines: 0.3px (weak) to 2.5px (strong)
        width = 0.3 + norm_weight * 2.2
        # Opacity also scales with weight
        opacity = 0.25 + norm_weight * 0.55
        
        edge_traces.append(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            mode='lines',
            line=dict(width=width, color=f'rgba(99, 179, 237, {opacity})'),
            hoverinfo='text',
            hovertext=f"Weight: {row['weight']:.3f}",
            showlegend=False
        ))
    
    # Node trace - bigger labels, better colors
    node_x = [pos[n][0] for n in G.nodes()]
    node_y = [pos[n][1] for n in G.nodes()]
    node_degrees = [G.degree(n) for n in G.nodes()]
    node_labels = list(G.nodes())
    max_degree = max(node_degrees) if node_degrees else 1
    
    # Truncate long labels for display
    display_labels = [n[:20] + '...' if len(n) > 20 else n for n in node_labels]
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=display_labels,
        textposition='bottom center',
        textfont=dict(size=11, color='#ffffff', family='Arial'),  # White, larger text
        hoverinfo='text',
        hovertext=[f"<b>{n}</b><br>Connections: {G.degree(n)}<br>Weight sum: {sum(G[n][nbr]['weight'] for nbr in G[n]):.2f}" for n in G.nodes()],
        marker=dict(
            size=[16 + (d / max_degree) * 30 for d in node_degrees],  # Bigger nodes
            color=node_degrees,
            colorscale=[
                [0, '#3b82f6'],      # Blue for low
                [0.5, '#8b5cf6'],    # Purple for mid  
                [1, '#f59e0b']       # Orange for high (hubs)
            ],
            colorbar=dict(
                title=dict(text='Connections', font=dict(color='#e0e0e0')),
                thickness=15, 
                x=1.02,
                tickfont=dict(color='#e0e0e0')
            ),
            line=dict(width=2, color='#1e293b')  # Subtle border
        ),
        showlegend=False
    )
    
    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        title=dict(
            text='🧠 Hebbian Memory Network', 
            font=dict(size=20, color='#f1f5f9', family='Arial Black'),
            x=0.5, xanchor='center'
        ),
        showlegend=False,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False),
        height=700,
        margin=dict(l=40, r=40, t=80, b=40),
        paper_bgcolor='#0f172a',  # Dark slate background
        plot_bgcolor='#0f172a',
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Stats below graph
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Nodes", len(G.nodes()))
    with col2:
        st.metric("Edges", len(G.edges()))
    with col3:
        hub_node = max(G.nodes(), key=lambda n: G.degree(n)) if G.nodes() else "N/A"
        st.metric("Top Hub", hub_node[:15] + "..." if len(hub_node) > 15 else hub_node)


def render_accuracy_chart(df: pd.DataFrame):
    """Render experiment accuracy comparison."""
    if df.empty:
        return
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Baseline',
        x=df['run_id'],
        y=df['baseline_accuracy'],
        marker_color='#ef4444',
        text=[f"{v:.1%}" for v in df['baseline_accuracy']],
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name='Memory',
        x=df['run_id'],
        y=df['memory_accuracy'],
        marker_color='#22c55e',
        text=[f"{v:.1%}" for v in df['memory_accuracy']],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='📊 Baseline vs Memory Accuracy',
        barmode='group',
        yaxis_title='Accuracy',
        xaxis_title='Experiment Run',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e0e0'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_growth_chart(df: pd.DataFrame):
    """Render daily growth chart."""
    if df.empty:
        return
    
    fig = px.area(
        df, x='date', y='atoms_created',
        title='📈 Daily Concept Growth',
        labels={'atoms_created': 'New Concepts', 'date': 'Date'}
    )
    fig.update_traces(
        fill='tozeroy',
        line_color='#667eea',
        fillcolor='rgba(102, 126, 234, 0.3)'
    )
    fig.update_layout(
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e0e0'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ============================================
# Sidebar
# ============================================

with st.sidebar:
    st.markdown("## 🌌 Mnemoverse")
    st.markdown("---")
    
    # Connection status
    engine = get_engine()
    if engine:
        st.markdown('<span class="status-online">● Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-offline">● Offline</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### Navigation")
    page = st.radio(
        "Select View",
        ["🏠 Overview", "🧠 Memory Graph", "🔬 Experiments", "📦 Concepts", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### Quick Actions")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    auto_refresh = st.checkbox("Auto-refresh (60s)", value=False)
    if auto_refresh:
        import time
        time.sleep(60)
        st.rerun()
    
    st.markdown("---")
    
    # External links
    st.markdown("### 🔗 Links")
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("Phoenix", "http://localhost:6006", use_container_width=True)
    with col2:
        st.link_button("W&B", "https://wandb.ai", use_container_width=True)
    
    st.link_button("📂 GitHub", "https://github.com/mnemoverse", use_container_width=True)


# ============================================
# Main Content
# ============================================

# Header
st.markdown("""
<div class="main-header">
    <h1>🌌 Mnemoverse Dashboard</h1>
    <p>Unified Monitoring for AI Memory, Research & Agent Systems</p>
</div>
""", unsafe_allow_html=True)


if page == "🏠 Overview":
    # Load data
    kdm_stats = load_kdm_stats()
    daily_stats = load_daily_stats(14)
    experiments = load_experiment_runs(10)
    
    # Key metrics
    st.markdown("### 📊 System Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🧠 Concepts",
            f"{kdm_stats['state_atoms']:,}",
            help="Total concepts in memory"
        )
    with col2:
        st.metric(
            "⚡ Processes",
            f"{kdm_stats['process_atoms']:,}",
            help="Active process atoms"
        )
    with col3:
        st.metric(
            "🔗 Connections",
            f"{kdm_stats['hebbian_edges']:,}",
            help="Hebbian associations"
        )
    with col4:
        exp_count = len(experiments) if not experiments.empty else 0
        st.metric(
            "🔬 Experiments",
            f"{exp_count}",
            help="Recent experiment runs"
        )
    
    st.markdown("---")
    
    # Two-column layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Growth chart
        if not daily_stats.empty:
            render_growth_chart(daily_stats)
        else:
            st.info("📈 No daily stats available yet")
    
    with col2:
        # Latest experiment
        st.markdown("### 🎯 Latest Experiment")
        if not experiments.empty:
            latest = experiments.iloc[0]
            baseline = latest.get('baseline_accuracy', 0) or 0
            memory = latest.get('memory_accuracy', 0) or 0
            delta = memory - baseline
            
            st.metric("Baseline", f"{baseline:.1%}")
            st.metric("Memory", f"{memory:.1%}", delta=f"{delta:+.1%}")
            
            if delta > 0:
                st.success(f"✅ +{delta:.1%} improvement")
            elif delta < 0:
                st.warning(f"⚠️ {delta:.1%} regression")
            else:
                st.info("➖ No change")
        else:
            st.info("No experiments yet")
    
    st.markdown("---")
    
    # Quick Hebbian preview - show top weighted edges
    st.markdown("### 🕸️ Memory Network Preview")
    df_edges = load_hebbian_graph(min_weight=0.0)
    if not df_edges.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Edges", len(df_edges))
        col2.metric("Avg Weight", f"{df_edges['weight'].mean():.4f}")
        col3.metric("Max Weight", f"{df_edges['weight'].max():.4f}")
        st.info("👉 Go to **Memory Graph** for full visualization with filters")
    else:
        st.info("🔗 No connections yet. Run experiments to build the graph.")


elif page == "🧠 Memory Graph":
    st.markdown("### 🧠 Hebbian Memory Network")
    
    # Get stats for smart defaults
    stats = get_hebbian_stats()
    total_edges = int(stats.get('total_edges', 0))
    
    if total_edges == 0:
        st.info("🔗 No Hebbian edges found. Run experiments to build the memory network.")
    else:
        min_w = float(stats.get('min_weight', 0))
        max_w = float(stats.get('max_weight', 1))
        avg_w = float(stats.get('avg_weight', 0.5))
        p50 = float(stats.get('p50', avg_w))
        
        st.markdown(f"**Total edges in database:** {total_edges} | Weight range: {min_w:.4f} - {max_w:.4f}")
        
        # Filter controls
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            # Default to median to show ~50% of edges
            min_weight_filter = st.slider(
                "Minimum weight (filter weak connections)", 
                min_value=min_w,
                max_value=max_w,
                value=min(p50, max_w * 0.1),  # Default: 10% of max or median
                step=(max_w - min_w) / 100 if max_w > min_w else 0.01,
                format="%.4f"
            )
        with col2:
            st.markdown(f"**Showing edges with weight ≥ {min_weight_filter:.4f}**")
        with col3:
            if st.button("🔄 Refresh"):
                st.cache_data.clear()
                st.rerun()
        
        df_edges = load_hebbian_graph(min_weight=min_weight_filter)
    
        if not df_edges.empty:
            # Stats
            col1, col2, col3, col4 = st.columns(4)
            unique_nodes = len(set(df_edges['source'].tolist() + df_edges['target'].tolist()))
            col1.metric("Edges (filtered)", len(df_edges), delta=f"of {total_edges}")
            col2.metric("Concepts", unique_nodes)
            col3.metric("Avg Weight", f"{df_edges['weight'].mean():.4f}")
            col4.metric("Co-activations", int(df_edges['co_activation_count'].sum()))
            
            st.markdown("---")
            render_hebbian_network(df_edges)
            
            st.markdown("---")
            st.markdown("### 🔝 Strongest Connections")
            top = df_edges.nlargest(15, 'weight')[['source', 'target', 'weight', 'co_activation_count']]
            st.dataframe(top.style.format({'weight': '{:.4f}'}), use_container_width=True)
        else:
            st.warning("No edges match the filter. Try lowering the minimum weight.")


elif page == "🔬 Experiments":
    st.markdown("### 🔬 Experiment Results")
    
    experiments = load_experiment_runs(50)
    
    if experiments.empty:
        st.info("No experiments found. Run `python run_experiment.py` to generate data.")
    else:
        # Summary
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Runs", len(experiments))
        avg_delta = experiments['delta_accuracy'].mean() if 'delta_accuracy' in experiments.columns else 0
        col2.metric("Avg Improvement", f"{avg_delta:+.1%}" if avg_delta else "N/A")
        col3.metric("Tasks Completed", experiments['tasks_completed'].sum() if 'tasks_completed' in experiments.columns else 0)
        
        st.markdown("---")
        
        # Chart
        if 'baseline_accuracy' in experiments.columns and 'memory_accuracy' in experiments.columns:
            render_accuracy_chart(experiments.head(20))
        
        st.markdown("---")
        
        # Table
        st.dataframe(experiments, use_container_width=True, height=400)


elif page == "📦 Concepts":
    st.markdown("### 📦 Stored Concepts (State Atoms)")
    
    limit = st.slider("Number of concepts", 50, 500, 100, 50)
    atoms = load_state_atoms(limit)
    
    if atoms.empty:
        st.info("No concepts stored yet.")
    else:
        # Stats
        col1, col2, col3 = st.columns(3)
        col1.metric("Loaded", len(atoms))
        col2.metric("Avg Uses", f"{atoms['use_count'].mean():.1f}")
        domains = atoms['domain'].nunique() if 'domain' in atoms.columns else 0
        col3.metric("Domains", domains)
        
        st.markdown("---")
        
        # Table
        st.dataframe(atoms, use_container_width=True, height=400)
        
        # Domain chart
        if 'domain' in atoms.columns and not atoms['domain'].isna().all():
            st.markdown("---")
            st.markdown("### 🏷️ Domain Distribution")
            domain_counts = atoms['domain'].value_counts()
            fig = px.pie(values=domain_counts.values, names=domain_counts.index)
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e0e0e0')
            )
            st.plotly_chart(fig, use_container_width=True)


elif page == "⚙️ Settings":
    st.markdown("### ⚙️ Configuration")
    
    # Database
    st.markdown("#### 🗄️ Database Connection")
    db_url = get_db_url()
    if db_url:
        masked = db_url.split('@')[1] if '@' in db_url else 'configured'
        st.success(f"✅ Connected to: `...@{masked}`")
    else:
        st.error("❌ DATABASE_URL not configured")
        st.code("""
# Add to Streamlit secrets (.streamlit/secrets.toml):
DATABASE_URL = "postgresql://user:pass@host/db?sslmode=require"
        """)
    
    st.markdown("---")
    
    # Integrations
    st.markdown("#### 🔗 Integrations")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Phoenix Tracing**")
        st.link_button("Open Phoenix", "http://localhost:6006", use_container_width=True)
    with col2:
        st.markdown("**Weights & Biases**")
        st.link_button("Open W&B", "https://wandb.ai", use_container_width=True)
    with col3:
        st.markdown("**GitHub**")
        st.link_button("View Repos", "https://github.com/mnemoverse", use_container_width=True)
    
    st.markdown("---")
    
    # Debug
    with st.expander("🐛 Debug Info"):
        st.json({
            'database_connected': get_engine() is not None,
            'kdm_stats': load_kdm_stats(),
            'timestamp': datetime.now().isoformat()
        })


# ============================================
# Footer
# ============================================

st.markdown("""
<div class="footer">
    <p>
        <strong>Mnemoverse Dashboard</strong> v1.0<br>
        <a href="https://github.com/mnemoverse/mnemoverse-dashboard">GitHub</a> •
        <a href="https://github.com/mnemoverse/cognitive-kdm">cognitive-kdm</a> •
        <a href="https://github.com/mnemoverse/mnemoverse-arch">arch</a>
    </p>
    <p style="font-size: 0.8rem; opacity: 0.6;">
        Built with Streamlit • Data from Neon PostgreSQL
    </p>
</div>
""", unsafe_allow_html=True)
