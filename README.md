# Python-Based Command Terminal

A fully functioning command terminal that mimics the behavior of a real system terminal, built in Python. This project implements a comprehensive terminal emulator with advanced features including natural language processing for command interpretation.

## 🚀 Features

### Core Terminal Features
- **File and Directory Operations**: Complete support for ls, cd, pwd, mkdir, rmdir, rm, cp, mv, cat, touch, find, head, tail, wc, stat
- **System Monitoring**: Real-time system information with ps, top, free, df, uptime, kill, killall, who, whoami, uname
- **Built-in Commands**: help, history, clear, exit with proper error handling
- **Command History**: Persistent command history with easy retrieval
- **Error Handling**: Comprehensive error handling with user-friendly messages and suggestions
- **Colored Output**: Beautiful, colored terminal output with cross-platform support
- **Process Management**: Kill processes by PID or name with signal support

### Advanced Features
- **🤖 AI-Driven Natural Language Processing**: Convert plain English to terminal commands
  - "show me the files in this directory" → `ls`
  - "create a new folder called projects" → `mkdir projects`
  - "copy file.txt to backup folder" → `cp file.txt backup`
  - "find all python files" → `find . *.py`
  - "what processes are running" → `ps aux`
- **🌍 Web Terminal Interface**: Full browser-based terminal with modern UI
- **⚡ Real-time WebSocket Communication**: Instant command execution and responses
- **📱 Mobile Responsive**: Works perfectly on phones, tablets, and desktops
- **🔄 Session Management**: Multi-user support with isolated terminal sessions
- **Smart Command Suggestions**: Get helpful suggestions for mistyped or unclear commands
- **Extensible Architecture**: Modular design for easy feature additions

## Project Structure

```
python-terminal-project/
├── src/
│   ├── __init__.py
│   ├── terminal_engine.py      # Core terminal engine
│   ├── command_parser.py       # Command parsing logic
│   ├── file_operations.py      # File and directory operations
│   ├── system_monitor.py       # System monitoring tools
│   ├── ai_processor.py         # Natural language processing
│   └── utils/
│       ├── __init__.py
│       ├── error_handler.py    # Error handling utilities
│       └── formatter.py        # Output formatting
├── tests/
│   ├── __init__.py
│   └── test_terminal.py
├── main.py                     # Main application entry point
├── requirements.txt
└── README.md
```

## 🛠️ Installation

### Prerequisites
- Python 3.6 or higher
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd python-terminal-project
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the terminal**
   ```bash
   # CLI Version (Local)
   python main.py
   
   # Web Version (Browser-based)
   python web_terminal.py
   # Then visit http://localhost:5000
   ```

### Alternative Installation Options

- **Without colors**: `python main.py --no-colors`
- **Debug mode**: `python main.py --debug`
- **Help**: `python main.py --help`

## 🚀 Usage

### Standard Terminal Commands

#### File and Directory Operations
```bash
ls [options] [path]     # List directory contents
ls -la                  # List all files with detailed info
cd <directory>          # Change directory
cd ~                    # Go to home directory
cd ..                   # Go to parent directory
pwd                     # Print working directory
mkdir <directory>       # Create directory
rmdir <directory>       # Remove empty directory
rm <file>              # Remove file
rm -r <directory>      # Remove directory recursively
cp <source> <dest>     # Copy file or directory
mv <source> <dest>     # Move/rename file or directory
cat <file>             # Display file contents
touch <file>           # Create empty file or update timestamp
find <path> <pattern>  # Find files matching pattern
head <file>            # Show first 10 lines of file
tail <file>            # Show last 10 lines of file
wc <file>              # Count lines, words, and characters
stat <file>            # Show file statistics
```

#### System Monitoring
```bash
ps [options]           # List running processes
ps aux                 # Show all processes with detailed info
top                    # Show system processes (snapshot)
free [-h]              # Show memory usage
df [-h]                # Show disk space usage
uptime                 # Show system uptime
kill <pid>             # Terminate process by PID
kill -9 <pid>          # Force kill process
killall <name>         # Kill all processes by name
who                    # Show logged in users
whoami                 # Show current user
uname [-a]             # Show system information
```

#### Built-in Commands
```bash
help                   # Show available commands
history                # Show command history
clear                  # Clear the screen
exit                   # Exit the terminal
quit                   # Exit the terminal
```

### 🤖 AI-Powered Natural Language Commands

You can interact with the terminal using plain English! The AI processor understands natural language and converts it to appropriate terminal commands.

#### Direct Natural Language Input
Just type your request naturally:
```
show me the files in this directory
create a new folder called projects
copy README.md to backup folder
find all python files
what processes are running
show system memory usage
go to the home directory
delete the old log file
where am I?
what's in the Documents folder?
```

