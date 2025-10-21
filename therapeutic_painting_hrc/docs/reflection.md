# Therapeutic Co-Painting HRC Simulation: Reflection Document

**Course:** Human-Robot Collaboration
**Project:** Scenario Simulation Assignment
**Date:** October 2025

---

## 1. Scenario Choice & Realism

### Scenario Selection

We selected the **therapeutic collaborative painting scenario** for this simulation, where a patient and robot work together to create artwork reflecting the patient's emotional state. This scenario is inspired by CoFRIDA (Self-Supervised Fine-Tuning for Human-Robot Co-Painting), a cutting-edge system developed at Carnegie Mellon University for human-robot artistic collaboration.

### Mapping to Real-World Healthcare Needs

This scenario addresses several critical healthcare applications:

**Mental Health and Art Therapy:**
Art therapy is an evidence-based therapeutic intervention used in mental health treatment. Research shows that creative expression through art can help patients process emotions, reduce anxiety, and improve overall well-being. Our scenario simulates a robot assistant that could support art therapists by:
- Reducing patient hesitation and stagnation during creative blocks
- Providing consistent, non-judgmental collaboration
- Adapting its behavior based on patient engagement levels

**Patient Engagement:**
One of the primary challenges in therapeutic interventions is maintaining patient engagement. Our simulation directly tests whether proactive robot behavior (taking initiative, suggesting elements) improves engagement compared to reactive behavior (waiting for patient direction). This has practical implications for:
- Therapy session effectiveness
- Patient motivation and compliance
- Therapeutic alliance formation

**Assistive Technology for Cognitive Rehabilitation:**
Beyond mental health, collaborative art creation can serve as cognitive rehabilitation for patients recovering from stroke, traumatic brain injury, or dealing with neurodegenerative conditions. The robot's ability to provide structure and support while respecting patient autonomy is crucial for rehabilitation settings.

### Realism and Limitations

Our simulation captures the **core dynamics** of human-robot collaborative painting:
- Turn-taking and shared control
- Intent recognition under uncertainty
- Adaptive robot behavior based on patient state
- Collaborative goal achievement (creating artwork together)

However, we acknowledge several simplifications:
- **Discrete states:** Real patient emotions exist on a continuum, not discrete categories
- **Simplified sensing:** Real systems would use computer vision, physiological sensors, and multimodal input
- **No actual painting:** We simulate strokes as data points rather than generating actual images
- **Perfect motor control:** Real robots face physical constraints and noise in action execution

Despite these simplifications, the simulation provides valid insights into the behavioral dynamics and collaboration patterns that would occur in a real therapeutic painting scenario.

---

## 2. Technical Implementation

### Sense Component

The **sensing module** simulates observation of patient behavior:

**Observable Behaviors:**
- Drawing, Paused, Observing, Idle
- LongStroke, ShortStroke

**Hidden States (Ground Truth):**
- Engaged, NeedsSupport, Hesitant, Satisfied, Frustrated

**Noise Modeling:**
We implement sensor uncertainty by adding noise with probability 0.1, where observations can be randomly corrupted. This simulates:
- Computer vision errors in detecting patient actions
- Ambiguity in behavioral interpretation
- Temporal misalignment in sensing

The `PatientSimulator` class maintains the true hidden state and generates observations probabilistically using emission probabilities P(observation|state), creating realistic **partial observability**.

### Think Component

The robot's reasoning combines three key approaches:

#### 2.1 Hidden Markov Model (HMM) for Intent Recognition

The HMM infers patient intent from noisy observations:

**Forward Algorithm Implementation:**
```
belief(s') = α * P(obs|s') * Σ_s P(s'|s) * belief(s)
```

- **Transition Matrix (5x5):** Encodes how patient states evolve
- **Emission Matrix (5x6):** Maps states to observable behaviors
- **Belief Update:** Real-time inference using forward algorithm
- **Confidence Tracking:** Monitors certainty in state estimation

The HMM successfully handles partial observability by maintaining a probability distribution over all possible patient states rather than committing to a single hypothesis.

#### 2.2 BDI (Belief-Desire-Intention) Architecture

The robot controller uses BDI for high-level reasoning:

**Beliefs:**
- Patient state distribution (from HMM)
- Canvas state (coverage, stroke counts, colors)
- Interaction history (idle duration, turn-taking)
- Confidence in state inference

**Desires (Proactive Mode):**
- Increase engagement (priority: 0.9)
- Reduce stagnation (priority: 0.95)
- Create collaborative art (priority: 0.7)
- Provide structure (priority: 0.8)

**Desires (Reactive Mode):**
- Increase engagement (priority: 0.85)
- Respect autonomy (priority: 0.95)
- Create collaborative art (priority: 0.75)
- Respond to patient (priority: 0.9)

**Intentions:**
Action sequences generated through deliberation and planning, executed via the act component.

#### 2.3 MDP-Based Decision Making

We formulate action selection as an MDP:

**State Space:**
- Patient state (5 possibilities)
- Canvas coverage (empty/partial/full)
- Idle duration (none/short/long)
- Patient activity (active/inactive)

