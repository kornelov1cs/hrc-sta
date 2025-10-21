Design and simulate a scenario in which a robot and a human collaborate, based on the sense-
think-act loop that demonstrates the key steps in a simplified or toy manner, but with a clear
mapping of real-world issues in healthcare (safety, timeliness, comfort, ethical considerations,
etc.). The focus here is on developing the think-and-act component based on the methods you’ve
learned in the course. You can simulate the sense component (however, you can also use tools
like Mediapipe for hand or gaze tracking). Possible scenarios (choose one or propose your own
variant, for CBL-Students: use the theme mobility):
Robot Nurse Assistant in a hospital ward: A mobile robot aids nurses and doctors by fetching
supplies, delivering medications, or transporting lightweight equipment. The human
collaborator could be a busy nurse juggling multiple patients. The robot needs to recognize
when the nurse is ready for a handover (e.g., giving or receiving supplies) vs. when the nurse
is focused on other tasks.
Physical Therapy/Rehabilitation Support Robot: A robot assists a physical therapist and a
patient in guided exercises (e.g., range-of-motion tasks). The therapist’s or patient’s intent
(e.g., “NeedsSupport,” “PerformingExercise,” “Resting”) is not always explicit. The robot can
adjust resistance, hold a limb for balance, or offer encouragement/reminders.
Elderly Home-Care Robot: A companion robot in a home setting helps an elderly person with
daily tasks (fetching objects, reminding about medication, checking if the person needs
assistance). The robot must navigate domestic areas (kitchen, living room) while avoiding
collisions and respecting user’s personal space.
Steps :
Select one scenario from the list (or an instructor-approved variant). Clearly define:
Environment (clinic, home, therapy room)
Human user (patient, nurse, doctor, therapist, or elderly person)
Task (delivering medication, assisting with exercises, providing telepresence, etc.)
Identify key elements:
User: How will you model the human’s state (intent, readiness, need for help, level of
busy/fatigue)? What signals does the robot receive about the human (gestures, verbal cues, or
simplified random states)?
Robot: Define the robot’s sensors (e.g., position from odometry, overhead camera, user
signals) and actuators (e.g., moving to a location, handing over an item, physically assisting
the human). Decide on a simple geometry or discrete states for the robot’s location (like
“AtBin,” “AtPatient,” or a 2D coordinate). Think about how to model the beliefs, desires and
intentions of the robot.
Behavior Design: How does the robot interpret user signals (via an HMM, discrete BN, or
direct random transitions)? How does the robot decide actions (e.g., a small MDP policy, a
heuristic rule, or a “toy” Q-learning approach)? Include adaptation or learning: e.g., the user’s
state changes over time, and the robot adapts (updates beliefs or policy).
Implement the sense-think-act loop in a (toy) simulation:
Environment Representation
User and Robot Representation
Time-Stepped Simulation Loop
Stylized Visualization (Optional but Encouraged)
Reflection & Discussion: Write a short report (2-4 pages) explaining:
Scenario Choice & Realism : Why you chose this healthcare scenario, and how it maps to
real-world needs (patient safety, nurse workflow, therapy exercises, medication compliance,
etc.).
User Input & Robot Sensing : What signals or data you modeled, how you introduced
randomness or uncertainty, and how that simulates real sensor noise or incomplete knowledge
of user state.
Ethical & Practical Considerations : How does your design address safety or ethical
concerns? Could there be privacy or autonomy issues in a real system?
Deliverable : A documented Python script or notebook and a reflection document (2-4 pages, Arial
(11 point)): Discuss design decisions, how your system handles partial observability, noise, or
unpredictability in user state, and the key trade-offs in a healthcare context.