#### Explicit AI Commands
```bash
ai <query>             # Process natural language query
ask <query>            # Same as 'ai'
ai examples            # Show example natural language queries
```

#### AI Command Examples
```bash
ai "show me all files including hidden ones"
ask "create a directory called test_project"
ai "copy all text files to backup"
ask "find files containing 'python'"
ai "show me the system uptime"
```

### 📝 Example Session

```bash
$ python main.py

╭──────────────────────────────────────────────────────────────╮
│                    Python Terminal v1.0                      │
│              A Python-based Command Terminal                 │
╰──────────────────────────────────────────────────────────────╯

user@hostname:~$ ls
Documents  Downloads  Pictures  Desktop  python-terminal-project

user@hostname:~$ show me what's in the Documents folder
Executing: ls Documents
file1.txt  file2.pdf  notes.md  projects

user@hostname:~$ create a new directory called workspace
Executing: mkdir workspace

user@hostname:~$ what processes are running?
Executing: ps aux
USER       PID  PPID  %CPU %MEM STAT TIME COMMAND
root         1     0   0.0  0.1 S    00:01 /sbin/init
...

user@hostname:~$ help
Available Commands:
==================

Built-in Commands:
  exit, quit    - Exit the terminal
  help          - Show this help message
  ...

user@hostname:~$ exit
Goodbye!
```

## 🌍 Web Terminal

In addition to the CLI version, the project includes a **full web-based terminal** that runs in your browser!

### 🎆 Web Features

- **🔥 Browser-Based**: No installation needed - runs in any modern browser
- **🎨 Beautiful UI**: Professional dark theme with terminal aesthetics  
- **📱 Responsive Design**: Perfect on desktop, tablet, and mobile devices
- **⚡ Real-Time**: WebSocket-powered for instant command execution
- **👥 Multi-User**: Isolated sessions for multiple simultaneous users
- **🤖 Full AI Support**: Same natural language processing as CLI version
- **📊 Session Management**: Command history, current directory tracking
- **🌐 Deployable**: Ready for cloud hosting with live URL

### 🚀 Running the Web Terminal

```bash
# Start the web server
source venv/bin/activate
python web_terminal.py

# Open your browser to:
# http://localhost:5000
```

### 🎆 Web Terminal Screenshots

The web interface provides:
- **Modern terminal window** with macOS-style controls
- **Real-time command execution** with loading indicators
- **Interactive examples modal** with clickable commands
- **Status bar** showing current directory and connection status
- **Mobile-optimized layout** that works on any device

## 🌍 Live Deployment

https://python-terminal-1-5dm1.onrender.com

## 🏧 Architecture

The Python Terminal is built with a modular architecture for maintainability and extensibility:

```
python-terminal-project/
├── src/
│   ├── terminal_engine.py      # Core terminal engine and command coordinator
│   ├── command_parser.py       # Command line parsing and processing
│   ├── file_operations.py      # File and directory operations
│   ├── system_monitor.py       # System monitoring and process management
│   ├── ai_processor.py         # Natural language processing
│   └── utils/
│       ├── error_handler.py    # Centralized error handling
│       └── formatter.py        # Output formatting and colorization
├── main.py                     # Application entry point
├── test_terminal.py            # Test suite
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

### Key Components

- **TerminalEngine**: Central coordinator that manages command execution and module interaction
- **CommandParser**: Handles command line parsing, argument processing, and shell features
- **FileOperations**: Implements all file and directory operations with proper error handling
- **SystemMonitor**: Provides system monitoring capabilities using psutil
- **AIProcessor**: Natural language processing engine with pattern matching
- **ErrorHandler**: Centralized error handling with user-friendly messages
- **OutputFormatter**: Cross-platform colored output and text formatting

## 🧪 Testing

Run the test suite to verify everything is working correctly:

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
python test_terminal.py
```

The test suite validates:
- Basic terminal commands (pwd, ls, help)
- File operations (mkdir, rmdir, touch, rm)
- AI natural language processing
- System monitoring commands
- Error handling and edge cases

## 📜 Dependencies

The project uses the following Python packages:

- **psutil** (≥ 5.9.0): System and process monitoring
- **colorama** (≥ 0.4.6): Cross-platform colored output
- **prompt-toolkit** (≥ 3.0.36): Advanced terminal input handling
- **tabulate** (≥ 0.9.0): Pretty table formatting
- **click** (≥ 8.1.0): Command-line interface utilities

## 🔧 Development

### Adding New Commands

1. **File Operations**: Add to `FileOperations` class in `file_operations.py`
2. **System Commands**: Add to `SystemMonitor` class in `system_monitor.py`
3. **Built-in Commands**: Add to `builtin_commands` dict in `terminal_engine.py`
4. **AI Patterns**: Add natural language patterns to `ai_processor.py`

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

