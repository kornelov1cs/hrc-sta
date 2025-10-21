"""
Plotting functions for simulation visualization.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
import pandas as pd


def plot_canvas(canvas_strokes: List[Dict], width: int = 800, height: int = 600):
    """
    Plot the painting canvas with all strokes.

    Args:
        canvas_strokes: List of stroke dictionaries
        width: Canvas width
        height: Canvas height

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(10, 7.5))

    # Set canvas bounds
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect('equal')

    # White background
    ax.set_facecolor('white')

    # Plot each stroke
    for stroke in canvas_strokes:
        x, y = stroke['position']
        size = stroke['size']
        color = stroke['color']
        agent = stroke['agent']

        # Different shapes for patient vs robot
        if agent == 'patient':
            marker = 'o'
            alpha = 0.7
        else:
            marker = 's'
            alpha = 0.6

        ax.scatter(x, y, s=size**2, c=color, marker=marker, alpha=alpha, edgecolors='black', linewidths=0.5)

    # Legend
    patient_patch = mpatches.Patch(color='blue', label='Patient', alpha=0.7)
    robot_patch = mpatches.Patch(color='red', label='Robot', alpha=0.6)
    ax.legend(handles=[patient_patch, robot_patch], loc='upper right')

    ax.set_title('Collaborative Painting Canvas', fontsize=14, fontweight='bold')
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_belief_evolution(belief_history: List[Dict], timesteps: List[int]):
    """
    Plot evolution of robot's belief distribution over time.

    Args:
        belief_history: List of belief dictionaries
        timesteps: List of timestep numbers

    Returns:
        matplotlib Figure
    """
    # Convert to DataFrame
    states = list(belief_history[0].keys())
    data = {state: [b[state] for b in belief_history] for state in states}
    df = pd.DataFrame(data, index=timesteps)

    # Create stacked area plot
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.stackplot(
        df.index,
        *[df[state] for state in states],
        labels=states,
        alpha=0.7
    )

    ax.set_xlabel('Timestep', fontsize=12)
    ax.set_ylabel('Belief Probability', fontsize=12)
    ax.set_title('Robot Belief Distribution Over Time (HMM)', fontsize=14, fontweight='bold')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_engagement_timeline(
    timesteps: List[int],
    engagement_scores: List[float],
    robot_actions: List[str]
):
    """
    Plot patient engagement over time with robot actions annotated.

    Args:
        timesteps: Timestep numbers
        engagement_scores: Patient engagement scores
        robot_actions: Robot action labels

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(14, 5))

    # Plot engagement line
    ax.plot(timesteps, engagement_scores, linewidth=2, color='#2E86AB', marker='o', markersize=4)

    # Annotate significant robot actions
    significant_actions = ['InitiatePaint', 'SuggestColor', 'SuggestShape']
    for i, (t, action) in enumerate(zip(timesteps, robot_actions)):
        if any(sig_action in action for sig_action in significant_actions):
            ax.axvline(x=t, color='red', alpha=0.3, linestyle='--', linewidth=1)

    ax.set_xlabel('Timestep', fontsize=12)
    ax.set_ylabel('Engagement Score', fontsize=12)
    ax.set_title('Patient Engagement Over Time', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 1.1)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_action_timeline(
    timesteps: List[int],
    patient_actions: List[str],
    robot_actions: List[str]
):
    """
    Plot Gantt-style timeline of patient and robot actions.

    Args:
        timesteps: Timestep numbers
        patient_actions: Patient action labels
        robot_actions: Robot action labels

    Returns:
        plotly Figure
    """
    # Prepare data
    df_data = []

    for i, t in enumerate(timesteps):
        # Patient action
        if patient_actions[i] == 'paint':
            df_data.append({
                'Task': 'Patient',
                'Start': t,
                'Finish': t + 0.8,
                'Resource': 'Painting'
            })

        # Robot action
        if robot_actions[i] not in ['Wait', 'Observe']:
            df_data.append({
                'Task': 'Robot',
                'Start': t,
                'Finish': t + 0.8,
                'Resource': robot_actions[i]
            })

    df = pd.DataFrame(df_data)

    if df.empty:
        # Return empty figure
        fig = go.Figure()
        fig.add_annotation(
            text="No actions to display",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        return fig

    # Create Gantt chart
    fig = px.timeline(
        df,
        x_start='Start',
        x_end='Finish',
        y='Task',
        color='Resource',
        title='Activity Timeline'
    )

    fig.update_yaxes(categoryorder='total ascending')
    fig.update_layout(xaxis_title='Timestep', yaxis_title='Agent')

    return fig


def plot_state_comparison(history1: Dict, history2: Dict, label1: str, label2: str):
    """
    Compare two simulation runs side by side.

    Args:
        history1: History dict from first simulation
        history2: History dict from second simulation
        label1: Label for first simulation
        label2: Label for second simulation

    Returns:
        matplotlib Figure
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Engagement comparison
    axes[0, 0].plot(history1['timesteps'], history1['engagement_scores'],
                    label=label1, linewidth=2, marker='o', markersize=3)
    axes[0, 0].plot(history2['timesteps'], history2['engagement_scores'],
                    label=label2, linewidth=2, marker='s', markersize=3)
    axes[0, 0].set_title('Engagement Score Comparison', fontweight='bold')
    axes[0, 0].set_xlabel('Timestep')
    axes[0, 0].set_ylabel('Engagement')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Idle duration comparison
    axes[0, 1].plot(history1['timesteps'], history1['idle_durations'],
                    label=label1, linewidth=2, marker='o', markersize=3)
    axes[0, 1].plot(history2['timesteps'], history2['idle_durations'],
                    label=label2, linewidth=2, marker='s', markersize=3)
    axes[0, 1].set_title('Idle Duration Comparison', fontweight='bold')
    axes[0, 1].set_xlabel('Timestep')
    axes[0, 1].set_ylabel('Consecutive Idle Steps')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # Canvas coverage comparison
    coverage1 = [cs['coverage'] for cs in history1['canvas_states']]
    coverage2 = [cs['coverage'] for cs in history2['canvas_states']]
    axes[1, 0].plot(history1['timesteps'], coverage1,
                    label=label1, linewidth=2, marker='o', markersize=3)
    axes[1, 0].plot(history2['timesteps'], coverage2,
                    label=label2, linewidth=2, marker='s', markersize=3)
    axes[1, 0].set_title('Canvas Coverage Comparison', fontweight='bold')
    axes[1, 0].set_xlabel('Timestep')
    axes[1, 0].set_ylabel('Coverage (%)')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # Robot confidence comparison
    axes[1, 1].plot(history1['timesteps'], history1['robot_confidence'],
                    label=label1, linewidth=2, marker='o', markersize=3)
    axes[1, 1].plot(history2['timesteps'], history2['robot_confidence'],
                    label=label2, linewidth=2, marker='s', markersize=3)
    axes[1, 1].set_title('Robot Confidence Comparison', fontweight='bold')
    axes[1, 1].set_xlabel('Timestep')
    axes[1, 1].set_ylabel('Confidence in State Inference')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_summary_metrics(summary1: Dict, summary2: Dict, label1: str, label2: str):
    """
    Create bar chart comparing summary metrics.

    Args:
        summary1: Summary stats from first simulation
        summary2: Summary stats from second simulation
        label1: Label for first simulation
        label2: Label for second simulation

    Returns:
        matplotlib Figure
    """
    metrics = [
        ('avg_engagement', 'Avg Engagement'),
        ('turn_taking_percentage', 'Turn-Taking %'),
        ('avg_idle_duration', 'Avg Idle Duration'),
        ('avg_robot_confidence', 'Avg Confidence')
    ]

    values1 = [summary1[m[0]] for m in metrics]
    values2 = [summary2[m[0]] for m in metrics]
    labels = [m[1] for m in metrics]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, values1, width, label=label1, alpha=0.8)
    bars2 = ax.bar(x + width/2, values2, width, label=label2, alpha=0.8)

    ax.set_xlabel('Metric', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title('Summary Metrics Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2,
                height,
                f'{height:.2f}',
                ha='center',
                va='bottom',
                fontsize=9
            )

    plt.tight_layout()
    return fig


def plot_belief_heatmap(belief_history: List[Dict], timesteps: List[int]):
    """
    Create heatmap of belief distribution over time.

    Args:
        belief_history: List of belief dictionaries
        timesteps: Timestep numbers

    Returns:
        matplotlib Figure
    """
    states = list(belief_history[0].keys())
    data = np.array([[b[state] for state in states] for b in belief_history])

    fig, ax = plt.subplots(figsize=(12, 6))

    im = ax.imshow(data.T, aspect='auto', cmap='YlOrRd', interpolation='nearest')

    ax.set_xlabel('Timestep', fontsize=12)
    ax.set_ylabel('Patient State', fontsize=12)
    ax.set_title('Robot Belief Distribution Heatmap', fontsize=14, fontweight='bold')

    ax.set_yticks(np.arange(len(states)))
    ax.set_yticklabels(states)

    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Probability', rotation=270, labelpad=20)

    plt.tight_layout()
    return fig
