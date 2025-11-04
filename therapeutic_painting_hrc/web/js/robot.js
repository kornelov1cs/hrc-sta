/**
 * Robot module - Manages WebSocket communication with backend
 */

class RobotClient {
    constructor(canvasManager) {
        this.canvasManager = canvasManager;
        this.websocket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;

        this.setupPromptInput();
        this.connect();
    }

    connect() {
        // Determine WebSocket URL
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        this.updateConnectionStatus('connecting', 'Connecting...');

        try {
            this.websocket = new WebSocket(wsUrl);

            this.websocket.onopen = () => {
                this.onConnect();
            };

            this.websocket.onmessage = (event) => {
                this.onMessage(event);
            };

            this.websocket.onerror = (error) => {
                this.onError(error);
            };

            this.websocket.onclose = () => {
                this.onDisconnect();
            };

        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.updateConnectionStatus('error', 'Connection failed');
            this.attemptReconnect();
        }
    }

    onConnect() {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.updateConnectionStatus('connected', 'Connected');
        this.addMessage('Connected to robot assistant', 'system');
    }

    onMessage(event) {
        try {
            const message = JSON.parse(event.data);
            const { type, data } = message;

            switch (type) {
                case 'robot_action':
                    this.handleRobotAction(data);
                    break;

                case 'belief_update':
                    this.handleBeliefUpdate(data);
                    break;

                case 'session_reset':
                    this.handleSessionReset();
                    break;

                case 'error':
                    this.handleError(data);
                    break;

                default:
                    console.warn('Unknown message type:', type);
            }

        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }

    onError(error) {
        console.error('WebSocket error:', error);
        this.updateConnectionStatus('error', 'Connection error');
    }

    onDisconnect() {
        console.log('WebSocket disconnected');
        this.updateConnectionStatus('disconnected', 'Disconnected');
        this.addMessage('Disconnected from robot assistant', 'system');
        this.attemptReconnect();
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            this.updateConnectionStatus(
                'reconnecting',
                `Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`
            );

            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay);
        } else {
            this.updateConnectionStatus('error', 'Failed to connect');
            this.addMessage('Failed to connect to robot assistant. Please refresh the page.', 'error');
        }
    }

    sendUserStroke(strokeData) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            const message = {
                type: 'user_stroke',
                data: strokeData
            };

            this.websocket.send(JSON.stringify(message));
        } else {
            console.error('WebSocket not connected');
            this.addMessage('Cannot send stroke: not connected to robot', 'error');
        }
    }

    sendPrompt(prompt) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            const message = {
                type: 'prompt',
                data: { prompt }
            };

            this.websocket.send(JSON.stringify(message));
            this.addMessage(`You: "${prompt}"`, 'user');
        } else {
            console.error('WebSocket not connected');
            this.addMessage('Cannot send prompt: not connected to robot', 'error');
        }
    }

    requestState() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            const message = {
                type: 'get_state',
                data: {}
            };

            this.websocket.send(JSON.stringify(message));
        }
    }

    resetSession() {
        // Call REST API to reset session
        fetch('/api/reset', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log('Session reset:', data);
                this.addMessage('Session reset', 'system');
            })
            .catch(error => {
                console.error('Error resetting session:', error);
                this.addMessage('Error resetting session', 'error');
            });
    }

    handleRobotAction(data) {
        const { action_type, strokes, message } = data;

        // Update robot action display
        document.getElementById('robot-action').textContent =
            this.formatActionType(action_type);

        // Add robot strokes to canvas
        if (strokes && strokes.length > 0) {
            strokes.forEach(stroke => {
                this.canvasManager.addRobotStroke(stroke);
            });
        }

        // Display message
        if (message) {
            this.addMessage(message, 'robot');
        }
    }

    handleBeliefUpdate(data) {
        const { belief_distribution, current_state, canvas_coverage, total_strokes } = data;

        // Update patient state
        document.getElementById('patient-state').textContent =
            this.formatPatientState(current_state);

        // Update belief distribution bars
        this.updateBeliefBars(belief_distribution);

        // Update statistics (if they differ from local count)
        if (total_strokes !== undefined) {
            document.getElementById('total-strokes').textContent = total_strokes;
        }

        if (canvas_coverage !== undefined) {
            document.getElementById('canvas-coverage').textContent =
                Math.round(canvas_coverage * 100) + '%';
        }
    }

    handleSessionReset() {
        this.addMessage('Session reset by system', 'system');
        // Canvas is already cleared by the clear button handler
    }

    handleError(data) {
        const { message } = data;
        console.error('Server error:', message);
        this.addMessage(`Error: ${message}`, 'error');
    }

    updateBeliefBars(distribution) {
        const container = document.getElementById('belief-distribution');
        container.innerHTML = '';

        // Sort by probability
        const sorted = Object.entries(distribution).sort((a, b) => b[1] - a[1]);

        sorted.forEach(([state, probability]) => {
            const barContainer = document.createElement('div');
            barContainer.className = 'belief-bar-container';

            const label = document.createElement('span');
            label.className = 'belief-label';
            label.textContent = this.formatPatientState(state);

            const barWrapper = document.createElement('div');
            barWrapper.className = 'belief-bar-wrapper';

            const bar = document.createElement('div');
            bar.className = 'belief-bar';
            bar.style.width = `${probability * 100}%`;

            const value = document.createElement('span');
            value.className = 'belief-value';
            value.textContent = `${Math.round(probability * 100)}%`;

            barWrapper.appendChild(bar);
            barContainer.appendChild(label);
            barContainer.appendChild(barWrapper);
            barContainer.appendChild(value);

            container.appendChild(barContainer);
        });
    }

    formatActionType(actionType) {
        // Convert action type to readable format
        const actionMap = {
            'InitiatePaint': 'Initiating painting',
            'ContinuePatient': 'Continuing your work',
            'SuggestColor': 'Suggesting color',
            'SuggestShape': 'Suggesting shape',
            'RespondToPrompt': 'Responding to prompt',
            'Wait': 'Waiting',
            'Observe': 'Observing'
        };

        return actionMap[actionType] || actionType;
    }

    formatPatientState(state) {
        // Convert state to readable format
        const stateMap = {
            'Engaged': 'Engaged',
            'NeedsSupport': 'Needs Support',
            'Hesitant': 'Hesitant',
            'Satisfied': 'Satisfied',
            'Frustrated': 'Frustrated'
        };

        return stateMap[state] || state;
    }

    updateConnectionStatus(status, text) {
        const statusDot = document.getElementById('connection-status');
        const statusText = document.getElementById('connection-text');

        statusDot.className = 'status-dot';
        statusDot.classList.add(`status-${status}`);
        statusText.textContent = text;
    }

    addMessage(text, type = 'info') {
        const messageLog = document.getElementById('message-log');

        const messageElement = document.createElement('div');
        messageElement.className = `message message-${type}`;

        const timestamp = new Date().toLocaleTimeString();
        messageElement.innerHTML = `
            <span class="message-time">${timestamp}</span>
            <span class="message-text">${text}</span>
        `;

        messageLog.appendChild(messageElement);

        // Scroll to bottom
        messageLog.scrollTop = messageLog.scrollHeight;

        // Limit message history to 20 messages
        while (messageLog.children.length > 20) {
            messageLog.removeChild(messageLog.firstChild);
        }
    }

    setupPromptInput() {
        const promptInput = document.getElementById('prompt-input');
        const sendButton = document.getElementById('send-prompt-btn');

        const sendPrompt = () => {
            const prompt = promptInput.value.trim();
            if (prompt) {
                this.sendPrompt(prompt);
                promptInput.value = '';
            }
        };

        sendButton.addEventListener('click', sendPrompt);

        promptInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendPrompt();
            }
        });
    }
}

export { RobotClient };
