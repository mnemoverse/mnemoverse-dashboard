"""
Knowledge Graph Page
Hebbian network visualization.
"""

import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import sys
sys.path.insert(0, str(__file__).replace('pages/4_Knowledge_Graph.py', ''))

from db import run_query, run_scalar
from components import render_sidebar

st.set_page_config(page_title="Knowledge Graph | Mnemoverse", page_icon="🕸️", layout="wide")

# Header first
st.title("Knowledge Graph")

# Sidebar
schema = render_sidebar()

if not schema:
    st.warning("Select a schema to view data.")
    st.stop()

st.caption(f"Schema: `{schema}`")
st.divider()

# Stats
col1, col2, col3 = st.columns(3)

with col1:
    nodes = run_scalar("SELECT COUNT(*) FROM {schema}.state_atoms", schema)
    st.metric("Concepts", nodes or 0)

with col2:
    edges = run_scalar("SELECT COUNT(*) FROM {schema}.hebbian_edges", schema)
    st.metric("Connections", edges or 0)

with col3:
    avg_weight = run_scalar("SELECT AVG(weight) FROM {schema}.hebbian_edges", schema)
    st.metric("Avg Weight", f"{avg_weight:.4f}" if avg_weight else "N/A")

st.divider()

# Weight filter
if edges and edges > 0:
    min_weight = st.slider(
        "Minimum weight filter",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.01
    )
else:
    min_weight = 0.0

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
    st.info("No Hebbian edges found. Run experiment to build the knowledge graph.")
else:
    # Build NetworkX graph
    G = nx.Graph()
    for _, row in graph_data.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])
    
    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Edge traces
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Node traces
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    node_degrees = [G.degree(node) for node in G.nodes()]
    node_labels = list(G.nodes())
    
    # Truncate long labels
    display_labels = [n[:20] + '...' if len(n) > 20 else n for n in node_labels]
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=display_labels,
        textposition="top center",
        hovertext=[f"{n}\nConnections: {G.degree(n)}" for n in G.nodes()],
        marker=dict(
            size=[10 + d * 3 for d in node_degrees],
            color=node_degrees,
            colorscale='Blues',
            colorbar=dict(title="Connections"),
            line=dict(width=1, color='#333')
        )
    )
    
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=500
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption(f"Showing {len(G.nodes())} concepts, {len(G.edges())} connections (weight >= {min_weight})")

st.divider()

# Top connections table
st.subheader("Strongest Connections")

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
    st.info("No connections to display.")
else:
    st.dataframe(
        top_connections,
        use_container_width=True,
        hide_index=True,
        column_config={
            "source": "Source",
            "target": "Target",
            "weight": st.column_config.ProgressColumn(
                "Weight",
                format="%.4f",
                min_value=0,
                max_value=1,
            ),
            "co_activation_count": "Co-activations"
        }
    )
