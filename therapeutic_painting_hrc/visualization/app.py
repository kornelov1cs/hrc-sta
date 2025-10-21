"""
Streamlit web interface for therapeutic painting HRC simulation.
"""

import streamlit as st
import sys
from pathlib import Path
import json
import pandas as pd
import numpy as np
from streamlit_drawable_canvas import st_canvas

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from simulation import TherapeuticPaintingSimulation
from utils import PatientState, Color, Shape, Observation
from intent_recognition import PatientIntentHMM
from robot_controller import RobotBDI
from environment import TherapyEnvironment
from intelligent_painter import IntelligentPainter
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
        options=["Single Run", "Comparison", "Load Results", "Interactive Drawing"],
        index=0
    )

    if mode_option == "Single Run":
        single_run_interface()
    elif mode_option == "Comparison":
        comparison_interface()
    elif mode_option == "Load Results":
        load_results_interface()
    else:
        interactive_drawing_interface()


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


def interactive_drawing_interface():
    """Interface for interactive drawing with robot responses."""

    st.subheader("🎨 Interactive Co-Painting")
    st.markdown("Draw on the canvas and watch the robot respond to your artwork!")

    # Initialize session state
    if 'interactive_mode' not in st.session_state:
        st.session_state.interactive_mode = 'reactive'
        st.session_state.hmm = PatientIntentHMM()
        st.session_state.robot = None
        st.session_state.environment = None
        st.session_state.intelligent_painter = None
        st.session_state.stroke_count = 0
        st.session_state.canvas_key = 0
        st.session_state.robot_strokes = []
        st.session_state.user_strokes = []
        st.session_state.interaction_history = []

    # Sidebar controls
    st.sidebar.markdown("---")
    st.sidebar.subheader("Drawing Controls")

    # Robot mode
    robot_mode = st.sidebar.radio(
        "Robot Behavior",
        options=["reactive", "proactive"],
        index=0,
        help="Reactive: Robot waits for your action. Proactive: Robot suggests and initiates."
    )

    # Update mode if changed
    if robot_mode != st.session_state.interactive_mode:
        st.session_state.interactive_mode = robot_mode
        st.session_state.robot = RobotBDI(mode=robot_mode)
        st.session_state.environment = TherapyEnvironment(robot_mode=robot_mode)
        st.session_state.intelligent_painter = IntelligentPainter(mode=robot_mode)

    # Initialize components if needed
    if st.session_state.robot is None:
        st.session_state.robot = RobotBDI(mode=robot_mode)
        st.session_state.environment = TherapyEnvironment(robot_mode=robot_mode)
        st.session_state.intelligent_painter = IntelligentPainter(mode=robot_mode)

    # Drawing settings
    stroke_width = st.sidebar.slider("Brush Size", 1, 50, 10)
    stroke_color = st.sidebar.color_picker("Brush Color", "#FF6B6B")  # Default to RED

    st.sidebar.caption("💡 Available colors: Red, Blue, Yellow, Green, Purple, Orange")

    # Text prompt for robot
    st.sidebar.markdown("---")
    st.sidebar.subheader("Prompt Robot")
    text_prompt = st.sidebar.text_input(
        "Tell the robot what to draw:",
        placeholder="e.g., 'add some blue circles'"
    )

    if st.sidebar.button("Send Prompt"):
        if text_prompt:
            robot_response = handle_text_prompt(
                text_prompt,
                st.session_state.environment,
                st.session_state.intelligent_painter
            )
            st.session_state.robot_strokes.extend(robot_response)
            st.session_state.interaction_history.append({
                'type': 'prompt',
                'content': text_prompt,
                'response': len(robot_response)
            })

    # Clear canvas button
    if st.sidebar.button("Clear Canvas"):
        st.session_state.robot_strokes = []
        st.session_state.user_strokes = []
        st.session_state.stroke_count = 0
        st.session_state.canvas_key += 1
        st.session_state.hmm.reset()
        st.session_state.environment = TherapyEnvironment(robot_mode=robot_mode)
        st.session_state.interaction_history = []
        st.rerun()

    # Main canvas area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### Your Canvas")

        # Create canvas
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_color="#FFFFFF",
            height=600,
            width=800,
            drawing_mode="freedraw",
            key=f"canvas_{st.session_state.canvas_key}",
        )

        # Display combined visualization with robot strokes
        st.markdown("#### Collaborative Painting (with Robot)")
        all_strokes = [s.to_dict() for s in st.session_state.environment.canvas.strokes]
        if all_strokes:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 7.5))
            ax.set_xlim(0, 800)
            ax.set_ylim(0, 600)
            ax.set_aspect('equal')
            ax.set_facecolor('white')
            ax.invert_yaxis()  # Match canvas coordinates

            # Plot strokes
            for stroke in all_strokes:
                x, y = stroke['position']
                size = stroke['size']

                # Get color value
                color_val = stroke['color']
                if isinstance(color_val, str):
                    color_to_use = color_val
                else:
                    # Map Color enum names to hex
                    color_map = {
                        'Red': '#FF6B6B',
                        'Blue': '#4ECDC4',
                        'Yellow': '#FFE66D',
                        'Green': '#95E1D3',
                        'Purple': '#AA96DA',
                        'Orange': '#FCBF49'
                    }
                    color_to_use = color_map.get(color_val, '#FF6B6B')

                agent = stroke['agent']

                # Different markers for user vs robot
                if agent == 'patient':
                    marker = 'o'
                    alpha = 0.7
                    edgecolor = 'darkred'
                else:
                    marker = 's'
                    alpha = 0.8
                    edgecolor = 'darkblue'
                    linewidth = 2

                ax.scatter(x, y, s=size**2, c=color_to_use, marker=marker,
                          alpha=alpha, edgecolors=edgecolor, linewidths=linewidth if agent == 'robot' else 1)

            # Legend
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='red', edgecolor='darkred', label='Your strokes'),
                Patch(facecolor='blue', edgecolor='darkblue', label='Robot strokes', linewidth=2)
            ]
            ax.legend(handles=legend_elements, loc='upper right')

            ax.set_xlabel('X Position')
            ax.set_ylabel('Y Position')
            ax.grid(True, alpha=0.2)
            plt.tight_layout()

            st.pyplot(fig)
            plt.close()

        # Process canvas changes
        if canvas_result.json_data is not None:
            objects = canvas_result.json_data.get("objects", [])

            # Check if user added new strokes
            if len(objects) > st.session_state.stroke_count:
                new_strokes = objects[st.session_state.stroke_count:]
                st.session_state.stroke_count = len(objects)

                # Process new user strokes
                user_stroke_data = process_user_strokes(new_strokes)
                st.session_state.user_strokes.extend(user_stroke_data)

                # Update environment
                for stroke in user_stroke_data:
                    st.session_state.environment.canvas.add_stroke(
                        agent='patient',
                        position=stroke['position'],
                        color=stroke['color'],
                        shape=stroke['shape'],
                        size=stroke['size'],
                        timestamp=st.session_state.environment.current_timestep
                    )

                # Infer user state and get robot response
                observation = infer_observation_from_drawing(user_stroke_data)
                robot_response = get_robot_response(
                    observation,
                    st.session_state.hmm,
                    st.session_state.robot,
                    st.session_state.environment
                )

                if robot_response:
                    st.session_state.robot_strokes.extend(robot_response)
                    st.session_state.interaction_history.append({
                        'type': 'drawing',
                        'user_strokes': len(user_stroke_data),
                        'robot_strokes': len(robot_response),
                        'observation': observation.value,
                        'belief': st.session_state.hmm.get_most_likely_state()[0].value
                    })

                st.session_state.environment.step()

    with col2:
        st.markdown("#### Robot's Mind")

        # Display current belief
        belief_dict = st.session_state.hmm.get_belief_dict()
        most_likely, confidence = st.session_state.hmm.get_most_likely_state()

        st.metric("Inferred State", most_likely.value, f"{confidence:.1%} confidence")

        # Belief distribution
        st.markdown("**Belief Distribution:**")
        for state, prob in belief_dict.items():
            st.progress(prob, text=f"{state}: {prob:.2%}")

        st.markdown("---")

        # Canvas stats
        canvas_state = st.session_state.environment.get_canvas_state()
        st.markdown("**Canvas Statistics:**")
        st.write(f"Your strokes: {canvas_state.patient_strokes}")
        st.write(f"Robot strokes: {canvas_state.robot_strokes}")
        st.write(f"Coverage: {canvas_state.coverage:.1%}")

        st.markdown("---")

        # Recent interactions
        st.markdown("**Recent Interactions:**")
        if st.session_state.interaction_history:
            for i, interaction in enumerate(reversed(st.session_state.interaction_history[-5:])):
                if interaction['type'] == 'drawing':
                    st.text(f"Draw → {interaction['observation']}")
                    st.text(f"  Belief: {interaction['belief']}")
                    st.text(f"  Robot: {interaction['robot_strokes']} strokes")
                else:
                    st.text(f"Prompt: {interaction['content'][:30]}...")
                    st.text(f"  Robot: {interaction['response']} strokes")
                st.markdown("---")
        else:
            st.info("Start drawing to see interactions!")


