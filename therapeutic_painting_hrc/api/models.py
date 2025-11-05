"""
Pydantic models for API communication between fabric.js frontend and Python backend.
"""

from pydantic import BaseModel, Field
from typing import Tuple, Optional, List, Dict
from enum import Enum


class ColorEnum(str, Enum):
    """Color options matching src.utils.Color"""
    RED = "RED"
    BLUE = "BLUE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"
    PURPLE = "PURPLE"
    ORANGE = "ORANGE"


class ShapeEnum(str, Enum):
    """Shape options matching src.utils.Shape"""
    CIRCLE = "CIRCLE"
    SQUARE = "SQUARE"
    LINE = "LINE"
    CURVE = "CURVE"
    SPLASH = "SPLASH"


class StrokeRequest(BaseModel):
    """Request model for a user stroke"""
    agent: str = "patient"
    position: Tuple[int, int]
    color: ColorEnum
    shape: ShapeEnum
    size: int = Field(ge=1, le=100)
    timestamp: Optional[int] = None
    points: Optional[List[Tuple[int, int]]] = None  # For continuous paths

    class Config:
        json_schema_extra = {
            "example": {
                "agent": "patient",
                "position": [400, 300],
                "color": "BLUE",
                "shape": "CIRCLE",
                "size": 20,
                "points": None
            }
        }


class StrokeResponse(BaseModel):
    """Response model containing a stroke"""
    agent: str
    position: Tuple[int, int]
    color: str
    shape: str
    size: int
    timestamp: int
    points: Optional[List[Tuple[int, int]]] = None  # For continuous paths

    class Config:
        json_schema_extra = {
            "example": {
                "agent": "robot",
                "position": [420, 310],
                "color": "PURPLE",
                "shape": "CURVE",
                "size": 25,
                "timestamp": 1234567890,
                "points": None
            }
        }


class RobotActionResponse(BaseModel):
    """Response containing robot's action and any generated strokes"""
    action_type: str
    strokes: List[StrokeResponse] = []
    message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "action_type": "INITIATE_PAINT",
                "strokes": [
                    {
                        "agent": "robot",
                        "position": [420, 310],
                        "color": "PURPLE",
                        "shape": "CURVE",
                        "size": 25,
                        "timestamp": 1234567890,
                        "points": [[420, 310], [425, 315], [430, 318]]
                    }
                ],
                "message": "Robot is initiating painting to increase engagement"
            }
        }


class PromptRequest(BaseModel):
    """Request model for text prompt to robot"""
    prompt: str = Field(min_length=1, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Draw a happy sun in the corner"
            }
        }


class BeliefStateResponse(BaseModel):
    """Response containing current belief state distribution"""
    belief_distribution: Dict[str, float]
    current_state: str
    canvas_coverage: float
    total_strokes: int

    class Config:
        json_schema_extra = {
            "example": {
                "belief_distribution": {
                    "ENGAGED": 0.6,
                    "EXPLORING": 0.3,
                    "HESITANT": 0.1
                },
                "current_state": "ENGAGED",
                "canvas_coverage": 0.35,
                "total_strokes": 42
            }
        }


class WebSocketMessage(BaseModel):
    """WebSocket message format for real-time communication"""
    type: str  # "user_stroke", "robot_stroke", "belief_update", "error"
    data: dict

    class Config:
        json_schema_extra = {
            "example": {
                "type": "robot_stroke",
                "data": {
                    "agent": "robot",
                    "position": [420, 310],
                    "color": "PURPLE",
                    "shape": "CURVE",
                    "size": 25,
                    "timestamp": 1234567890,
                    "points": None
                }
            }
        }
