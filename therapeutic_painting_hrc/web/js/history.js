/**
 * History module - Manages undo/redo functionality
 */

class HistoryManager {
    constructor(canvasManager) {
        this.canvasManager = canvasManager;
        this.history = [];
        this.currentIndex = -1;
        this.maxHistory = 50; // Maximum number of states to keep
        this.isRestoring = false; // Flag to prevent saving during restore
        this.setupHistoryListeners();
    }

    setupHistoryListeners() {
        // Check if undo/redo buttons exist before setting up listeners
        const undoBtn = document.getElementById('undo-btn');
        const redoBtn = document.getElementById('redo-btn');

        if (undoBtn) {
            undoBtn.addEventListener('click', () => this.undo());
        }

        if (redoBtn) {
            redoBtn.addEventListener('click', () => this.redo());
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Z for undo
            if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
                e.preventDefault();
                this.undo();
            }
            // Ctrl/Cmd + Shift + Z or Ctrl/Cmd + Y for redo
            else if ((e.ctrlKey || e.metaKey) && (e.shiftKey && e.key === 'z' || e.key === 'y')) {
                e.preventDefault();
                this.redo();
            }
        });
    }

    saveState() {
        if (this.isRestoring) return;

        // Get current canvas state
        const state = JSON.stringify(this.canvasManager.canvas.toJSON([
            '_isPatientStroke',
            '_isRobotStroke'
        ]));

        // Remove any states after current index (when undoing then making new change)
        if (this.currentIndex < this.history.length - 1) {
            this.history = this.history.slice(0, this.currentIndex + 1);
        }

        // Add new state
        this.history.push(state);

        // Limit history size
        if (this.history.length > this.maxHistory) {
            this.history.shift();
        } else {
            this.currentIndex++;
        }

        this.updateButtons();
    }

    undo() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.restoreState(this.history[this.currentIndex]);
            this.updateButtons();
        }
    }

    redo() {
        if (this.currentIndex < this.history.length - 1) {
            this.currentIndex++;
            this.restoreState(this.history[this.currentIndex]);
            this.updateButtons();
        }
    }

    restoreState(stateJson) {
        this.isRestoring = true;

        const canvas = this.canvasManager.canvas;

        // Clear canvas
        canvas.clear();
        canvas.backgroundColor = '#FFFFFF';

        // Restore state
        canvas.loadFromJSON(JSON.parse(stateJson), () => {
            // Recalculate stroke counts
            this.recalculateStrokeCounts();

            // Update layer visibility
            this.canvasManager.layerManager.updateLayerVisibility();

            canvas.renderAll();
            this.isRestoring = false;
        });
    }

    recalculateStrokeCounts() {
        const canvas = this.canvasManager.canvas;
        const objects = canvas.getObjects();

        let patientCount = 0;
        let robotCount = 0;

        objects.forEach(obj => {
            if (obj._isPatientStroke) {
                patientCount++;
            } else if (obj._isRobotStroke) {
                robotCount++;
            }
        });

        this.canvasManager.patientStrokeCount = patientCount;
        this.canvasManager.robotStrokeCount = robotCount;
        this.canvasManager.updateStatistics();
    }

    updateButtons() {
        const undoBtn = document.getElementById('undo-btn');
        const redoBtn = document.getElementById('redo-btn');

        if (undoBtn) undoBtn.disabled = this.currentIndex <= 0;
        if (redoBtn) redoBtn.disabled = this.currentIndex >= this.history.length - 1;
    }

    clear() {
        this.history = [];
        this.currentIndex = -1;
        this.updateButtons();
    }

    canUndo() {
        return this.currentIndex > 0;
    }

    canRedo() {
        return this.currentIndex < this.history.length - 1;
    }
}

export { HistoryManager };
