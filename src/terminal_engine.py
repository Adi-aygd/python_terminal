import os
import sys
import shlex
from typing import Dict, List, Tuple, Optional, Any
from .command_parser import CommandParser
from .file_operations import FileOperations
from .system_monitor import SystemMonitor
from .ai_processor import AIProcessor
from .utils.error_handler import ErrorHandler
from .utils.formatter import OutputFormatter


class TerminalEngine:
    """
    Main terminal engine that handles command execution and coordination
    between different modules.
    """
    
    def __init__(self):
        """Initialize the terminal engine with all necessary components."""
        self.current_directory = os.getcwd()
        self.command_parser = CommandParser()
        self.file_ops = FileOperations()
        self.system_monitor = SystemMonitor()
        self.ai_processor = AIProcessor()
        self.error_handler = ErrorHandler()
        self.formatter = OutputFormatter()
        self.command_history: List[str] = []
        self.running = True
        
        # Built-in commands that are handled by the terminal engine
        self.builtin_commands = {
            'exit': self._handle_exit,
            'quit': self._handle_exit,
            'help': self._handle_help,
            'history': self._handle_history,
            'clear': self._handle_clear,
            'cd': self._handle_cd,
            'pwd': self._handle_pwd,
            'ai': self._handle_ai,
            'ask': self._handle_ai,
        }
    
    def execute_command(self, command_line: str) -> Tuple[str, int]:
        """
        Execute a command and return the output and exit code.
        
        Args:
            command_line: The command string to execute
            
        Returns:
            Tuple of (output_string, exit_code)
        """
        if not command_line.strip():
            return "", 0
        
        # Add to history
        self.command_history.append(command_line)
        
        try:
            # First, check if this looks like a natural language query
            if self.ai_processor.is_natural_language_query(command_line):
                ai_command = self.ai_processor.process_query(command_line)
                if ai_command:
                    # Execute the AI-generated command
                    return self.execute_command(ai_command)
                else:
                    # Provide suggestions if AI couldn't process the query
                    suggestions = self.ai_processor.get_suggestions(command_line)
                    if suggestions:
                        suggestion_text = "I couldn't understand that command. Did you mean:\n" + "\n".join(f"  • {s}" for s in suggestions)
                        return suggestion_text, 1
                    else:
                        return "I couldn't understand that command. Type 'help' for available commands or 'ai examples' for natural language examples.", 1
            
            # Parse the command
            command, args = self.command_parser.parse_command(command_line)
            
            # Check if it's a built-in command
            if command in self.builtin_commands:
                return self.builtin_commands[command](args)
            
            # Check if it's a file operation
            elif command in self.file_ops.get_supported_commands():
                return self.file_ops.execute_command(command, args, self.current_directory)
            
            # Check if it's a system monitoring command
            elif command in self.system_monitor.get_supported_commands():
                return self.system_monitor.execute_command(command, args)
            
            # Try to execute as a system command
            else:
                return self._execute_system_command(command, args)
                
        except Exception as e:
            error_msg = self.error_handler.handle_error(e, command_line)
            return error_msg, 1
    
    def _execute_system_command(self, command: str, args: List[str]) -> Tuple[str, int]:
        """Execute a system command using subprocess."""
        import subprocess
        
        try:
            cmd_list = [command] + args
            result = subprocess.run(
                cmd_list,
                capture_output=True,
                text=True,
                cwd=self.current_directory,
                timeout=30
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n{result.stderr}"
            
            return output, result.returncode
            
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds", 1
        except FileNotFoundError:
            return f"Command '{command}' not found", 127
        except Exception as e:
            return f"Error executing command: {str(e)}", 1
    
    def _handle_exit(self, args: List[str]) -> Tuple[str, int]:
        """Handle exit command."""
        self.running = False
        return "Goodbye!", 0
    
    def _handle_help(self, args: List[str]) -> Tuple[str, int]:
        """Handle help command."""
        help_text = """
Available Commands:
==================

Built-in Commands:
  exit, quit    - Exit the terminal
  help          - Show this help message
  history       - Show command history
  clear         - Clear the screen
  cd <dir>      - Change directory
  pwd           - Print working directory

File Operations:
  ls [options] [path]     - List directory contents
  mkdir <dir>             - Create directory
  rmdir <dir>             - Remove empty directory
  rm <file/dir>           - Remove file or directory
  cp <src> <dest>         - Copy file or directory
  mv <src> <dest>         - Move/rename file or directory
  cat <file>              - Display file contents
  touch <file>            - Create empty file
  find <path> <name>      - Find files/directories

System Monitoring:
  ps [options]            - List running processes
  top                     - Show system processes (snapshot)
  df [path]               - Show disk space usage
  free                    - Show memory usage
  uptime                  - Show system uptime

AI Commands:
  ai <query>        - Process natural language query
  ask <query>       - Same as 'ai'
  ai examples       - Show natural language examples

System Commands:
  Any other command will be passed to the system shell.

Examples:
  ls -la
  mkdir new_folder
  cp file1.txt backup/
  ps aux
  find . *.py

Natural Language Examples:
  "show me the files in this directory"
  "create a new folder called projects"
  "copy file.txt to backup folder"
  "find all python files"
  "what processes are running"
        """
        return help_text, 0
    
    def _handle_history(self, args: List[str]) -> Tuple[str, int]:
        """Handle history command."""
        if not self.command_history:
            return "No commands in history", 0
        
        history_text = ""
        for i, cmd in enumerate(self.command_history[-50:], 1):  # Show last 50 commands
            history_text += f"{i:3d}  {cmd}\n"
        
        return history_text, 0
    
    def _handle_clear(self, args: List[str]) -> Tuple[str, int]:
        """Handle clear command."""
        # Return ANSI escape sequence to clear screen
        return "\033[2J\033[H", 0
    
    def _handle_cd(self, args: List[str]) -> Tuple[str, int]:
        """Handle cd command."""
        if not args:
            # Go to home directory
            target_dir = os.path.expanduser("~")
        else:
            target_dir = args[0]
        
        try:
            # Handle special cases
            if target_dir == "-":
                # Go back to previous directory (simplified version)
                target_dir = os.path.expanduser("~")
            elif target_dir.startswith("~"):
                target_dir = os.path.expanduser(target_dir)
            elif not os.path.isabs(target_dir):
                target_dir = os.path.join(self.current_directory, target_dir)
            
            # Normalize the path
            target_dir = os.path.abspath(target_dir)
            
            if not os.path.exists(target_dir):
                return f"cd: no such file or directory: {args[0] if args else '~'}", 1
            
            if not os.path.isdir(target_dir):
                return f"cd: not a directory: {args[0] if args else '~'}", 1
            
            self.current_directory = target_dir
            os.chdir(target_dir)  # Also change the actual working directory
            return "", 0
            
        except PermissionError:
            return f"cd: permission denied: {args[0] if args else '~'}", 1
        except Exception as e:
            return f"cd: {str(e)}", 1
    
    def _handle_pwd(self, args: List[str]) -> Tuple[str, int]:
        """Handle pwd command."""
        return self.current_directory, 0
    
    def _handle_ai(self, args: List[str]) -> Tuple[str, int]:
        """Handle AI natural language processing commands."""
        if not args:
            return "Usage: ai <natural language query>\nExample: ai 'show me the files in this directory'\nType 'ai examples' for more examples.", 1
        
        query = ' '.join(args)
        
        # Special case for examples
        if query.lower() in ['examples', 'example', 'help']:
            examples = self.ai_processor.get_example_queries()
            output = "Natural Language Examples:\n\n"
            for i, example in enumerate(examples, 1):
                output += f"{i:2d}. {example}\n"
            output += "\nYou can also use these queries directly without the 'ai' command."
            return output, 0
        
        # Process the natural language query
        ai_command = self.ai_processor.process_query(query)
        if ai_command:
            output = f"Executing: {ai_command}\n"
            result, exit_code = self.execute_command(ai_command)
            return output + result, exit_code
        else:
            # Provide suggestions if AI couldn't process the query
            suggestions = self.ai_processor.get_suggestions(query)
            if suggestions:
                suggestion_text = "I couldn't understand that query. Did you mean:\n" + "\n".join(f"  • {s}" for s in suggestions)
                return suggestion_text, 1
            else:
                return "I couldn't understand that query. Type 'ai examples' for example queries.", 1
    
    def get_current_directory(self) -> str:
        """Get the current working directory."""
        return self.current_directory
    
    def is_running(self) -> bool:
        """Check if the terminal is still running."""
        return self.running
    
    def get_command_history(self) -> List[str]:
        """Get the command history."""
        return self.command_history.copy()