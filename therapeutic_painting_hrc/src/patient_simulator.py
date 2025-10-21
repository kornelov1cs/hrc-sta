"""
Patient simulator with state machine modeling patient's internal state
and observable behaviors during therapeutic painting session.
"""

from typing import Dict, Optional, Tuple
import numpy as np
import random

from utils import (
    PatientState,
    Observation,
    RobotAction,
    Color,
    Shape,
    calculate_engagement_score,
    add_noise_to_observation,
    sample_from_distribution
)


class PatientSimulator:
    """
    Simulates patient behavior during therapeutic painting session.
    Maintains hidden internal state and generates observable behaviors.
    """

    def __init__(self, initial_state: PatientState = PatientState.HESITANT):
        """
        Initialize patient simulator.

        Args:
            initial_state: Starting internal state
        """
        self.true_state = initial_state
        self.engagement_level = calculate_engagement_score(initial_state)
        self.consecutive_idle_steps = 0
        self.total_strokes = 0
        self.last_observation = Observation.IDLE

        # State transition probabilities (baseline, modified by robot actions)
        self.transition_probs = self._initialize_transition_probabilities()

        # Observation emission probabilities P(observation | state)
        self.emission_probs = self._initialize_emission_probabilities()

    def _initialize_transition_probabilities(self) -> Dict[PatientState, Dict[PatientState, float]]:
        """
        Initialize state transition probability matrix.

        Returns:
            Nested dict: P(next_state | current_state)
        """
        return {
            PatientState.ENGAGED: {
                PatientState.ENGAGED: 0.6,
                PatientState.NEEDS_SUPPORT: 0.1,
                PatientState.HESITANT: 0.05,
                PatientState.SATISFIED: 0.2,
                PatientState.FRUSTRATED: 0.05
            },
            PatientState.NEEDS_SUPPORT: {
                PatientState.ENGAGED: 0.3,
                PatientState.NEEDS_SUPPORT: 0.4,
                PatientState.HESITANT: 0.15,
                PatientState.SATISFIED: 0.05,
                PatientState.FRUSTRATED: 0.1
            },
            PatientState.HESITANT: {
                PatientState.ENGAGED: 0.2,
                PatientState.NEEDS_SUPPORT: 0.25,
                PatientState.HESITANT: 0.35,
                PatientState.SATISFIED: 0.05,
                PatientState.FRUSTRATED: 0.15
            },
            PatientState.SATISFIED: {
                PatientState.ENGAGED: 0.1,
                PatientState.NEEDS_SUPPORT: 0.05,
                PatientState.HESITANT: 0.05,
                PatientState.SATISFIED: 0.75,
                PatientState.FRUSTRATED: 0.05
            },
            PatientState.FRUSTRATED: {
                PatientState.ENGAGED: 0.1,
                PatientState.NEEDS_SUPPORT: 0.2,
                PatientState.HESITANT: 0.25,
                PatientState.SATISFIED: 0.05,
                PatientState.FRUSTRATED: 0.4
            }
        }

    def _initialize_emission_probabilities(self) -> Dict[PatientState, Dict[Observation, float]]:
        """
        Initialize observation emission probability matrix.

        Returns:
            Nested dict: P(observation | state)
        """
        return {
            PatientState.ENGAGED: {
                Observation.DRAWING: 0.4,
                Observation.PAUSED: 0.05,
                Observation.OBSERVING: 0.1,
                Observation.IDLE: 0.05,
                Observation.LONG_STROKE: 0.3,
                Observation.SHORT_STROKE: 0.1
            },
            PatientState.NEEDS_SUPPORT: {
                Observation.DRAWING: 0.1,
                Observation.PAUSED: 0.3,
                Observation.OBSERVING: 0.25,
                Observation.IDLE: 0.15,
                Observation.LONG_STROKE: 0.05,
                Observation.SHORT_STROKE: 0.15
            },
            PatientState.HESITANT: {
                Observation.DRAWING: 0.1,
                Observation.PAUSED: 0.25,
                Observation.OBSERVING: 0.2,
                Observation.IDLE: 0.25,
                Observation.LONG_STROKE: 0.05,
                Observation.SHORT_STROKE: 0.15
            },
            PatientState.SATISFIED: {
                Observation.DRAWING: 0.15,
                Observation.PAUSED: 0.1,
                Observation.OBSERVING: 0.4,
                Observation.IDLE: 0.1,
                Observation.LONG_STROKE: 0.15,
                Observation.SHORT_STROKE: 0.1
            },
            PatientState.FRUSTRATED: {
                Observation.DRAWING: 0.05,
                Observation.PAUSED: 0.2,
                Observation.OBSERVING: 0.1,
                Observation.IDLE: 0.35,
                Observation.LONG_STROKE: 0.05,
                Observation.SHORT_STROKE: 0.25
            }
        }

    def generate_observation(self, add_noise: bool = True) -> Observation:
        """
        Generate observable behavior based on current hidden state.

        Args:
            add_noise: Whether to add sensor noise

        Returns:
            Observable patient behavior
        """
        # Sample observation from emission probabilities
        observation = sample_from_distribution(
            self.emission_probs[self.true_state]
        )

        if add_noise:
            observation = add_noise_to_observation(observation)

        self.last_observation = observation
        return observation

    def update_state(
        self,
        robot_action: Optional[str] = None,
        canvas_state: Optional[Dict] = None
    ) -> None:
        """
        Update patient's internal state based on robot action and environment.

        Args:
            robot_action: Recent robot action
            canvas_state: Current canvas state
        """
        # Get base transition probabilities
        transition_dist = self.transition_probs[self.true_state].copy()

        # Modify probabilities based on robot action
        if robot_action:
            transition_dist = self._adjust_for_robot_action(
                transition_dist, robot_action
            )

        # Modify probabilities based on canvas state
        if canvas_state:
            transition_dist = self._adjust_for_canvas_state(
                transition_dist, canvas_state
            )

        # Sample next state
        next_state = sample_from_distribution(transition_dist)
        self.true_state = next_state

        # Update engagement level
        self.engagement_level = calculate_engagement_score(next_state)

    def _adjust_for_robot_action(
        self,
        transition_dist: Dict[PatientState, float],
        robot_action: str
    ) -> Dict[PatientState, float]:
        """
        Adjust state transition probabilities based on robot's action.

        Args:
            transition_dist: Base transition probabilities
            robot_action: Robot action taken

        Returns:
            Adjusted transition probabilities
        """
        # Create modifiable copy
        adjusted = transition_dist.copy()

        # Proactive actions (robot initiates)
        if robot_action in [RobotAction.INITIATE_PAINT.value, RobotAction.SUGGEST_COLOR.value, RobotAction.SUGGEST_SHAPE.value]:
            if self.true_state == PatientState.HESITANT:
                # Proactive help reduces hesitation
                adjusted[PatientState.ENGAGED] *= 1.5
                adjusted[PatientState.HESITANT] *= 0.6
            elif self.true_state == PatientState.NEEDS_SUPPORT:
                # Proactive support increases engagement
                adjusted[PatientState.ENGAGED] *= 1.6
                adjusted[PatientState.NEEDS_SUPPORT] *= 0.7
            elif self.true_state == PatientState.ENGAGED:
                # But might frustrate already engaged patient
                adjusted[PatientState.FRUSTRATED] *= 1.3

        # Reactive actions (robot responds)
        elif robot_action in [RobotAction.CONTINUE_PATIENT.value, RobotAction.RESPOND_TO_PROMPT.value]:
            if self.true_state == PatientState.ENGAGED:
                # Responsive collaboration maintains engagement
                adjusted[PatientState.ENGAGED] *= 1.4
                adjusted[PatientState.SATISFIED] *= 1.2
            elif self.true_state == PatientState.NEEDS_SUPPORT:
                # But doesn't help as much when patient needs initiative
                adjusted[PatientState.FRUSTRATED] *= 1.2

        # Robot waiting/observing
        elif robot_action in [RobotAction.WAIT.value, RobotAction.OBSERVE.value]:
            if self.true_state == PatientState.NEEDS_SUPPORT:
                # Patient needing support becomes frustrated if robot waits
                adjusted[PatientState.FRUSTRATED] *= 1.5
                adjusted[PatientState.HESITANT] *= 1.3

        # Normalize
        total = sum(adjusted.values())
        return {k: v / total for k, v in adjusted.items()}

    def _adjust_for_canvas_state(
        self,
        transition_dist: Dict[PatientState, float],
        canvas_state: Dict
    ) -> Dict[PatientState, float]:
        """
        Adjust state transition probabilities based on canvas state.

        Args:
            transition_dist: Current transition probabilities
            canvas_state: Canvas state dictionary

        Returns:
            Adjusted transition probabilities
        """
        adjusted = transition_dist.copy()

        coverage = canvas_state.get('coverage', 0)
        patient_strokes = canvas_state.get('patient_strokes', 0)

        # If canvas is getting full, patient more likely to be satisfied
        if coverage > 0.6:
            adjusted[PatientState.SATISFIED] *= 1.4
            adjusted[PatientState.ENGAGED] *= 0.9

        # If patient hasn't painted much, might be hesitant or frustrated
        if patient_strokes < 3:
            adjusted[PatientState.HESITANT] *= 1.2
            adjusted[PatientState.NEEDS_SUPPORT] *= 1.2

        # Normalize
        total = sum(adjusted.values())
        return {k: v / total for k, v in adjusted.items()}

    def get_painting_action(self, observation: Observation) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Determine if patient is painting and generate action parameters.

        Args:
            observation: Current observation

        Returns:
            Tuple of (action_type, action_parameters) or (None, None)
        """
        # Observations that involve painting
        painting_obs = [
            Observation.DRAWING,
            Observation.LONG_STROKE,
            Observation.SHORT_STROKE
        ]

        if observation in painting_obs:
            # Generate painting parameters
            stroke_size = 40 if observation == Observation.LONG_STROKE else 20

            params = {
                'position': (
                    np.random.randint(50, 750),
                    np.random.randint(50, 550)
                ),
                'color': random.choice(list(Color)),
                'shape': random.choice(list(Shape)),
                'size': stroke_size
            }

            self.total_strokes += 1
            self.consecutive_idle_steps = 0

            return ('paint', params)
        else:
            # Patient is not painting
            self.consecutive_idle_steps += 1
            return (None, None)

    def get_state_info(self) -> Dict:
        """
        Get current patient state information for logging.

        Returns:
            Dictionary with state information
        """
        return {
            'true_state': self.true_state.value,
            'engagement_level': self.engagement_level,
            'last_observation': self.last_observation.value,
            'total_strokes': self.total_strokes,
            'consecutive_idle_steps': self.consecutive_idle_steps
        }

    def reset(self, initial_state: PatientState = PatientState.HESITANT) -> None:
        """
        Reset patient simulator for new session.

        Args:
            initial_state: Starting state for new session
        """
        self.true_state = initial_state
        self.engagement_level = calculate_engagement_score(initial_state)
        self.consecutive_idle_steps = 0
        self.total_strokes = 0
        self.last_observation = Observation.IDLE
