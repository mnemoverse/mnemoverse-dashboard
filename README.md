# Mnemoverse Dashboard

🌌 Unified monitoring dashboard for all Mnemoverse projects.

## Features

- **Real-time Stats** - State atoms, process atoms, Hebbian edges
- **Memory Graph** - Interactive Hebbian network visualization
- **Experiment Tracking** - Baseline vs Memory accuracy comparison
- **Concept Browser** - Browse stored concepts and domains

## Data Sources

All data comes from **Neon PostgreSQL** (`kdm` schema):
- `kdm.state_atoms` - Stored concepts
- `kdm.process_atoms` - Active processes
- `kdm.hebbian_edges` - Concept associations
- `kdm.experiment_runs` - Experiment results

## Deployment

### Streamlit Cloud (Recommended)

1. Fork this repo to your GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Deploy from `main` branch, file: `streamlit_app.py`
5. Add secrets:

```toml
# .streamlit/secrets.toml
DATABASE_URL = "postgresql://user:pass@host/db?sslmode=require"
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export DATABASE_URL="postgresql://..."

# Run
streamlit run streamlit_app.py
```

## Projects Writing Data

- **cognitive-kdm** - Knowledge Delta Memory experiments
- **mnemoverse-arch** - Agent architecture metrics
- **research-agent** - Research pipeline stats

## Screenshots

![Dashboard Overview](docs/screenshots/overview.png)
![Memory Graph](docs/screenshots/graph.png)

## License

MIT
