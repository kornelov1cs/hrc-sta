"""
Environment module containing Canvas and TherapyEnvironment classes.
Manages the state of the collaborative painting session.
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime

from utils import Color, Shape, CANVAS_WIDTH, CANVAS_HEIGHT


@dataclass
class Stroke:
    """Represents a single brush stroke on the canvas."""

    agent: str  # 'patient' or 'robot'
    position: Tuple[int, int]  # (x, y) coordinates
    color: Color
    shape: Shape
    size: int  # Stroke size in pixels
    timestamp: int  # Simulation timestep when stroke was made

    def to_dict(self) -> Dict:
        """Convert stroke to dictionary for logging."""
        return {
            'agent': self.agent,
            'position': self.position,
            'color': self.color.value,
            'shape': self.shape.value,
            'size': self.size,
            'timestamp': self.timestamp
        }


class Canvas:
    """
    Represents the painting canvas with stroke tracking.
    """

    def __init__(self, width: int = CANVAS_WIDTH, height: int = CANVAS_HEIGHT):
        """
        Initialize canvas.

        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
        """
        self.width = width
        self.height = height
        self.strokes: List[Stroke] = []

    def add_stroke(
        self,
        agent: str,
        position: Tuple[int, int],
        color: Color,
        shape: Shape,
        size: int,
        timestamp: int
    ) -> None:
        """
        Add a stroke to the canvas.

        Args:
            agent: 'patient' or 'robot'
            position: (x, y) coordinates
            color: Stroke color
            shape: Stroke shape
            size: Stroke size in pixels
            timestamp: When stroke was made
        """
        stroke = Stroke(
            agent=agent,
            position=position,
            color=color,
            shape=shape,
            size=size,
            timestamp=timestamp
        )
        self.strokes.append(stroke)

    def get_coverage(self) -> float:
        """
        Calculate approximate canvas coverage percentage.

        Returns:
            Coverage as proportion (0-1)
        """
        if not self.strokes:
            return 0.0

        total_area = self.width * self.height
        stroke_area = sum(stroke.size ** 2 for stroke in self.strokes)

        # Cap at 100% even with overlapping strokes
        return min(1.0, stroke_area / total_area)

    def get_patient_strokes(self) -> List[Stroke]:
        """Get all strokes made by patient."""
        return [s for s in self.strokes if s.agent == 'patient']

    def get_robot_strokes(self) -> List[Stroke]:
        """Get all strokes made by robot."""
        return [s for s in self.strokes if s.agent == 'robot']

    def get_color_palette_used(self) -> List[Color]:
        """Get list of unique colors used on canvas."""
        return list(set(stroke.color for stroke in self.strokes))

    def get_recent_activity(self, window: int = 3) -> Dict[str, int]:
        """
        Get stroke counts in recent timestep window.

        Args:
            window: Number of recent timesteps to consider

        Returns:
            Dictionary with patient and robot stroke counts
        """
        if not self.strokes:
            return {'patient': 0, 'robot': 0}

        latest_time = max(stroke.timestamp for stroke in self.strokes)
        recent_strokes = [
            s for s in self.strokes
            if s.timestamp > latest_time - window
        ]

        return {
            'patient': sum(1 for s in recent_strokes if s.agent == 'patient'),
            'robot': sum(1 for s in recent_strokes if s.agent == 'robot')
        }

    def to_dict(self) -> Dict:
        """Convert canvas state to dictionary for logging."""
        return {
            'width': self.width,
            'height': self.height,
            'strokes': [stroke.to_dict() for stroke in self.strokes],
            'coverage': self.get_coverage(),
            'total_strokes': len(self.strokes),
            'patient_strokes': len(self.get_patient_strokes()),
            'robot_strokes': len(self.get_robot_strokes())
        }


@dataclass
class CanvasState:
    """Snapshot of canvas state at a particular timestep."""

    coverage: float
    total_strokes: int
    patient_strokes: int
    robot_strokes: int
    colors_used: int
    recent_patient_activity: int
    recent_robot_activity: int

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'coverage': self.coverage,
            'total_strokes': self.total_strokes,
            'patient_strokes': self.patient_strokes,
            'robot_strokes': self.robot_strokes,
            'colors_used': self.colors_used,
            'recent_patient_activity': self.recent_patient_activity,
            'recent_robot_activity': self.recent_robot_activity
        }


class TherapyEnvironment:
    """
    Manages the overall therapy session environment.
    Coordinates canvas state, timing, and turn-taking.
    """

    def __init__(self, robot_mode: str = 'proactive'):
        """
        Initialize therapy environment.

        Args:
            robot_mode: 'proactive' or 'reactive'
        """
        self.robot_mode = robot_mode
        self.canvas = Canvas()
        self.current_timestep = 0
        self.idle_duration = 0  # Consecutive timesteps with no activity
        self.last_actor = None  # 'patient' or 'robot'
        self.session_start_time = datetime.now()

    def get_canvas_state(self) -> CanvasState:
        """
        Get current canvas state snapshot.

        Returns:
            CanvasState object with current metrics
        """
        recent_activity = self.canvas.get_recent_activity(window=3)

        return CanvasState(
            coverage=self.canvas.get_coverage(),
            total_strokes=len(self.canvas.strokes),
            patient_strokes=len(self.canvas.get_patient_strokes()),
            robot_strokes=len(self.canvas.get_robot_strokes()),
            colors_used=len(self.canvas.get_color_palette_used()),
            recent_patient_activity=recent_activity['patient'],
            recent_robot_activity=recent_activity['robot']
        )

    def apply_patient_action(self, action: str, params: Optional[Dict] = None) -> None:
        """
        Apply patient's painting action to environment.

        Args:
            action: Action type ('paint', 'pause', 'observe', etc.)
            params: Action parameters (position, color, shape, size)
        """
        if action == 'paint' and params:
            self.canvas.add_stroke(
                agent='patient',
                position=params.get('position', (
                    np.random.randint(0, self.canvas.width),
                    np.random.randint(0, self.canvas.height)
                )),
                color=params.get('color', np.random.choice(list(Color))),
                shape=params.get('shape', np.random.choice(list(Shape))),
                size=params.get('size', np.random.randint(10, 50)),
                timestamp=self.current_timestep
            )
            self.idle_duration = 0
            self.last_actor = 'patient'
        else:
            # Patient is not painting (paused, observing, idle)
            self.idle_duration += 1

    def apply_robot_action(self, action_type: str, params: Optional[Dict] = None) -> None:
        """
        Apply robot's action to environment.

        Args:
            action_type: Type of robot action
            params: Action parameters
        """
        from utils import RobotAction

        # Actions that involve painting
        painting_actions = [
            RobotAction.INITIATE_PAINT.value,
            RobotAction.CONTINUE_PATIENT.value,
            RobotAction.RESPOND_TO_PROMPT.value
        ]

        if action_type in painting_actions and params:
            self.canvas.add_stroke(
                agent='robot',
                position=params.get('position', (
                    np.random.randint(0, self.canvas.width),
                    np.random.randint(0, self.canvas.height)
                )),
                color=params.get('color', np.random.choice(list(Color))),
                shape=params.get('shape', np.random.choice(list(Shape))),
                size=params.get('size', np.random.randint(10, 50)),
                timestamp=self.current_timestep
            )
            self.idle_duration = 0
            self.last_actor = 'robot'
        elif action_type in [RobotAction.WAIT.value, RobotAction.OBSERVE.value]:
            # Robot observes without acting
            pass
        else:
            # Suggestion actions don't add strokes
            self.idle_duration = 0 if self.last_actor else self.idle_duration + 1

    def step(self) -> None:
        """Advance simulation by one timestep."""
        self.current_timestep += 1

    def is_turn_taking_smooth(self) -> bool:
        """
        Check if there's smooth turn-taking (alternating patient and robot).

        Returns:
            True if last two actions alternated between patient and robot
        """
        if len(self.canvas.strokes) < 2:
            return False

        last_two = self.canvas.strokes[-2:]
        return last_two[0].agent != last_two[1].agent

    def reset(self) -> None:
        """Reset environment for a new simulation run."""
        self.canvas = Canvas()
        self.current_timestep = 0
        self.idle_duration = 0
        self.last_actor = None
        self.session_start_time = datetime.now()

    def to_dict(self) -> Dict:
        """Convert environment state to dictionary for logging."""
        return {
            'robot_mode': self.robot_mode,
            'current_timestep': self.current_timestep,
            'idle_duration': self.idle_duration,
            'last_actor': self.last_actor,
            'canvas': self.canvas.to_dict(),
            'canvas_state': self.get_canvas_state().to_dict()
        }
