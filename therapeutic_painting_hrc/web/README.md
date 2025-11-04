# Therapeutic Painting - Fabric.js Canvas

An interactive web application for collaborative painting with an intelligent robot assistant using fabric.js.

## Features

### Drawing Tools
- **Multiple brush types**: Pencil, marker, spray, and eraser
- **Shape tools**: Circle, square, line, curve, and splash effects
- **Color palette**: 6 therapeutic colors (red, blue, yellow, green, purple, orange)
- **Adjustable brush size**: 5-80 pixels

### Advanced Capabilities
- **Layer management**: Toggle visibility of patient vs robot strokes independently
- **Undo/Redo**: Full history support with up to 50 states
- **Real-time collaboration**: WebSocket connection for instant robot responses
- **Text prompts**: Ask the robot to draw specific things

### Robot Intelligence
- **BDI Architecture**: Robot uses Belief-Desire-Intention reasoning
- **HMM State Inference**: Infers patient emotional state from drawing patterns
- **Contextual painting**: Robot strokes adapt to patient state and canvas composition
- **Multiple action types**: Initiate, continue, suggest, or observe

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify installation**:
   ```bash
   python -c "import fastapi; import uvicorn; print('FastAPI installed successfully')"
   ```

## Running the Application

1. **Start the FastAPI server**:
   ```bash
   python api/server.py
   ```

   The server will start on `http://localhost:8000`

2. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

3. **Start painting!** The robot will respond to your strokes in real-time.

## Usage Guide

### Basic Drawing
1. Select a color from the color palette
2. Choose a brush type (pencil, marker, spray, or eraser)
3. Adjust the brush size using the slider
4. Draw on the canvas
5. The robot will respond based on your drawing patterns

### Using Text Prompts
1. Type a description in the prompt input at the bottom (e.g., "Draw a happy sun")
2. Press Enter or click "Send"
3. The robot will generate a stroke based on your prompt

### Layer Controls
- **Your Strokes**: Toggle to show/hide your own strokes
- **Robot Strokes**: Toggle to show/hide robot-generated strokes
- Use this to see individual contributions or the combined artwork

### History Management
- **Undo**: Click the Undo button or press Ctrl+Z (⌘+Z on Mac)
- **Redo**: Click the Redo button or press Ctrl+Y (⌘+Y on Mac)
- **Clear**: Clears the entire canvas (confirmation required)

### Robot Status Panel
Monitor the robot's activity in the right sidebar:
- **Connection Status**: Shows WebSocket connection state
- **Current Action**: What the robot is currently doing
- **Patient State**: The robot's inference of your emotional state
- **Belief Distribution**: Probability distribution over possible states
- **Canvas Statistics**: Stroke counts and coverage
- **Message Log**: Recent robot actions and system messages

## Architecture

### Backend (Python/FastAPI)
- **api/server.py**: Main FastAPI application with WebSocket support
- **api/models.py**: Pydantic models for API communication
- **src/**: Existing robot controller, HMM, and intelligent painter

### Frontend (HTML/CSS/JavaScript)
- **web/index.html**: Main application interface
- **web/css/styles.css**: Comprehensive styling
- **web/js/canvas.js**: Fabric.js canvas management
- **web/js/tools.js**: Drawing tool selection and configuration
- **web/js/layers.js**: Layer visibility management
- **web/js/history.js**: Undo/redo functionality
- **web/js/robot.js**: WebSocket client for robot communication

### Communication Flow
```
User draws on canvas (fabric.js)
    ↓
WebSocket message to backend
    ↓
HMM infers patient state
    ↓
Robot BDI deliberates action
    ↓
Intelligent painter generates stroke
    ↓
WebSocket message to frontend
    ↓
Robot stroke rendered on canvas
```

## API Endpoints

### REST API
- `GET /`: Serve web application
- `POST /api/stroke`: Process user stroke, get robot response
- `POST /api/prompt`: Send text prompt to robot
- `GET /api/state`: Get current belief state and statistics
- `POST /api/reset`: Reset painting session

### WebSocket
- `ws://localhost:8000/ws`: Real-time bidirectional communication

#### Message Types
- **user_stroke**: User drawing event
- **prompt**: Text prompt from user
- **robot_action**: Robot's response with strokes
- **belief_update**: Updated patient state distribution
- **session_reset**: Session cleared
- **error**: Error message

## Customization

### Robot Behavior Mode
Edit `api/server.py` line 68 to change robot mode:
```python
self.robot = RobotBDI(mode='proactive')  # or 'reactive'
```

- **Proactive**: Robot takes initiative, fills spaces, provides structure
- **Reactive**: Robot follows user's lead, matches style, harmonizes

### Canvas Dimensions
Edit `web/js/canvas.js` lines 19-20:
```javascript
const CANVAS_WIDTH = 800;
const CANVAS_HEIGHT = 600;
```

### Colors
Add or modify colors in `src/utils.py` and update:
- `web/js/canvas.js`: COLOR_MAP
- `web/index.html`: Color palette buttons

## Troubleshooting

### WebSocket Connection Failed
- Ensure the FastAPI server is running
- Check browser console for errors
- Verify port 8000 is not blocked by firewall

### Robot Not Responding
- Check the connection status indicator (should be green)
- Look at the message log for errors
- Verify backend logs for exceptions

### Canvas Not Rendering
- Check browser console for JavaScript errors
- Ensure fabric.js CDN is accessible
- Verify all JavaScript modules loaded correctly

### Import Errors
If you see import errors about `utils`, `environment`, etc., make sure you're running the server from the project root directory:
```bash
cd /path/to/therapeutic_painting_hrc
python api/server.py
```

## Browser Compatibility

Tested and working on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Maximum 50 undo/redo states stored
- Message log limited to 20 messages
- Canvas objects are non-selectable for better performance
- WebSocket reconnection with exponential backoff

## Future Enhancements

Potential additions:
- Export canvas as image (PNG/SVG)
- Save/load sessions
- Multi-user collaboration
- Voice prompts
- Animation of robot strokes
- Brush texture customization
- More sophisticated shape recognition

## License

Part of the Therapeutic Painting HRC project.
