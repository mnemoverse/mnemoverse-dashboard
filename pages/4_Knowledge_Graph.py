"""
Knowledge Graph Page - Hebbian Network Visualization.

Visualizes the concept co-activation network built during learning:
- Nodes = Concepts (state atoms)
- Edges = Hebbian connections (concepts used together)
- Edge weight = Connection strength (0-1)

Hebbian Learning:
"Neurons that fire together, wire together"
When concepts are retrieved together for a task, their connection strengthens.

Data Sources:
- {schema}.state_atoms - Concept nodes
- {schema}.hebbian_edges - Connection edges with weights
"""

import sys
from pathlib import Path

import networkx as nx
import plotly.graph_objects as go
import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components import page_header, render_sidebar
from db import run_query, run_scalar
from metric_definitions import (
    HELP_AVG_WEIGHT,
    HELP_CONCEPTS,
    HELP_CONNECTIONS,
)

# ==============================================================================
# Page Configuration
# ==============================================================================

st.set_page_config(
    page_title="Knowledge Graph | Mnemoverse",
    page_icon="🕸️",
    layout="wide"
)

# ==============================================================================
# Sidebar & Header
# ==============================================================================

schema = render_sidebar()

if not schema:
    st.warning("Select a schema to view data.")
    st.stop()

page_header("🕸️ Knowledge Graph", schema)

# Page intro
st.info(
    "🔗 **Concept Connections:** Visualize how concepts link together. "
    "Based on Hebbian learning — \"neurons that fire together, wire together.\""
)

# ==============================================================================
# Graph Statistics
# ==============================================================================

st.subheader("📊 Graph Statistics")
st.caption("Network metrics. More connections = richer knowledge structure.")

col1, col2, col3 = st.columns(3)

with col1:
    nodes = run_scalar("SELECT COUNT(*) FROM {schema}.state_atoms", schema) or 0
    st.metric("Concepts", nodes, help=HELP_CONCEPTS)

with col2:
    edges = run_scalar("SELECT COUNT(*) FROM {schema}.hebbian_edges", schema) or 0
    st.metric("Connections", edges, help=HELP_CONNECTIONS)

with col3:
    avg_weight = run_scalar(
        "SELECT AVG(weight) FROM {schema}.hebbian_edges", schema
    )
    st.metric("Avg Weight", f"{avg_weight:.4f}" if avg_weight else "N/A", help=HELP_AVG_WEIGHT)

st.divider()

# ==============================================================================
# Weight Filter
# ==============================================================================

if edges > 0:
    st.caption("🔧 **Filter Settings**")
    min_weight = st.slider(
        "Minimum edge weight",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.01,
        help="Hide weak connections to focus on strong relationships"
    )
else:
    min_weight = 0.0

# ==============================================================================
# Graph Visualization
# ==============================================================================

st.subheader("🌐 Concept Network")

# Load graph data
graph_data = run_query(f"""
    SELECT 
        s.concept as source,
        t.concept as target,
        e.weight,
        e.co_activation_count
    FROM {{schema}}.hebbian_edges e
    JOIN {{schema}}.state_atoms s ON e.source_id = s.id
    JOIN {{schema}}.state_atoms t ON e.target_id = t.id
    WHERE e.weight >= {min_weight}
    ORDER BY e.weight DESC
    LIMIT 200
""", schema)

if graph_data.empty:
    st.info(
        "📭 No Hebbian edges found. Run an experiment to build the knowledge graph."
    )
else:
    # Build NetworkX graph
    G = nx.Graph()
    for _, row in graph_data.iterrows():
        G.add_edge(
            row['source'],
            row['target'],
            weight=row['weight'],
            co_activations=row['co_activation_count']
        )
    
    # Compute layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Build edge traces
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines',
        name='Connections'
    )
    
    # Build node traces
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    node_degrees = [G.degree(node) for node in G.nodes()]
    node_labels = list(G.nodes())
    
    # Truncate long labels for display
    display_labels = [
        n[:20] + '...' if len(n) > 20 else n
        for n in node_labels
    ]
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=display_labels,
        textposition="top center",
        textfont=dict(size=9),
        hovertext=[
            f"<b>{n}</b><br>Connections: {G.degree(n)}"
            for n in G.nodes()
        ],
        marker=dict(
            size=[10 + d * 3 for d in node_degrees],
            color=node_degrees,
            colorscale='Blues',
            colorbar=dict(
                title="Connections",
                thickness=15,
                len=0.5
            ),
            line=dict(width=1, color='#333')
        ),
        name='Concepts'
    )
    
    # Create figure
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption(
        f"📊 Showing **{len(G.nodes())}** concepts, "
        f"**{len(G.edges())}** connections (weight ≥ {min_weight})"
    )

st.divider()

# ==============================================================================
# Strongest Connections Table
# ==============================================================================

st.subheader("🔗 Strongest Connections")

top_connections = run_query("""
    SELECT 
        s.concept as source,
        t.concept as target,
        e.weight,
        e.co_activation_count
    FROM {schema}.hebbian_edges e
    JOIN {schema}.state_atoms s ON e.source_id = s.id
    JOIN {schema}.state_atoms t ON e.target_id = t.id
    ORDER BY e.weight DESC
    LIMIT 20
""", schema)

if top_connections.empty:
    st.info("📭 No connections to display.")
else:
    st.dataframe(
        top_connections,
        use_container_width=True,
        hide_index=True,
        column_config={
            "source": st.column_config.TextColumn(
                "Source",
                help="First concept in the connection"
            ),
            "target": st.column_config.TextColumn(
                "Target",
                help="Second concept in the connection"
            ),
            "weight": st.column_config.ProgressColumn(
                "Weight",
                format="%.4f",
                min_value=0,
                max_value=1,
                help="Connection strength (0-1)"
            ),
            "co_activation_count": st.column_config.NumberColumn(
                "Co-activations",
                help="Times these concepts were used together"
            )
        }
    )
