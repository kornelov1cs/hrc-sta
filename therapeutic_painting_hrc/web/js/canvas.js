/**
 * Canvas module - Manages fabric.js canvas and drawing operations
 */

import { ToolManager } from './tools.js';
import { LayerManager } from './layers.js';
import { HistoryManager } from './history.js';
import { RobotClient } from './robot.js';

// Color mapping from enum to hex
const COLOR_MAP = {
    'RED': '#FF6B6B',
    'BLUE': '#4ECDC4',
    'YELLOW': '#FFE66D',
    'GREEN': '#95E1D3',
    'PURPLE': '#AA96DA',
    'ORANGE': '#FCBF49'
};

// Canvas dimensions
const CANVAS_WIDTH = 800;
const CANVAS_HEIGHT = 600;

class CanvasManager {
    constructor() {
        // Initialize fabric canvas
        this.canvas = new fabric.Canvas('painting-canvas', {
            width: CANVAS_WIDTH,
            height: CANVAS_HEIGHT,
            backgroundColor: '#FFFFFF',
            isDrawingMode: true,
            selection: false
        });

        // Initialize managers
        this.toolManager = new ToolManager(this);
        this.layerManager = new LayerManager(this);
        this.historyManager = new HistoryManager(this);
        this.robotClient = new RobotClient(this);

        // Current drawing state
        this.currentColor = 'RED';
        this.currentShape = 'CIRCLE';
        this.currentSize = 20;
        this.currentTool = 'pencil';

        // Statistics
        this.patientStrokeCount = 0;
        this.robotStrokeCount = 0;

        // Setup event listeners
        this.setupEventListeners();

        // Configure initial brush
        this.updateBrush();
    }

    setupEventListeners() {
        // Path created event (when user finishes drawing a stroke)
        this.canvas.on('path:created', (e) => {
            const path = e.path;
            this.handleUserStroke(path);
        });

        // Object added event (for robot strokes)
        this.canvas.on('object:added', (e) => {
            // Don't trigger history for robot strokes during initial add
            if (!e.target._isRobotStroke) {
                this.historyManager.saveState();
            }
        });
    }

    updateBrush() {
        if (this.currentTool === 'eraser') {
            // Eraser mode
            this.canvas.freeDrawingBrush.color = '#FFFFFF';
            this.canvas.freeDrawingBrush.width = this.currentSize * 2;
        } else {
            // Drawing mode
            const hexColor = COLOR_MAP[this.currentColor];
            this.canvas.freeDrawingBrush.color = hexColor;
            this.canvas.freeDrawingBrush.width = this.currentSize;

            // Set brush type
            if (this.currentTool === 'spray') {
                this.canvas.freeDrawingBrush = new fabric.SprayBrush(this.canvas);
                this.canvas.freeDrawingBrush.color = hexColor;
                this.canvas.freeDrawingBrush.width = this.currentSize;
                this.canvas.freeDrawingBrush.density = 20;
            } else if (this.currentTool === 'marker') {
                this.canvas.freeDrawingBrush = new fabric.PencilBrush(this.canvas);
                this.canvas.freeDrawingBrush.color = hexColor;
                this.canvas.freeDrawingBrush.width = this.currentSize * 1.5;
            } else {
                // Default pencil
                this.canvas.freeDrawingBrush = new fabric.PencilBrush(this.canvas);
                this.canvas.freeDrawingBrush.color = hexColor;
                this.canvas.freeDrawingBrush.width = this.currentSize;
            }
        }
    }

    handleUserStroke(path) {
        // Mark as patient stroke
        path.set({
            _isPatientStroke: true,
            selectable: false,
            evented: false
        });

        this.patientStrokeCount++;

        // Get path bounds for position
        const bounds = path.getBoundingRect();
        const centerX = Math.round(bounds.left + bounds.width / 2);
        const centerY = Math.round(bounds.top + bounds.height / 2);

        // Infer shape based on path characteristics
        const inferredShape = this.inferShape(path);

        // Create stroke data for backend
        const strokeData = {
            agent: 'patient',
            position: [centerX, centerY],
            color: this.currentColor,
            shape: inferredShape,
            size: this.currentSize
        };

        // Send to robot via WebSocket
        this.robotClient.sendUserStroke(strokeData);

        // Update statistics
        this.updateStatistics();
    }

    inferShape(path) {
        // Simple shape inference based on path properties
        const pathLength = path.path.length;

        if (this.currentTool === 'spray') {
            return 'SPLASH';
        }

        // Analyze path to infer shape
        if (pathLength < 5) {
            return 'CIRCLE';  // Short strokes are circles
        } else if (pathLength < 15) {
            return 'LINE';    // Medium strokes are lines
        } else {
            return 'CURVE';   // Long strokes are curves
        }
    }

