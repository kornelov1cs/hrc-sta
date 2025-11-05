"""
Stroke analysis module for understanding canvas state and user drawing patterns.
Provides spatial, color, and compositional analysis for intelligent robot painting.
"""

import numpy as np
from typing import Dict, List, Tuple
from collections import Counter
from dataclasses import dataclass

from utils import Color, CANVAS_WIDTH, CANVAS_HEIGHT


@dataclass
class CanvasAnalysis:
    """Results of canvas analysis."""
    # Spatial analysis
    empty_regions: List[Tuple[int, int]]  # Centers of empty regions
    high_density_regions: List[Tuple[int, int]]  # Crowded areas
    spatial_balance: float  # 0-1, how balanced is the composition

    # Color analysis
    dominant_colors: List[Color]  # Most used colors
    color_diversity: float  # 0-1, how many different colors
    suggested_colors: List[Color]  # Harmonious color suggestions

    # Pattern analysis
    avg_stroke_size: float
    stroke_density: float  # Strokes per unit area
    user_activity_level: str  # 'low', 'medium', 'high'

    # Compositional
    needs_fill_areas: bool  # Large empty regions exist
    is_balanced: bool  # Left-right, top-bottom balance


class StrokeAnalyzer:
    """
    Analyzes canvas to understand user's drawing patterns and provide
    contextual information for intelligent robot stroke generation.
    """

    def __init__(self, canvas_width: int = CANVAS_WIDTH, canvas_height: int = CANVAS_HEIGHT):
        """
        Initialize stroke analyzer.

        Args:
            canvas_width: Canvas width in pixels
            canvas_height: Canvas height in pixels
        """
        self.width = canvas_width
        self.height = canvas_height

        # Create grid for spatial analysis
        self.grid_size = 100  # Grid cell size
        self.grid_cols = canvas_width // self.grid_size
        self.grid_rows = canvas_height // self.grid_size

    def analyze(self, strokes: List[Dict]) -> CanvasAnalysis:
        """
        Perform comprehensive canvas analysis.

        Args:
            strokes: List of stroke dictionaries with position, color, size, agent

        Returns:
            CanvasAnalysis object with analysis results
        """
        if not strokes:
            return self._empty_canvas_analysis()

        # Separate user and robot strokes
        user_strokes = [s for s in strokes if s.get('agent') == 'patient']
        # robot_strokes not currently used in analysis but available for future features

        # Perform analyses
        spatial_analysis = self._analyze_spatial(strokes)
        color_analysis = self._analyze_colors(user_strokes)
        pattern_analysis = self._analyze_patterns(user_strokes)

        return CanvasAnalysis(
            empty_regions=spatial_analysis['empty_regions'],
            high_density_regions=spatial_analysis['dense_regions'],
            spatial_balance=spatial_analysis['balance'],
            dominant_colors=color_analysis['dominant'],
            color_diversity=color_analysis['diversity'],
            suggested_colors=color_analysis['suggestions'],
            avg_stroke_size=pattern_analysis['avg_size'],
            stroke_density=pattern_analysis['density'],
            user_activity_level=pattern_analysis['activity_level'],
            needs_fill_areas=spatial_analysis['needs_fill'],
            is_balanced=spatial_analysis['is_balanced']
        )

    def _empty_canvas_analysis(self) -> CanvasAnalysis:
        """Return analysis for empty canvas."""
        return CanvasAnalysis(
            empty_regions=[(self.width // 2, self.height // 2)],
            high_density_regions=[],
            spatial_balance=1.0,
            dominant_colors=[],
            color_diversity=0.0,
            suggested_colors=[Color.BLUE, Color.RED, Color.YELLOW],
            avg_stroke_size=20.0,
            stroke_density=0.0,
            user_activity_level='low',
            needs_fill_areas=True,
            is_balanced=True
        )

    def _analyze_spatial(self, strokes: List[Dict]) -> Dict:
        """
        Analyze spatial distribution of strokes.

        Args:
            strokes: All strokes on canvas

        Returns:
            Dictionary with spatial analysis results
        """
        # Create density heatmap using grid
        density_grid = np.zeros((self.grid_rows, self.grid_cols))

        for stroke in strokes:
            pos = stroke.get('position', (0, 0))
            size = stroke.get('size', 20)

            # Find grid cell
            grid_x = min(int(pos[0] / self.grid_size), self.grid_cols - 1)
            grid_y = min(int(pos[1] / self.grid_size), self.grid_rows - 1)

            # Add density (weighted by stroke size)
            density_grid[grid_y, grid_x] += (size / 20.0)

        # Find empty regions (low density cells)
        empty_regions = []
        dense_regions = []

        threshold_empty = 0.5
        threshold_dense = 3.0

        for i in range(self.grid_rows):
            for j in range(self.grid_cols):
                center_x = j * self.grid_size + self.grid_size // 2
                center_y = i * self.grid_size + self.grid_size // 2

                if density_grid[i, j] < threshold_empty:
                    empty_regions.append((center_x, center_y))
                elif density_grid[i, j] > threshold_dense:
                    dense_regions.append((center_x, center_y))

        # Calculate balance (left-right, top-bottom)
        left_half = density_grid[:, :self.grid_cols//2].sum()
        right_half = density_grid[:, self.grid_cols//2:].sum()
        top_half = density_grid[:self.grid_rows//2, :].sum()
        bottom_half = density_grid[self.grid_rows//2:, :].sum()

        total_density = density_grid.sum()
        if total_density > 0:
            lr_balance = 1 - abs(left_half - right_half) / total_density
            tb_balance = 1 - abs(top_half - bottom_half) / total_density
            balance = (lr_balance + tb_balance) / 2
        else:
            balance = 1.0

        return {
            'empty_regions': empty_regions[:10],  # Limit to top 10
            'dense_regions': dense_regions[:5],
            'balance': balance,
            'needs_fill': len(empty_regions) > (self.grid_rows * self.grid_cols) / 3,
            'is_balanced': balance > 0.7
        }

    def _analyze_colors(self, user_strokes: List[Dict]) -> Dict:
        """
        Analyze color usage and suggest harmonious colors.

        Args:
            user_strokes: User's strokes only

        Returns:
            Dictionary with color analysis
        """
        if not user_strokes:
            return {
                'dominant': [],
                'diversity': 0.0,
                'suggestions': [Color.BLUE, Color.RED, Color.YELLOW]
            }

        # Count color usage
        colors_used = [stroke.get('color', Color.RED) for stroke in user_strokes]
        color_counts = Counter(colors_used)

        # Get dominant colors (top 3)
        dominant = [color for color, count in color_counts.most_common(3)]

        # Calculate diversity
        unique_colors = len(color_counts)
        total_possible = len(Color)
        diversity = unique_colors / total_possible

        # Suggest harmonious colors
        suggestions = self._get_harmonious_colors(dominant)

        return {
            'dominant': dominant,
            'diversity': diversity,
            'suggestions': suggestions
        }

    def _get_harmonious_colors(self, used_colors: List[Color]) -> List[Color]:
        """
        Suggest harmonious colors based on color theory.

        Args:
            used_colors: Colors already used

        Returns:
            List of suggested colors
        """
        if not used_colors:
            return [Color.BLUE, Color.RED, Color.YELLOW]

        # Color harmony rules (complementary and analogous)
        harmony_map = {
            Color.RED: [Color.GREEN, Color.ORANGE, Color.PURPLE],
            Color.BLUE: [Color.ORANGE, Color.GREEN, Color.PURPLE],
            Color.YELLOW: [Color.PURPLE, Color.ORANGE, Color.GREEN],
            Color.GREEN: [Color.RED, Color.BLUE, Color.YELLOW],
            Color.PURPLE: [Color.YELLOW, Color.BLUE, Color.RED],
            Color.ORANGE: [Color.BLUE, Color.RED, Color.YELLOW]
        }

        suggestions = []
        for color in used_colors[:2]:  # Use top 2 colors
            if isinstance(color, Color):
                suggestions.extend(harmony_map.get(color, []))

        # Remove duplicates and already used colors
        suggestions = [c for c in suggestions if c not in used_colors]

        # Return top 3 unique suggestions
        seen = set()
        unique_suggestions = []
        for color in suggestions:
            if color not in seen:
                seen.add(color)
                unique_suggestions.append(color)
                if len(unique_suggestions) >= 3:
                    break

        # If not enough suggestions, add unused colors
        if len(unique_suggestions) < 3:
            all_colors = list(Color)
            for color in all_colors:
                if color not in used_colors and color not in unique_suggestions:
                    unique_suggestions.append(color)
                    if len(unique_suggestions) >= 3:
                        break

        return unique_suggestions[:3]

    def _analyze_patterns(self, user_strokes: List[Dict]) -> Dict:
        """
        Analyze user's drawing patterns and style.

        Args:
            user_strokes: User's strokes only

        Returns:
            Dictionary with pattern analysis
        """
        if not user_strokes:
            return {
                'avg_size': 20.0,
                'density': 0.0,
                'activity_level': 'low'
            }

        # Average stroke size
        sizes = [stroke.get('size', 20) for stroke in user_strokes]
        avg_size = np.mean(sizes) if sizes else 20.0

        # Stroke density (strokes per 10000 pixels)
        canvas_area = self.width * self.height
        density = len(user_strokes) / (canvas_area / 10000)

        # Activity level
        if len(user_strokes) < 5:
            activity_level = 'low'
        elif len(user_strokes) < 15:
            activity_level = 'medium'
        else:
            activity_level = 'high'

        return {
            'avg_size': avg_size,
            'density': density,
            'activity_level': activity_level
        }

    def find_best_stroke_position(
        self,
        analysis: CanvasAnalysis,
        preference: str = 'empty'
    ) -> Tuple[int, int]:
        """
        Find optimal position for next robot stroke.

        Args:
            analysis: Canvas analysis results
            preference: 'empty' (fill gaps), 'dense' (add to existing), 'balanced' (improve balance)

        Returns:
            (x, y) position for stroke
        """
        if preference == 'empty' and analysis.empty_regions:
            # Choose random empty region
            return analysis.empty_regions[np.random.randint(len(analysis.empty_regions))]

        elif preference == 'dense' and analysis.high_density_regions:
            # Add near existing strokes
            region = analysis.high_density_regions[np.random.randint(len(analysis.high_density_regions))]
            # Offset slightly from center
            offset_x = np.random.randint(-50, 50)
            offset_y = np.random.randint(-50, 50)
            return (
                max(50, min(self.width - 50, region[0] + offset_x)),
                max(50, min(self.height - 50, region[1] + offset_y))
            )

        else:
            # Random position
            return (
                np.random.randint(50, self.width - 50),
                np.random.randint(50, self.height - 50)
            )
