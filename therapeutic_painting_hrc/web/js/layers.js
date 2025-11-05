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
        if (showPatientCheckbox) {
            showPatientCheckbox.addEventListener('change', (e) => {
                this.showPatientLayer = e.target.checked;
                this.updateLayerVisibility();
            });
        }

        // Robot layer toggle
        const showRobotCheckbox = document.getElementById('show-robot');
        if (showRobotCheckbox) {
            showRobotCheckbox.addEventListener('change', (e) => {
                this.showRobotLayer = e.target.checked;
                this.updateLayerVisibility();
            });
        }
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
        const showPatientCheckbox = document.getElementById('show-patient');
        const showRobotCheckbox = document.getElementById('show-robot');
        if (showPatientCheckbox) showPatientCheckbox.checked = true;
        if (showRobotCheckbox) showRobotCheckbox.checked = true;
        this.updateLayerVisibility();
    }

    showOnlyPatient() {
        this.showPatientLayer = true;
        this.showRobotLayer = false;
        const showPatientCheckbox = document.getElementById('show-patient');
        const showRobotCheckbox = document.getElementById('show-robot');
        if (showPatientCheckbox) showPatientCheckbox.checked = true;
        if (showRobotCheckbox) showRobotCheckbox.checked = false;
        this.updateLayerVisibility();
    }

    showOnlyRobot() {
        this.showPatientLayer = false;
        this.showRobotLayer = true;
        const showPatientCheckbox = document.getElementById('show-patient');
        const showRobotCheckbox = document.getElementById('show-robot');
        if (showPatientCheckbox) showPatientCheckbox.checked = false;
        if (showRobotCheckbox) showRobotCheckbox.checked = true;
        this.updateLayerVisibility();
    }
}

export { LayerManager };