**Action Space (Proactive):**
- InitiatePaint, SuggestColor, SuggestShape
- ContinuePatient, Wait, Observe

**Action Space (Reactive):**
- RespondToPrompt, ContinuePatient
- SuggestColor (only when very stuck), Wait, Observe

**Policy Implementation:**
We use **rule-based policies** tailored to each mode rather than value iteration, as the focus is on demonstrating behavioral differences rather than optimal control. The policies encode therapeutic principles:
- Proactive: Takes initiative, especially when patient is hesitant or frustrated
- Reactive: Waits for patient signals, prioritizes autonomy

### Act Component

Robot actions are executed through the `TherapyEnvironment`:

**Painting Actions:**
- Generate stroke parameters (position, color, shape, size)
- Add strokes to canvas with agent attribution
- Update environment state

**Non-Painting Actions:**
- Suggestions (verbal cues, simulated)
- Observing (passive monitoring)
- Waiting (respecting patient space)

Patient actions are simulated based on their observation, creating realistic interaction dynamics.

### Integration: Sense-Think-Act Loop

The main simulation implements a clean sense-think-act cycle:

```
For each timestep:
  1. SENSE: Observe patient behavior (with noise)
  2. THINK:
     a. Update HMM beliefs
     b. Update robot BDI beliefs
     c. Deliberate on desires
     d. Plan actions using MDP policy
  3. ACT:
     a. Execute robot action
     b. Simulate patient action
     c. Update environment
  4. LOG: Record all states and actions
  5. UPDATE: Transition patient state based on robot action
```

This architecture ensures clear separation of concerns while enabling complex emergent behavior.

---

## 3. User Input & Robot Sensing

### Patient State Modeling

The patient is modeled as a **partially observable stochastic process**:

**State Transitions:**
Patient states evolve based on:
- Baseline transition probabilities (Markov chain)
- Robot actions (modify transition probabilities)
- Canvas state (e.g., high coverage increases satisfaction)

For example, when the patient is hesitant and the robot takes a proactive action (InitiatePaint), the transition probabilities are adjusted:
- P(Engaged) increases by 50%
- P(Hesitant) decreases by 40%

This creates realistic **robot influence** on patient state.

### Uncertainty and Incomplete Knowledge

We simulate real-world uncertainty through:

**1. Sensor Noise:**
- 10% probability of incorrect observation
- Simulates vision system errors and behavioral ambiguity

**2. Partial Observability:**
- True patient state is hidden
- Robot only sees observable behaviors
- Must infer intent probabilistically

**3. State Transition Randomness:**
- Patient doesn't always respond predictably to robot actions
- Stochastic transitions reflect human variability

**4. Delayed Effects:**
- Robot actions affect state transitions, not immediate state
- Reflects realistic lag in therapeutic response

### Validation Through Metrics

The simulation tracks metrics that validate realistic behavior:
- **Belief Entropy:** High entropy indicates uncertainty
- **Confidence Levels:** Average robot confidence is ~0.40-0.50, showing realistic uncertainty
- **State Misalignment:** Robot's inferred state often differs from true state, especially early in sessions

---

## 4. Ethical & Practical Considerations

### Patient Autonomy

**Primary Concern:** Does the robot respect patient agency in creative expression?

**Proactive Mode Risks:**
- Over-directing the creative process
- Undermining patient's sense of ownership
- Causing frustration if robot is too pushy

**Reactive Mode Benefits:**
- Prioritizes patient initiative (desire: respect_autonomy, priority 0.95)
- Only intervenes when patient signals need for help
- Maintains patient as primary creative agent

**Design Decision:** Our BDI architecture explicitly models "respect_autonomy" as a high-priority desire in reactive mode, ensuring the robot doesn't dominate the collaboration.

### Privacy and Emotional Expression

**Concern:** Artwork reflects patient's emotional state, which is sensitive information.

**Considerations:**
- Canvas content could reveal private emotional struggles
- Observation and analysis of behavior raises privacy questions
- Data storage and sharing protocols must protect patient confidentiality

**Real-World Requirements:**
- Informed consent for robot-assisted therapy
- Data encryption and anonymization
- Clear policies on who can access therapy session data
- Patient right to delete or withhold data

### Safety

**Physical Safety:**
In a real implementation with a physical robot:
- Robot must operate in safe workspace
- Collision avoidance when patient moves
- Emergency stop mechanisms
- Soft materials and force-limited actuators

**Psychological Safety:**
- Robot must not induce anxiety or frustration
- Behavior should be predictable and transparent
- Option for patient to pause or end session
- Human therapist oversight recommended

### Therapeutic Value vs. Intrusion

**Key Question:** When is proactive behavior helpful vs. intrusive?

**Our Findings Suggest:**
- Proactive behavior may help when patient is hesitant or stuck
- But can frustrate already-engaged patients
- Context-awareness is crucial

**Ethical Implication:** Robot should adapt its proactivity level based on patient preference and state, not follow a one-size-fits-all approach. Future work could allow patients to adjust robot behavior style.

