#!/usr/bin/env python3
"""
Python Terminal - Main Application

A fully functioning command terminal that mimics the behavior of a real system terminal.
"""

import os
import sys
import signal
import getpass
import socket
from typing import Optional

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.terminal_engine import TerminalEngine
from src.utils.formatter import OutputFormatter
from src.utils.error_handler import ErrorHandler


class PythonTerminal:
    """
    Main terminal application class.
    """
    
    def __init__(self, use_colors: bool = True, debug_mode: bool = False):
        """
        Initialize the Python terminal.
        
        Args:
            use_colors: Whether to use colored output
            debug_mode: Whether to enable debug mode
        """
        self.engine = TerminalEngine()
        self.formatter = OutputFormatter(use_colors=use_colors)
        self.error_handler = ErrorHandler(debug_mode=debug_mode)
        
        # Get system information
        try:
            self.username = getpass.getuser()
        except Exception:
            self.username = "user"
        
        try:
            self.hostname = socket.gethostname().split('.')[0]
        except Exception:
            self.hostname = "localhost"
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._handle_interrupt)
        
        self.running = True
    
    def _handle_interrupt(self, signum, frame):
        """Handle Ctrl+C interrupt."""
        print("\n" + self.error_handler.handle_keyboard_interrupt())
        self._show_prompt()
    
    def _show_prompt(self):
        """Display the command prompt."""
        current_dir = self.engine.get_current_directory()
        prompt = self.formatter.format_prompt(self.username, self.hostname, current_dir)
        print(prompt, end='', flush=True)
    
    def _show_welcome_message(self):
        """Display welcome message."""
        welcome_text = """
╔══════════════════════════════════════════════════════════════╗
║                    Python Terminal v1.0                      ║
║              A Python-based Command Terminal                 ║
╚══════════════════════════════════════════════════════════════╝

Welcome! This is a fully functional terminal implemented in Python.

Features:
• File and directory operations (ls, cd, mkdir, rm, cp, mv, etc.)
• System monitoring (ps, top, free, df, uptime)
• Command history and built-in help
• Error handling and auto-suggestions
• Colored output support

Type 'help' for a list of available commands or 'exit' to quit.
        """
        
        if self.formatter.use_colors:
            # Colorize the welcome message
            lines = welcome_text.split('\n')
            colored_lines = []
            for line in lines:
                if '║' in line and 'Python Terminal' in line:
                    colored_lines.append(self.formatter.colorize(line, 'green', 'bright'))
                elif '║' in line and 'Python-based' in line:
                    colored_lines.append(self.formatter.colorize(line, 'cyan'))
                elif line.startswith('Features:'):
                    colored_lines.append(self.formatter.colorize(line, 'yellow', 'bright'))
                elif line.startswith('•'):
                    colored_lines.append(self.formatter.colorize(line, 'white'))
                elif 'help' in line or 'exit' in line:
                    colored_lines.append(self.formatter.colorize(line, 'green'))
                else:
                    colored_lines.append(line)
            welcome_text = '\n'.join(colored_lines)
        
        print(welcome_text)
    
    def _process_command(self, command_line: str) -> bool:
        """
        Process a command line and return whether to continue running.
        
        Args:
            command_line: The command to process
            
        Returns:
            False if the terminal should exit, True otherwise
        """
        try:
            output, exit_code = self.engine.execute_command(command_line)
            
            # Display output if there is any
            if output:
                if exit_code != 0:
                    # Format error output
                    print(self.formatter.format_error(output))
                else:
                    print(output)
            
            # Check if the engine is still running
            return self.engine.is_running()
            
        except KeyboardInterrupt:
            print("\n" + self.error_handler.handle_keyboard_interrupt())
            return True
        except EOFError:
            print("\nGoodbye!")
            return False
        except Exception as e:
            error_msg = self.error_handler.handle_error(e, "command execution")
            print(self.formatter.format_error(error_msg))
            return True
    
    def run(self):
        """Run the main terminal loop."""
        self._show_welcome_message()
        
        try:
            while self.running:
                try:
                    self._show_prompt()
                    
                    # Read command from user
                    command_line = input().strip()
                    
                    if command_line:
                        # Process the command
                        self.running = self._process_command(command_line)
                    
                except EOFError:
                    # Handle Ctrl+D
                    print("\nGoodbye!")
                    break
                except KeyboardInterrupt:
                    # Handle Ctrl+C
                    print()
                    continue
                except Exception as e:
                    error_msg = self.error_handler.handle_error(e, "terminal loop")
                    print(self.formatter.format_error(error_msg))
                    continue
        
        except Exception as e:
            error_msg = self.error_handler.handle_error(e, "terminal startup")
            print(self.formatter.format_error(error_msg))
            return 1
        
        return 0


def main():
    """Main entry point for the terminal application."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Python Terminal - A fully functional command terminal implementation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start with default settings
  python main.py --no-colors        # Start without colored output
  python main.py --debug            # Start in debug mode
        """
    )
    
    parser.add_argument(
        '--no-colors', 
        action='store_true',
        help='Disable colored output'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode (show full error tracebacks)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Python Terminal v1.0'
    )
    
    args = parser.parse_args()
    
    # Create and run the terminal
    terminal = PythonTerminal(
        use_colors=not args.no_colors,
        debug_mode=args.debug
    )
    
    try:
        exit_code = terminal.run()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()