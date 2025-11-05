"""
Utility functions and constants for the therapeutic painting simulation.
"""

from enum import Enum
from typing import Dict
import numpy as np


# ============================================================================
# Constants
# ============================================================================

class PatientState(Enum):
    """Hidden states representing patient's internal state."""
    ENGAGED = "Engaged"
    NEEDS_SUPPORT = "NeedsSupport"
    HESITANT = "Hesitant"
    SATISFIED = "Satisfied"
    FRUSTRATED = "Frustrated"


class Observation(Enum):
    """Observable patient behaviors."""
    DRAWING = "Drawing"
    PAUSED = "Paused"
    OBSERVING = "Observing"
    IDLE = "Idle"
    LONG_STROKE = "LongStroke"
    SHORT_STROKE = "ShortStroke"


class RobotAction(Enum):
    """Possible robot actions."""
    INITIATE_PAINT = "InitiatePaint"
    SUGGEST_COLOR = "SuggestColor"
    SUGGEST_SHAPE = "SuggestShape"
    CONTINUE_PATIENT = "ContinuePatient"
    RESPOND_TO_PROMPT = "RespondToPrompt"
    WAIT = "Wait"
    OBSERVE = "Observe"


class Color(Enum):
    """Available paint colors."""
    RED = "#FF6B6B"
    BLUE = "#4ECDC4"
    YELLOW = "#FFE66D"
    GREEN = "#95E1D3"
    PURPLE = "#AA96DA"
    ORANGE = "#FCBF49"


class Shape(Enum):
    """Recognizable shapes."""
    CIRCLE = "Circle"
    SQUARE = "Square"
    LINE = "Line"
    CURVE = "Curve"
    SPLASH = "Splash"


# Canvas dimensions (pixels)
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

# Simulation parameters
DEFAULT_TIMESTEPS = 30
NOISE_LEVEL = 0.1  # Probability of noisy observations


# ============================================================================
# Helper Functions
# ============================================================================

def normalize_probabilities(probs: np.ndarray) -> np.ndarray:
    """
    Normalize a probability distribution.

    Args:
        probs: Array of probabilities

    Returns:
        Normalized probability distribution
    """
    total = np.sum(probs)
    if total == 0:
        return np.ones_like(probs) / len(probs)
    return probs / total


def sample_from_distribution(distribution: Dict[any, float]) -> any:
    """
    Sample an item from a probability distribution.

    Args:
        distribution: Dictionary mapping items to probabilities

    Returns:
        Sampled item
    """
    items = list(distribution.keys())
    probs = list(distribution.values())
    probs = normalize_probabilities(np.array(probs))
    return np.random.choice(items, p=probs)


def add_noise_to_observation(observation: Observation, noise_level: float = NOISE_LEVEL) -> Observation:
    """
    Add noise to an observation to simulate sensor uncertainty.

    Args:
        observation: True observation
        noise_level: Probability of returning incorrect observation

    Returns:
        Possibly noisy observation
    """
    if np.random.random() < noise_level:
        # Return random different observation
        observations = [obs for obs in Observation if obs != observation]
        return np.random.choice(observations)
    return observation


def calculate_engagement_score(patient_state: PatientState) -> float:
    """
    Calculate engagement score based on patient state.

    Args:
        patient_state: Current patient state

    Returns:
        Engagement score (0-1)
    """
    engagement_mapping = {
        PatientState.ENGAGED: 1.0,
        PatientState.NEEDS_SUPPORT: 0.6,
        PatientState.HESITANT: 0.4,
        PatientState.SATISFIED: 0.8,
        PatientState.FRUSTRATED: 0.2
    }
    return engagement_mapping.get(patient_state, 0.5)


def get_state_index(state: PatientState) -> int:
    """Get integer index for a patient state."""
    states = list(PatientState)
    return states.index(state)


def get_observation_index(obs: Observation) -> int:
    """Get integer index for an observation."""
    observations = list(Observation)
    return observations.index(obs)


def format_timestamp(step: int) -> str:
    """
    Format timestep as MM:SS.

    Args:
        step: Simulation timestep (each step = 2 seconds)

    Returns:
        Formatted time string
    """
    seconds = step * 2
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"
