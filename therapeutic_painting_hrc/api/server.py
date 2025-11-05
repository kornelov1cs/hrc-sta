"""
FastAPI server providing REST and WebSocket endpoints for the therapeutic painting system.
Integrates robot controller, HMM, and environment for real-time collaboration.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import time
from typing import List, Dict
import asyncio

from api.models import (
    StrokeRequest,
    StrokeResponse,
    RobotActionResponse,
    PromptRequest,
    BeliefStateResponse,
    WebSocketMessage,
    ColorEnum,
    ShapeEnum
)

# Import existing system components
from utils import Color, Shape, PatientState, RobotAction, Observation
from environment import Canvas, Stroke
from intent_recognition import PatientIntentHMM
from robot_controller import RobotBDI
from intelligent_painter import IntelligentPainter


# ============================================================================
# Application Setup
# ============================================================================

app = FastAPI(title="Therapeutic Painting HRC API", version="1.0.0")

# Enable CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (web frontend)
web_path = Path(__file__).parent.parent / "web"
app.mount("/static", StaticFiles(directory=str(web_path)), name="static")


# ============================================================================
# Global State Management
# ============================================================================

class SessionManager:
    """Manages active painting sessions."""

    def __init__(self):
        self.canvas = Canvas()
        self.hmm = PatientIntentHMM()
        self.robot = RobotBDI(mode='proactive')  # Can be configured
        self.current_timestep = 0
        self.active_websockets: List[WebSocket] = []
        self.idle_duration = 0
        self.last_patient_stroke_time = 0
        self.last_robot_stroke_time = 0

    def reset(self):
        """Reset session to initial state."""
        self.canvas = Canvas()
        self.hmm = PatientIntentHMM()
        self.robot = RobotBDI(mode='proactive')
        self.current_timestep = 0
        self.idle_duration = 0
        self.last_patient_stroke_time = 0
        self.last_robot_stroke_time = 0

    def add_user_stroke(self, stroke_data: StrokeRequest) -> Observation:
        """
        Add user stroke to canvas and infer observation.

        Args:
            stroke_data: Stroke data from frontend

        Returns:
            Inferred observation for HMM
        """
        # Convert enum strings to actual enums
        color = Color[stroke_data.color.value]
        shape = Shape[stroke_data.shape.value]

        # Add stroke to canvas
        self.canvas.add_stroke(
            agent="patient",
            position=stroke_data.position,
            color=color,
            shape=shape,
            size=stroke_data.size,
            timestamp=self.current_timestep
        )

        # Infer observation based on stroke characteristics
        observation = self._infer_observation(stroke_data)

        # Update HMM belief state
        self.hmm.update_belief(observation)

        # Update tracking
        self.idle_duration = 0  # Reset idle counter on user activity
        self.last_patient_stroke_time = self.current_timestep

        self.current_timestep += 1
        return observation

    def _infer_observation(self, stroke_data: StrokeRequest) -> Observation:
        """
        Infer observation from stroke characteristics.

        Args:
            stroke_data: Stroke data

        Returns:
            Observation enum
        """
        # Simple heuristic: classify based on size and shape
        if stroke_data.size > 40:
            return Observation.LONG_STROKE
        elif stroke_data.size < 15:
            return Observation.SHORT_STROKE
        else:
            return Observation.DRAWING

    def get_robot_action(self) -> RobotActionResponse:
        """
        Get robot's next action based on current state.

        Returns:
            Robot action with generated strokes
        """
        try:
            # Calculate recent activity
            recent_patient_strokes = len([s for s in self.canvas.strokes
                                         if s.agent == 'patient' and
                                         self.current_timestep - s.timestamp < 5])
            recent_robot_strokes = len([s for s in self.canvas.strokes
                                       if s.agent == 'robot' and
                                       self.current_timestep - s.timestamp < 5])

            # Get canvas state
            canvas_state = {
                'coverage': self.canvas.get_coverage(),
                'stroke_count': len(self.canvas.strokes),
                'recent_patient_activity': recent_patient_strokes,
                'recent_robot_activity': recent_robot_strokes
            }

            # Check turn-taking smoothness (alternating actions)
            turn_taking_smooth = (
                abs(self.last_patient_stroke_time - self.last_robot_stroke_time) <= 2
            )

            # Increment idle duration if no recent patient activity
            if recent_patient_strokes == 0:
                self.idle_duration += 1
            else:
                self.idle_duration = 0

            # Convert strokes to dict format for robot
            strokes_dict = [s.to_dict() for s in self.canvas.strokes]

            # Robot perceives, deliberates, plans, executes
            self.robot.perceive(
                self.hmm,
                canvas_state,
                self.idle_duration,
                turn_taking_smooth,
                strokes_dict
            )
            self.robot.deliberate()
            self.robot.plan()
            action_type, params = self.robot.execute()

            # Debug logging
            print(f"Robot action: {action_type}, params: {params}")
            print(f"Canvas state: {canvas_state}")
            print(f"Idle duration: {self.idle_duration}")
            most_likely_state, confidence = self.hmm.get_most_likely_state()
            print(f"Patient state: {most_likely_state} (confidence: {confidence:.2f})")

            # Generate robot strokes based on action
            robot_strokes = []

            # Force robot to paint more often in response to user activity
            # If robot chooses non-painting actions but user just drew, make it paint instead
            # Handle both enum and string action types
            action_value = action_type.value if hasattr(action_type, 'value') else str(action_type)

            if (action_value in ['Wait', 'Observe', 'SuggestColor', 'SuggestShape'] and
                recent_patient_strokes > 0):
                print(f"Overriding {action_type} to CONTINUE_PATIENT due to recent user activity")
                action_type = RobotAction.CONTINUE_PATIENT
                action_value = action_type.value

            # Check if we should paint (handle both enum and string)
            should_paint = (
                action_type in [RobotAction.INITIATE_PAINT, RobotAction.CONTINUE_PATIENT, RobotAction.RESPOND_TO_PROMPT] or
                action_value in ['InitiatePaint', 'ContinuePatient', 'RespondToPrompt']
            )

            if should_paint:
                # Generate stroke using intelligent painter
                most_likely_state, _ = self.hmm.get_most_likely_state()
                stroke_params = self.robot.intelligent_painter.generate_stroke(
                    strokes=strokes_dict,
                    patient_state=most_likely_state,
                    action_type=action_value
                )

                # Add to canvas
                color = stroke_params['color']
                shape = stroke_params['shape']
                position = stroke_params['position']
                size = stroke_params['size']
                points = stroke_params.get('points', None)  # Get continuous path points if available

                self.canvas.add_stroke(
                    agent="robot",
                    position=position,
                    color=color,
                    shape=shape,
                    size=size,
                    timestamp=self.current_timestep
                )

                # Create response stroke - handle both enum and string
                color_name = color.name if hasattr(color, 'name') else str(color)
                shape_name = shape.name if hasattr(shape, 'name') else str(shape)

                robot_strokes.append(StrokeResponse(
                    agent="robot",
                    position=position,
                    color=color_name,
                    shape=shape_name,
                    size=size,
                    timestamp=self.current_timestep,
                    points=points
                ))

                # Update robot stroke tracking
                self.last_robot_stroke_time = self.current_timestep

            self.current_timestep += 1

            return RobotActionResponse(
                action_type=action_value,
                strokes=robot_strokes,
                message=self._get_action_message(action_type)
            )
        except Exception as e:
            print(f"Error in get_robot_action: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _get_action_message(self, action) -> str:
        """Get human-readable message for robot action (handles both enum and string)."""
        # Convert to string value if it's an enum
        action_str = action.value if hasattr(action, 'value') else str(action)

        messages = {
            "InitiatePaint": "Robot is starting to paint",
            "ContinuePatient": "Robot is continuing your work",
            "SuggestColor": "Robot suggests trying a new color",
            "SuggestShape": "Robot suggests a different shape",
            "RespondToPrompt": "Robot is responding to your prompt",
            "Wait": "Robot is waiting for you",
            "Observe": "Robot is observing your work"
        }
        return messages.get(action_str, "Robot is thinking")

    def get_belief_state(self) -> BeliefStateResponse:
        """Get current belief state distribution."""
        distribution = self.hmm.get_belief_dict()
        most_likely_state, confidence = self.hmm.get_most_likely_state()

        return BeliefStateResponse(
            belief_distribution={state: float(prob)
                               for state, prob in distribution.items()},
            current_state=most_likely_state.value,
            canvas_coverage=self.canvas.get_coverage(),
            total_strokes=len(self.canvas.strokes)
        )


# Global session manager
session = SessionManager()


# ============================================================================
# REST API Endpoints
# ============================================================================

@app.get("/")
async def read_root():
    """Serve the main web application."""
    return FileResponse(str(web_path / "index.html"))


@app.post("/api/stroke", response_model=RobotActionResponse)
async def process_stroke(stroke: StrokeRequest):
    """
    Process a user stroke and get robot response.

    Args:
        stroke: User stroke data

    Returns:
        Robot action with generated strokes
    """
    try:
        # Add user stroke
        observation = session.add_user_stroke(stroke)

        # Get robot response
        robot_response = session.get_robot_action()

        # Broadcast to all connected WebSocket clients
        if session.active_websockets:
            message = WebSocketMessage(
                type="robot_action",
                data=robot_response.model_dump()
            )
            await broadcast_message(message.model_dump())

        return robot_response

    except Exception as e:
        print(f"Error in process_stroke: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/prompt", response_model=RobotActionResponse)
async def process_prompt(prompt: PromptRequest):
    """
    Process a text prompt and generate robot strokes.

    Args:
        prompt: Text prompt for robot

    Returns:
        Robot action with generated strokes
    """
    try:
        # Generate strokes from prompt (returns a list)
        strokes_dict = [s.to_dict() for s in session.canvas.strokes]
        generated_strokes = session.robot.intelligent_painter.generate_from_prompt(
            strokes=strokes_dict,
            prompt=prompt.prompt
        )

        # Process each generated stroke
        robot_strokes = []
        for stroke_params in generated_strokes:
            # Add to canvas
            color = stroke_params['color']
            shape = stroke_params['shape']
            position = stroke_params['position']
            size = stroke_params['size']
            points = stroke_params.get('points', None)  # Get continuous path points if available

            session.canvas.add_stroke(
                agent="robot",
                position=position,
                color=color,
                shape=shape,
                size=size,
                timestamp=session.current_timestep
            )

            # Handle both enum and string for color/shape
            color_name = color.name if hasattr(color, 'name') else str(color)
            shape_name = shape.name if hasattr(shape, 'name') else str(shape)

            robot_strokes.append(StrokeResponse(
                agent="robot",
                position=position,
                color=color_name,
                shape=shape_name,
                size=size,
                timestamp=session.current_timestep,
                points=points
            ))

            session.current_timestep += 1

        # Update robot stroke tracking
        session.last_robot_stroke_time = session.current_timestep

        response = RobotActionResponse(
            action_type="RESPOND_TO_PROMPT",
            strokes=robot_strokes,
            message=f"Robot painted {len(robot_strokes)} stroke(s) based on: '{prompt.prompt}'"
        )

        return response

    except Exception as e:
        print(f"Error in process_prompt: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/state", response_model=BeliefStateResponse)
async def get_state():
    """Get current belief state and canvas statistics."""
    return session.get_belief_state()


@app.post("/api/reset")
async def reset_session():
    """Reset the painting session."""
    session.reset()

    # Notify all WebSocket clients
    if session.active_websockets:
        message = WebSocketMessage(
            type="session_reset",
            data={}
        )
        await broadcast_message(message.model_dump())

    return {"status": "success", "message": "Session reset"}


# ============================================================================
# WebSocket Endpoint for Real-time Communication
# ============================================================================

async def broadcast_message(message: dict):
    """Broadcast message to all connected WebSocket clients."""
    disconnected = []
    for websocket in session.active_websockets:
        try:
            await websocket.send_json(message)
        except:
            disconnected.append(websocket)

    # Remove disconnected clients
    for ws in disconnected:
        session.active_websockets.remove(ws)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time stroke communication.

    Message format:
    {
        "type": "user_stroke" | "prompt" | "get_state",
        "data": {...}
    }
    """
    await websocket.accept()
    session.active_websockets.append(websocket)

    try:
        # Send initial state
        initial_state = session.get_belief_state()
        await websocket.send_json({
            "type": "belief_update",
            "data": initial_state.model_dump()
        })

        while True:
            # Receive message
            data = await websocket.receive_json()
            message_type = data.get("type")
            message_data = data.get("data", {})

            if message_type == "user_stroke":
                # Process user stroke
                stroke = StrokeRequest(**message_data)
                observation = session.add_user_stroke(stroke)

                # Get robot response
                robot_response = session.get_robot_action()

                # Send robot action
                await websocket.send_json({
                    "type": "robot_action",
                    "data": robot_response.model_dump()
                })

                # Send updated belief state
                belief_state = session.get_belief_state()
                await websocket.send_json({
                    "type": "belief_update",
                    "data": belief_state.model_dump()
                })

            elif message_type == "prompt":
                # Process text prompt
                prompt = message_data.get("prompt", "")
                if prompt:
                    prompt_req = PromptRequest(prompt=prompt)
                    robot_response = await process_prompt(prompt_req)

                    await websocket.send_json({
                        "type": "robot_action",
                        "data": robot_response.model_dump()
                    })

            elif message_type == "get_state":
                # Send current state
                belief_state = session.get_belief_state()
                await websocket.send_json({
                    "type": "belief_update",
                    "data": belief_state.model_dump()
                })

    except WebSocketDisconnect:
        session.active_websockets.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        import traceback
        traceback.print_exc()
        try:
            await websocket.send_json({
                "type": "error",
                "data": {"message": str(e)}
            })
        except:
            pass
        if websocket in session.active_websockets:
            session.active_websockets.remove(websocket)


# ============================================================================
# Server Startup
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
