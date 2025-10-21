"""
Streamlit web interface for therapeutic painting HRC simulation.
"""

import streamlit as st
import sys
from pathlib import Path
import json
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from simulation import TherapeuticPaintingSimulation
from utils import PatientState
import plotting


# Page config
st.set_page_config(
    page_title="Therapeutic Painting HRC",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit app."""

    # Header
    st.markdown('<div class="main-header">🎨 Therapeutic Co-Painting HRC Simulation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Comparing Proactive vs Reactive Robot Behavior</div>', unsafe_allow_html=True)

    # Sidebar
    st.sidebar.title("Simulation Controls")

    # Mode selection
    mode_option = st.sidebar.selectbox(
        "Select Mode",
        options=["Single Run", "Comparison", "Load Results"],
        index=0
    )

    if mode_option == "Single Run":
        single_run_interface()
    elif mode_option == "Comparison":
        comparison_interface()
    else:
        load_results_interface()


def single_run_interface():
    """Interface for running a single simulation."""

    st.sidebar.markdown("---")
    st.sidebar.subheader("Configuration")

    # Parameters
    robot_mode = st.sidebar.radio(
        "Robot Mode",
        options=["proactive", "reactive"],
        index=0
    )

    num_steps = st.sidebar.slider(
        "Number of Timesteps",
        min_value=10,
        max_value=50,
        value=30,
        step=5
    )

    initial_state = st.sidebar.selectbox(
        "Initial Patient State",
        options=["Hesitant", "Engaged", "NeedsSupport", "Satisfied", "Frustrated"],
        index=0
    )

    add_noise = st.sidebar.checkbox("Add Sensor Noise", value=True)

    # Run button
    if st.sidebar.button("🚀 Run Simulation", type="primary"):
        run_single_simulation(robot_mode, num_steps, initial_state, add_noise)


def run_single_simulation(robot_mode: str, num_steps: int, initial_state_str: str, add_noise: bool):
    """Run a single simulation and display results."""

    # Map string to enum
    state_map = {
        'Engaged': PatientState.ENGAGED,
        'NeedsSupport': PatientState.NEEDS_SUPPORT,
        'Hesitant': PatientState.HESITANT,
        'Satisfied': PatientState.SATISFIED,
        'Frustrated': PatientState.FRUSTRATED
    }
    initial_state = state_map[initial_state_str]

    # Progress
    with st.spinner(f"Running {robot_mode} simulation..."):
        sim = TherapeuticPaintingSimulation(
            mode=robot_mode,
            num_steps=num_steps,
            initial_patient_state=initial_state,
            add_noise=add_noise
        )

        sim.run(verbose=False)
        st.session_state['last_simulation'] = sim

    st.success(f"Simulation complete! ({robot_mode.upper()} mode)")

    # Display results
    display_simulation_results(sim)


def display_simulation_results(sim: TherapeuticPaintingSimulation):
    """Display results from a simulation."""

    history = sim.history
    summary = sim._get_summary_stats()

    # Summary metrics
    st.subheader("📊 Summary Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Avg Engagement",
            f"{summary['avg_engagement']:.2f}",
            delta=f"{summary['max_engagement'] - summary['min_engagement']:.2f}"
        )

    with col2:
        st.metric(
            "Total Strokes",
            summary['total_strokes'],
            delta=f"P: {summary['patient_strokes']}, R: {summary['robot_strokes']}"
        )

    with col3:
        st.metric(
            "Max Idle Duration",
            f"{summary['max_idle_duration']} steps"
        )

    with col4:
        st.metric(
            "Turn-Taking",
            f"{summary['turn_taking_percentage']:.1f}%"
        )

    st.markdown("---")

    # Visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Engagement", "🧠 Beliefs", "🎨 Canvas", "📋 Details"])

    with tab1:
        st.subheader("Patient Engagement Over Time")
        fig_engagement = plotting.plot_engagement_timeline(
            history['timesteps'],
            history['engagement_scores'],
            history['robot_actions']
        )
        st.pyplot(fig_engagement)

        st.subheader("Activity Timeline")
        fig_timeline = plotting.plot_action_timeline(
            history['timesteps'],
            history['patient_actions'],
            history['robot_actions']
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

    with tab2:
        st.subheader("Robot Belief Evolution (HMM)")
        fig_belief = plotting.plot_belief_evolution(
            history['robot_beliefs'],
            history['timesteps']
        )
        st.pyplot(fig_belief)

        st.subheader("Belief Heatmap")
        fig_heatmap = plotting.plot_belief_heatmap(
            history['robot_beliefs'],
            history['timesteps']
        )
        st.pyplot(fig_heatmap)

    with tab3:
        st.subheader("Collaborative Painting Canvas")
        canvas_strokes = sim.environment.canvas.strokes
        stroke_dicts = [s.to_dict() for s in canvas_strokes]

        if stroke_dicts:
            fig_canvas = plotting.plot_canvas(stroke_dicts)
            st.pyplot(fig_canvas)
        else:
            st.info("No strokes on canvas yet.")

    with tab4:
        st.subheader("Detailed History")

        # Create DataFrame
        df = pd.DataFrame({
            'Timestep': history['timesteps'],
            'Patient State': history['patient_true_states'],
            'Observation': history['patient_observations'],
            'Robot Belief': history['robot_most_likely_state'],
            'Confidence': [f"{c:.2f}" for c in history['robot_confidence']],
            'Robot Action': history['robot_actions'],
            'Engagement': [f"{e:.2f}" for e in history['engagement_scores']],
            'Idle': history['idle_durations']
        })

        st.dataframe(df, use_container_width=True, height=400)

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name=f"{sim.run_id}_history.csv",
            mime="text/csv"
        )


def comparison_interface():
    """Interface for comparing proactive vs reactive modes."""

    st.sidebar.markdown("---")
    st.sidebar.subheader("Configuration")

    num_steps = st.sidebar.slider(
        "Number of Timesteps",
        min_value=10,
        max_value=50,
        value=30,
        step=5
    )

    initial_state = st.sidebar.selectbox(
        "Initial Patient State",
        options=["Hesitant", "Engaged", "NeedsSupport", "Satisfied", "Frustrated"],
        index=0
    )

    add_noise = st.sidebar.checkbox("Add Sensor Noise", value=True)

    if st.sidebar.button("🔄 Run Comparison", type="primary"):
        run_comparison(num_steps, initial_state, add_noise)


def run_comparison(num_steps: int, initial_state_str: str, add_noise: bool):
    """Run and compare proactive vs reactive simulations."""

    state_map = {
        'Engaged': PatientState.ENGAGED,
        'NeedsSupport': PatientState.NEEDS_SUPPORT,
        'Hesitant': PatientState.HESITANT,
        'Satisfied': PatientState.SATISFIED,
        'Frustrated': PatientState.FRUSTRATED
    }
    initial_state = state_map[initial_state_str]

    # Run both simulations
    col1, col2 = st.columns(2)

    with col1:
        with st.spinner("Running PROACTIVE simulation..."):
            sim_proactive = TherapeuticPaintingSimulation(
                mode='proactive',
                num_steps=num_steps,
                initial_patient_state=initial_state,
                add_noise=add_noise
            )
            sim_proactive.run(verbose=False)

    with col2:
        with st.spinner("Running REACTIVE simulation..."):
            sim_reactive = TherapeuticPaintingSimulation(
                mode='reactive',
                num_steps=num_steps,
                initial_patient_state=initial_state,
                add_noise=add_noise
            )
            sim_reactive.run(verbose=False)

    st.success("Both simulations complete!")

    # Store in session state
    st.session_state['comparison'] = {
        'proactive': sim_proactive,
        'reactive': sim_reactive
    }

    # Display comparison
    display_comparison(sim_proactive, sim_reactive)


def display_comparison(sim_proactive: TherapeuticPaintingSimulation, sim_reactive: TherapeuticPaintingSimulation):
    """Display comparison of two simulations."""

    st.subheader("📊 Comparative Analysis: Proactive vs Reactive")

    summary_pro = sim_proactive._get_summary_stats()
    summary_react = sim_reactive._get_summary_stats()

    # Summary comparison
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Avg Engagement",
            f"P: {summary_pro['avg_engagement']:.2f}",
            delta=f"R: {summary_react['avg_engagement']:.2f}"
        )

    with col2:
        st.metric(
            "Total Strokes",
            f"P: {summary_pro['total_strokes']}",
            delta=f"R: {summary_react['total_strokes']}"
        )

    with col3:
        st.metric(
            "Max Idle",
            f"P: {summary_pro['max_idle_duration']}",
            delta=f"R: {summary_react['max_idle_duration']}"
        )

    with col4:
        st.metric(
            "Turn-Taking %",
            f"P: {summary_pro['turn_taking_percentage']:.1f}",
            delta=f"R: {summary_react['turn_taking_percentage']:.1f}"
        )

    st.markdown("---")

    # Visualizations
    tab1, tab2, tab3 = st.tabs(["📈 Comparisons", "🎨 Canvases", "📋 Summary"])

    with tab1:
        st.subheader("Metric Comparisons")
        fig_comparison = plotting.plot_state_comparison(
            sim_proactive.history,
            sim_reactive.history,
            "Proactive",
            "Reactive"
        )
        st.pyplot(fig_comparison)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Proactive Canvas")
            strokes_pro = [s.to_dict() for s in sim_proactive.environment.canvas.strokes]
            if strokes_pro:
                fig_pro = plotting.plot_canvas(strokes_pro)
                st.pyplot(fig_pro)
            else:
                st.info("No strokes")

        with col2:
            st.subheader("Reactive Canvas")
            strokes_react = [s.to_dict() for s in sim_reactive.environment.canvas.strokes]
            if strokes_react:
                fig_react = plotting.plot_canvas(strokes_react)
                st.pyplot(fig_react)
            else:
                st.info("No strokes")

    with tab3:
        st.subheader("Summary Metrics Comparison")
        fig_summary = plotting.plot_summary_metrics(
            summary_pro,
            summary_react,
            "Proactive",
            "Reactive"
        )
        st.pyplot(fig_summary)

        # Detailed comparison table
        st.subheader("Detailed Statistics")

        comparison_df = pd.DataFrame({
            'Metric': [
                'Average Engagement',
                'Total Strokes',
                'Patient Strokes',
                'Robot Strokes',
                'Max Idle Duration',
                'Avg Idle Duration',
                'Turn-Taking %',
                'Avg Robot Confidence',
                'Final Coverage'
            ],
            'Proactive': [
                f"{summary_pro['avg_engagement']:.3f}",
                summary_pro['total_strokes'],
                summary_pro['patient_strokes'],
                summary_pro['robot_strokes'],
                summary_pro['max_idle_duration'],
                f"{summary_pro['avg_idle_duration']:.2f}",
                f"{summary_pro['turn_taking_percentage']:.1f}%",
                f"{summary_pro['avg_robot_confidence']:.3f}",
                f"{summary_pro['final_coverage']:.2%}"
            ],
            'Reactive': [
                f"{summary_react['avg_engagement']:.3f}",
                summary_react['total_strokes'],
                summary_react['patient_strokes'],
                summary_react['robot_strokes'],
                summary_react['max_idle_duration'],
                f"{summary_react['avg_idle_duration']:.2f}",
                f"{summary_react['turn_taking_percentage']:.1f}%",
                f"{summary_react['avg_robot_confidence']:.3f}",
                f"{summary_react['final_coverage']:.2%}"
            ]
        })

        st.dataframe(comparison_df, use_container_width=True)


def load_results_interface():
    """Interface for loading and viewing saved results."""

    st.sidebar.markdown("---")
    st.sidebar.info("Load previously saved simulation results from data/simulation_logs/")

    # Find saved results
    logs_dir = Path(__file__).parent.parent / 'data' / 'simulation_logs'

    if not logs_dir.exists():
        st.warning("No saved results found. Run some simulations first!")
        return

    json_files = list(logs_dir.glob("*.json"))

    if not json_files:
        st.warning("No saved results found. Run some simulations first!")
        return

    # File selector
    selected_file = st.sidebar.selectbox(
        "Select Result File",
        options=[f.name for f in json_files],
        index=0
    )

    if selected_file:
        filepath = logs_dir / selected_file

        # Load data
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Display info
        st.subheader(f"📁 Loaded: {selected_file}")

        st.info(f"""
        **Run ID:** {data['run_id']}
        **Mode:** {data['mode']}
        **Timesteps:** {data['num_steps']}
        **Timestamp:** {data['timestamp']}
        """)

        # Recreate simulation object for display
        # (We'll just use the history and summary)
        history = data['history']
        summary = data['summary']

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Avg Engagement", f"{summary['avg_engagement']:.2f}")

        with col2:
            st.metric("Total Strokes", summary['total_strokes'])

        with col3:
            st.metric("Max Idle", summary['max_idle_duration'])

        with col4:
            st.metric("Turn-Taking %", f"{summary['turn_taking_percentage']:.1f}%")

        # Show plots
        st.markdown("---")

        fig_engagement = plotting.plot_engagement_timeline(
            history['timesteps'],
            history['engagement_scores'],
            history['robot_actions']
        )
        st.pyplot(fig_engagement)

        fig_belief = plotting.plot_belief_evolution(
            history['robot_beliefs'],
            history['timesteps']
        )
        st.pyplot(fig_belief)


if __name__ == '__main__':
    main()
