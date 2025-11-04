"""
Fabric.js Canvas Component for Streamlit
A custom component providing professional drawing capabilities with real-time collaboration.
"""

import os
import streamlit.components.v1 as components

# Create a _RELEASE constant to determine if we're in development or production
_RELEASE = True

# Declare component
if not _RELEASE:
    _component_func = components.declare_component(
        "fabric_canvas",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend")
    _component_func = components.declare_component("fabric_canvas", path=build_dir)


def fabric_canvas(
    width=800,
    height=600,
    brush_color="#FF0000",
    brush_size=5,
    robot_strokes=None,
    clear_canvas=False,
    key=None
):
    """
    Create a collaborative drawing canvas using Fabric.js.

    Parameters
    ----------
    width : int
        Canvas width in pixels (default: 800)
    height : int
        Canvas height in pixels (default: 600)
    brush_color : str
        Initial brush color in hex format (default: "#FF0000")
    brush_size : int
        Initial brush size in pixels (default: 5)
    robot_strokes : list
        List of robot strokes to add to canvas. Each stroke should be a dict with:
        - x: x-coordinate
        - y: y-coordinate
        - color: hex color string
        - size: stroke size
        - shape: one of ['circle', 'square', 'line', 'splash']
    clear_canvas : bool
        If True, clears the canvas (default: False)
    key : str
        An optional key that uniquely identifies this component

    Returns
    -------
    dict or None
        Returns stroke data when user draws on canvas:
        - type: 'new_stroke' or 'all_strokes'
        - data: stroke information
    """
    robot_strokes = robot_strokes or []

    component_value = _component_func(
        width=width,
        height=height,
        color=brush_color,
        brushSize=brush_size,
        robot_strokes=robot_strokes,
        clear_canvas=clear_canvas,
        key=key,
        default=None
    )

    return component_value


__all__ = ['fabric_canvas']