    addRobotStroke(strokeData) {
        // Add robot stroke to canvas
        const { position, color, shape, size } = strokeData;
        const hexColor = COLOR_MAP[color];

        let fabricObject;

        // Create appropriate fabric object based on shape
        switch (shape) {
            case 'CIRCLE':
                fabricObject = new fabric.Circle({
                    left: position[0] - size / 2,
                    top: position[1] - size / 2,
                    radius: size / 2,
                    fill: hexColor,
                    stroke: hexColor,
                    strokeWidth: 2
                });
                break;

            case 'SQUARE':
                fabricObject = new fabric.Rect({
                    left: position[0] - size / 2,
                    top: position[1] - size / 2,
                    width: size,
                    height: size,
                    fill: hexColor,
                    stroke: hexColor,
                    strokeWidth: 2
                });
                break;

            case 'LINE':
                const lineLength = size * 2;
                const angle = Math.random() * Math.PI * 2;
                const x2 = position[0] + Math.cos(angle) * lineLength;
                const y2 = position[1] + Math.sin(angle) * lineLength;
                fabricObject = new fabric.Line(
                    [position[0], position[1], x2, y2],
                    {
                        stroke: hexColor,
                        strokeWidth: size / 4
                    }
                );
                break;

            case 'CURVE':
                // Create a curved path
                const curvePath = this.generateCurvePath(position, size);
                fabricObject = new fabric.Path(curvePath, {
                    fill: '',
                    stroke: hexColor,
                    strokeWidth: size / 4
                });
                break;

            case 'SPLASH':
                // Create multiple small circles for splash effect
                const splashGroup = this.createSplash(position, size, hexColor);
                fabricObject = splashGroup;
                break;

            default:
                fabricObject = new fabric.Circle({
                    left: position[0] - size / 2,
                    top: position[1] - size / 2,
                    radius: size / 2,
                    fill: hexColor
                });
        }

        // Mark as robot stroke
        fabricObject.set({
            _isRobotStroke: true,
            selectable: false,
            evented: false
        });

        // Add to canvas
        this.canvas.add(fabricObject);
        this.robotStrokeCount++;

        // Update layer visibility
        this.layerManager.updateLayerVisibility();

        // Update statistics
        this.updateStatistics();

        // Save state for history
        this.historyManager.saveState();
    }

    generateCurvePath(position, size) {
        // Generate a curved path using SVG path commands
        const [x, y] = position;
        const controlX1 = x + size * (Math.random() - 0.5);
        const controlY1 = y + size * (Math.random() - 0.5);
        const controlX2 = x + size * (Math.random() - 0.5);
        const controlY2 = y + size * (Math.random() - 0.5);
        const endX = x + size * (Math.random() * 2 - 1);
        const endY = y + size * (Math.random() * 2 - 1);

        return `M ${x} ${y} C ${controlX1} ${controlY1}, ${controlX2} ${controlY2}, ${endX} ${endY}`;
    }

    createSplash(position, size, color) {
        // Create splash effect with multiple small circles
        const circles = [];
        const numCircles = 5 + Math.floor(Math.random() * 5);

        for (let i = 0; i < numCircles; i++) {
            const angle = (Math.PI * 2 * i) / numCircles + Math.random();
            const distance = (size / 2) * Math.random();
            const circleSize = (size / 4) * (0.3 + Math.random() * 0.7);

            const circle = new fabric.Circle({
                left: position[0] + Math.cos(angle) * distance - circleSize / 2,
                top: position[1] + Math.sin(angle) * distance - circleSize / 2,
                radius: circleSize,
                fill: color,
                opacity: 0.6 + Math.random() * 0.4
            });

            circles.push(circle);
        }

        return new fabric.Group(circles, {
            selectable: false,
            evented: false
        });
    }

    updateStatistics() {
        // Update stroke counts
        document.getElementById('patient-strokes').textContent = this.patientStrokeCount;
        document.getElementById('robot-strokes').textContent = this.robotStrokeCount;
        document.getElementById('total-strokes').textContent =
            this.patientStrokeCount + this.robotStrokeCount;

        // Calculate coverage (rough estimate based on object count)
        const coverage = Math.min(
            ((this.patientStrokeCount + this.robotStrokeCount) / 100) * 100,
            100
        );
        document.getElementById('canvas-coverage').textContent =
            Math.round(coverage) + '%';
    }

    clearCanvas() {
        this.canvas.clear();
        this.canvas.backgroundColor = '#FFFFFF';
        this.patientStrokeCount = 0;
        this.robotStrokeCount = 0;
        this.updateStatistics();
        this.historyManager.clear();
    }

    setColor(color) {
        this.currentColor = color;
        this.updateBrush();
    }

    setShape(shape) {
        this.currentShape = shape;
    }

    setSize(size) {
        this.currentSize = size;
        this.updateBrush();
    }

    setTool(tool) {
        this.currentTool = tool;
        this.updateBrush();
    }
}

// Initialize canvas when DOM is loaded
let canvasManager;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        canvasManager = new CanvasManager();
        window.canvasManager = canvasManager;
    });
} else {
    canvasManager = new CanvasManager();
    window.canvasManager = canvasManager;
}

export { CanvasManager, COLOR_MAP };
