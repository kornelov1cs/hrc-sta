"""
Robot controller implementing BDI (Belief-Desire-Intention) architecture
and MDP-based decision-making for therapeutic painting collaboration.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass

from utils import (
    PatientState,
    RobotAction,
    Color,
    Shape
)
from intent_recognition import PatientIntentHMM


@dataclass
class Desire:
    """Represents a robot goal/desire."""
    name: str
    priority: float  # 0-1, higher is more important
    satisfied: bool = False


class RobotBDI:
    """
    BDI architecture for robot decision-making.

    Beliefs: Probability distribution over patient states, canvas state
    Desires: Goals to achieve (engagement, collaboration, art quality)
    Intentions: Planned sequence of actions
    """

    def __init__(self, mode: str = 'proactive'):
        """
        Initialize BDI robot controller.

        Args:
            mode: 'proactive' or 'reactive'
        """
        self.mode = mode

        # Beliefs
        self.beliefs = {
            'patient_state_distribution': None,  # From HMM
            'most_likely_patient_state': None,
            'patient_state_confidence': 0.0,
            'canvas_coverage': 0.0,
            'idle_duration': 0,
            'recent_patient_activity': 0,
            'recent_robot_activity': 0,
            'turn_taking_smooth': False
        }

        # Desires
        self.desires = self._initialize_desires()

        # Intentions (action queue)
        self.intentions: List[Tuple[RobotAction, Dict]] = []

        # MDP components
        self.mdp = TherapeuticPaintingMDP(mode=mode)

        # Action history
        self.action_history: List[str] = []

    def _initialize_desires(self) -> List[Desire]:
        """
        Initialize robot desires/goals.

        Returns:
            List of Desire objects
        """
        if self.mode == 'proactive':
            return [
                Desire(name="increase_engagement", priority=0.9),
                Desire(name="reduce_stagnation", priority=0.95),
                Desire(name="collaborative_art", priority=0.7),
                Desire(name="provide_structure", priority=0.8)
            ]
        else:  # reactive
            return [
                Desire(name="increase_engagement", priority=0.85),
                Desire(name="respect_autonomy", priority=0.95),
                Desire(name="collaborative_art", priority=0.75),
                Desire(name="respond_to_patient", priority=0.9)
            ]

    def perceive(
        self,
        hmm: PatientIntentHMM,
        canvas_state: Dict,
        idle_duration: int,
        turn_taking_smooth: bool
    ) -> None:
        """
        Update beliefs from sensors (HMM and environment).

        Args:
            hmm: Patient intent HMM with updated beliefs
            canvas_state: Current canvas state
            idle_duration: Consecutive idle timesteps
            turn_taking_smooth: Whether turn-taking is alternating
        """
        most_likely, confidence = hmm.get_most_likely_state()

        self.beliefs.update({
            'patient_state_distribution': hmm.belief_state.copy(),
            'most_likely_patient_state': most_likely,
            'patient_state_confidence': confidence,
            'canvas_coverage': canvas_state.get('coverage', 0),
            'idle_duration': idle_duration,
            'recent_patient_activity': canvas_state.get('recent_patient_activity', 0),
            'recent_robot_activity': canvas_state.get('recent_robot_activity', 0),
            'turn_taking_smooth': turn_taking_smooth,
            'belief_entropy': hmm.get_belief_entropy()
        })

    def deliberate(self) -> Desire:
        """
        Select which desire to pursue based on current beliefs.

        Returns:
            Highest priority unsatisfied desire
        """
        # Evaluate desire satisfaction
        for desire in self.desires:
            desire.satisfied = self._is_desire_satisfied(desire)

        # Find highest priority unsatisfied desire
        unsatisfied = [d for d in self.desires if not d.satisfied]

        if not unsatisfied:
            # All desires satisfied, pursue collaborative art
            return next(
                (d for d in self.desires if d.name == "collaborative_art"),
                self.desires[0]
            )

        return max(unsatisfied, key=lambda d: d.priority)

    def _is_desire_satisfied(self, desire: Desire) -> bool:
        """
        Check if a desire is currently satisfied.

        Args:
            desire: Desire to check

        Returns:
            True if desire is satisfied
        """
        if desire.name == "increase_engagement":
            # Satisfied if patient is engaged or satisfied
            likely_state = self.beliefs['most_likely_patient_state']
            return likely_state in [PatientState.ENGAGED, PatientState.SATISFIED]

        elif desire.name == "reduce_stagnation":
            # Satisfied if idle duration is low
            return self.beliefs['idle_duration'] < 3

        elif desire.name == "respect_autonomy":
            # Satisfied if patient has been active recently
            return self.beliefs['recent_patient_activity'] > 0

        elif desire.name == "collaborative_art":
            # Satisfied if both parties contributing
            return (
                self.beliefs['recent_patient_activity'] > 0 and
                self.beliefs['recent_robot_activity'] > 0
            )

        elif desire.name == "provide_structure":
            # Satisfied if robot has contributed recently
            return self.beliefs['recent_robot_activity'] > 0

        elif desire.name == "respond_to_patient":
            # Satisfied if robot responds when patient acts
            return (
                self.beliefs['recent_patient_activity'] == 0 or
                self.beliefs['recent_robot_activity'] > 0
            )

        return False

    def plan(self) -> None:
        """
        Generate action plan (intentions) to achieve selected desire.
        Uses MDP policy to select actions.
        """
        # Clear current intentions
        self.intentions = []

        # Get MDP state representation
        mdp_state = self._get_mdp_state()

        # Get action from MDP policy
        action = self.mdp.select_action(mdp_state, self.beliefs)

        # Generate action parameters
        params = self._generate_action_params(action)

        # Add to intention queue
        self.intentions.append((action, params))

    def _get_mdp_state(self) -> Tuple:
        """
        Convert beliefs to MDP state representation.

        Returns:
            Tuple representing current MDP state
        """
        # Discretize beliefs into MDP state
        patient_state = self.beliefs['most_likely_patient_state']

        coverage_discrete = (
            'empty' if self.beliefs['canvas_coverage'] < 0.2 else
            'partial' if self.beliefs['canvas_coverage'] < 0.6 else
            'full'
        )

        idle_discrete = (
            'none' if self.beliefs['idle_duration'] == 0 else
            'short' if self.beliefs['idle_duration'] < 3 else
            'long'
        )

        patient_active = self.beliefs['recent_patient_activity'] > 0

        return (patient_state, coverage_discrete, idle_discrete, patient_active)

    def _generate_action_params(self, action: RobotAction) -> Dict:
        """
        Generate parameters for a robot action.

        Args:
            action: Robot action to parameterize

        Returns:
            Dictionary of action parameters
        """
        # Actions that involve painting
        painting_actions = [
            RobotAction.INITIATE_PAINT,
            RobotAction.CONTINUE_PATIENT,
            RobotAction.RESPOND_TO_PROMPT
        ]

        if action in painting_actions:
            return {
                'position': (
                    np.random.randint(50, 750),
                    np.random.randint(50, 550)
                ),
                'color': np.random.choice(list(Color)),
                'shape': np.random.choice(list(Shape)),
                'size': np.random.randint(20, 40)
            }

        elif action == RobotAction.SUGGEST_COLOR:
            return {
                'suggested_color': np.random.choice(list(Color))
            }

        elif action == RobotAction.SUGGEST_SHAPE:
            return {
                'suggested_shape': np.random.choice(list(Shape))
            }

        else:
            return {}

    def execute(self) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Execute next intention from action queue.

        Returns:
            Tuple of (action_type, action_parameters)
        """
        if not self.intentions:
            # No planned actions, default to observe
            return (RobotAction.OBSERVE.value, {})

        # Pop next intention
        action, params = self.intentions.pop(0)

        # Log action
        self.action_history.append(action.value)

        return (action.value, params)

    def reset(self) -> None:
        """Reset robot controller for new session."""
        self.beliefs = {k: None if 'state' in k else 0.0
                       for k in self.beliefs.keys()}
        self.desires = self._initialize_desires()
        self.intentions = []
        self.action_history = []


