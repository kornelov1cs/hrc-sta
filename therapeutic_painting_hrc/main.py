#!/usr/bin/env python3
"""
Command-line interface for therapeutic painting HRC simulation.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from simulation import TherapeuticPaintingSimulation, run_comparative_study
from utils import PatientState


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Therapeutic Collaborative Painting HRC Simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run single proactive simulation
  python main.py --mode proactive --steps 30

  # Run single reactive simulation
  python main.py --mode reactive --steps 30 --no-noise

  # Run comparative study
  python main.py --compare --runs 5 --steps 30

  # Run with specific initial patient state
  python main.py --mode proactive --initial-state Frustrated
        """
    )

    parser.add_argument(
        '--mode',
        choices=['proactive', 'reactive'],
        default='proactive',
        help='Robot behavior mode (default: proactive)'
    )

    parser.add_argument(
        '--steps',
        type=int,
        default=30,
        help='Number of simulation timesteps (default: 30)'
    )

    parser.add_argument(
        '--initial-state',
        choices=['Engaged', 'NeedsSupport', 'Hesitant', 'Satisfied', 'Frustrated'],
        default='Hesitant',
        help='Initial patient state (default: Hesitant)'
    )

    parser.add_argument(
        '--no-noise',
        action='store_true',
        help='Disable sensor noise'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress step-by-step output'
    )

    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save results to file'
    )

    parser.add_argument(
        '--compare',
        action='store_true',
        help='Run comparative study (proactive vs reactive)'
    )

    parser.add_argument(
        '--runs',
        type=int,
        default=5,
        help='Number of runs per condition in comparative study (default: 5)'
    )

    args = parser.parse_args()

    # Map string to PatientState enum
    state_map = {
        'Engaged': PatientState.ENGAGED,
        'NeedsSupport': PatientState.NEEDS_SUPPORT,
        'Hesitant': PatientState.HESITANT,
        'Satisfied': PatientState.SATISFIED,
        'Frustrated': PatientState.FRUSTRATED
    }
    initial_state = state_map[args.initial_state]

    if args.compare:
        # Run comparative study
        results = run_comparative_study(
            num_steps=args.steps,
            num_runs=args.runs
        )
        print("\nComparative study complete. Check data/simulation_logs/ for results.")
    else:
        # Run single simulation
        sim = TherapeuticPaintingSimulation(
            mode=args.mode,
            num_steps=args.steps,
            initial_patient_state=initial_state,
            add_noise=not args.no_noise
        )

        sim.run(verbose=not args.quiet)

        if not args.no_save:
            sim.save_results()


if __name__ == '__main__':
    main()
