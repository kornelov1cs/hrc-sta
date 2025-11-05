/**
 * Layers module - Manages visibility of patient and robot stroke layers
 */

class LayerManager {
    constructor(canvasManager) {
        this.canvasManager = canvasManager;
        this.showPatientLayer = true;
        this.showRobotLayer = true;
        this.setupLayerListeners();
    }

    setupLayerListeners() {
        // Patient layer toggle
        const showPatientCheckbox = document.getElementById('show-patient');
        showPatientCheckbox.addEventListener('change', (e) => {
            this.showPatientLayer = e.target.checked;
            this.updateLayerVisibility();
        });

        // Robot layer toggle
        const showRobotCheckbox = document.getElementById('show-robot');
        showRobotCheckbox.addEventListener('change', (e) => {
            this.showRobotLayer = e.target.checked;
            this.updateLayerVisibility();
        });
    }

    updateLayerVisibility() {
        const canvas = this.canvasManager.canvas;
        const objects = canvas.getObjects();

        objects.forEach(obj => {
            if (obj._isPatientStroke) {
                obj.set('visible', this.showPatientLayer);
            } else if (obj._isRobotStroke) {
                obj.set('visible', this.showRobotLayer);
            }
        });

        canvas.renderAll();
    }

    showAllLayers() {
        this.showPatientLayer = true;
        this.showRobotLayer = true;
        document.getElementById('show-patient').checked = true;
        document.getElementById('show-robot').checked = true;
        this.updateLayerVisibility();
    }

    showOnlyPatient() {
        this.showPatientLayer = true;
        this.showRobotLayer = false;
        document.getElementById('show-patient').checked = true;
        document.getElementById('show-robot').checked = false;
        this.updateLayerVisibility();
    }

    showOnlyRobot() {
        this.showPatientLayer = false;
        this.showRobotLayer = true;
        document.getElementById('show-patient').checked = false;
        document.getElementById('show-robot').checked = true;
        this.updateLayerVisibility();
    }
}

export { LayerManager };
