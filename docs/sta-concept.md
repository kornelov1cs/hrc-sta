● 1. Select one scenario from the list (or an instructor-approved variant).
Clearly define:
○ Environment (clinic, home, therapy room)
● therapy room
○ Human user (patient, nurse, doctor, therapist, or elderly person)
● Mental health patient
○ Task (delivering medication, assisting with exercises, providing
telepresence, etc.)
● Therapeutic painting
● 2. Identify key elements:
○ User: How will you model the human’s state (intent, readiness,
need for help, level of busy/fatigue)? What signals does the
robot receive about the human (gestures, verbal cues, or
simplified random states)?
● Emotion: random from array → do we provide robot
human emotion right away or do we detect?
→ from selected emotion, vary rapidity/color
warmth/pause times of painting actions, sth robot can
interpret → how busy as well
● environment canvas + 2d plane? with distance to canvas
variable → recognize user intent to paint/swap of
position/if close but not doing anything = need for
help/fatigue → new input like not previously used color
● The robot would detect verbal cues to start drawing or
help the human. It would also detect if the human steps
away from the canvas or stops drawing for a while, after
which the robot would ask for a status, or if it can start
painting.
○ Robot: Define the robot’s sensors (e.g., position from odometry,
overhead camera, user signals) and actuators (e.g., moving to a
location, handing over an item, physically assisting the human).
Decide on a simple geometry or discrete states for the robot’s
location (like “AtBin,” “AtPatient,” or a 2D coordinate). Think
about how to model the beliefs, desires and intentions of the
robot.
● Sensors: camera, position, microphone
● Location: distance from canvas (maybe x&y)
● States: idle, painting, moving
●
○ Behavior Design: How does the robot interpret user signals (via
an HMM, discrete BN, or direct random transitions)? How does
the robot decide actions (e.g., a small MDP policy, a heuristic
rule, or a “toy” Q-learning approach)? Include adaptation or

learning: e.g., the user’s state changes over time, and the robot
adapts (updates beliefs or policy).
● HMM (hidden markov model)
● 3. Implement the sense-think-act loop in a (toy) simulation:
○ Environment Representation
○ User and Robot Representation
○ Time-Stepped Simulation Loop
○ Stylized Visualization (Optional but Encouraged)
● 4. Reflection & Discussion: Write a short report (2-4 pages) explaining:
○ **Scenario Choice & Realism** : Why you chose this healthcare
scenario, and how it maps to real-world needs (patient safety,
nurse workflow, therapy exercises, medication compliance,
etc.).
○ **User Input & Robot Sensing** : What signals or data you
modeled, how you introduced randomness or uncertainty, and
how that simulates real sensor noise or incomplete knowledge
of user state.
○ **Ethical & Practical Considerations** : How does your design
address safety or ethical concerns? Could there be privacy or
autonomy issues in a real system?
