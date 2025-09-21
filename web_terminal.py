#!/usr/bin/env python3
"""
Web Terminal - Flask Application

A web-based interface for the Python Terminal that can be hosted online.
"""

import sys
import os
import json
import threading
import time
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import uuid

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.terminal_engine import TerminalEngine
from src.utils.formatter import OutputFormatter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store terminal sessions
terminal_sessions = {}

class WebTerminalSession:
    """Represents a web terminal session for a user."""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.engine = TerminalEngine()
        self.formatter = OutputFormatter(use_colors=False)  # HTML will handle colors
        self.command_history = []
        self.created_at = time.time()
    
    def execute_command(self, command_line):
        """Execute a command and return formatted result."""
        try:
            # Add to history
            if command_line.strip():
                self.command_history.append(command_line)
            
            # Execute command
            output, exit_code = self.engine.execute_command(command_line)
            
            return {
                'command': command_line,
                'output': output,
                'exit_code': exit_code,
                'current_dir': self.engine.get_current_directory(),
                'timestamp': time.time()
            }
        except Exception as e:
            return {
                'command': command_line,
                'output': f'Error: {str(e)}',
                'exit_code': 1,
                'current_dir': self.engine.get_current_directory(),
                'timestamp': time.time()
            }

def get_or_create_session(session_id=None):
    """Get existing session or create a new one."""
    if session_id is None:
        session_id = str(uuid.uuid4())
    
    if session_id not in terminal_sessions:
        terminal_sessions[session_id] = WebTerminalSession(session_id)
    
    return terminal_sessions[session_id], session_id

def cleanup_old_sessions():
    """Clean up sessions older than 1 hour."""
    current_time = time.time()
    old_sessions = []
    
    for session_id, terminal_session in terminal_sessions.items():
        if current_time - terminal_session.created_at > 3600:  # 1 hour
            old_sessions.append(session_id)
    
    for session_id in old_sessions:
        del terminal_sessions[session_id]

# Clean up old sessions periodically
def periodic_cleanup():
    while True:
        time.sleep(300)  # Every 5 minutes
        cleanup_old_sessions()

cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    """Main terminal page."""
    return render_template('terminal.html')

@app.route('/api/execute', methods=['POST'])
def execute_command():
    """Execute a terminal command via API."""
    data = request.get_json()
    command = data.get('command', '').strip()
    session_id = data.get('session_id')
    
    terminal_session, session_id = get_or_create_session(session_id)
    result = terminal_session.execute_command(command)
    result['session_id'] = session_id
    
    return jsonify(result)

@app.route('/api/session', methods=['POST'])
def create_session():
    """Create a new terminal session."""
    terminal_session, session_id = get_or_create_session()
    
    return jsonify({
        'session_id': session_id,
        'current_dir': terminal_session.engine.get_current_directory(),
        'welcome_message': get_welcome_message()
    })

@app.route('/api/history/<session_id>')
def get_history(session_id):
    """Get command history for a session."""
    if session_id in terminal_sessions:
        return jsonify({
            'history': terminal_sessions[session_id].command_history,
            'current_dir': terminal_sessions[session_id].engine.get_current_directory()
        })
    else:
        return jsonify({'error': 'Session not found'}), 404

@app.route('/api/examples')
def get_examples():
    """Get example commands and AI queries."""
    examples = {
        'basic_commands': [
            'ls',
            'pwd',
            'ls -la',
            'help',
            'history'
        ],
        'file_operations': [
            'mkdir test_folder',
            'touch test_file.txt',
            'cat README.md',
            'cp file1.txt file2.txt',
            'rm test_file.txt'
        ],
        'system_monitoring': [
            'ps',
            'free -h',
            'df -h',
            'uptime',
            'whoami'
        ],
        'ai_natural_language': [
            'show me the files in this directory',
            'create a new folder called projects',
            'what processes are running',
            'show system memory usage',
            'delete the test folder',
            'copy README.md to backup'
        ]
    }
    return jsonify(examples)

def get_welcome_message():
    """Get the welcome message for the web terminal."""
    return """
🌐 Python Web Terminal v1.0
==========================

Welcome to the web-based Python Terminal! 

Features:
• Full terminal command support
• 🤖 AI-powered natural language processing
• Real-time command execution
• File and system operations
• Cross-platform compatibility

Try these commands:
• 'help' - Show available commands
• 'ai examples' - Show AI command examples
• 'ls' - List files
• "show me the current directory" - Natural language!

Type your commands below and press Enter to execute.
    """.strip()

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('connected', {'message': 'Connected to Python Web Terminal'})

@socketio.on('execute_command')
def handle_command(data):
    """Handle command execution via WebSocket."""
    command = data.get('command', '').strip()
    session_id = data.get('session_id')
    
    terminal_session, session_id = get_or_create_session(session_id)
    result = terminal_session.execute_command(command)
    result['session_id'] = session_id
    
    emit('command_result', result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"""
🌐 Python Web Terminal Starting...
================================

Server will be available at:
• Local: http://localhost:{port}
• Network: http://0.0.0.0:{port}

Features enabled:
✅ REST API endpoints
✅ WebSocket real-time communication  
✅ AI natural language processing
✅ Session management
✅ Command history

Press Ctrl+C to stop the server.
    """)
    
    socketio.run(app, host='0.0.0.0', port=port, debug=debug)
