## Installation

### Setup Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
# 1. Setup environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run a quick simulation
cd src
python3 -m simulation

# OR use the CLI
python3 main.py --mode proactive --steps 30
```

## Usage

### Run Simulation (CLI)

```bash
# Single proactive simulation
python3 main.py --mode proactive --steps 30

# Single reactive simulation
python3 main.py --mode reactive --steps 30

# Comparative study (multiple runs)
python3 main.py --compare --runs 5 --steps 30

# Custom options
python3 main.py --mode proactive --steps 20 --initial-state Frustrated --no-noise
```

Results are saved to `data/simulation_logs/` as JSON files with complete state history.

### Launch Web Visualization (Optional)

For real-time human-robot interaction:

```bash
# Using the provided script
./start_canvas.sh

# Or manually
python api/server.py
```

Then open http://localhost:8000 in your browser.

## Logging & Analysis

All simulation runs produce comprehensive JSON logs:

- Timestep-by-timestep state history
- Patient true states and observations
- Robot beliefs (HMM distributions) and actions
- Canvas states (coverage, strokes, colors)
- Engagement metrics and idle duration
- Belief entropy for uncertainty tracking

Example log location: `data/simulation_logs/proactive_20251105_123456.json`

## References

- CoFRIDA: Self-Supervised Fine-Tuning for Human-Robot Co-Painting
  - Paper: https://pschaldenbrand.github.io/cofrida/
  - GitHub: https://github.com/cmubig/Frida
