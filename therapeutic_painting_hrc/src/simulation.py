"""
Main simulation module implementing the sense-think-act loop for
therapeutic collaborative painting.
"""

import json
from typing import Dict, List
from datetime import datetime
from pathlib import Path

from environment import TherapyEnvironment
from patient_simulator import PatientSimulator
from intent_recognition import PatientIntentHMM
from robot_controller import RobotBDI
from utils import PatientState, Observation, format_timestamp


class TherapeuticPaintingSimulation:
    """
    Main simulation coordinating patient, robot, and environment.
    Implements sense-think-act loop.
    """

    def __init__(
        self,
        mode: str = 'proactive',
        num_steps: int = 30,
        initial_patient_state: PatientState = PatientState.HESITANT,
        add_noise: bool = True
    ):
        """
        Initialize simulation.

        Args:
            mode: 'proactive' or 'reactive'
            num_steps: Number of simulation timesteps
            initial_patient_state: Initial patient state
            add_noise: Whether to add sensor noise
        """
        self.mode = mode
        self.num_steps = num_steps
        self.add_noise = add_noise

        # Initialize components
        self.environment = TherapyEnvironment(robot_mode=mode)
        self.patient = PatientSimulator(initial_state=initial_patient_state)
        self.hmm = PatientIntentHMM()
        self.robot = RobotBDI(mode=mode)

        # Logging
        self.history: Dict[str, List] = {
            'timesteps': [],
            'patient_true_states': [],
            'patient_observations': [],
            'patient_actions': [],
            'robot_beliefs': [],
            'robot_most_likely_state': [],
            'robot_confidence': [],
            'robot_actions': [],
            'canvas_states': [],
            'engagement_scores': [],
            'idle_durations': [],
            'turn_taking': [],
            'belief_entropy': []
        }

        self.run_id = None
        self.run_timestamp = None

    def run(self, verbose: bool = True) -> Dict:
        """
        Run the simulation for specified number of timesteps.

        Args:
            verbose: Whether to print step-by-step updates

        Returns:
            Dictionary with simulation history
        """
        self.run_timestamp = datetime.now()
        self.run_id = f"{self.mode}_{self.run_timestamp.strftime('%Y%m%d_%H%M%S')}"

        if verbose:
            print(f"\n{'='*60}")
            print(f"Therapeutic Painting Simulation - {self.mode.upper()} Mode")
            print(f"{'='*60}\n")
            print(f"Initial Patient State: {self.patient.true_state.value}")
            print(f"Timesteps: {self.num_steps}\n")

        for step in range(self.num_steps):
            if verbose:
                print(f"\n--- Step {step} [{format_timestamp(step)}] ---")

            # === SENSE ===
            observation = self._sense(verbose)

            # === THINK ===
            robot_action, robot_params = self._think(observation, verbose)

            # === ACT ===
            self._act(robot_action, robot_params, verbose)

            # === LOG ===
            self._log_step(step, observation, robot_action)

            # === UPDATE ===
            self._update_states(robot_action)

            # Advance time
            self.environment.step()

        if verbose:
            print(f"\n{'='*60}")
            print("Simulation Complete")
            print(f"{'='*60}\n")
            self._print_summary()

        return self.history

    def _sense(self, verbose: bool) -> Observation:
        """
        SENSE: Observe patient behavior.

        Args:
            verbose: Whether to print

        Returns:
            Patient observation
        """
        observation = self.patient.generate_observation(add_noise=self.add_noise)

        if verbose:
            print(f"  SENSE: Patient observed -> {observation.value}")
            if self.add_noise:
                print(f"         (True state: {self.patient.true_state.value})")

        return observation

    def _think(self, observation: Observation, verbose: bool) -> tuple:
        """
        THINK: Update beliefs and plan robot action.

        Args:
            observation: Patient observation
            verbose: Whether to print

        Returns:
            Tuple of (robot_action, robot_params)
        """
        # Update HMM beliefs
        self.hmm.update_belief(observation)
        most_likely, confidence = self.hmm.get_most_likely_state()

        if verbose:
            print(f"  THINK: HMM inference -> {most_likely.value} ({confidence:.2f})")

        # Update robot beliefs
        canvas_state = self.environment.get_canvas_state()

        # Convert canvas strokes to dict format for intelligent painter
        canvas_strokes = [s.to_dict() for s in self.environment.canvas.strokes]

        self.robot.perceive(
            hmm=self.hmm,
            canvas_state=canvas_state.to_dict(),
            idle_duration=self.environment.idle_duration,
            turn_taking_smooth=self.environment.is_turn_taking_smooth(),
            canvas_strokes=canvas_strokes
        )

        # Deliberate and plan
        active_desire = self.robot.deliberate()
        self.robot.plan()

        if verbose:
            print(f"         Active desire: {active_desire.name}")

        # Execute
        robot_action, robot_params = self.robot.execute()

        if verbose:
            print(f"         Robot decides: {robot_action}")

        return robot_action, robot_params

    def _act(self, robot_action: str, robot_params: Dict, verbose: bool) -> None:
        """
        ACT: Execute patient and robot actions.

        Args:
            robot_action: Robot action to execute
            robot_params: Robot action parameters
            verbose: Whether to print
        """
        # Patient acts based on their observation
        patient_action_type, patient_params = self.patient.get_painting_action(
            self.patient.last_observation
        )

        # Apply actions to environment
        if patient_action_type:
            self.environment.apply_patient_action(patient_action_type, patient_params)
            if verbose:
                print(f"  ACT:   Patient -> {patient_action_type}")

        self.environment.apply_robot_action(robot_action, robot_params)
        if verbose:
            print(f"         Robot -> {robot_action}")

    def _log_step(self, step: int, observation: Observation, robot_action: str) -> None:
        """
        Log data from current timestep.

        Args:
            step: Current timestep
            observation: Patient observation
            robot_action: Robot action taken
        """
        canvas_state = self.environment.get_canvas_state()
        most_likely, confidence = self.hmm.get_most_likely_state()

        self.history['timesteps'].append(step)
        self.history['patient_true_states'].append(self.patient.true_state.value)
        self.history['patient_observations'].append(observation.value)
        self.history['patient_actions'].append(
            'paint' if observation in [Observation.DRAWING, Observation.LONG_STROKE, Observation.SHORT_STROKE]
            else 'idle'
        )
        self.history['robot_beliefs'].append(self.hmm.get_belief_dict())
        self.history['robot_most_likely_state'].append(most_likely.value)
        self.history['robot_confidence'].append(confidence)
        self.history['robot_actions'].append(robot_action)
        self.history['canvas_states'].append(canvas_state.to_dict())
        self.history['engagement_scores'].append(self.patient.engagement_level)
        self.history['idle_durations'].append(self.environment.idle_duration)
        self.history['turn_taking'].append(self.environment.is_turn_taking_smooth())
        self.history['belief_entropy'].append(self.hmm.get_belief_entropy())

    def _update_states(self, robot_action: str) -> None:
        """
        Update patient state based on robot action and environment.

        Args:
            robot_action: Robot action that was taken
        """
        canvas_state = self.environment.get_canvas_state().to_dict()
        self.patient.update_state(robot_action=robot_action, canvas_state=canvas_state)

    def _print_summary(self) -> None:
        """Print simulation summary statistics."""
        total_strokes = self.history['canvas_states'][-1]['total_strokes']
        patient_strokes = self.history['canvas_states'][-1]['patient_strokes']
        robot_strokes = self.history['canvas_states'][-1]['robot_strokes']
        avg_engagement = sum(self.history['engagement_scores']) / len(self.history['engagement_scores'])
        max_idle = max(self.history['idle_durations'])
        avg_idle = sum(self.history['idle_durations']) / len(self.history['idle_durations'])
        smooth_turns = sum(self.history['turn_taking'])
        avg_confidence = sum(self.history['robot_confidence']) / len(self.history['robot_confidence'])

        print("Summary Statistics:")
        print(f"  Total Strokes: {total_strokes} (Patient: {patient_strokes}, Robot: {robot_strokes})")
        print(f"  Average Engagement: {avg_engagement:.2f}")
        print(f"  Idle Time: max={max_idle}, avg={avg_idle:.2f}")
        print(f"  Smooth Turn-Taking: {smooth_turns} / {len(self.history['turn_taking'])}")
        print(f"  Average Robot Confidence: {avg_confidence:.2f}")
        print(f"  Final Canvas Coverage: {self.history['canvas_states'][-1]['coverage']:.2%}")

    def save_results(self, output_dir: str = '../data/simulation_logs') -> str:
        """
        Save simulation results to JSON file.

        Args:
            output_dir: Directory to save results

        Returns:
            Path to saved file
        """
        # Create output directory
        output_path = Path(__file__).parent.parent / 'data' / 'simulation_logs'
        output_path.mkdir(parents=True, exist_ok=True)

        # Prepare data
        results = {
            'run_id': self.run_id,
            'mode': self.mode,
            'timestamp': self.run_timestamp.isoformat(),
            'num_steps': self.num_steps,
            'add_noise': self.add_noise,
            'history': self.history,
            'summary': self._get_summary_stats()
        }

        # Save to file
        filename = f"{self.run_id}.json"
        filepath = output_path / filename

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to: {filepath}")
        return str(filepath)

    def _get_summary_stats(self) -> Dict:
        """
        Calculate summary statistics.

        Returns:
            Dictionary of summary statistics
        """
        if not self.history['timesteps']:
            return {}

        return {
            'total_strokes': self.history['canvas_states'][-1]['total_strokes'],
            'patient_strokes': self.history['canvas_states'][-1]['patient_strokes'],
            'robot_strokes': self.history['canvas_states'][-1]['robot_strokes'],
            'avg_engagement': sum(self.history['engagement_scores']) / len(self.history['engagement_scores']),
            'min_engagement': min(self.history['engagement_scores']),
            'max_engagement': max(self.history['engagement_scores']),
            'max_idle_duration': max(self.history['idle_durations']),
            'avg_idle_duration': sum(self.history['idle_durations']) / len(self.history['idle_durations']),
            'total_idle_steps': sum(1 for idle in self.history['idle_durations'] if idle > 0),
            'smooth_turn_taking_count': sum(self.history['turn_taking']),
            'turn_taking_percentage': sum(self.history['turn_taking']) / len(self.history['turn_taking']) * 100,
            'avg_robot_confidence': sum(self.history['robot_confidence']) / len(self.history['robot_confidence']),
            'final_coverage': self.history['canvas_states'][-1]['coverage'],
            'avg_belief_entropy': sum(self.history['belief_entropy']) / len(self.history['belief_entropy'])
        }

    def reset(self) -> None:
        """Reset simulation for new run."""
        self.environment.reset()
        self.patient.reset()
        self.hmm.reset()
        self.robot.reset()
        self.history = {key: [] for key in self.history.keys()}
        self.run_id = None
        self.run_timestamp = None


