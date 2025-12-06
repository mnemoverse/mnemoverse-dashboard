"""
Metric Definitions - Short Help Texts for Dashboard.

Compact explanations for the ? help buttons.
Keep each under 2-3 sentences for clean UX.
"""

# ==============================================================================
# Overview Page
# ==============================================================================

HELP_STATE_ATOMS = "Learned concepts from successful solutions. Higher = more knowledge."
HELP_PROCESS_ATOMS = "All solution attempts (successful + failed). Raw memory size."
HELP_HEBBIAN_EDGES = "Links between concepts used together. Shows knowledge structure."
HELP_FEEDBACK_EVENTS = "Positive/negative signals from task outcomes. Drives learning."

# ==============================================================================
# Learning Curve Page
# ==============================================================================

HELP_TASKS_SOLVED = "Total task attempts with valid task_id."
HELP_CORRECT = "Tasks where model produced correct output."
HELP_ACCURACY = "Success rate: correct / total × 100%"
HELP_MEMORY_SIZE = "Total atoms stored. X-axis of learning curve."

HELP_BASELINE = "Performance WITHOUT memory. Control group (~26% for ARC)."
HELP_MEMORY_MODE = "Performance WITH KDMemory. Should exceed baseline."
HELP_DELTA = "Memory improvement: memory_acc - baseline_acc. Positive = memory helps."

HELP_LEARNING_CURVE = "Key hypothesis: accuracy should increase as memory grows."

# ==============================================================================
# Memory State Page
# ==============================================================================

HELP_ADALINE_UPDATES = "Weight adjustments from feedback. More = more learning."
HELP_AVG_ERROR = "Prediction accuracy. Lower = better predictions."
HELP_LEARNING_RATE = "Update step size (η). Controls learning speed."

HELP_UTILITY = "Predicted usefulness (0-1). High = likely to help solve tasks."
HELP_USE_COUNT = "Times this concept was retrieved for tasks."
HELP_FEEDBACK_POS = "Positive feedback count. Concept helped solve task."
HELP_FEEDBACK_NEG = "Negative feedback count. Concept didn't help."

# ==============================================================================
# Knowledge Graph Page
# ==============================================================================

HELP_CONCEPTS = "Unique learned patterns. Nodes in the graph."
HELP_CONNECTIONS = "Hebbian links between concepts. Edges in the graph."
HELP_AVG_WEIGHT = "Mean connection strength (0-1). Higher = stronger associations."

HELP_EDGE_WEIGHT = "Connection strength. Increases with co-activation."
HELP_COACTIVATIONS = "Times two concepts were retrieved together for same task."

HELP_WEIGHT_FILTER = "Hide weak connections. Focus on strong relationships."

# ==============================================================================
# Section Headers
# ==============================================================================

HELP_OVERVIEW = "Quick stats showing current memory state and last experiment."
HELP_LEARNING_CURVE_PAGE = "Main analysis: does accuracy improve as memory grows?"
HELP_MEMORY_STATE_PAGE = "Adaline perceptron state and concept utilities."
HELP_KNOWLEDGE_GRAPH_PAGE = "Hebbian network: concepts that fire together, wire together."
HELP_ADMIN_PAGE = "Schema management and database diagnostics."
HELP_TOOLS_PAGE = "Links to external observability tools."


# ==============================================================================
# Legacy (for backward compatibility)
# ==============================================================================

# Keep old names as aliases
METRIC_STATE_ATOMS = HELP_STATE_ATOMS
METRIC_PROCESS_ATOMS = HELP_PROCESS_ATOMS
METRIC_HEBBIAN_EDGES = HELP_HEBBIAN_EDGES
METRIC_FEEDBACK_EVENTS = HELP_FEEDBACK_EVENTS
METRIC_TASKS_SOLVED = HELP_TASKS_SOLVED
METRIC_CORRECT = HELP_CORRECT
METRIC_ACCURACY = HELP_ACCURACY
METRIC_MEMORY_SIZE = HELP_MEMORY_SIZE
METRIC_BASELINE = HELP_BASELINE
METRIC_MEMORY_MODE = HELP_MEMORY_MODE
METRIC_DELTA = HELP_DELTA
METRIC_ADALINE_UPDATES = HELP_ADALINE_UPDATES
METRIC_AVG_ERROR = HELP_AVG_ERROR
METRIC_LEARNING_RATE = HELP_LEARNING_RATE
METRIC_UTILITY = HELP_UTILITY
METRIC_USE_COUNT = HELP_USE_COUNT
METRIC_CONCEPTS = HELP_CONCEPTS
METRIC_CONNECTIONS = HELP_CONNECTIONS
METRIC_AVG_WEIGHT = HELP_AVG_WEIGHT
METRIC_EDGE_WEIGHT = HELP_EDGE_WEIGHT
METRIC_COACTIVATIONS = HELP_COACTIVATIONS