def process_user_strokes(canvas_objects):
    """Convert canvas drawing objects to stroke format."""
    strokes = []

    for obj in canvas_objects:
        if obj['type'] == 'path':
            # Extract path information
            path_data = obj.get('path', [])
            if not path_data:
                continue

            # Get approximate position (center of path)
            points = []
            for segment in path_data:
                if len(segment) >= 3:
                    points.append((segment[1], segment[2]))

            if not points:
                continue

            avg_x = sum(p[0] for p in points) / len(points)
            avg_y = sum(p[1] for p in points) / len(points)

            # Convert color
            color = convert_hex_to_color(obj.get('stroke', '#000000'))

            # Estimate size from stroke width
            size = int(obj.get('strokeWidth', 10))

            strokes.append({
                'position': (int(avg_x), int(avg_y)),
                'color': color,
                'shape': Shape.CIRCLE,  # Default shape
                'size': size
            })

    return strokes


def convert_hex_to_color(hex_color):
    """Convert hex color to nearest Color enum using color distance."""
    def hex_to_rgb(hex_str):
        """Convert hex string to RGB tuple."""
        hex_str = hex_str.lstrip('#')
        if len(hex_str) == 3:
            hex_str = ''.join([c*2 for c in hex_str])
        try:
            return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        except:
            return (255, 0, 0)  # Default to red if parsing fails

    def color_distance(rgb1, rgb2):
        """Calculate Euclidean distance between two RGB colors."""
        return sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)) ** 0.5

    # Convert input color to RGB
    input_rgb = hex_to_rgb(hex_color)

    # Map each Color enum to its RGB value
    color_map = {
        Color.RED: hex_to_rgb(Color.RED.value),
        Color.BLUE: hex_to_rgb(Color.BLUE.value),
        Color.YELLOW: hex_to_rgb(Color.YELLOW.value),
        Color.GREEN: hex_to_rgb(Color.GREEN.value),
        Color.PURPLE: hex_to_rgb(Color.PURPLE.value),
        Color.ORANGE: hex_to_rgb(Color.ORANGE.value),
    }

    # Find the closest color
    closest_color = min(color_map.items(), key=lambda x: color_distance(input_rgb, x[1]))
    return closest_color[0]


