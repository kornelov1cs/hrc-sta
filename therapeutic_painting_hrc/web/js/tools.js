/**
 * Tools module - Manages drawing tool selection and configuration
 */

class ToolManager {
    constructor(canvasManager) {
        this.canvasManager = canvasManager;
        this.setupToolListeners();
    }

    setupToolListeners() {
        // Tool buttons (pencil, marker, spray, eraser)
        const toolButtons = document.querySelectorAll('.tool-btn');
        toolButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tool = e.currentTarget.dataset.tool;
                this.selectTool(tool);
            });
        });

        // Shape buttons
        const shapeButtons = document.querySelectorAll('.shape-btn');
        shapeButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const shape = e.currentTarget.dataset.shape;
                this.selectShape(shape);
            });
        });

        // Color buttons
        const colorButtons = document.querySelectorAll('.color-btn');
        colorButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const color = e.currentTarget.dataset.color;
                this.selectColor(color);
            });
        });

        // Brush size slider
        const brushSizeSlider = document.getElementById('brush-size');
        const sizeValue = document.getElementById('size-value');
        brushSizeSlider.addEventListener('input', (e) => {
            const size = parseInt(e.target.value);
            sizeValue.textContent = size;
            this.canvasManager.setSize(size);
        });

        // Action buttons
        document.getElementById('undo-btn').addEventListener('click', () => {
            this.canvasManager.historyManager.undo();
        });

        document.getElementById('redo-btn').addEventListener('click', () => {
            this.canvasManager.historyManager.redo();
        });

        document.getElementById('clear-btn').addEventListener('click', () => {
            if (confirm('Are you sure you want to clear the canvas?')) {
                this.canvasManager.clearCanvas();
                this.canvasManager.robotClient.resetSession();
            }
        });
    }

    selectTool(tool) {
        // Update active state
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tool="${tool}"]`).classList.add('active');

        // Update canvas
        this.canvasManager.setTool(tool);
    }

    selectShape(shape) {
        // Update active state
        document.querySelectorAll('.shape-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-shape="${shape}"]`).classList.add('active');

        // Update canvas
        this.canvasManager.setShape(shape);
    }

    selectColor(color) {
        // Update active state
        document.querySelectorAll('.color-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-color="${color}"]`).classList.add('active');

        // Update canvas
        this.canvasManager.setColor(color);
    }
}

export { ToolManager };
