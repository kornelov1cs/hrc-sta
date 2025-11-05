"""
Path generation module for creating continuous, flowing strokes.

Provides various algorithms to generate natural-looking continuous paths
for robot drawing strokes, making them appear more human-like and artistic.
"""

import numpy as np
from typing import List, Tuple
import math


class PathGenerator:
    """Generates continuous paths for robot drawing strokes."""

    def __init__(self, canvas_width: int = 800, canvas_height: int = 600):
        """
        Initialize path generator.

        Args:
            canvas_width: Canvas width in pixels
            canvas_height: Canvas height in pixels
        """
        self.width = canvas_width
        self.height = canvas_height

    def generate_smooth_curve(
        self,
        start_pos: Tuple[int, int],
        length: float,
        direction: float = None,
        curvature: float = 0.3,
        num_points: int = 50
    ) -> List[Tuple[int, int]]:
        """
        Generate a smooth, flowing curve using Catmull-Rom spline.

        Args:
            start_pos: Starting position (x, y)
            length: Length of the curve in pixels
            direction: Initial direction in radians (None for random)
            curvature: How much the curve bends (0.0-1.0)
            num_points: Number of points in the path

        Returns:
            List of (x, y) points forming a smooth curve
        """
        if direction is None:
            direction = np.random.uniform(0, 2 * np.pi)

        # Generate control points for the curve
        control_points = []
        x, y = start_pos
        current_dir = direction

        # Create 4-6 control points
        num_control = np.random.randint(4, 7)
        segment_length = length / (num_control - 1)

        for i in range(num_control):
            control_points.append((x, y))

            # Vary direction for natural curvature
            current_dir += np.random.uniform(-curvature, curvature)

            # Move to next control point
            x += segment_length * np.cos(current_dir)
            y += segment_length * np.sin(current_dir)

            # Keep within canvas bounds
            x = np.clip(x, 10, self.width - 10)
            y = np.clip(y, 10, self.height - 10)

        # Interpolate smooth curve through control points
        path = self._catmull_rom_spline(control_points, num_points)

        return path

    def generate_wavy_line(
        self,
        start_pos: Tuple[int, int],
        end_pos: Tuple[int, int],
        frequency: float = 2.0,
        amplitude: float = 20.0,
        num_points: int = 50
    ) -> List[Tuple[int, int]]:
        """
        Generate a wavy line between two points.

        Args:
            start_pos: Starting position (x, y)
            end_pos: Ending position (x, y)
            frequency: Number of waves
            amplitude: Height of waves in pixels
            num_points: Number of points in the path

        Returns:
            List of (x, y) points forming a wavy line
        """
        x1, y1 = start_pos
        x2, y2 = end_pos

        # Calculate line direction and perpendicular
        dx = x2 - x1
        dy = y2 - y1
        length = np.sqrt(dx**2 + dy**2)

        if length == 0:
            return [start_pos]

        # Unit vector along the line
        ux = dx / length
        uy = dy / length

        # Perpendicular vector
        px = -uy
        py = ux

        path = []
        for i in range(num_points):
            t = i / (num_points - 1)

            # Linear interpolation along the line
            base_x = x1 + t * dx
            base_y = y1 + t * dy

            # Add sinusoidal wave perpendicular to line
            wave_offset = amplitude * np.sin(t * frequency * 2 * np.pi)
            x = base_x + wave_offset * px
            y = base_y + wave_offset * py

            path.append((int(round(x)), int(round(y))))

        return path

    def generate_spiral(
        self,
        center: Tuple[int, int],
        start_radius: float,
        end_radius: float,
        turns: float = 2.0,
        num_points: int = 100
    ) -> List[Tuple[int, int]]:
        """
        Generate a spiral path.

        Args:
            center: Center position (x, y)
            start_radius: Starting radius in pixels
            end_radius: Ending radius in pixels
            turns: Number of complete turns
            num_points: Number of points in the path

        Returns:
            List of (x, y) points forming a spiral
        """
        cx, cy = center
        path = []

        for i in range(num_points):
            t = i / (num_points - 1)

            # Radius grows/shrinks linearly
            radius = start_radius + t * (end_radius - start_radius)

            # Angle increases for spiral effect
            angle = t * turns * 2 * np.pi

            # Calculate position
            x = cx + radius * np.cos(angle)
            y = cy + radius * np.sin(angle)

            # Keep within canvas bounds
            x = np.clip(x, 0, self.width)
            y = np.clip(y, 0, self.height)

            path.append((int(round(x)), int(round(y))))

        return path

    def generate_zigzag(
        self,
        start_pos: Tuple[int, int],
        end_pos: Tuple[int, int],
        amplitude: float = 30.0,
        segments: int = 8,
        num_points: int = 50
    ) -> List[Tuple[int, int]]:
        """
        Generate an energetic zigzag path.

        Args:
            start_pos: Starting position (x, y)
            end_pos: Ending position (x, y)
            amplitude: Width of zigzag in pixels
            segments: Number of zigzag segments
            num_points: Number of points in the path

        Returns:
            List of (x, y) points forming a zigzag
        """
        x1, y1 = start_pos
        x2, y2 = end_pos

        # Calculate line direction and perpendicular
        dx = x2 - x1
        dy = y2 - y1
        length = np.sqrt(dx**2 + dy**2)

        if length == 0:
            return [start_pos]

        # Unit vectors
        ux = dx / length
        uy = dy / length
        px = -uy
        py = ux

        path = []
        for i in range(num_points):
            t = i / (num_points - 1)

            # Linear interpolation along the line
            base_x = x1 + t * dx
            base_y = y1 + t * dy

            # Zigzag pattern using triangle wave
            zigzag_t = (t * segments) % 1.0
            zigzag_offset = (2 * abs(zigzag_t - 0.5) - 0.5) * 2 * amplitude

            x = base_x + zigzag_offset * px
            y = base_y + zigzag_offset * py

            path.append((int(round(x)), int(round(y))))

        return path

    def generate_circle_path(
        self,
        center: Tuple[int, int],
        radius: float,
        start_angle: float = 0,
        end_angle: float = 2 * np.pi,
        num_points: int = 50
    ) -> List[Tuple[int, int]]:
        """
        Generate a circular or arc path.

        Args:
            center: Center position (x, y)
            radius: Circle radius in pixels
            start_angle: Starting angle in radians
            end_angle: Ending angle in radians
            num_points: Number of points in the path

        Returns:
            List of (x, y) points forming a circle/arc
        """
        cx, cy = center
        path = []

        for i in range(num_points):
            t = i / (num_points - 1)
            angle = start_angle + t * (end_angle - start_angle)

            x = cx + radius * np.cos(angle)
            y = cy + radius * np.sin(angle)

            path.append((int(round(x)), int(round(y))))

        return path

    def generate_bezier_curve(
        self,
        start_pos: Tuple[int, int],
        control1: Tuple[int, int],
        control2: Tuple[int, int],
        end_pos: Tuple[int, int],
        num_points: int = 50
    ) -> List[Tuple[int, int]]:
        """
        Generate a cubic Bezier curve.

        Args:
            start_pos: Starting position (x, y)
            control1: First control point (x, y)
            control2: Second control point (x, y)
            end_pos: Ending position (x, y)
            num_points: Number of points in the path

        Returns:
            List of (x, y) points forming a Bezier curve
        """
        path = []

        for i in range(num_points):
            t = i / (num_points - 1)

            # Cubic Bezier formula
            x = (1-t)**3 * start_pos[0] + \
                3 * (1-t)**2 * t * control1[0] + \
                3 * (1-t) * t**2 * control2[0] + \
                t**3 * end_pos[0]

            y = (1-t)**3 * start_pos[1] + \
                3 * (1-t)**2 * t * control1[1] + \
                3 * (1-t) * t**2 * control2[1] + \
                t**3 * end_pos[1]

            path.append((int(round(x)), int(round(y))))

        return path

    def add_organic_variation(
        self,
        path: List[Tuple[int, int]],
        noise_amount: float = 2.0
    ) -> List[Tuple[int, int]]:
        """
        Add subtle random variation to make path look more organic.

        Args:
            path: Original path
            noise_amount: Amount of random noise to add (in pixels)

        Returns:
            Path with added variation
        """
        varied_path = []

        for x, y in path:
            # Add random offset
            dx = np.random.uniform(-noise_amount, noise_amount)
            dy = np.random.uniform(-noise_amount, noise_amount)

            new_x = int(round(x + dx))
            new_y = int(round(y + dy))

            # Keep within canvas bounds
            new_x = np.clip(new_x, 0, self.width)
            new_y = np.clip(new_y, 0, self.height)

            varied_path.append((new_x, new_y))

        return varied_path

    def _catmull_rom_spline(
        self,
        control_points: List[Tuple[float, float]],
        num_points: int
    ) -> List[Tuple[int, int]]:
        """
        Generate smooth curve through control points using Catmull-Rom spline.

        Args:
            control_points: List of control points
            num_points: Total number of points to generate

        Returns:
            Smooth curve through control points
        """
        if len(control_points) < 2:
            return [(int(round(p[0])), int(round(p[1]))) for p in control_points]

        # Extend endpoints for better curve behavior
        extended_points = [control_points[0]] + control_points + [control_points[-1]]

        path = []
        num_segments = len(control_points) - 1
        points_per_segment = max(num_points // num_segments, 2)

        for i in range(1, len(extended_points) - 2):
            p0 = extended_points[i - 1]
            p1 = extended_points[i]
            p2 = extended_points[i + 1]
            p3 = extended_points[i + 2]

            for j in range(points_per_segment):
                t = j / points_per_segment

                # Catmull-Rom formula
                x = 0.5 * (
                    (2 * p1[0]) +
                    (-p0[0] + p2[0]) * t +
                    (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0]) * t**2 +
                    (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0]) * t**3
                )

                y = 0.5 * (
                    (2 * p1[1]) +
                    (-p0[1] + p2[1]) * t +
                    (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1]) * t**2 +
                    (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1]) * t**3
                )

                path.append((int(round(x)), int(round(y))))

        # Add final point
        final = control_points[-1]
        path.append((int(round(final[0])), int(round(final[1]))))

        return path

    def generate_contextual_path(
        self,
        start_pos: Tuple[int, int],
        size: float,
        style: str = 'smooth',
        direction: float = None
    ) -> List[Tuple[int, int]]:
        """
        Generate a contextual path based on style descriptor.

        Args:
            start_pos: Starting position
            size: Size/length of the stroke
            style: Style descriptor ('smooth', 'energetic', 'playful', 'structured', 'calming')
            direction: Optional preferred direction in radians

        Returns:
            List of points forming the path
        """
        if direction is None:
            direction = np.random.uniform(0, 2 * np.pi)

        length = size * 3  # Path length proportional to size

        if style == 'smooth' or style == 'calming':
            # Smooth, flowing curve
            return self.generate_smooth_curve(
                start_pos,
                length,
                direction,
                curvature=0.2,
                num_points=int(length / 2)
            )

        elif style == 'energetic':
            # Energetic zigzag
            end_x = start_pos[0] + length * np.cos(direction)
            end_y = start_pos[1] + length * np.sin(direction)
            end_pos = (
                int(np.clip(end_x, 0, self.width)),
                int(np.clip(end_y, 0, self.height))
            )
            return self.generate_zigzag(
                start_pos,
                end_pos,
                amplitude=size * 0.5,
                segments=8,
                num_points=50
            )

        elif style == 'playful':
            # Spiral
            return self.generate_spiral(
                start_pos,
                start_radius=size * 0.5,
                end_radius=size * 1.5,
                turns=2.0,
                num_points=80
            )

        elif style == 'structured':
            # Controlled curve with less variation
            return self.generate_smooth_curve(
                start_pos,
                length,
                direction,
                curvature=0.15,
                num_points=int(length / 3)
            )

        elif style == 'flowing':
            # Wavy, organic flow
            end_x = start_pos[0] + length * np.cos(direction)
            end_y = start_pos[1] + length * np.sin(direction)
            end_pos = (
                int(np.clip(end_x, 0, self.width)),
                int(np.clip(end_y, 0, self.height))
            )
            return self.generate_wavy_line(
                start_pos,
                end_pos,
                frequency=2.5,
                amplitude=size * 0.3,
                num_points=60
            )

        else:
            # Default to smooth curve
            return self.generate_smooth_curve(
                start_pos,
                length,
                direction,
                curvature=0.3,
                num_points=50
            )