def infer_observation_from_drawing(stroke_data):
    """Infer patient observation from drawing activity."""
    if not stroke_data:
        return Observation.IDLE

    num_strokes = len(stroke_data)

    if num_strokes >= 3:
        return Observation.LONG_STROKE
    elif num_strokes >= 1:
        return Observation.SHORT_STROKE
    else:
        return Observation.DRAWING


def get_robot_response(observation, hmm, robot, environment):
    """Get robot's response to user drawing."""
    # Update HMM belief
    hmm.update_belief(observation)

    # Get canvas strokes for intelligent painting
    canvas_strokes = [s.to_dict() for s in environment.canvas.strokes]

    # Update robot perception
    canvas_state = environment.get_canvas_state()
    robot.perceive(
        hmm=hmm,
        canvas_state=canvas_state.to_dict(),
        idle_duration=environment.idle_duration,
        turn_taking_smooth=environment.is_turn_taking_smooth(),
        canvas_strokes=canvas_strokes
    )

    # Deliberate and plan
    robot.deliberate()
    robot.plan()

    # Execute action
    action, params = robot.execute()

    # Apply robot action to environment
    environment.apply_robot_action(action, params)

    # Return robot strokes if any were created
    robot_strokes = []
    if params and 'position' in params:
        robot_strokes.append({
            'position': params['position'],
            'color': params.get('color', Color.RED),
            'shape': params.get('shape', Shape.CIRCLE),
            'size': params.get('size', 20),
            'agent': 'robot'
        })

    return robot_strokes


def handle_text_prompt(prompt, environment, intelligent_painter):
    """Handle text prompt from user to robot using intelligent painter."""
    # Get current canvas strokes
    canvas_strokes = [s.to_dict() for s in environment.canvas.strokes]

    # Use intelligent painter to generate strokes from prompt
    generated_strokes = intelligent_painter.generate_from_prompt(
        strokes=canvas_strokes,
        prompt=prompt
    )

    # Add generated strokes to environment
    robot_strokes = []
    for stroke_params in generated_strokes:
        environment.canvas.add_stroke(
            agent='robot',
            position=stroke_params['position'],
            color=stroke_params['color'],
            shape=stroke_params['shape'],
            size=stroke_params['size'],
            timestamp=environment.current_timestep
        )

        robot_strokes.append({
            **stroke_params,
            'agent': 'robot'
        })

    environment.step()

    return robot_strokes


if __name__ == '__main__':
    main()
