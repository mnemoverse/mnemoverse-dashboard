"""
Metric Definitions - Documentation for Dashboard Metrics.

This module contains descriptions for all metrics displayed in the dashboard.
Used by info_tooltip() to provide consistent documentation.
"""

# ==============================================================================
# Overview Page Metrics
# ==============================================================================

METRIC_STATE_ATOMS = """
**State Atoms** — Persistent concepts in memory.

- **What**: Learned patterns from successful task solutions
- **Source**: `{schema}.state_atoms` table
- **Updates**: Created when a new concept is learned
- **Contains**: Concept name, embedding, utility scores, feedback counts

Higher count = more knowledge accumulated.
"""

METRIC_PROCESS_ATOMS = """
**Process Atoms** — Solution attempts.

- **What**: Individual LLM responses to task queries
- **Source**: `{schema}.process_atoms` table
- **Updates**: Created on every solution attempt (successful or not)
- **Contains**: Query, response, task_id, is_successful flag

Both successful and failed attempts are stored for learning.
"""

METRIC_HEBBIAN_EDGES = """
**Hebbian Edges** — Concept connections.

- **What**: Links between concepts that were used together
- **Source**: `{schema}.hebbian_edges` table
- **Updates**: Weight increases when concepts co-activate
- **Contains**: source_id, target_id, weight (0-1), co_activation_count

Based on Hebbian learning: "Neurons that fire together, wire together."
"""

METRIC_FEEDBACK_EVENTS = """
**Feedback Events** — Learning signals.

- **What**: Positive/negative signals from task outcomes
- **Source**: `{schema}.feedback_events` table
- **Updates**: Created when task is solved or failed
- **Contains**: concept_id, feedback_type, timestamp

Used to update Adaline utility predictions.
"""

# ==============================================================================
# Learning Curve Page Metrics
# ==============================================================================

METRIC_TASKS_SOLVED = """
**Tasks Solved** — Total solution attempts.

- **What**: Count of process atoms with a task_id
- **Query**: `COUNT(*) FROM process_atoms WHERE task_id IS NOT NULL`
- **Includes**: Both successful and failed attempts

This is the X-axis of the learning curve.
"""

METRIC_CORRECT = """
**Correct** — Successful solutions.

- **What**: Tasks where the model produced correct output
- **Query**: `COUNT(*) FROM process_atoms WHERE is_successful = true`
- **Determined by**: Comparison with expected ARC-AGI output

Target: Higher than baseline (no memory).
"""

METRIC_ACCURACY = """
**Accuracy** — Success rate.

- **Formula**: `correct / total × 100%`
- **Baseline**: ~26% for ARC-AGI without memory
- **Target**: Significant improvement with memory

The key metric for validating the memory hypothesis.
"""

METRIC_MEMORY_SIZE = """
**Memory Size** — Total atoms stored.

- **What**: All process atoms in the schema
- **Growth**: Increases with each experiment task
- **Hypothesis**: Accuracy should improve as memory grows

The X-axis of the key learning curve chart.
"""

METRIC_BASELINE = """
**Baseline** — Performance without memory.

- **Mode**: `baseline` in experiment_runs
- **Process**: Model solves tasks without retrieving past solutions
- **Purpose**: Control group for measuring memory benefit

Typical ARC-AGI baseline: 20-30%.
"""

METRIC_MEMORY_MODE = """
**Memory Mode** — Performance with KDMemory.

- **Mode**: `memory` in experiment_runs
- **Process**: Model retrieves relevant past solutions before solving
- **Retrieval**: Top-k similar concepts by embedding similarity

Should outperform baseline if memory is helping.
"""

METRIC_DELTA = """
**Delta** — Memory improvement.

- **Formula**: `memory_accuracy - baseline_accuracy`
- **Positive**: Memory is helping
- **Negative**: Memory may be hurting (noise, irrelevant retrievals)
- **Zero**: No effect

Target: Significant positive delta (>5%).
"""

# ==============================================================================
# Memory State Page Metrics
# ==============================================================================

METRIC_ADALINE_UPDATES = """
**Adaline Updates** — Weight adjustments.

- **What**: Number of times the perceptron weights were updated
- **Trigger**: Feedback events (positive/negative)
- **Source**: `adaline_state.update_count`

More updates = more learning from feedback.
"""

METRIC_AVG_ERROR = """
**Average Error** — Prediction accuracy.

- **What**: Mean squared error of utility predictions
- **Formula**: `(predicted_utility - actual_outcome)²`
- **Target**: Lower is better (predictions match outcomes)

Decreases as Adaline learns which concepts are useful.
"""

METRIC_LEARNING_RATE = """
**Learning Rate (η)** — Update step size.

- **What**: How much weights change per update
- **Typical**: 0.01 - 0.1
- **Trade-off**: Higher = faster learning but less stable

May be adaptive (decreasing over time).
"""

METRIC_UTILITY = """
**Adaline Utility** — Predicted usefulness.

- **Range**: 0.0 to 1.0
- **High (>0.7)**: Concept likely to help solve tasks
- **Low (<0.3)**: Concept rarely helpful
- **Updates**: Based on feedback after retrieval

Used to rank concepts during retrieval.
"""

METRIC_USE_COUNT = """
**Use Count** — Retrieval frequency.

- **What**: Times this concept was retrieved for a task
- **High count**: Frequently relevant concept
- **Zero**: Never retrieved (may need better embedding)

Popular concepts get more feedback and learning.
"""

# ==============================================================================
# Knowledge Graph Page Metrics
# ==============================================================================

METRIC_CONCEPTS = """
**Concepts** — Graph nodes.

- **What**: Unique state atoms in the schema
- **Visualization**: Nodes in the network graph
- **Size in graph**: Proportional to connection count

Core building blocks of the knowledge graph.
"""

METRIC_CONNECTIONS = """
**Connections** — Graph edges.

- **What**: Hebbian links between concepts
- **Formation**: Created when concepts co-activate
- **Strength**: Weight (0-1) from reinforcement

Dense connections = integrated knowledge.
"""

METRIC_AVG_WEIGHT = """
**Average Weight** — Mean connection strength.

- **Range**: 0.0 to 1.0
- **High (>0.5)**: Strong, frequently reinforced connections
- **Low (<0.2)**: Weak, rarely co-activated links

Indicates overall network integration.
"""

METRIC_EDGE_WEIGHT = """
**Edge Weight** — Connection strength.

- **Range**: 0.0 to 1.0
- **Growth**: Increases with each co-activation
- **Decay**: May decrease without reinforcement (optional)

Higher weight = more reliable association.
"""

METRIC_COACTIVATIONS = """
**Co-activations** — Joint retrievals.

- **What**: Times two concepts were retrieved together
- **Formula**: Count of tasks where both concepts helped
- **Correlation**: Higher count → higher weight

Raw count underlying the weight calculation.
"""
