# Mnemoverse Dashboard

🧠 Analytics dashboard for KDMemory (Knowledge Delta Memory) experiments.

## Features

- **📊 Overview** - Quick stats: state atoms, process atoms, Hebbian edges, feedback
- **📈 Learning Curve** - Accuracy vs memory size (key hypothesis visualization)
- **🧠 Memory State** - Adaline learning, concept utilities, feedback distribution
- **🕸️ Knowledge Graph** - Interactive Hebbian network visualization
- **⚙️ Admin** - Schema management, diagnostics, cache control
- **🔧 Tools** - Links to W&B, Phoenix, Neon, GitHub

## Pages

| Page | Purpose |
|------|---------|
| Overview | Key metrics and last experiment summary |
| Learning Curve | **Main analysis** - Does accuracy improve with memory? |
| Memory State | Adaline perceptron state, concept utilities |
| Knowledge Graph | Hebbian network visualization |
| Admin | Schema management, connection diagnostics |
| Tools | External observability integrations |

## Data Sources

PostgreSQL database with **multi-schema** support:

| Schema | Purpose |
|--------|---------|
| `kdm` | Default experiment schema |
| `kdm_exp_*` | Isolated experiment environments |
| `kdm_clean` | Fresh schema for controlled experiments |

### Tables

- `state_atoms` - Learned concepts with embeddings and utility scores
- `process_atoms` - Solution attempts (successful and failed)
- `hebbian_edges` - Co-activation links between concepts
- `feedback_events` - Learning signals (positive/negative)
- `adaline_state` - Perceptron weights and learning state
- `experiment_runs` - Experiment metadata and results

## Deployment

### Streamlit Cloud (Recommended)

1. Fork this repo to your GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Deploy from `main` branch, file: `streamlit_app.py`
5. Add secrets:

```toml
# .streamlit/secrets.toml
DATABASE_URL = "postgresql://user:pass@host.neon.tech/db?sslmode=require"
```

### Local Development

```bash
# Clone and install
git clone https://github.com/mnemoverse/mnemoverse-dashboard.git
cd mnemoverse-dashboard
pip install -r requirements.txt

# Set environment variable
export DATABASE_URL="postgresql://..."

# Run dashboard
streamlit run streamlit_app.py
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## Architecture

```
mnemoverse-dashboard/
├── streamlit_app.py      # Entry point
├── components.py         # Shared UI components (sidebar, header, tooltips)
├── db.py                 # Database utilities (connection, queries)
├── metric_definitions.py # Documentation for all metrics
├── requirements.txt      # Dependencies
├── pages/
│   ├── 1_Overview.py
│   ├── 2_Learning_Curve.py
│   ├── 3_Memory_State.py
│   ├── 4_Knowledge_Graph.py
│   ├── 5_Admin.py
│   └── 6_Tools.py
└── tests/
    ├── conftest.py       # Pytest fixtures
    ├── test_db.py        # Database utility tests
    ├── test_components.py # Component tests
    └── test_pages.py     # Page logic tests
```

## Integrations

| Tool | Purpose | Link |
|------|---------|------|
| **Neon** | PostgreSQL database | console.neon.tech |
| **W&B** | Experiment tracking | wandb.ai/mnemoverse/arc-kdm-experiments |
| **Phoenix** | LLM tracing | app.phoenix.arize.com |
| **GitHub** | Source code | github.com/mnemoverse/cognitive-kdm |

## Version

**v0.3** - December 2024

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT
