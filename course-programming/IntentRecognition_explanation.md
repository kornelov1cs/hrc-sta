# Intent Recognition Notebook Explanation

## Overview of `IntentRecognition.ipynb`

This notebook demonstrates **intent recognition for a 2-DOF (two degree-of-freedom) robotic arm**. It's a machine learning exercise that predicts where a robot arm is trying to reach based on observing its movement trajectory.

---

## What It Does:

### 1. **Robot Simulation** (Cells 1-4)

- Implements **forward kinematics** for a 2-link planar robot arm
- The robot has two joints (θ₁, θ₂) and two links of length 1.0
- Generates trajectories from a starting position to different target positions
- Creates both **full trajectories** (complete movements) and **partial trajectories** (movements stopped halfway)

### 2. **Dataset Creation** (Cells 5-6)

Creates synthetic data with:

- **Two target positions** defined in joint space:
  - Target 1: (60°, -30°)
  - Target 2: (30°, 45°)
- **200 trajectories per target** (20 time steps each)
- Each target gets both full and partial trajectories
- Adds **noise** to simulate real-world sensor data
- Results in **12,000 data points** total

### 3. **Visualization** (Cell 7)

- Animates the robot arm movement
- Shows targets as colored dots (red and green)
- Displays the two-link arm moving through space

### 4. **Machine Learning Classification** (Cells 8-9)

- **Feature extraction**: Uses final position (x, y), total displacement (dx, dy), and whether trajectory is partial
- **Model**: Decision Tree Classifier
- **Goal**: Predict which target the robot is moving toward
- **Results**:
  - Overall accuracy: **80.6%**
  - Full trajectories: **86.5%** accuracy
  - Partial trajectories: **73.2%** accuracy (harder because movement is incomplete)

### 5. **Suggested Improvements** (Cell 10)

The notebook suggests exploring:

- Effect of trajectory partiality on accuracy
- Different ML models (SVM, Random Forest, Neural Networks)
- Better feature engineering

---

## Real-World Application:

This type of system is useful for **Human-Robot Collaboration**:

- Predicting human intent from partial movements
- Anticipating where someone is reaching
- Enabling robots to assist proactively (e.g., handing tools before being asked)

**The key insight**: Even with incomplete (partial) trajectories, you can predict the final goal with decent accuracy!
