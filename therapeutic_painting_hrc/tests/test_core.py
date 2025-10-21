"""
Basic unit tests for therapeutic painting simulation components.
Run with: python -m pytest tests/
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import numpy as np
from environment import Canvas, TherapyEnvironment, CanvasState
from patient_simulator import PatientSimulator
from intent_recognition import PatientIntentHMM
from robot_controller import RobotBDI
from utils import PatientState, Observation, Color, Shape


class TestCanvas:
    """Test Canvas functionality."""

    def test_canvas_initialization(self):
        """Test canvas initializes correctly."""
        canvas = Canvas(width=800, height=600)
        assert canvas.width == 800
        assert canvas.height == 600
        assert len(canvas.strokes) == 0
        assert canvas.get_coverage() == 0.0

    def test_add_stroke(self):
        """Test adding strokes to canvas."""
        canvas = Canvas()
        canvas.add_stroke(
            agent='patient',
            position=(100, 100),
            color=Color.RED,
            shape=Shape.CIRCLE,
            size=30,
            timestamp=0
        )
        assert len(canvas.strokes) == 1
        assert canvas.strokes[0].agent == 'patient'
        assert canvas.get_coverage() > 0

    def test_stroke_counts(self):
        """Test patient and robot stroke counting."""
        canvas = Canvas()
        canvas.add_stroke('patient', (100, 100), Color.RED, Shape.CIRCLE, 20, 0)
        canvas.add_stroke('robot', (200, 200), Color.BLUE, Shape.SQUARE, 25, 1)
        canvas.add_stroke('patient', (300, 300), Color.GREEN, Shape.LINE, 15, 2)

        assert len(canvas.get_patient_strokes()) == 2
        assert len(canvas.get_robot_strokes()) == 1


class TestPatientSimulator:
    """Test patient simulator."""

    def test_initialization(self):
        """Test patient initializes with correct state."""
        patient = PatientSimulator(initial_state=PatientState.ENGAGED)
        assert patient.true_state == PatientState.ENGAGED
        assert patient.engagement_level > 0

    def test_observation_generation(self):
        """Test observation generation."""
        patient = PatientSimulator(initial_state=PatientState.ENGAGED)
        obs = patient.generate_observation(add_noise=False)
        assert isinstance(obs, Observation)

    def test_state_update(self):
        """Test patient state updates."""
        patient = PatientSimulator(initial_state=PatientState.HESITANT)
        initial_state = patient.true_state

        # Update multiple times
        for _ in range(5):
            patient.update_state(robot_action='InitiatePaint', canvas_state={})

        # State should potentially change (though not guaranteed due to randomness)
        assert isinstance(patient.true_state, PatientState)


class TestHMM:
    """Test HMM intent recognition."""

    def test_initialization(self):
        """Test HMM initializes with uniform belief."""
        hmm = PatientIntentHMM()
        assert len(hmm.belief_state) == 5
        assert np.isclose(np.sum(hmm.belief_state), 1.0)

    def test_belief_update(self):
        """Test belief updates maintain probability distribution."""
        hmm = PatientIntentHMM()

        # Update with observation
        hmm.update_belief(Observation.DRAWING)

        assert np.isclose(np.sum(hmm.belief_state), 1.0)
        assert all(0 <= p <= 1 for p in hmm.belief_state)

    def test_most_likely_state(self):
        """Test getting most likely state."""
        hmm = PatientIntentHMM()
        hmm.update_belief(Observation.DRAWING)
        state, confidence = hmm.get_most_likely_state()

        assert isinstance(state, PatientState)
        assert 0 <= confidence <= 1

    def test_viterbi(self):
        """Test Viterbi algorithm."""
        hmm = PatientIntentHMM()
        observations = [Observation.DRAWING, Observation.PAUSED, Observation.IDLE]
        states = hmm.viterbi(observations)

        assert len(states) == 3
        assert all(isinstance(s, PatientState) for s in states)


class TestRobotController:
    """Test robot BDI controller."""

    def test_initialization(self):
        """Test robot controller initializes."""
        robot = RobotBDI(mode='proactive')
        assert robot.mode == 'proactive'
        assert len(robot.desires) > 0

    def test_different_modes(self):
        """Test proactive and reactive modes have different desires."""
        robot_pro = RobotBDI(mode='proactive')
        robot_react = RobotBDI(mode='reactive')

        pro_desire_names = [d.name for d in robot_pro.desires]
        react_desire_names = [d.name for d in robot_react.desires]

        # Proactive has "provide_structure", reactive has "respect_autonomy"
        assert 'provide_structure' in pro_desire_names
        assert 'respect_autonomy' in react_desire_names

    def test_perceive_and_execute(self):
        """Test perceive-deliberate-plan-execute cycle."""
        robot = RobotBDI(mode='proactive')
        hmm = PatientIntentHMM()

        # Update HMM
        hmm.update_belief(Observation.HESITANT)

        # Perceive
        canvas_state = CanvasState(
            coverage=0.1,
            total_strokes=2,
            patient_strokes=1,
            robot_strokes=1,
            colors_used=2,
            recent_patient_activity=0,
            recent_robot_activity=1
        )

        robot.perceive(hmm, canvas_state.to_dict(), idle_duration=0, turn_taking_smooth=False)

        # Deliberate and plan
        desire = robot.deliberate()
        robot.plan()

        # Execute
        action, params = robot.execute()

        assert action is not None
        assert isinstance(params, dict)


class TestTherapyEnvironment:
    """Test therapy environment."""

    def test_initialization(self):
        """Test environment initializes."""
        env = TherapyEnvironment(robot_mode='proactive')
        assert env.robot_mode == 'proactive'
        assert env.current_timestep == 0
        assert env.idle_duration == 0

    def test_apply_actions(self):
        """Test applying patient and robot actions."""
        env = TherapyEnvironment()

        # Apply patient action
        env.apply_patient_action('paint', {
            'position': (100, 100),
            'color': Color.RED,
            'shape': Shape.CIRCLE,
            'size': 20
        })

        assert len(env.canvas.strokes) == 1
        assert env.last_actor == 'patient'

        # Apply robot action
        env.apply_robot_action('InitiatePaint', {
            'position': (200, 200),
            'color': Color.BLUE,
            'shape': Shape.SQUARE,
            'size': 25
        })

        assert len(env.canvas.strokes) == 2
        assert env.last_actor == 'robot'

    def test_step(self):
        """Test environment timestep advancement."""
        env = TherapyEnvironment()
        initial_time = env.current_timestep

        env.step()

        assert env.current_timestep == initial_time + 1


def test_simulation_runs():
    """Integration test: full simulation runs without errors."""
    from simulation import TherapeuticPaintingSimulation

    sim = TherapeuticPaintingSimulation(
        mode='proactive',
        num_steps=5,
        initial_patient_state=PatientState.HESITANT,
        add_noise=False
    )

    history = sim.run(verbose=False)

    assert len(history['timesteps']) == 5
    assert len(history['patient_true_states']) == 5
    assert len(history['robot_actions']) == 5


if __name__ == '__main__':
    # Run tests
    import pytest
    pytest.main([__file__, '-v'])
