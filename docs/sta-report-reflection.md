● **Scenario Choice & Realism** : Why you chose this healthcare scenario, and how it
maps to real-world needs (patient safety, nurse workflow, therapy exercises,
medication compliance, etc.).
For the simulation art therapy is digitally modeled to study the potential benefits
without the requirement of a real clinic implementation. This setup helps in
understanding how complex it might be to bring robot-assisted art therapy into an
everyday practice while allowing us to test ideas more safely. By simulating a patient
and robot interaction, the researchers can gain valuable insights into how they
communicate, engage, and respond emotionally. Studies show that art therapy
supports mental health by reducing depression, anxiety, and trauma symptoms. This
simulation builds on prior research but targets some unexplored context using the
robots to assist with therapeutic painting. Robots can encourage patients to
participate more, ease the anxiety, and make the therapy session more accessible
when therapists are not always available. Overall, this simulation offers a thoughtful
way to study patient engagement, emotional effects, and practical use, which helps
in guiding future healthcare solutions.

- helps us model how complex it would be to do this properly IRL
- bases on previous research but basically none regarding this specific scenario →
  further exploration
- using robots in this sort of therapy can reduce anxiety and increase availability
- by simulating this scenario further insights can be gained on the patient/robot
  dynamics

● **User Input & Robot Sensing** : What signals or data you modeled, how you
introduced randomness or uncertainty, and how that simulates real sensor noise or
incomplete knowledge of user state.
In this simulation, the user input consists of visible actions such as drawing, pausing,
or waiting, which provides clear signals to the robot about the current behavior of the
user or an emotional state. The robot uses simulated sensors that will function like
eyes to observe and interpret these actions. However, the perception of the robot is
not flawless, it occasionally misinterprets the user’s actions due to a deliberate 10
percent chance of error, which is mimicking the imperfections of real-world sensors
like blurry cameras or missed movements. This imperfect information requires the
robot to make probabilistic estimates of the feelings or intentions of the users, as it
cannot directly observe internal states. Adding to this, the user’s emotional state can
change unpredictably, and the responses of the robot may not produce immediate
effects, introducing the natural variability. This incorporation of uncertainty and partial
knowledge enables the robot to realistically manage the noisy and incomplete user
data, these capabilities significantly improves the responsiveness of the robot and
the adaptability during interactions, enabling it to react appropriately even in
uncertain and dynamic situations. This thoughtful design mirrors the challenges
faced by real robots in understanding and collaborating with humans in dynamic and
uncertain environments.

● **Ethical & Practical Considerations** : How does your design address safety or
ethical concerns? Could there be privacy or autonomy issues in a real system?
The design of this therapeutic collaboration painting simulation places strong
emphasis on ethical responsibility and patient safety, ensuring that every interaction
remains secure, transparent, and supportive. Comprehensive safety measures such
as safe operating distances, and risk assessment protocols are implemented to
prevent physical accidents and maintain reliable, controlled interactions between the
robot and the user. Alongside physical safety, the design considers mental and
emotional well-being by promoting psychological comfort, trust, and low cognitive
load, especially for individuals with physical limitations. The behavior of the robot is
designed to be adaptive and transparent, aiming to reduce anxiety and enhance the
sense of control of the patient. Protecting the privacy remains a fundamental priority
because the artwork produced may express sensitive emotional experiences. This
requires strong data protection measures, clearly informed consent procedures, and
strict confidentiality protocols to safeguards patient information.Through this careful
integration of safety provisions, and ethical awareness, the system aspires to create
a therapeutic collaboration built on trust, dignity, and accountability in real-world
healthcare applications.
