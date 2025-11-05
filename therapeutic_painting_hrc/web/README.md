# Therapeutic Painting - HRC Web Visualization

A simplified web interface for demonstrating human-robot collaboration in therapeutic painting. This visualization shows the SENSE-THINK-ACT loop with HMM intent recognition, BDI architecture, and MDP decision-making.

## Purpose

This interface provides a "simple but compelling visualization" (per assignment criteria) that demonstrates:
- **SENSE**: HMM-based patient state inference from drawing behavior
- **THINK**: BDI architecture selecting actions via MDP policy
- **ACT**: Robot executing collaborative painting actions

## Features

### Drawing Tools (Simplified)
- **Single brush type**: Pencil for freehand drawing
- **6 therapeutic colors**: Red (energizing), Blue (calming), Yellow (uplifting), Green (balancing), Purple (creative), Orange (warm)
- **Adjustable brush size**: 10-50 pixels
- **2 basic shapes**: Circle and square for quick composition

### HRC System Visualization
- **Real-time belief state**: Visual display of HMM probability distribution over patient states
- **BDI decision process**: Shows active desires and selected intentions
- **Robot actions**: Displays current robot action and reasoning
- **Canvas statistics**: Tracks patient vs robot contributions
- **Activity log**: Records major events and state changes

## Installation & Running

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the application** using the provided script:
   ```bash
   ./start_canvas.sh
   ```

   Or manually:
   ```bash
   python api/server.py
   ```

3. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

## Usage

1. **Draw on the canvas** using the provided colors and tools
2. **Observe the robot status panel** on the right to see:
   - How the HMM updates beliefs about your emotional state
   - What desires the BDI system activates
   - Which action the MDP policy selects
3. **Watch the robot respond** with collaborative painting actions
4. **Optional**: Use the text prompt to request specific robot actions

## Architecture

```
Patient Drawing → HMM (SENSE) → BDI + MDP (THINK) → Robot Action (ACT)
                     ↓                  ↓                    ↓
                Belief Update    Desire Selection     Canvas Update
```

### Key Components

- **HMM Intent Recognition** (`src/intent_recognition.py`): Forward algorithm for belief updates
- **BDI Controller** (`src/robot_controller.py`): Belief-Desire-Intention architecture
- **MDP Policy** (`src/robot_controller.py`): Action selection based on state and mode
- **WebSocket Communication** (`api/server.py`): Real-time updates between frontend and backend

## Design Rationale

This interface is intentionally simplified to focus on demonstrating the HRC concepts rather than providing a feature-rich painting application. The emphasis is on making the robot's intelligence visible through:
- Clear labeling of SENSE-THINK-ACT stages
- Real-time visualization of belief distributions
- Explanatory text connecting features to course concepts (HMM, BDI, MDP)

## File Structure

```
web/
├── index.html              # Main interface (simplified, ~180 lines)
├── css/
│   └── styles.css          # Styling
└── js/
    ├── canvas.js           # Fabric.js canvas management
    ├── tools.js            # Tool selection and configuration
    └── robot.js            # WebSocket communication with backend
```

## Notes

- Removed features from earlier versions: multiple brush types, undo/redo, layer controls
- Focus shifted to HRC demonstration over painting features
- Aligns with assignment requirement for "simple but compelling visualization"
