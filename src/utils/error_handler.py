"""
Error Handler

This module provides centralized error handling for the terminal.
"""

import sys
import traceback
from typing import Any, Optional


class ErrorHandler:
    """
    Handles and formats errors consistently across the terminal.
    """
    
    def __init__(self, debug_mode: bool = False):
        """
        Initialize error handler.
        
        Args:
            debug_mode: If True, show full tracebacks
        """
        self.debug_mode = debug_mode
    
    def handle_error(self, exception: Exception, context: str = "") -> str:
        """
        Handle an exception and return a formatted error message.
        
        Args:
            exception: The exception that occurred
            context: Additional context about where the error occurred
            
        Returns:
            Formatted error message
        """
        if self.debug_mode:
            # In debug mode, show full traceback
            return f"Error: {str(exception)}\n{traceback.format_exc()}"
        else:
            # In normal mode, show user-friendly error message
            error_type = type(exception).__name__
            error_msg = str(exception)
            
            # Handle common exceptions with user-friendly messages
            if isinstance(exception, FileNotFoundError):
                return f"File or directory not found: {error_msg}"
            elif isinstance(exception, PermissionError):
                return f"Permission denied: {error_msg}"
            elif isinstance(exception, IsADirectoryError):
                return f"Is a directory: {error_msg}"
            elif isinstance(exception, NotADirectoryError):
                return f"Not a directory: {error_msg}"
            elif isinstance(exception, OSError):
                return f"System error: {error_msg}"
            elif isinstance(exception, ValueError):
                return f"Invalid value: {error_msg}"
            elif isinstance(exception, KeyError):
                return f"Key error: {error_msg}"
            elif isinstance(exception, IndexError):
                return f"Index error: {error_msg}"
            elif isinstance(exception, TypeError):
                return f"Type error: {error_msg}"
            else:
                # Generic error message
                if context:
                    return f"Error in {context}: {error_msg}"
                else:
                    return f"Error: {error_msg}"
    
    def handle_command_not_found(self, command: str) -> str:
        """
        Handle command not found error.
        
        Args:
            command: The command that was not found
            
        Returns:
            Error message with suggestions
        """
        message = f"Command '{command}' not found."
        
        # Suggest common alternatives for typos
        suggestions = self._get_command_suggestions(command)
        if suggestions:
            message += f"\nDid you mean: {', '.join(suggestions)}?"
        
        return message
    
    def handle_invalid_arguments(self, command: str, error_msg: str = "") -> str:
        """
        Handle invalid arguments error.
        
        Args:
            command: The command with invalid arguments
            error_msg: Specific error message
            
        Returns:
            Error message with usage hint
        """
        message = f"Invalid arguments for '{command}'"
        if error_msg:
            message += f": {error_msg}"
        
        message += f"\nType 'help {command}' for usage information."
        return message
    
    def handle_permission_error(self, path: str, operation: str = "") -> str:
        """
        Handle permission errors for file operations.
        
        Args:
            path: The path that caused the permission error
            operation: The operation being attempted
            
        Returns:
            User-friendly error message
        """
        if operation:
            return f"Permission denied: cannot {operation} '{path}'"
        else:
            return f"Permission denied: '{path}'"
    
    def handle_file_not_found(self, path: str, operation: str = "") -> str:
        """
        Handle file not found errors.
        
        Args:
            path: The path that was not found
            operation: The operation being attempted
            
        Returns:
            User-friendly error message
        """
        if operation:
            return f"Cannot {operation} '{path}': No such file or directory"
        else:
            return f"'{path}': No such file or directory"
    
    def handle_directory_not_empty(self, path: str) -> str:
        """
        Handle directory not empty errors.
        
        Args:
            path: The directory path
            
        Returns:
            Error message with suggestion
        """
        return f"Directory not empty: '{path}'\nUse 'rm -r' to remove directory and its contents."
    
    def handle_disk_full(self, path: str = "") -> str:
        """
        Handle disk full errors.
        
        Args:
            path: The path where the error occurred
            
        Returns:
            Error message
        """
        if path:
            return f"No space left on device: '{path}'"
        else:
            return "No space left on device"
    
    def handle_timeout_error(self, command: str, timeout: int) -> str:
        """
        Handle command timeout errors.
        
        Args:
            command: The command that timed out
            timeout: The timeout value in seconds
            
        Returns:
            Error message
        """
        return f"Command '{command}' timed out after {timeout} seconds"
    
    def handle_keyboard_interrupt(self) -> str:
        """
        Handle keyboard interrupt (Ctrl+C).
        
        Returns:
            User-friendly message
        """
        return "^C\nOperation cancelled by user"
    
    def validate_path(self, path: str) -> Optional[str]:
        """
        Validate a file path and return error message if invalid.
        
        Args:
            path: The path to validate
            
        Returns:
            Error message if path is invalid, None if valid
        """
        if not path:
            return "Path cannot be empty"
        
        if len(path) > 4096:  # Typical max path length
            return "Path too long"
        
        # Check for invalid characters (basic check)
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in invalid_chars:
            if char in path:
                return f"Invalid character '{char}' in path"
        
        return None
    
    def validate_filename(self, filename: str) -> Optional[str]:
        """
        Validate a filename and return error message if invalid.
        
        Args:
            filename: The filename to validate
            
        Returns:
            Error message if filename is invalid, None if valid
        """
        if not filename:
            return "Filename cannot be empty"
        
        if filename in ['.', '..']:
            return f"Invalid filename: '{filename}'"
        
        if len(filename) > 255:  # Typical max filename length
            return "Filename too long"
        
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in invalid_chars:
            if char in filename:
                return f"Invalid character '{char}' in filename"
        
        return None
    
    def _get_command_suggestions(self, command: str) -> list:
        """
        Get command suggestions for typos.
        
        Args:
            command: The mistyped command
            
        Returns:
            List of suggested commands
        """
        # Common commands that users might mistype
        common_commands = [
            'ls', 'cd', 'pwd', 'mkdir', 'rmdir', 'rm', 'cp', 'mv', 'cat', 'touch',
            'find', 'grep', 'head', 'tail', 'wc', 'chmod', 'chown', 'stat',
            'ps', 'top', 'free', 'df', 'uptime', 'kill', 'killall', 'who', 'whoami',
            'uname', 'history', 'help', 'clear', 'exit', 'quit'
        ]
        
        suggestions = []
        command_lower = command.lower()
        
        # Find commands with similar starting letters
        for cmd in common_commands:
            if cmd.startswith(command_lower[:2]) and cmd != command_lower:
                suggestions.append(cmd)
        
        # Find commands with similar length and characters
        if not suggestions:
            for cmd in common_commands:
                if abs(len(cmd) - len(command)) <= 1:
                    # Simple character similarity check
                    common_chars = set(cmd) & set(command_lower)
                    if len(common_chars) >= min(len(cmd), len(command)) - 1:
                        suggestions.append(cmd)
        
        return suggestions[:3]  # Return max 3 suggestions
    
    def set_debug_mode(self, debug_mode: bool) -> None:
        """
        Set debug mode on or off.
        
        Args:
            debug_mode: Whether to enable debug mode
        """
        self.debug_mode = debug_mode
    
    def log_error(self, error: str, level: str = "ERROR") -> None:
        """
        Log an error message.
        
        Args:
            error: The error message to log
            level: The log level (ERROR, WARNING, INFO)
        """
        # In a more complete implementation, this could write to a log file
        if self.debug_mode:
            print(f"[{level}] {error}", file=sys.stderr)