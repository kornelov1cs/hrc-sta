# Therapeutic Co-Painting HRC Simulation

A simulation of human-robot collaborative therapeutic painting, comparing proactive vs reactive robot behavior modes.

## Project Overview

This simulation implements a sense-think-act loop for a therapeutic painting scenario where a patient and robot collaborate to create artwork reflecting the patient's emotional state. The robot can operate in two modes:

- **Proactive**: Robot initiates painting, suggests colors/shapes unprompted
- **Reactive**: Robot waits for patient direction, responds to patient actions

## Research Question

Does a proactive robot collaborator improve patient engagement compared to a reactive collaborator?

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

# 3. Run a quick test
python3 main.py --mode proactive --steps 20

# 4. Launch web interface
streamlit run visualization/app.py
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

### Launch Web Interface
```bash
streamlit run visualization/app.py
```

The web interface provides:
- Interactive simulation configuration
- Real-time visualization of belief distributions
- Canvas display with patient and robot strokes
- Comparative analysis of proactive vs reactive modes
- Downloadable results

## Project Structure

```
therapeutic_painting_hrc/
├── src/                        # Core simulation components
│   ├── environment.py          # Canvas and therapy room state
│   ├── patient_simulator.py    # Patient state machine and behavior
│   ├── intent_recognition.py   # HMM for patient intent inference
│   ├── robot_controller.py     # BDI architecture + MDP decision-making
│   ├── robot_actuator.py       # Robot action execution
│   ├── simulation.py           # Main sense-think-act loop
│   └── utils.py                # Helper functions and constants
├── visualization/              # Web interface and plotting
│   ├── app.py                  # Streamlit web interface
│   ├── plotting.py             # Matplotlib visualizations
│   └── components.py           # Reusable UI components
├── data/simulation_logs/       # Simulation run data
├── tests/                      # Unit tests
├── docs/                       # Reflection document
└── main.py                     # CLI entry point
```

## Technical Approach

### Sense Component
- Patient state observation (Drawing, Paused, Observing, Idle, etc.)
- Canvas state tracking (stroke count, coverage, colors used)
- Noise/uncertainty modeling

### Think Component
- **HMM**: Infers patient intent from observations
  - States: Engaged, NeedsSupport, Hesitant, Satisfied, Frustrated
  - Forward algorithm for belief updates
- **BDI Architecture**: Robot reasoning framework
  - Beliefs: Patient state distribution, canvas state
  - Desires: Increase engagement, reduce stagnation, create harmonious art
  - Intentions: Planned action sequences
- **MDP**: Decision-making for action selection
  - Different policies for proactive vs reactive modes

### Act Component
- Robot painting actions (strokes, color/shape suggestions)
- Turn-taking management
- Timing and pacing control

## Evaluation Metrics

**Objective Measures**:
- Total drawing time
- Idle time
- Pen-on-paper time
- Turn-taking smoothness
- Number of collaborative exchanges

**Simulated Subjective Measures**:
- Engagement score
- Collaboration quality
- Stagnation moments

## References

Based on CoFRIDA: Self-Supervised Fine-Tuning for Human-Robot Co-Painting
- Paper: https://pschaldenbrand.github.io/cofrida/
- GitHub: https://github.com/cmubig/Frida

## Authors

HRC Project Team - University of Tartu
