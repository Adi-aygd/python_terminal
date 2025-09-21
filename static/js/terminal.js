// Python Web Terminal JavaScript

class WebTerminal {
    constructor() {
        this.sessionId = null;
        this.commandHistory = [];
        this.historyIndex = -1;
        this.socket = null;
        
        // DOM elements
        this.terminalOutput = document.getElementById('terminal-output');
        this.commandInput = document.getElementById('command-input');
        this.promptElement = document.getElementById('prompt');
        this.currentDirElement = document.getElementById('current-dir');
        this.connectionStatus = document.getElementById('connection-status');
        this.sessionInfo = document.getElementById('session-info');
        this.sessionIdElement = document.getElementById('session-id');
        this.loadingElement = document.getElementById('loading');
        
        this.init();
    }
    
    async init() {
        await this.createSession();
        this.setupSocketIO();
        this.setupEventListeners();
        this.focusInput();
        this.showWelcomeMessage();
    }
    
    async createSession() {
        try {
            const response = await fetch('/api/session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            this.sessionId = data.session_id;
            this.updateCurrentDir(data.current_dir);
            this.updateSessionInfo();
            
            // Show welcome message
            this.addOutputLine(data.welcome_message, 'info');
            
        } catch (error) {
            console.error('Failed to create session:', error);
            this.addOutputLine('Failed to connect to server', 'error');
        }
    }
    
    setupSocketIO() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            this.updateConnectionStatus(true);
        });
        
        this.socket.on('disconnect', () => {
            this.updateConnectionStatus(false);
        });
        
        this.socket.on('command_result', (result) => {
            this.handleCommandResult(result);
        });
    }
    
    setupEventListeners() {
        // Command input
        this.commandInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.executeCommand();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateHistory(-1);
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.navigateHistory(1);
            } else if (e.key === 'Tab') {
                e.preventDefault();
                // TODO: Add auto-completion
            }
        });
        
        // Header buttons
        document.getElementById('clear-btn').addEventListener('click', () => {
            this.clearTerminal();
        });
        
        document.getElementById('help-btn').addEventListener('click', () => {
            this.executeCommandString('help');
        });
        
        document.getElementById('examples-btn').addEventListener('click', () => {
            this.showExamples();
        });
        
        // Modal close
        document.querySelector('.close-modal').addEventListener('click', () => {
            this.closeModal();
        });
        
        // Click outside modal to close
        document.getElementById('examples-modal').addEventListener('click', (e) => {
            if (e.target.id === 'examples-modal') {
                this.closeModal();
            }
        });
        
        // Focus input when clicking on terminal
        this.terminalOutput.addEventListener('click', () => {
            this.focusInput();
        });
    }
    
    async executeCommand() {
        const command = this.commandInput.value.trim();
        if (!command) return;
        
        // Add to history
        this.commandHistory.push(command);
        this.historyIndex = this.commandHistory.length;
        
        // Show command in terminal
        this.addCommandLine(command);
        this.commandInput.value = '';
        
        // Show loading
        this.showLoading();
        
        try {
            // Execute via REST API
            const response = await fetch('/api/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    command: command,
                    session_id: this.sessionId
                })
            });
            
            const result = await response.json();
            this.handleCommandResult(result);
            
        } catch (error) {
            console.error('Command execution failed:', error);
            this.addOutputLine(`Error: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    executeCommandString(command) {
        this.commandInput.value = command;
        this.executeCommand();
    }
    
    handleCommandResult(result) {
        // Update current directory
        if (result.current_dir) {
            this.updateCurrentDir(result.current_dir);
        }
        
        // Show output
        if (result.output) {
            const cssClass = result.exit_code === 0 ? 'success' : 'error';
            this.addOutputLine(result.output, cssClass);
        }
        
        // Scroll to bottom
        this.scrollToBottom();
    }
    
    addCommandLine(command) {
        const commandElement = document.createElement('div');
        commandElement.className = 'command-line new';
        commandElement.innerHTML = `
            <span class="command-prompt">$ </span>
            <span class="command-text">${this.escapeHtml(command)}</span>
        `;
        this.terminalOutput.appendChild(commandElement);
        this.scrollToBottom();
    }
    
    addOutputLine(output, cssClass = '') {
        if (!output) return;
        
        const outputElement = document.createElement('div');
        outputElement.className = `command-output ${cssClass}`;
        outputElement.textContent = output;
        this.terminalOutput.appendChild(outputElement);
        this.scrollToBottom();
    }
    
    navigateHistory(direction) {
        if (this.commandHistory.length === 0) return;
        
        this.historyIndex += direction;
        
        if (this.historyIndex < 0) {
            this.historyIndex = 0;
        } else if (this.historyIndex >= this.commandHistory.length) {
            this.historyIndex = this.commandHistory.length;
            this.commandInput.value = '';
            return;
        }
        
        this.commandInput.value = this.commandHistory[this.historyIndex];
    }
    
    clearTerminal() {
        this.terminalOutput.innerHTML = '';
        this.focusInput();
    }
    
    focusInput() {
        this.commandInput.focus();
    }
    
    scrollToBottom() {
        this.terminalOutput.scrollTop = this.terminalOutput.scrollHeight;
    }
    
    updateCurrentDir(dir) {
        this.currentDirElement.textContent = dir;
        // Update prompt to show shortened path
        const shortDir = this.shortenPath(dir);
        this.promptElement.textContent = `${shortDir}$ `;
    }
    
    shortenPath(path) {
        if (path.length <= 30) return path;
        
        const parts = path.split('/');
        if (parts.length <= 3) return path;
        
        return '.../' + parts.slice(-2).join('/');
    }
    
    updateConnectionStatus(connected) {
        if (connected) {
            this.connectionStatus.textContent = 'Connected';
            this.connectionStatus.className = 'status-connected';
        } else {
            this.connectionStatus.textContent = 'Disconnected';
            this.connectionStatus.className = 'status-disconnected';
        }
    }
    
    updateSessionInfo() {
        if (this.sessionId) {
            this.sessionInfo.textContent = `Python Terminal - Session Active`;
            this.sessionIdElement.textContent = `Session: ${this.sessionId.slice(0, 8)}...`;
        }
    }
    
    showLoading() {
        this.loadingElement.style.display = 'flex';
    }
    
    hideLoading() {
        this.loadingElement.style.display = 'none';
    }
    
    async showExamples() {
        try {
            const response = await fetch('/api/examples');
            const examples = await response.json();
            
            // Populate modal with examples
            for (const [category, commands] of Object.entries(examples)) {
                const container = document.getElementById(category.replace('_', '-'));
                if (container) {
                    container.innerHTML = '';
                    commands.forEach(command => {
                        const element = document.createElement('div');
                        element.className = 'example-command';
                        element.innerHTML = `<code>${this.escapeHtml(command)}</code>`;
                        element.addEventListener('click', () => {
                            this.executeCommandString(command);
                            this.closeModal();
                        });
                        container.appendChild(element);
                    });
                }
            }
            
            // Show modal
            document.getElementById('examples-modal').style.display = 'block';
            
        } catch (error) {
            console.error('Failed to load examples:', error);
            this.addOutputLine('Failed to load examples', 'error');
        }
    }
    
    closeModal() {
        document.getElementById('examples-modal').style.display = 'none';
        this.focusInput();
    }
    
    showWelcomeMessage() {
        // Add some interactive hints
        setTimeout(() => {
            this.addOutputLine('\\n💡 Try typing "help" for available commands or click "Examples" for more ideas!', 'info');
            this.addOutputLine('🤖 You can also use natural language like "show me the files" or "create a folder called test"', 'info');
        }, 1000);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize terminal when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.terminal = new WebTerminal();
});

// Global keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+L to clear terminal
    if (e.ctrlKey && e.key === 'l') {
        e.preventDefault();
        if (window.terminal) {
            window.terminal.clearTerminal();
        }
    }
    
    // Escape to close modal
    if (e.key === 'Escape') {
        if (window.terminal) {
            window.terminal.closeModal();
        }
    }
});