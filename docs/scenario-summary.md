<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# We have a project due in our HRC class. I have attached our group's research project proposal (hrc-project-proposal.pdf).

We are trying to base it off of Cofrida, which is a "CoFRIDA: Self-Supervised Fine-Tuning for Human-Robot Co-Painting". Could you summarize the paper for me? And after, I need to create a scenario simulation, which should be done in code and documentation. I have attached a file called "scenario-description.pdf" that has the guidelines on how to construct that.

How would you approach this?

For resource, here are links to the CoFrida website and github:

[https://pschaldenbrand.github.io/cofrida/](https://pschaldenbrand.github.io/cofrida/)

[https://github.com/cmubig/Frida](https://github.com/cmubig/Frida)

Now let me create a comprehensive summary document with CoFRIDA paper summary and implementation guidance:

# Summary: CoFRIDA Paper and HRC Project Approach

## Part 1: CoFRIDA Paper Summary

**CoFRIDA: Self-Supervised Fine-Tuning for Human-Robot Co-Painting** is a groundbreaking robotic painting framework developed at Carnegie Mellon University that enables true human-robot collaborative art creation. The system addresses a critical limitation in prior robot painting work: while systems like FRIDA could paint from user inputs, they excluded humans from the creative process after the initial prompt.[^1]

### Core Innovation

CoFRIDA introduces the concept of **co-painting**, which differs fundamentally from traditional image editing tasks like in-painting. In co-painting, the robot must add content that engages with existing human-created work without overwriting it, requiring preservation and enhancement of the full canvas rather than localized radical changes.[^1]

### Technical Architecture

CoFRIDA consists of three primary components:[^2][^1]

1. **Co-Painting Module**: Uses a fine-tuned Instruct-Pix2Pix model to generate pixel predictions of how the robot should complete paintings given current canvas state and text descriptions[^2][^1]
2. **FRIDA System**: A robotic painting framework using Real2Sim2Real methodology to simulate high-fidelity brush strokes and plan actions from target images[^1][^2]
3. **Self-Supervised Fine-Tuning**: A novel training procedure that encodes robotic constraints into pre-trained models[^2][^1]

### Self-Supervised Data Creation

The training data is generated automatically without human annotation. The process involves:[^1]

- Using FRIDA to simulate paintings of images from the LAION art dataset
- Creating partial paintings by selectively removing strokes (random subsets, salient regions, semantic regions, or all strokes)
- Fine-tuning Instruct-Pix2Pix to predict full paintings from partial paintings and text prompts[^1]

This approach solves two critical problems: (1) pre-trained models don't understand robot constraints, and (2) they tend to overwrite existing canvas content.[^2][^1]

### Learning Robotic Constraints

CoFRIDA successfully encodes physical constraints into the image generator. The system learns to generate images that account for:[^1]

- **Limited tools**: Large brushes mean fine details aren't achievable
- **Fixed color palettes**: Generated images use only available colors
- **Stroke limits**: Complex scenes are simplified to match robot capabilities[^1]

This isn't just style transfer—the correlation analysis shows CoFRIDA reduces semantic sim-to-real gap (∆sem = 0.052) compared to baselines (0.192-0.195), indicating it learns actual constraints rather than superficial appearance.[^1]

### Evaluation Results

In user studies with 24 participants, CoFRIDA's completed drawings were found substantially more similar to text prompts than baselines. The system achieved:[^1]

- **Better text-image alignment**: 80% of participants preferred CoFRIDA over FRIDA, 60% over untuned Instruct-Pix2Pix[^1]
- **Lower semantic sim-to-real gap**: Minimal loss of meaning between planned and executed paintings
- **Generalization**: Works with mixed media even when trained only on single-medium data[^2][^1]


### Real-World Applications

CoFRIDA enables multiple interaction patterns:[^2][^1]

- **Iterative co-painting**: Multiple turns of human-robot collaboration without overwriting
- **Mixed-media collaboration**: Robot adapts when humans use different materials (e.g., watercolors when robot has markers)
- **Never-ending canvas**: Continuous scrolling paper for unlimited collaborative drawings[^2]


### Significance for Art Therapy

The paper emphasizes strong evidence for co-creative agents in art therapy. Physical embodiment combined with collaborative creation offers particular benefits for therapeutic contexts, which directly connects to your project proposal's focus on patient engagement in mental health settings.[^3][^1]

***

## Part 2: Approach to Your HRC Scenario Simulation

Based on your project proposal, assignment requirements, and CoFRIDA's methodology, here's a comprehensive approach:[^4][^3]

### Project Context

Your group is investigating whether **proactive vs. reactive robot behavior** affects patient engagement in collaborative therapeutic painting. This builds on CoFRIDA's co-painting framework but focuses on the behavioral dynamics of collaboration rather than technical image generation.[^3]

### Scenario Design

**Environment**: Therapy room with digital/physical canvas
**Participants**: Patient (primary) and collaborative painting robot
**Task**: Create artwork reflecting patient's current emotions
**Goal**: Neither patient nor robot can achieve final product alone—robot provides structure/variation, patient provides meaning/emotion[^3]

### Implementation Strategy

#### 1. SENSE Component

**Patient State Modeling**:

```python
# Hidden states (not directly observable)
patient_states = ["Engaged", "NeedsSupport", "Hesitant", "Satisfied", "Frustrated"]

# Observable behaviors
observations = ["Drawing", "Paused", "Observing", "Idle", "LongStroke", "ShortStroke"]
```

**Canvas State Sensing**:

- Number of patient strokes
- Number of robot strokes
- Canvas coverage percentage
- Time since last activity
- Color palette usage

**Implementation**: Simulate sensor readings with controlled randomness to model uncertainty and noise.[^4]

#### 2. THINK Component

**Intent Recognition via Hidden Markov Model (HMM)**:[^4][^2]

```python
class PatientIntentHMM:
    def __init__(self):
        # Transition probabilities between hidden states
        self.transition_matrix = np.array([...])
        
        # Emission probabilities: P(observation | state)
        self.emission_matrix = np.array([...])
        
        # Current belief distribution over states
        self.belief_state = np.array([1/n_states] * n_states)
    
    def update_belief(self, observation):
        # Forward algorithm for belief update
        # P(state_t | obs_1:t)
        pass
    
    def predict_next_state(self):
        # Prediction step using transition model
        pass
```

**Decision-Making via BDI + MDP**:[^4][^2]

The robot maintains:

- **Beliefs**: Probability distribution over patient states from HMM
- **Desires**: Goals (increase engagement, reduce idle time, create harmonious artwork)
- **Intentions**: Current plan of actions

```python
class RobotBDI:
    def __init__(self, mode='proactive'):
        self.mode = mode  # 'proactive' or 'reactive'
        self.beliefs = {}
        self.desires = self._initialize_desires()
        self.intentions = []
        
    def perceive(self, patient_hmm, canvas_state):
        # Update beliefs from HMM and sensors
        self.beliefs['patient_state'] = patient_hmm.belief_state
        self.beliefs['canvas_state'] = canvas_state
        
    def deliberate(self):
        # Select which desire to pursue based on beliefs
        # Proactive: prioritize initiation and suggestion
        # Reactive: prioritize continuation and response
        pass
        
    def plan(self):
        # Generate action sequence using MDP policy or rules
        if self.mode == 'proactive':
            # Actions: InitiatePainting, SuggestColor, SuggestShape, Wait
            pass
        else:  # reactive
            # Actions: ContinuePatient, RespondToPrompt, Wait
            pass
            
    def execute(self):
        # Perform first action in intention queue
        pass
```

**MDP Formulation**:[^4][^2]

- **States**: (patient_state, canvas_coverage, idle_duration, turn_taking_state)
- **Actions**: Proactive: {InitiatePaint, SuggestColor, SuggestShape, Wait, Observe}; Reactive: {ContinueWork, RespondToPrompt, Wait, Observe}
- **Transition Model**: P(s'|s,a) based on action effects and patient response
- **Reward Function**:
    - +10 for reducing patient idle time
    - +5 for maintaining engagement
    - -5 for interrupting engaged patient
    - +15 for collaborative turn-taking
    - -10 for long periods of robot inactivity (reactive mode issue)


#### 3. ACT Component

**Robot Actions**:

```python
class RobotActuator:
    def __init__(self, canvas):
        self.canvas = canvas
        
    def paint_stroke(self, position, color, shape, size):
        # Add robot stroke to canvas
        # Record: timestamp, position, properties
        self.canvas.add_stroke('robot', position, color, shape, size)
        
    def suggest_element(self, suggestion_type, parameters):
        # Visual or verbal suggestion (simulated)
        # Log suggestion for later analysis
        pass
        
    def wait_observe(self, duration):
        # Robot observes without action
        pass
```


#### 4. Simulation Loop

```python
def run_simulation(mode='proactive', num_steps=20):
    # Initialize
    env = TherapyEnvironment()
    patient = PatientSimulator()
    robot = CollaborativeRobot(mode=mode)
    hmm = PatientIntentHMM()
    
    history = {
        'timesteps': [],
        'patient_states': [],
        'observations': [],
        'robot_beliefs': [],
        'robot_actions': [],
        'canvas_states': [],
        'engagement_scores': []
    }
    
    for t in range(num_steps):
        # === SENSE ===
        patient_action = patient.act()  # Simulate patient behavior
        observation = env.observe(patient_action)
        canvas_state = env.get_canvas_state()
        
        # === THINK ===
        hmm.update_belief(observation)
        robot.perceive(hmm, canvas_state)
        robot.deliberate()
        robot.plan()
        
        # === ACT ===
        robot_action = robot.execute()
        env.apply_robot_action(robot_action)
        
        # === LOG ===
        history['timesteps'].append(t)
        history['patient_states'].append(patient.true_state)
        history['observations'].append(observation)
        history['robot_beliefs'].append(hmm.belief_state.copy())
        history['robot_actions'].append(robot_action)
        history['canvas_states'].append(canvas_state.copy())
        history['engagement_scores'].append(patient.engagement_level)
        
        # Update patient based on robot action and environment
        patient.update(robot_action, env)
        
        # Print step summary
        print(f"Step {t}: Patient={patient.true_state}, "
              f"Obs={observation}, Robot={robot_action}")
    
    return history, env
```


### Evaluation Metrics

To match your research proposal:[^3]

**Objective Measures**:

- Time spent drawing (patient + robot)
- Idle time (periods with no activity)
- Pen-on-paper time (active painting)
- Turn-taking smoothness (transitions between patient and robot)
- Number of collaborative exchanges

**Simulated Subjective Measures**:

- Engagement score (modeled based on patient state transitions)
- Collaboration quality (based on turn-taking patterns)
- Stagnation moments (long idle periods)


### Visualization

Create compelling visualizations:[^4]

```python
import matplotlib.pyplot as plt

def visualize_simulation(history):
    fig, axes = plt.subplots(3, 2, figsize=(14, 10))
    
    # Plot 1: Patient state over time
    # Plot 2: Robot belief distribution over time (heatmap)
    # Plot 3: Canvas coverage over time
    # Plot 4: Engagement score over time
    # Plot 5: Action timeline (Gantt chart)
    # Plot 6: Final canvas visualization
    
    plt.tight_layout()
    plt.show()
```


### Reflection Document Structure

Following assignment requirements:[^4]

**1. Scenario Choice \& Realism (0.5 pages)**

- Why collaborative therapeutic painting
- Connection to real mental health applications
- How CoFRIDA's co-painting principles apply
- Benefits of physical embodiment in therapy[^1]

**2. Technical Implementation (1.5 pages)**

- HMM for intent recognition: states, observations, transition/emission probabilities
- BDI architecture for robot reasoning
- MDP formulation for decision-making in proactive vs. reactive modes
- How partial observability and uncertainty are handled

**3. User Input \& Robot Sensing (0.5 pages)**

- Simulated patient behaviors and state transitions
- Sensor noise modeling (random perturbations)
- Canvas state representation
- How this simulates real sensor limitations

**4. Ethical \& Practical Considerations (0.5 pages)**

- Patient autonomy: ensuring robot doesn't dominate creative process
- Privacy: canvas content as emotional expression
- Safety: in physical system, robot workspace constraints
- Therapeutic value: when is proactive behavior helpful vs. intrusive?
- Informed consent for therapy applications

**5. Results \& Discussion (0.5 pages)**

- Comparison of proactive vs. reactive modes
- Engagement patterns observed
- Moments of successful collaboration vs. stagnation
- How robot beliefs aligned with true patient states

**6. Limitations (0.5 pages)**

- Simplified patient model (real humans more complex)
- Discrete states vs. continuous emotions
- No actual image generation (CoFRIDA level)
- Limited turn-taking model
- Need for real user studies


### Key Design Considerations

**From CoFRIDA's Lessons**:[^1]

1. **Avoid Overwriting**: Reactive robot must build on patient work, not replace it
2. **Adapt to Medium**: Robot should handle when patient uses unexpected colors/tools
3. **Iterative Refinement**: Support multiple turns of collaboration
4. **Semantic Understanding**: Robot should understand intent, not just mimic strokes

**From Your Proposal**:[^3]

1. **Proactive Mode**: Robot can initiate to prevent stagnation, but risks overwhelming patient
2. **Reactive Mode**: Robot waits for patient, ensures patient agency, but might lead to more idle time
3. **Wizard-of-Oz Feasibility**: Your simulation provides computational model that could later be wizard-controlled

**From Assignment Requirements**:[^4]

1. **Healthcare Context**: Clear mapping to therapy workflows and patient needs
2. **Partial Observability**: HMM handles uncertainty in patient state
3. **Adaptation**: Robot updates beliefs and policy based on observations
4. **Time-Stepped**: Clean sense-think-act loop for minimum 10 steps
5. **PEP-8 Compliance**: Well-documented, modular code

### Implementation Timeline

1. **Phase 1**: Implement basic environment, patient simulator, canvas state (2-3 hours)
2. **Phase 2**: Implement HMM for intent recognition (2-3 hours)
3. **Phase 3**: Implement BDI + MDP/rule-based decision making (3-4 hours)
4. **Phase 4**: Complete sense-think-act loop and logging (2 hours)
5. **Phase 5**: Run simulations for both modes, generate visualizations (2 hours)
6. **Phase 6**: Write reflection document (3-4 hours)

**Total estimated time**: 14-18 hours

### Code Structure Template

```
therapeutic_painting_hrc/
├── environment.py          # Canvas, therapy room state
├── patient_simulator.py    # Patient state and behavior
├── intent_recognition.py   # HMM implementation
├── robot_controller.py     # BDI + MDP decision making
├── robot_actuator.py       # Action execution
├── simulation.py           # Main sense-think-act loop
├── visualization.py        # Plotting and analysis
├── main.py                 # Entry point
└── utils.py               # Helper functions
```


### Resources to Reference

1. **CoFRIDA GitHub**: https://github.com/cmubig/Frida - Study the architecture[^2]
2. **HMM Tutorial**: Implementation patterns for belief updates[^2]
3. **MDP Toolbox**: Python MDP libraries for decision-making[^2]
4. **Lecture 4 Materials**: BDI agents, Bayesian networks, HMM examples[^2]

### Success Criteria

Your simulation should demonstrate:

✅ **Completeness**: Clear scenario, state definitions, working sense-think-act loop
✅ **Technical Soundness**: HMM produces plausible beliefs, decision layer selects reasonable actions
✅ **Clarity**: Well-documented code, insightful reflection document
✅ **Insight**: Discusses safety, ethics, privacy, limitations
✅ **Creativity Bonus**: Novel visualization showing proactive vs. reactive differences

***

## Key Takeaways

**CoFRIDA's Main Contribution**: Enables true human-robot co-creation through self-supervised learning of robot constraints and co-painting that preserves human work.[^1]

**Your Project's Focus**: Tests whether proactive robot initiative improves engagement compared to reactive response in therapeutic painting contexts.[^3]

**Implementation Path**: Build a sense-think-act simulation using HMM for intent recognition and BDI+MDP for decision-making, comparing proactive vs. reactive robot behaviors across objective and subjective measures.[^3][^4]

**The Connection**: Both projects explore human-robot collaborative creativity, but CoFRIDA focuses on technical painting capabilities while your project investigates interaction dynamics and their therapeutic impact.

This approach provides a computationally sound foundation for your later Wizard-of-Oz study while fulfilling all assignment requirements for the scenario simulation.[^3][^4]
<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29][^30][^31][^32][^33][^34][^35][^36][^37][^38][^39][^40][^41][^42][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: cofrida.pdf

[^2]: Lecture4.pdf

[^3]: hrc-project-proposal.pdf

[^4]: scenario-description.pdf

[^5]: https://ieeexplore.ieee.org/document/10527509/

[^6]: https://ieeexplore.ieee.org/document/10537726/

[^7]: https://link.springer.com/10.1007/s12369-023-01018-9

[^8]: https://link.springer.com/10.1007/s00170-023-11404-2

[^9]: https://ieeexplore.ieee.org/document/10309328/

[^10]: https://ieeexplore.ieee.org/document/10125740/

[^11]: https://ieeexplore.ieee.org/document/10449476/

[^12]: https://link.springer.com/10.1007/s00170-024-13639-z

[^13]: https://dl.acm.org/doi/10.1145/3736422

[^14]: https://www.mdpi.com/2079-8954/11/3/152

[^15]: http://arxiv.org/pdf/2412.13474.pdf

[^16]: http://arxiv.org/pdf/2404.01702.pdf

[^17]: https://www.mdpi.com/1424-8220/23/13/5798/pdf?version=1687354699

[^18]: https://downloads.hindawi.com/journals/mpe/2013/384865.pdf

[^19]: http://arxiv.org/pdf/1405.6341.pdf

[^20]: https://dl.acm.org/doi/pdf/10.1145/3610978.3640598

[^21]: https://www.mdpi.com/1424-8220/21/11/3673/pdf

[^22]: http://arxiv.org/pdf/2402.14525.pdf

[^23]: http://dtransposed.github.io/blog/2018/04/01/Robot-Localization/

[^24]: https://pymdptoolbox.readthedocs.io

[^25]: https://www.mlwires.com/meet-frida-the-ai-controlled-robot-for-physical-paintings/

[^26]: https://github.com/nickbirnberg/HMM-localisation

[^27]: https://github.com/LeoMartinezTAMUK/Markov_Decision_Process

[^28]: https://pschaldenbrand.github.io/frida/

[^29]: https://alessandro.ronc.one/papers/2018_Grigore_IROS_assistance_prediction.pdf

[^30]: https://gibberblot.github.io/rl-notes/single-agent/MDPs.html

[^31]: https://pschaldenbrand.github.io/cofrida/

[^32]: https://ijrpr.com/uploads/V6ISSUE5/IJRPR47242.pdf

[^33]: https://www.geeksforgeeks.org/python/implement-value-iteration-in-python/

[^34]: https://github.com/cmubig/Frida

[^35]: https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2021.734548/full

[^36]: https://www.reinforcementlearningpath.com/markov-decision-process-mdp-application-1/

[^37]: https://frida-robot.vercel.app

[^38]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9920522/

[^39]: https://towardsdatascience.com/introducing-markov-decision-processes-setting-up-gymnasium-environments-and-solving-them-via-e806c36dc04f/

[^40]: https://www.youtube.com/watch?v=e2vHvYgjiYg

[^41]: https://research.tue.nl/files/226587942/machines_10_00957_v2.pdf

[^42]: https://www.youtube.com/watch?v=UuTkioxL9bQ

