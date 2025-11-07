"""
Hidden Markov Model (HMM) for patient intent recognition.
Infers patient's hidden internal state from observable behaviors.
"""

from typing import List, Dict, Tuple
import numpy as np

from utils import (
    PatientState,
    Observation,
    get_state_index,
    get_observation_index,
    normalize_probabilities
)


class PatientIntentHMM:
    """
    Hidden Markov Model for inferring patient intent from observations.

    The HMM maintains a belief distribution over patient states and updates
    this belief using the forward algorithm as new observations arrive.
    """

    def __init__(self):
        """Initialize HMM with transition and emission matrices."""
        self.states = list(PatientState)
        self.observations = list(Observation)
        self.n_states = len(self.states)
        self.n_observations = len(self.observations)

        # Initialize matrices
        self.transition_matrix = self._build_transition_matrix()
        self.emission_matrix = self._build_emission_matrix()

        # Initialize uniform belief distribution
        self.belief_state = np.ones(self.n_states) / self.n_states

        # Store history for analysis
        self.belief_history: List[np.ndarray] = []
        self.observation_history: List[Observation] = []

    def _build_transition_matrix(self) -> np.ndarray:
        """
        Build state transition probability matrix.

        PARAMETER JUSTIFICATION (per assignment criteria):
        Transition probabilities model realistic patient emotional dynamics:
        - High self-transition (0.6-0.75): Stable states (ENGAGED, SATISFIED)
          persist, reflecting sustained emotional states in therapy
        - Medium self-transition (0.35-0.4): Uncertain states (HESITANT,
          FRUSTRATED) are less stable, can improve or worsen
        - Positive transitions: ENGAGED -> SATISFIED (0.2), NEEDS_SUPPORT ->
          ENGAGED (0.3) model therapeutic progress
        - Negative transitions: Small probabilities (0.05-0.15) for regression
          to negative states, reflecting therapy challenges

        Returns:
            Matrix A where A[i,j] = P(state_j | state_i)
        """
        # Define transition probabilities (should match patient simulator)
        transitions = {
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

        # Build matrix
        matrix = np.zeros((self.n_states, self.n_states))
        for i, state_i in enumerate(self.states):
            for j, state_j in enumerate(self.states):
                matrix[i, j] = transitions[state_i][state_j]

        return matrix

    def _build_emission_matrix(self) -> np.ndarray:
        """
        Build observation emission probability matrix.

        PARAMETER JUSTIFICATION:
        Emission probabilities link hidden emotional states to observable behaviors:
        - ENGAGED: High prob. of DRAWING (0.4) and LONG_STROKE (0.3), low IDLE (0.05)
          -> Active, confident painting behavior
        - NEEDS_SUPPORT: High PAUSED (0.3) and OBSERVING (0.25), medium IDLE (0.15)
          -> Patient seeking guidance but not completely stuck
        - HESITANT: High IDLE (0.25) and PAUSED (0.25), low LONG_STROKE (0.05)
          -> Uncertain, tentative behavior
        - SATISFIED: High OBSERVING (0.4), balanced activity
          -> Contentment leads to stepping back and appreciating
        - FRUSTRATED: High IDLE (0.35) and SHORT_STROKE (0.25), low DRAWING (0.05)
          -> Giving up or making erratic attempts

        Returns:
            Matrix B where B[i,k] = P(observation_k | state_i)
        """
        # Define emission probabilities (should match patient simulator)
        emissions = {
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

        # Build matrix
        matrix = np.zeros((self.n_states, self.n_observations))
        for i, state in enumerate(self.states):
            for k, obs in enumerate(self.observations):
                matrix[i, k] = emissions[state][obs]

        return matrix

    def update_belief(self, observation: Observation) -> np.ndarray:
        """
        Update belief distribution using forward algorithm.

        Implements: belief(s') = α * P(obs|s') * Σ_s P(s'|s) * belief(s)

        Args:
            observation: New observation received

        Returns:
            Updated belief distribution
        """
        obs_idx = get_observation_index(observation)

        # Prediction step: belief_pred = transition_matrix^T @ belief
        belief_pred = self.transition_matrix.T @ self.belief_state

        # Update step: belief = emission * belief_pred
        emission_probs = self.emission_matrix[:, obs_idx]
        belief_updated = emission_probs * belief_pred

        # Normalize
        self.belief_state = normalize_probabilities(belief_updated)

        # Store history
        self.belief_history.append(self.belief_state.copy())
        self.observation_history.append(observation)

        return self.belief_state

    def predict_next_state(self) -> np.ndarray:
        """
        Predict belief distribution for next timestep.

        Returns:
            Predicted belief distribution
        """
        return self.transition_matrix.T @ self.belief_state

    def get_most_likely_state(self) -> Tuple[PatientState, float]:
        """
        Get the most likely current patient state.

        Returns:
            Tuple of (most_likely_state, probability)
        """
        max_idx = np.argmax(self.belief_state)
        return self.states[max_idx], self.belief_state[max_idx]

    def get_state_probability(self, state: PatientState) -> float:
        """
        Get probability of a specific patient state.

        Args:
            state: Patient state to query

        Returns:
            Probability of that state
        """
        state_idx = get_state_index(state)
        return self.belief_state[state_idx]

    def viterbi(self, observations: List[Observation]) -> List[PatientState]:
        """
        Find most likely sequence of states using Viterbi algorithm.

        Args:
            observations: Sequence of observations

        Returns:
            Most likely sequence of states
        """
        T = len(observations)

        # Initialize DP table and backpointers
        delta = np.zeros((T, self.n_states))
        psi = np.zeros((T, self.n_states), dtype=int)

        # Initialization (t=0)
        obs_idx = get_observation_index(observations[0])
        delta[0] = self.belief_state * self.emission_matrix[:, obs_idx]
        delta[0] = normalize_probabilities(delta[0])

        # Recursion (t=1..T-1)
        for t in range(1, T):
            obs_idx = get_observation_index(observations[t])
            for j in range(self.n_states):
                # For each state j, find best previous state
                trans_probs = delta[t - 1] * self.transition_matrix[:, j]
                psi[t, j] = np.argmax(trans_probs)
                delta[t, j] = (
                    trans_probs[psi[t, j]] *
                    self.emission_matrix[j, obs_idx]
                )

            # Normalize to prevent underflow
            if delta[t].sum() > 0:
                delta[t] = normalize_probabilities(delta[t])

        # Backtracking
        states = [0] * T
        states[-1] = np.argmax(delta[-1])

        for t in range(T - 2, -1, -1):
            states[t] = psi[t + 1, states[t + 1]]

        # Convert indices to states
        return [self.states[idx] for idx in states]

    def get_belief_entropy(self) -> float:
        """
        Calculate entropy of current belief distribution.
        Higher entropy = more uncertainty.

        Returns:
            Entropy in bits
        """
        # Avoid log(0)
        probs = self.belief_state + 1e-10
        return -np.sum(probs * np.log2(probs))

    def reset(self) -> None:
        """Reset HMM to initial state."""
        self.belief_state = np.ones(self.n_states) / self.n_states
        self.belief_history = []
        self.observation_history = []

    def get_belief_dict(self) -> Dict[str, float]:
        """
        Get current belief as dictionary for logging.

        Returns:
            Dictionary mapping state names to probabilities
        """
        return {
            state.value: prob
            for state, prob in zip(self.states, self.belief_state)
        }

    def get_summary(self) -> Dict:
        """
        Get summary statistics about HMM performance.

        Returns:
            Dictionary with summary statistics
        """
        most_likely, confidence = self.get_most_likely_state()

        return {
            'most_likely_state': most_likely.value,
            'confidence': confidence,
            'entropy': self.get_belief_entropy(),
            'belief_distribution': self.get_belief_dict(),
            'observation_count': len(self.observation_history)
        }
