"""
Intelligent painting module that generates contextually appropriate robot strokes
based on canvas analysis, patient state, and robot behavior mode.
"""

import numpy as np
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from utils import Color, Shape, PatientState, CANVAS_WIDTH, CANVAS_HEIGHT
from stroke_analyzer import StrokeAnalyzer, CanvasAnalysis


class IntelligentPainter:
    """
    Generates intelligent robot painting strokes based on context.

    Considers:
    - Canvas state (spatial distribution, colors, density)
    - Patient emotional state
    - Robot behavior mode (proactive vs reactive)
    - Compositional principles (balance, harmony, contrast)
    """

    def __init__(
        self,
        canvas_width: int = CANVAS_WIDTH,
        canvas_height: int = CANVAS_HEIGHT,
        mode: str = 'proactive'
    ):
        """
        Initialize intelligent painter.

        Args:
            canvas_width: Canvas width in pixels
            canvas_height: Canvas height in pixels
            mode: Robot behavior mode ('proactive' or 'reactive')
        """
        self.width = canvas_width
        self.height = canvas_height
        self.mode = mode
        self.analyzer = StrokeAnalyzer(canvas_width, canvas_height)

    def generate_stroke(
        self,
        strokes: List[Dict],
        patient_state: Optional[PatientState] = None,
        action_type: str = 'paint'
    ) -> Dict:
        """
        Generate an intelligent robot stroke.

        Args:
            strokes: Current canvas strokes
            patient_state: Current patient emotional state
            action_type: Type of action ('paint', 'suggest', 'continue')

        Returns:
            Dictionary with stroke parameters (position, color, shape, size)
        """
        # Analyze current canvas
        analysis = self.analyzer.analyze(strokes)

        # Generate stroke based on mode and patient state
        if self.mode == 'proactive':
            return self._generate_proactive_stroke(analysis, patient_state, action_type)
        else:
            return self._generate_reactive_stroke(analysis, patient_state, action_type)

    def _generate_proactive_stroke(
        self,
        analysis: CanvasAnalysis,
        patient_state: Optional[PatientState],
        action_type: str
    ) -> Dict:
        """
        Generate stroke for proactive robot mode.

        Proactive robot:
        - Takes initiative
        - Fills empty spaces
        - Introduces new colors/shapes
        - Provides structure

        Args:
            analysis: Canvas analysis
            patient_state: Patient state
            action_type: Action type

        Returns:
            Stroke parameters
        """
        # Determine stroke characteristics based on patient state
        if patient_state == PatientState.FRUSTRATED:
            # Calm, harmonious strokes
            color = self._choose_calming_color(analysis)
            size = self._get_size_for_mood('calm', analysis)
            shape = Shape.CIRCLE  # Soft shapes
            position = self._get_balanced_position(analysis)

        elif patient_state == PatientState.HESITANT:
            # Provide structure and guidance
            color = self._choose_bold_color(analysis)
            size = self._get_size_for_mood('confident', analysis)
            shape = self._choose_structural_shape()
            position = self._get_empty_position(analysis)

        elif patient_state == PatientState.NEEDS_SUPPORT:
            # Complementary, supportive strokes
            color = self._choose_complementary_color(analysis)
            size = self._get_size_for_mood('supportive', analysis)
            shape = self._match_user_style(analysis)
            position = self._get_nearby_position(analysis)

        elif patient_state == PatientState.ENGAGED:
            # Continue the flow, don't interrupt
            color = self._choose_harmonious_color(analysis)
            size = self._get_size_for_mood('flowing', analysis)
            shape = self._choose_complementary_shape(analysis)
            position = self._get_balanced_position(analysis)

        else:  # SATISFIED or None
            # Add finishing touches
            color = self._choose_accent_color(analysis)
            size = self._get_size_for_mood('detail', analysis)
            shape = Shape.SPLASH  # Decorative
            position = self._get_empty_position(analysis)

        return {
            'position': position,
            'color': color,
            'shape': shape,
            'size': int(size)
        }

    def _generate_reactive_stroke(
        self,
        analysis: CanvasAnalysis,
        patient_state: Optional[PatientState],
        action_type: str
    ) -> Dict:
        """
        Generate stroke for reactive robot mode.

        Reactive robot:
        - Responds to user's lead
        - Matches user's style
        - Fills gaps user left
        - Harmonizes with existing work

        Args:
            analysis: Canvas analysis
            patient_state: Patient state
            action_type: Action type

        Returns:
            Stroke parameters
        """
        # Reactive mode: follow user's lead
        if analysis.user_activity_level == 'low':
            # Minimal intervention
            color = self._choose_harmonious_color(analysis)
            size = self._get_size_for_mood('subtle', analysis)
            shape = Shape.CIRCLE
            position = self._get_balanced_position(analysis)

        else:
            # Respond to user's style
            color = self._choose_user_color_palette(analysis)
            size = analysis.avg_stroke_size * np.random.uniform(0.8, 1.2)
            shape = self._match_user_style(analysis)
            position = self._get_complementary_position(analysis)

        return {
            'position': position,
            'color': color,
            'shape': shape,
            'size': int(size)
        }

    # ==================== Color Selection Methods ====================

    def _choose_calming_color(self, analysis: CanvasAnalysis) -> Color:
        """Choose calming colors (cool tones)."""
        calming_colors = [Color.BLUE, Color.GREEN, Color.PURPLE]
        # Prefer colors not already dominant
        available = [c for c in calming_colors if c not in analysis.dominant_colors]
        return random.choice(available) if available else Color.BLUE

    def _choose_bold_color(self, analysis: CanvasAnalysis) -> Color:
        """Choose bold, confident colors."""
        bold_colors = [Color.RED, Color.ORANGE, Color.YELLOW]
        available = [c for c in bold_colors if c not in analysis.dominant_colors]
        return random.choice(available) if available else Color.RED

    def _choose_complementary_color(self, analysis: CanvasAnalysis) -> Color:
        """Choose color complementary to user's dominant colors."""
        if analysis.suggested_colors:
            return random.choice(analysis.suggested_colors)
        return random.choice(list(Color))

    def _choose_harmonious_color(self, analysis: CanvasAnalysis) -> Color:
        """Choose harmonious color from palette."""
        if analysis.dominant_colors:
            # 70% chance of using dominant color, 30% complementary
            if np.random.random() < 0.7:
                return random.choice(analysis.dominant_colors)
            elif analysis.suggested_colors:
                return random.choice(analysis.suggested_colors)
        return random.choice(list(Color))

    def _choose_accent_color(self, analysis: CanvasAnalysis) -> Color:
        """Choose accent/highlight color."""
        if analysis.suggested_colors:
            return analysis.suggested_colors[0]
        return Color.ORANGE

    def _choose_user_color_palette(self, analysis: CanvasAnalysis) -> Color:
        """Match user's color palette."""
        if analysis.dominant_colors:
            return random.choice(analysis.dominant_colors)
        return random.choice(list(Color))

    # ==================== Shape Selection Methods ====================

    def _choose_structural_shape(self) -> Shape:
        """Choose structural, confident shapes."""
        return random.choice([Shape.SQUARE, Shape.LINE])

    def _choose_complementary_shape(self, analysis: CanvasAnalysis) -> Shape:
        """Choose shape that complements composition."""
        # Simple heuristic: vary shapes
        return random.choice(list(Shape))

    def _match_user_style(self, analysis: CanvasAnalysis) -> Shape:
        """Try to match user's style."""
        # For now, default to circle (could be enhanced with shape counting)
        return random.choice([Shape.CIRCLE, Shape.CURVE])

    # ==================== Size Selection Methods ====================

    def _get_size_for_mood(self, mood: str, analysis: CanvasAnalysis) -> float:
        """
        Get stroke size appropriate for mood/intent.

        Args:
            mood: Mood descriptor
            analysis: Canvas analysis

        Returns:
            Stroke size in pixels
        """
        base_size = analysis.avg_stroke_size if analysis.avg_stroke_size > 0 else 25.0

        size_modifiers = {
            'calm': 0.8,
            'confident': 1.3,
            'supportive': 1.0,
            'flowing': 1.1,
            'detail': 0.6,
            'subtle': 0.7,
            'bold': 1.4
        }

        modifier = size_modifiers.get(mood, 1.0)
        size = base_size * modifier * np.random.uniform(0.85, 1.15)

        # Clamp to reasonable range
        return max(10, min(50, size))

    # ==================== Position Selection Methods ====================

    def _get_empty_position(self, analysis: CanvasAnalysis) -> Tuple[int, int]:
        """Get position in empty region."""
        return self.analyzer.find_best_stroke_position(analysis, preference='empty')

    def _get_balanced_position(self, analysis: CanvasAnalysis) -> Tuple[int, int]:
        """Get position that improves balance."""
        if analysis.is_balanced:
            return self._get_empty_position(analysis)
        else:
            # Could be smarter about this - for now, use empty
            return self._get_empty_position(analysis)

    def _get_nearby_position(self, analysis: CanvasAnalysis) -> Tuple[int, int]:
        """Get position near existing strokes."""
        return self.analyzer.find_best_stroke_position(analysis, preference='dense')

    def _get_complementary_position(self, analysis: CanvasAnalysis) -> Tuple[int, int]:
        """Get position that complements existing composition."""
        if analysis.needs_fill_areas:
            return self._get_empty_position(analysis)
        else:
            return self._get_nearby_position(analysis)

    # ==================== Text Prompt Methods ====================

    def generate_from_prompt(
        self,
        strokes: List[Dict],
        prompt: str
    ) -> List[Dict]:
        """
        Generate strokes based on text prompt.

        Args:
            strokes: Current canvas strokes
            prompt: Text prompt from user

        Returns:
            List of stroke dictionaries
        """
        analysis = self.analyzer.analyze(strokes)
        prompt_lower = prompt.lower()

        # Parse color
        color = self._parse_color_from_prompt(prompt_lower)

        # Parse shape
        shape = self._parse_shape_from_prompt(prompt_lower)

        # Parse quantity
        num_strokes = self._parse_quantity_from_prompt(prompt_lower)

        # Parse size
        size = self._parse_size_from_prompt(prompt_lower, analysis)

        # Parse location
        location_preference = self._parse_location_from_prompt(prompt_lower)

        # Generate strokes
        generated_strokes = []
        for _ in range(num_strokes):
            position = self._get_position_for_location(location_preference, analysis)

            generated_strokes.append({
                'position': position,
                'color': color,
                'shape': shape,
                'size': int(size * np.random.uniform(0.9, 1.1))
            })

        return generated_strokes

    def _parse_color_from_prompt(self, prompt: str) -> Color:
        """Extract color from text prompt."""
        if 'blue' in prompt:
            return Color.BLUE
        elif 'red' in prompt:
            return Color.RED
        elif 'yellow' in prompt:
            return Color.YELLOW
        elif 'green' in prompt:
            return Color.GREEN
        elif 'purple' in prompt:
            return Color.PURPLE
        elif 'orange' in prompt:
            return Color.ORANGE
        return random.choice(list(Color))

    def _parse_shape_from_prompt(self, prompt: str) -> Shape:
        """Extract shape from text prompt."""
        if 'circle' in prompt or 'dot' in prompt or 'round' in prompt:
            return Shape.CIRCLE
        elif 'square' in prompt or 'box' in prompt or 'rectangle' in prompt:
            return Shape.SQUARE
        elif 'line' in prompt or 'stroke' in prompt:
            return Shape.LINE
        elif 'curve' in prompt or 'wavy' in prompt:
            return Shape.CURVE
        elif 'splash' in prompt or 'spray' in prompt:
            return Shape.SPLASH
        return Shape.CIRCLE

    def _parse_quantity_from_prompt(self, prompt: str) -> int:
        """Extract quantity from text prompt."""
        if 'one' in prompt or 'a ' in prompt or 'single' in prompt:
            return 1
        elif 'two' in prompt or 'couple' in prompt:
            return 2
        elif 'few' in prompt or 'some' in prompt:
            return np.random.randint(3, 6)
        elif 'several' in prompt:
            return np.random.randint(4, 8)
        elif 'many' in prompt or 'lot' in prompt:
            return np.random.randint(7, 12)

        # Try to find numbers
        import re
        numbers = re.findall(r'\d+', prompt)
        if numbers:
            return min(int(numbers[0]), 20)  # Cap at 20

        return np.random.randint(2, 5)

    def _parse_size_from_prompt(self, prompt: str, analysis: CanvasAnalysis) -> float:
        """Extract size from text prompt."""
        if 'tiny' in prompt or 'small' in prompt:
            return 15
        elif 'large' in prompt or 'big' in prompt:
            return 40
        elif 'huge' in prompt:
            return 50
        return analysis.avg_stroke_size if analysis.avg_stroke_size > 0 else 25

    def _parse_location_from_prompt(self, prompt: str) -> str:
        """Extract location preference from prompt."""
        if 'top' in prompt:
            return 'top'
        elif 'bottom' in prompt:
            return 'bottom'
        elif 'left' in prompt:
            return 'left'
        elif 'right' in prompt:
            return 'right'
        elif 'center' in prompt or 'middle' in prompt:
            return 'center'
        elif 'around' in prompt or 'near' in prompt:
            return 'dense'
        elif 'empty' in prompt or 'gap' in prompt:
            return 'empty'
        return 'random'

    def _get_position_for_location(
        self,
        location: str,
        analysis: CanvasAnalysis
    ) -> Tuple[int, int]:
        """Get position based on location preference."""
        if location == 'top':
            return (
                np.random.randint(50, self.width - 50),
                np.random.randint(50, self.height // 3)
            )
        elif location == 'bottom':
            return (
                np.random.randint(50, self.width - 50),
                np.random.randint(2 * self.height // 3, self.height - 50)
            )
        elif location == 'left':
            return (
                np.random.randint(50, self.width // 3),
                np.random.randint(50, self.height - 50)
            )
        elif location == 'right':
            return (
                np.random.randint(2 * self.width // 3, self.width - 50),
                np.random.randint(50, self.height - 50)
            )
        elif location == 'center':
            return (
                np.random.randint(self.width // 3, 2 * self.width // 3),
                np.random.randint(self.height // 3, 2 * self.height // 3)
            )
        elif location == 'dense':
            return self._get_nearby_position(analysis)
        elif location == 'empty':
            return self._get_empty_position(analysis)
        else:
            return (
                np.random.randint(50, self.width - 50),
                np.random.randint(50, self.height - 50)
            )