class TherapeuticPaintingMDP:
    """
    Markov Decision Process for robot action selection.
    Different policies for proactive vs reactive modes.
    """

    def __init__(self, mode: str = 'proactive'):
        """
        Initialize MDP.

        Args:
            mode: 'proactive' or 'reactive'
        """
        self.mode = mode

        # Define reward function weights
        self.rewards = self._initialize_rewards()

    def _initialize_rewards(self) -> Dict[str, float]:
        """
        Initialize reward function weights.

        Returns:
            Dictionary of reward values
        """
        return {
            'reduce_idle': 15.0,
            'maintain_engagement': 10.0,
            'interrupt_engaged': -8.0,
            'collaborative_turn': 12.0,
            'robot_inactive_long': -10.0,
            'help_frustrated': 15.0,
            'support_hesitant': 12.0,
            'respect_satisfied': 5.0
        }

    def select_action(self, state: Tuple, beliefs: Dict) -> RobotAction:
        """
        Select action based on current state and mode.

        Args:
            state: MDP state tuple
            beliefs: Current belief dictionary

        Returns:
            Selected RobotAction
        """
        patient_state, coverage, idle, patient_active = state

        if self.mode == 'proactive':
            return self._proactive_policy(
                patient_state, coverage, idle, patient_active, beliefs
            )
        else:
            return self._reactive_policy(
                patient_state, coverage, idle, patient_active, beliefs
            )

    def _proactive_policy(
        self,
        patient_state: PatientState,
        coverage: str,
        idle: str,
        patient_active: bool,
        beliefs: Dict
    ) -> RobotAction:
        """
        Proactive mode policy: Robot takes initiative.

        Args:
            patient_state: Most likely patient state
            coverage: Canvas coverage level
            idle: Idle duration level
            patient_active: Whether patient is currently active
            beliefs: Full belief dictionary

        Returns:
            Selected action
        """
        # High priority: Address stagnation
        if idle == 'long':
            # Patient stuck, robot initiates
            return RobotAction.INITIATE_PAINT

        # Patient frustrated or hesitant: provide support
        if patient_state == PatientState.FRUSTRATED:
            return RobotAction.SUGGEST_COLOR

        if patient_state == PatientState.HESITANT:
            if idle == 'short':
                return RobotAction.INITIATE_PAINT
            else:
                return RobotAction.SUGGEST_SHAPE

        # Patient needs support: be proactive
        if patient_state == PatientState.NEEDS_SUPPORT:
            return RobotAction.INITIATE_PAINT

        # Patient engaged: don't interrupt too much, but can suggest
        if patient_state == PatientState.ENGAGED:
            if patient_active:
                # Patient actively working, wait
                return RobotAction.WAIT
            else:
                # Patient paused, can continue their work
                return RobotAction.CONTINUE_PATIENT

        # Patient satisfied: observe and occasionally add
        if patient_state == PatientState.SATISFIED:
            if coverage == 'partial' and not patient_active:
                return RobotAction.CONTINUE_PATIENT
            else:
                return RobotAction.OBSERVE

        # Default: initiate if canvas empty, otherwise wait
        if coverage == 'empty':
            return RobotAction.INITIATE_PAINT
        else:
            return RobotAction.WAIT

    def _reactive_policy(
        self,
        patient_state: PatientState,
        coverage: str,
        idle: str,
        patient_active: bool,
        beliefs: Dict
    ) -> RobotAction:
        """
        Reactive mode policy: Robot responds to patient.

        Args:
            patient_state: Most likely patient state
            coverage: Canvas coverage level
            idle: Idle duration level
            patient_active: Whether patient is currently active
            beliefs: Full belief dictionary

        Returns:
            Selected action
        """
        # Only act in response to patient activity or explicit need
        recent_patient_activity = beliefs.get('recent_patient_activity', 0)

        # Critical: very long idle, must help
        if idle == 'long' and patient_state == PatientState.FRUSTRATED:
            return RobotAction.RESPOND_TO_PROMPT

        # Patient is actively working: respond by continuing
        if patient_active or recent_patient_activity > 0:
            if patient_state == PatientState.ENGAGED:
                return RobotAction.CONTINUE_PATIENT
            elif patient_state == PatientState.NEEDS_SUPPORT:
                return RobotAction.RESPOND_TO_PROMPT
            else:
                # Patient working but we're not sure state, continue their work
                return RobotAction.CONTINUE_PATIENT

        # Patient satisfied: respect their completion
        if patient_state == PatientState.SATISFIED:
            return RobotAction.OBSERVE

        # Patient hesitant but not acting: wait for them to start
        if patient_state == PatientState.HESITANT:
            if idle == 'long':
                # Very stuck, provide gentle suggestion
                return RobotAction.SUGGEST_COLOR
            else:
                return RobotAction.WAIT

        # Patient frustrated: wait for their direction
        if patient_state == PatientState.FRUSTRATED:
            if idle == 'short':
                return RobotAction.WAIT
            else:
                # Extended frustration, offer help
                return RobotAction.SUGGEST_SHAPE

        # Default: wait for patient to act
        return RobotAction.WAIT

    def calculate_reward(
        self,
        state: Tuple,
        action: RobotAction,
        next_state: Tuple,
        beliefs: Dict
    ) -> float:
        """
        Calculate reward for taking action in state.

        Args:
            state: Current state
            action: Action taken
            next_state: Resulting state
            beliefs: Current beliefs

        Returns:
            Reward value
        """
        reward = 0.0

        patient_state, _, idle, patient_active = state
        next_patient_state, _, next_idle, next_patient_active = next_state

        # Reward reducing idle time
        if idle == 'long' and next_idle != 'long':
            reward += self.rewards['reduce_idle']

        # Reward maintaining engagement
        if next_patient_state == PatientState.ENGAGED:
            reward += self.rewards['maintain_engagement']

        # Penalize interrupting engaged patient
        if (patient_state == PatientState.ENGAGED and
                patient_active and
                action in [RobotAction.INITIATE_PAINT, RobotAction.SUGGEST_COLOR]):
            reward += self.rewards['interrupt_engaged']

        # Reward collaborative turn-taking
        if beliefs.get('turn_taking_smooth', False):
            reward += self.rewards['collaborative_turn']

        # Penalize long robot inactivity (especially in proactive mode)
        robot_inactive = beliefs.get('recent_robot_activity', 0) == 0
        if robot_inactive and idle == 'long' and self.mode == 'proactive':
            reward += self.rewards['robot_inactive_long']

        return reward
