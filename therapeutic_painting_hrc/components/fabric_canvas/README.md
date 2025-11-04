# Fabric.js Canvas Component for Streamlit

A custom Streamlit component that provides professional collaborative drawing capabilities using Fabric.js.

## Features

- **True Collaborative Drawing**: User and robot draw on the same canvas in real-time
- **Professional Drawing Experience**: Powered by Fabric.js library
- **Real-time Stroke Rendering**: Robot strokes appear instantly without page refresh
- **Multiple Stroke Types**: Supports circles, squares, lines, and splash effects
- **Bidirectional Communication**: Seamless data flow between frontend and backend
- **Customizable Appearance**: Adjustable brush colors, sizes, and canvas dimensions

## Architecture

### Frontend (`frontend/index.html`)
- HTML5 Canvas with Fabric.js integration
- Loaded from CDN: `fabric@5.3.0`
- Interactive drawing controls (color picker, brush size slider, clear button)
- Real-time stroke capture and transmission to Streamlit backend
- Robot stroke rendering with multiple shape types

### Backend (`__init__.py`)
- Python wrapper for the Streamlit component
- Handles bidirectional communication with frontend
- Processes stroke data from user drawings
- Sends robot strokes to be rendered on canvas

## Component API

```python
from fabric_canvas import fabric_canvas

canvas_result = fabric_canvas(
    width=800,              # Canvas width in pixels
    height=600,             # Canvas height in pixels
    brush_color="#FF0000",  # Initial brush color (hex)
    brush_size=5,           # Initial brush size in pixels
    robot_strokes=[         # List of robot strokes to render
        {
            'x': 100,
            'y': 200,
            'color': '#4ECDC4',
            'size': 20,
            'shape': 'circle'  # 'circle', 'square', 'line', 'splash'
        }
    ],
    clear_canvas=False,     # Clear the canvas if True
    key="canvas_1"          # Unique component key
)
```

## Return Value

The component returns stroke data when the user draws:

```python
{
    'type': 'new_stroke',
    'data': {
        'id': 'user_1699123456789_0',
        'color': '#FF0000',
        'width': 5,
        'path': [...],  # Fabric.js path data
        'timestamp': 1699123456789
    }
}
```

## Integration Example

```python
import streamlit as st
from fabric_canvas import fabric_canvas

# Initialize session state
if 'robot_strokes' not in st.session_state:
    st.session_state.robot_strokes = []

# Render canvas
canvas_result = fabric_canvas(
    width=800,
    height=600,
    brush_color="#FF0000",
    brush_size=5,
    robot_strokes=st.session_state.robot_strokes,
    key="my_canvas"
)

# Process user strokes
if canvas_result and canvas_result['type'] == 'new_stroke':
    stroke_data = canvas_result['data']

    # Your logic to generate robot response
    robot_stroke = generate_robot_response(stroke_data)

    # Add robot stroke
    st.session_state.robot_strokes.append({
        'x': robot_stroke['x'],
        'y': robot_stroke['y'],
        'color': '#4ECDC4',
        'size': 20,
        'shape': 'square'
    })

    st.rerun()  # Refresh to show robot stroke
```

## Stroke Shapes

The component supports multiple robot stroke shapes:

- **circle**: Circular marker
- **square**: Square marker
- **line**: Rotated line
- **splash**: Multiple small circles creating a splash effect
- **curve**: Default fallback to circle

## Technical Details

### Communication Protocol

1. **Frontend → Backend**: User stroke data sent via `postMessage` with type `streamlit:setComponentValue`
2. **Backend → Frontend**: Robot strokes passed as component arguments via `streamlit:render` message
3. **Component Ready**: Frontend notifies backend when loaded via `streamlit:componentReady`

### Stroke Processing

User drawings are captured as Fabric.js paths and converted to stroke data:
- Path segments are analyzed to determine average position
- Color and brush size are extracted from path properties
- Each stroke is assigned a unique ID for tracking

Robot strokes are rendered as Fabric.js objects:
- Different shapes use different Fabric.js primitives (Circle, Rect, Line)
- All robot objects are marked as `selectable: false`
- Strokes are added to the canvas and rendered immediately

## Dependencies

- **Frontend**: Fabric.js 5.3.0 (loaded from CDN)
- **Backend**: Streamlit components API (included with Streamlit)

## Directory Structure

```
fabric_canvas/
├── __init__.py          # Python component interface
├── frontend/
│   └── index.html       # Fabric.js frontend
└── README.md           # This file
```

## Usage in Therapeutic Painting HRC

This component is integrated into the Interactive Co-Painting mode in `visualization/app.py`:

1. User draws on canvas with mouse/stylus
2. Strokes are captured and sent to backend
3. Backend processes stroke via HMM intent recognition
4. Robot controller generates response action
5. Robot stroke is converted to fabric format and added to session state
6. Canvas refreshes to display robot's collaborative artwork
7. Both user and robot strokes appear on the same canvas in real-time

## Performance Considerations

- Canvas uses HTML5 Canvas element for optimal rendering
- Fabric.js provides efficient path rendering
- Robot strokes are batched in session state to minimize re-renders
- Component uses unique keys to manage canvas state

## Browser Compatibility

Works with all modern browsers supporting:
- HTML5 Canvas
- ES6 JavaScript
- PostMessage API
- Fabric.js 5.3.0

## Future Enhancements

- [ ] Undo/Redo functionality
- [ ] Export canvas as image (PNG/SVG)
- [ ] Multi-layer support
- [ ] Custom brush patterns
- [ ] Animation effects for robot strokes
- [ ] Touch/stylus pressure sensitivity