### Bias and Fairness

**Potential Biases:**
- HMM trained on limited patient behaviors may not generalize
- Cultural differences in emotional expression
- Artist vs. non-artist patient differences

**Mitigation:**
- Diverse patient simulation scenarios
- Customizable models per patient population
- Regular human therapist oversight

---

## 5. Results & Discussion

### Comparative Analysis: Proactive vs Reactive

We ran multiple simulations comparing the two modes. Sample results from 20-step simulations:

**Proactive Mode:**
- Average Engagement: 0.60
- Total Strokes: 14 (Patient: 8, Robot: 6)
- Max Idle Duration: 0 steps
- Turn-Taking: 40% smooth alternation
- Robot Confidence: 0.40

**Reactive Mode:**
- Average Engagement: 0.75
- Total Strokes: 26 (Patient: 10, Robot: 16)
- Max Idle Duration: 0 steps
- Turn-Taking: 55% smooth alternation
- Robot Confidence: 0.46

**Interpretation:**
In these runs, the reactive mode achieved **higher engagement** and **more collaborative output**. This suggests that respecting patient autonomy and responding to their initiative may be more effective than proactive suggestions.

However, this finding should be interpreted cautiously:
- Results vary based on initial patient state and random seed
- Longer simulations needed to assess sustained engagement
- Real patient preferences may differ significantly

### Key Insights

**1. HMM Belief Tracking Works:**
The HMM successfully infers patient state with reasonable accuracy (40-50% confidence), demonstrating that probabilistic intent recognition is feasible even with noisy observations.

**2. Behavioral Differentiation:**
Proactive and reactive modes produce clearly different behavior:
- Proactive: More InitiatePaint, SuggestColor actions
- Reactive: More Wait, ContinuePatient actions

**3. Turn-Taking Emerges:**
Even without explicit turn-taking rules, the simulation shows realistic alternation between patient and robot actions, with reactive mode achieving smoother turn-taking.

**4. Adaptation to Patient State:**
Both modes successfully adapt behavior based on inferred patient state, demonstrating that BDI + MDP provides effective high-level reasoning.

### Limitations

**1. Simplified Patient Model:**
Real patients have:
- Complex emotional states beyond 5 categories
- Long-term goals and preferences
- Learning and memory of past interactions
- Individual differences in creative style

**2. No Visual Content:**
Our simulation tracks strokes as data points but doesn't generate actual images. Real systems must reason about:
- Visual composition and aesthetics
- Color harmony and contrast
- Symbolic meaning of shapes and colors

**3. No Haptic Interaction:**
Physical co-painting involves:
- Sharing painting tools
- Spatial coordination
- Tactile feedback

**4. Single Session:**
Therapeutic relationships develop over multiple sessions. Our simulation doesn't model:
- Patient-robot relationship building
- Learning patient preferences over time
- Progress tracking across sessions

**5. No Human Therapist:**
Real art therapy involves a trained therapist who:
- Guides therapeutic goals
- Interprets artwork symbolism
- Provides emotional support
The robot should augment, not replace, human therapists.

---

## 6. Conclusion

This simulation successfully demonstrates the **sense-think-act loop** for therapeutic collaborative painting. We implemented:

✅ **Sense:** Noisy observation of patient behavior
✅ **Think:** HMM intent recognition + BDI reasoning + MDP decision-making
✅ **Act:** Context-appropriate robot actions
✅ **Adaptation:** Robot behavior adjusts based on patient state
✅ **Comparison:** Clear behavioral differences between proactive and reactive modes

The simulation provides valuable insights into human-robot collaboration dynamics and raises important questions about autonomy, engagement, and therapeutic value. While simplified, it captures core challenges of real-world healthcare robotics:
- Partial observability and uncertainty
- Balancing assistance with autonomy
- Adapting to human state and preferences
- Safety and ethical considerations

### Future Work

To move toward real-world deployment:
1. **User Studies:** Test with actual patients to validate engagement hypotheses
2. **Visual Generation:** Integrate image generation (e.g., using CoFRIDA's methods)
3. **Physical Robot:** Implement on robotic arm with painting capabilities
4. **Therapist Interface:** Allow therapists to monitor and guide robot behavior
5. **Personalization:** Learn individual patient preferences and creative styles
6. **Multi-Session:** Track progress and relationship development over time

This simulation provides a strong computational foundation for future research in therapeutic human-robot collaboration.

---

## References

1. Schaldenbrand, P., Parmar, G., Zhu, J.Y., McCann, J., & Oh, J. (2024). CoFRIDA: Self-Supervised Fine-Tuning for Human-Robot Co-Painting. *IEEE International Conference on Robotics and Automation (ICRA)*.

2. Cooney, M., & Berck, P. (2019). Designing a robot which paints with a human: visual metaphors to convey contingency and artistry. *ICRA-X Robots Art Program*.

3. Lecture Materials: Human-Robot Collaboration Course, University of Tartu, 2025.

---

**Word Count:** ~2,400 words (approximately 8 pages single-spaced, 4 pages double-spaced in Arial 11pt)
