# Sense-think-act: Design and Implement an HRC Scenario

**Due:** 7 Nov by 23:59
**Points:** 10
**Submission:** Text entry box or file upload

---

## Assignment Overview

Design and simulate a scenario in which a robot and a human collaborate, based on the sense-think-act loop that demonstrates the key steps in a simplified or toy manner, but with a clear mapping of real-world issues in healthcare (safety, timeliness, comfort, ethical considerations, etc.).

The focus here is on developing the **think-and-act component** based on the methods you've learned in the course. You can simulate the sense component (however, you can also use tools like Mediapipe for hand or gaze tracking).

---

## Possible Scenarios

Choose one or propose your own variant (for CBL-Students: use the theme mobility):

### 1. Robot Nurse Assistant in a Hospital Ward
A mobile robot aids nurses and doctors by fetching supplies, delivering medications, or transporting lightweight equipment. The human collaborator could be a busy nurse juggling multiple patients. The robot needs to recognize when the nurse is ready for a handover (e.g., giving or receiving supplies) vs. when the nurse is focused on other tasks.

### 2. Physical Therapy/Rehabilitation Support Robot
A robot assists a physical therapist and a patient in guided exercises (e.g., range-of-motion tasks). The therapist's or patient's intent (e.g., "NeedsSupport," "PerformingExercise," "Resting") is not always explicit. The robot can adjust resistance, hold a limb for balance, or offer encouragement/reminders.

### 3. Elderly Home-Care Robot
A companion robot in a home setting helps an elderly person with daily tasks (fetching objects, reminding about medication, checking if the person needs assistance). The robot must navigate domestic areas (kitchen, living room) while avoiding collisions and respecting user's personal space.

---

## Steps

### 1. Select and Define Your Scenario

Select one scenario from the list (or an instructor-approved variant). Clearly define:
- **Environment** (clinic, home, therapy room)
- **Human user** (patient, nurse, doctor, therapist, or elderly person)
- **Task** (delivering medication, assisting with exercises, providing telepresence, etc.)

### 2. Identify Key Elements

#### User
How will you model the human's state (intent, readiness, need for help, level of busy/fatigue)? What signals does the robot receive about the human (gestures, verbal cues, or simplified random states)?

#### Robot
Define the robot's sensors (e.g., position from odometry, overhead camera, user signals) and actuators (e.g., moving to a location, handing over an item, physically assisting the human). Decide on a simple geometry or discrete states for the robot's location (like "AtBin," "AtPatient," or a 2D coordinate). Think about how to model the beliefs, desires and intentions of the robot.

#### Behavior Design
How does the robot interpret user signals (via an HMM, discrete BN, or direct random transitions)? How does the robot decide actions (e.g., a small MDP policy, a heuristic rule, or a "toy" Q-learning approach)? Include adaptation or learning: e.g., the user's state changes over time, and the robot adapts (updates beliefs or policy).

### 3. Implement the Sense-Think-Act Loop

Implement in a (toy) simulation:
- **Environment Representation**
- **User and Robot Representation**
- **Time-Stepped Simulation Loop**
- **Stylized Visualization** (Optional but Encouraged)

### 4. Reflection & Discussion

Write a short report (2-4 pages) explaining:

- **Scenario Choice & Realism:** Why you chose this healthcare scenario, and how it maps to real-world needs (patient safety, nurse workflow, therapy exercises, medication compliance, etc.).

- **User Input & Robot Sensing:** What signals or data you modeled, how you introduced randomness or uncertainty, and how that simulates real sensor noise or incomplete knowledge of user state.

- **Ethical & Practical Considerations:** How does your design address safety or ethical concerns? Could there be privacy or autonomy issues in a real system?

---

## Deliverable

A documented Python script or notebook and a reflection document (2-4 pages, Arial 11 point): Discuss design decisions, how your system handles partial observability, noise, or unpredictability in user state, and the key trade-offs in a healthcare context.

---

## Evaluation

### Gates

| Gate | Requirement | Consequence if unmet |
|------|-------------|---------------------|
| **G1** | Submission includes (a) a runnable Python script/notebook and (b) a reflection document 2-4 pages. | Fail (G1) – rubric not applied |
| **G2** | Simulation demonstrates a full sense-think-act loop for ≥ 10 time-steps without runtime errors. | Fail (G2) |

### Rubric

#### Completeness (20%)
Does the submission clearly define the scenario, user state, robot tasks, and environment layout? Does the code simulate user changes in state, robot's decisions, and execution over multiple time steps?

#### Technical Soundness (30%)
Are the elements of intent recognition (HMM/BN) or decision-making (MDP or rule-based) reasonably implemented (even if simplified)? Are the code and logic consistent with the assignment's requirements?

#### Clarity & Organization (30%)
- Is the code well-documented, easy to follow, and does it run without errors?
- Does the reflection document provide meaningful insight into design choices and constraints?

#### Insight & Reflection (20%)
- Does the student discuss relevant (healthcare) considerations (safety, ethics, privacy)?
- Are the limitations of the toy simulation acknowledged?

#### Creativity / Realism (Bonus Points)
- Is the chosen scenario or approach novel or particularly well-aligned with actual (healthcare) workflows?
- Does the submission include a simple but compelling visualization of the scenario?

---

## Detailed Criteria & Points

### Completeness & Scenario Definition (20 pts)
- Scenario, user states, robot tasks, and environment layout all clearly described.
- Code logs state changes and robot actions every step.

### Technical Soundness (30 pts)
- Intent-recognition block (e.g., HMM, BN) implemented and produces plausible outputs.
- Decision layer (MDP, Q-learning, heuristic rules) selects actions consistent with course methods.
- Parameters or design choices briefly justified in code comments or the report.

### Code & Document Clarity (30 pts)
- Script/notebook is modular, commented, PEP-8 compliant, and runs "out of the box".
- Reflection explains design choices, constraints, and any trade-offs.
- Figures or tables (if any) have labels and captions.

### Insight & Reflection (20 pts)
- Discussion covers safety, ethics, privacy, user experience, and limitations of the toy model.
- Clear links to real (healthcare) workflows.

### Creativity (Bonus pts)
- Scenario or visualization is notably novel and well aligned with real practice.
- Contains simple but compelling visualization of the scenario.