def run_comparative_study(num_steps: int = 30, num_runs: int = 5) -> Dict[str, List[Dict]]:
    """
    Run comparative study of proactive vs reactive modes.

    Args:
        num_steps: Timesteps per simulation
        num_runs: Number of runs per condition

    Returns:
        Dictionary with results for each mode
    """
    results = {'proactive': [], 'reactive': []}

    print("\n" + "="*70)
    print("COMPARATIVE STUDY: Proactive vs Reactive Robot Collaboration")
    print("="*70 + "\n")

    for mode in ['proactive', 'reactive']:
        print(f"\n{'*'*70}")
        print(f"Running {mode.upper()} mode simulations ({num_runs} runs)")
        print('*'*70)

        for run in range(num_runs):
            print(f"\n--- {mode.upper()} Run {run + 1}/{num_runs} ---")

            sim = TherapeuticPaintingSimulation(
                mode=mode,
                num_steps=num_steps,
                initial_patient_state=PatientState.HESITANT
            )

            sim.run(verbose=False)
            filepath = sim.save_results()

            results[mode].append({
                'run': run + 1,
                'filepath': filepath,
                'summary': sim._get_summary_stats()
            })

    print("\n" + "="*70)
    print("Comparative Study Complete!")
    print("="*70 + "\n")

    # Print comparison
    _print_comparison(results)

    return results


def _print_comparison(results: Dict[str, List[Dict]]) -> None:
    """Print comparison of proactive vs reactive results."""
    print("\nCOMPARATIVE RESULTS:")
    print("-" * 70)

    metrics = [
        ('avg_engagement', 'Average Engagement'),
        ('total_strokes', 'Total Strokes'),
        ('max_idle_duration', 'Max Idle Duration'),
        ('turn_taking_percentage', 'Turn-Taking %'),
        ('avg_robot_confidence', 'Avg Robot Confidence')
    ]

    for metric_key, metric_name in metrics:
        proactive_values = [r['summary'][metric_key] for r in results['proactive']]
        reactive_values = [r['summary'][metric_key] for r in results['reactive']]

        pro_mean = sum(proactive_values) / len(proactive_values)
        react_mean = sum(reactive_values) / len(reactive_values)

        print(f"\n{metric_name}:")
        print(f"  Proactive: {pro_mean:.2f}")
        print(f"  Reactive:  {react_mean:.2f}")
        print(f"  Difference: {pro_mean - react_mean:+.2f}")
