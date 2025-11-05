# Therapeutic Co-Painting HRC Simulation

A human-robot collaborative therapeutic painting system demonstrating SENSE-THINK-ACT architecture with HMM intent recognition, BDI reasoning, and MDP decision-making.

## Project Overview

This project implements a complete HRC system for a therapeutic painting scenario where a patient and robot collaborate to create artwork. The robot observes patient behavior, infers emotional state, and adapts its actions to provide appropriate support.

### Robot Behavior Modes

- **Proactive**: Robot initiates painting, suggests colors/shapes, takes initiative
- **Reactive**: Robot waits for patient direction, responds to patient needs

### Assignment Compliance

This project fulfills the HRC course requirements:
- ✅ **Intent Recognition**: Hidden Markov Model (HMM) with forward algorithm
- ✅ **Decision Layer**: Belief-Desire-Intention (BDI) architecture + Markov Decision Process (MDP)
- ✅ **SENSE-THINK-ACT Loop**: Complete implementation with logging
- ✅ **Scenario Documentation**: Therapeutic painting with clear user states and robot tasks
- ✅ **Reflection Document**: Comprehensive discussion in `docs/reflection.md`
- ✅ **Visualization**: Simple but compelling web interface showing HRC concepts

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

The web interface demonstrates:
- **SENSE**: Real-time HMM belief state visualization
- **THINK**: BDI desires and MDP action selection
- **ACT**: Robot painting actions on shared canvas
- **Statistics**: Canvas coverage, stroke counts, activity log

## Project Structure

```
therapeutic_painting_hrc/
├── src/                         # Core simulation (SENSE-THINK-ACT loop)
│   ├── environment.py           # Canvas and therapy room state
│   ├── patient_simulator.py     # Patient state machine and behavior
│   ├── intent_recognition.py    # HMM for patient intent inference
│   ├── robot_controller.py      # BDI architecture + MDP policies
│   ├── intelligent_painter.py   # Contextual stroke generation
│   ├── path_generator.py        # Stroke path planning
│   ├── stroke_analyzer.py       # Canvas analysis
│   ├── simulation.py            # Main simulation loop
│   └── utils.py                 # Enums and helper functions
├── api/                         # FastAPI server for web interface
│   ├── server.py                # REST + WebSocket endpoints
│   └── models.py                # Pydantic schemas
├── web/                         # Simplified web visualization
│   ├── index.html               # Main interface (~180 lines)
│   ├── css/styles.css           # Styling
│   └── js/                      # Canvas, tools, robot communication
├── data/simulation_logs/        # JSON logs with complete state history
├── docs/                        # Reflection document
│   └── reflection.md            # 8-page comprehensive reflection
├── course-programming/          # Reference materials from course
├── main.py                      # CLI entry point
└── start_canvas.sh              # Quick-start script for web interface
```

## Technical Approach

### SENSE Component
- **Patient Observation**: Tracks drawing activity, idle duration, stroke patterns
- **Canvas State**: Monitors coverage, stroke count, color usage
- **Noise Modeling**: Simulates sensor uncertainty for realism

### THINK Component

#### 1. Hidden Markov Model (HMM)
- **States**: Engaged, NeedsSupport, Hesitant, Satisfied, Frustrated
- **Observations**: Drawing, Paused, Observing, Idle, LongStroke, ShortStroke
- **Algorithm**: Forward algorithm for belief distribution updates
- **Implementation**: `src/intent_recognition.py`

#### 2. BDI Architecture
- **Beliefs**: Patient state distribution (from HMM), canvas state, idle duration
- **Desires**:
  - Proactive: Increase engagement, reduce stagnation, provide structure
  - Reactive: Respect autonomy, respond to prompts, support when needed
- **Intentions**: Action sequences selected by MDP policy
- **Implementation**: `src/robot_controller.py`

#### 3. Markov Decision Process (MDP)
- **State Space**: (patient_state, canvas_coverage, idle_duration, patient_activity)
- **Actions**: InitiatePaint, SuggestColor, SuggestShape, ContinuePatient, Wait, Observe, RespondToPrompt
- **Reward Function**: Balances engagement, autonomy, and therapeutic goals
- **Policies**: Distinct proactive vs reactive strategies
- **Implementation**: `src/robot_controller.py` (TherapeuticPaintingMDP class)

### ACT Component
- **Robot Painting**: Generates contextual strokes using `intelligent_painter.py`
- **Turn-Taking**: Manages patient-robot interaction timing
- **Action Execution**: Updates canvas state and triggers next SENSE cycle

## Logging & Analysis

All simulation runs produce comprehensive JSON logs:
- Timestep-by-timestep state history
- Patient true states and observations
- Robot beliefs (HMM distributions) and actions
- Canvas states (coverage, strokes, colors)
- Engagement metrics and idle duration
- Belief entropy for uncertainty tracking

Example log location: `data/simulation_logs/proactive_20251105_123456.json`

## Evaluation Metrics

**Objective Measures**:
- Canvas coverage percentage
- Patient vs robot stroke ratio
- Idle time duration
- Turn-taking smoothness
- Belief confidence (entropy)

**Simulated Subjective Measures**:
- Engagement score (derived from patient state)
- Collaboration quality
- Stagnation prevention

## Design Rationale

### Why Therapeutic Painting?
- Natural collaborative activity requiring shared intent
- Observable behavioral signals (stroke patterns, pauses)
- Clear therapeutic goals (engagement, self-expression)
- Relevant to real healthcare robotics applications

### Parameter Justification
All HMM transition/emission probabilities and MDP reward weights are documented in code comments (per assignment criteria). See:
- `src/intent_recognition.py` lines 44-127 (HMM matrices)
- `src/robot_controller.py` lines 358-384 (MDP rewards)

## References

**Inspiration**:
- CoFRIDA: Self-Supervised Fine-Tuning for Human-Robot Co-Painting
  - Paper: https://pschaldenbrand.github.io/cofrida/
  - GitHub: https://github.com/cmubig/Frida

**Course Materials**:
- See `course-programming/` for BDI, Bayesian Networks, and Intent Recognition exercises

## Documentation

- **Reflection Document**: `docs/reflection.md` (comprehensive 8-page analysis)
- **Scenario Description**: `docs/scenario-description.md` (assignment criteria)
- **Web Interface Guide**: `web/README.md`

## Authors

HRC Course Project - University of Tartu, 2025
