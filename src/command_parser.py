"""
Command Parser

This module handles parsing command line input, including handling
quotes, escape characters, and argument splitting.
"""

import shlex
import re
from typing import List, Tuple, Optional


class CommandParser:
    """
    Parses command line input into command and arguments.
    """
    
    def __init__(self):
        """Initialize the command parser."""
        pass
    
    def parse_command(self, command_line: str) -> Tuple[str, List[str]]:
        """
        Parse a command line into command and arguments.
        
        Args:
            command_line: The raw command line string
            
        Returns:
            Tuple of (command, arguments_list)
        """
        command_line = command_line.strip()
        
        if not command_line:
            return "", []
        
        try:
            # Use shlex to properly handle quotes and escapes
            tokens = shlex.split(command_line)
        except ValueError as e:
            # Handle unclosed quotes or other parsing errors
            # Fall back to simple split
            tokens = command_line.split()
        
        if not tokens:
            return "", []
        
        command = tokens[0]
        args = tokens[1:] if len(tokens) > 1 else []
        
        return command, args
    
    def parse_options(self, args: List[str]) -> Tuple[List[str], List[str]]:
        """
        Separate options (starting with -) from regular arguments.
        
        Args:
            args: List of command arguments
            
        Returns:
            Tuple of (options, remaining_args)
        """
        options = []
        remaining_args = []
        
        for arg in args:
            if arg.startswith('-') and len(arg) > 1:
                options.append(arg)
            else:
                remaining_args.append(arg)
        
        return options, remaining_args
    
    def expand_wildcards(self, pattern: str, current_dir: str) -> List[str]:
        """
        Expand shell wildcards like * and ?.
        
        Args:
            pattern: Pattern with potential wildcards
            current_dir: Current directory path
            
        Returns:
            List of expanded filenames
        """
        import glob
        import os
        
        if '*' in pattern or '?' in pattern or '[' in pattern:
            # Handle absolute vs relative paths
            if os.path.isabs(pattern):
                matches = glob.glob(pattern)
            else:
                full_pattern = os.path.join(current_dir, pattern)
                matches = glob.glob(full_pattern)
                # Convert back to relative paths if original was relative
                matches = [os.path.relpath(match, current_dir) for match in matches]
            
            return sorted(matches) if matches else [pattern]
        else:
            return [pattern]
    
    def parse_redirections(self, args: List[str]) -> Tuple[List[str], Optional[str], Optional[str], bool]:
        """
        Parse output redirections (>, >>, <).
        
        Args:
            args: Command arguments
            
        Returns:
            Tuple of (cleaned_args, output_file, input_file, append_mode)
        """
        cleaned_args = []
        output_file = None
        input_file = None
        append_mode = False
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            if arg == '>':
                # Output redirection
                if i + 1 < len(args):
                    output_file = args[i + 1]
                    i += 2
                else:
                    cleaned_args.append(arg)
                    i += 1
            elif arg == '>>':
                # Append redirection
                if i + 1 < len(args):
                    output_file = args[i + 1]
                    append_mode = True
                    i += 2
                else:
                    cleaned_args.append(arg)
                    i += 1
            elif arg == '<':
                # Input redirection
                if i + 1 < len(args):
                    input_file = args[i + 1]
                    i += 2
                else:
                    cleaned_args.append(arg)
                    i += 1
            elif arg.startswith('>'):
                # Combined redirection like >file
                if len(arg) > 1:
                    if arg.startswith('>>'):
                        output_file = arg[2:]
                        append_mode = True
                    else:
                        output_file = arg[1:]
                else:
                    cleaned_args.append(arg)
                i += 1
            else:
                cleaned_args.append(arg)
                i += 1
        
        return cleaned_args, output_file, input_file, append_mode
    
    def is_background_command(self, command_line: str) -> Tuple[str, bool]:
        """
        Check if command should run in background (ends with &).
        
        Args:
            command_line: The command line string
            
        Returns:
            Tuple of (cleaned_command_line, is_background)
        """
        command_line = command_line.strip()
        
        if command_line.endswith('&'):
            return command_line[:-1].strip(), True
        else:
            return command_line, False
    
    def split_pipeline(self, command_line: str) -> List[str]:
        """
        Split command line by pipes (|) for pipeline processing.
        
        Args:
            command_line: The command line string
            
        Returns:
            List of individual commands in the pipeline
        """
        # Simple pipe splitting - doesn't handle quotes properly
        # This is a simplified version
        if '|' not in command_line:
            return [command_line]
        
        commands = []
        current_cmd = ""
        in_quotes = False
        quote_char = None
        
        for char in command_line:
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
                current_cmd += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current_cmd += char
            elif char == '|' and not in_quotes:
                commands.append(current_cmd.strip())
                current_cmd = ""
            else:
                current_cmd += char
        
        if current_cmd.strip():
            commands.append(current_cmd.strip())
        
        return commands
    
    def normalize_path(self, path: str, current_dir: str) -> str:
        """
        Normalize a file path, handling ~ and relative paths.
        
        Args:
            path: The path to normalize
            current_dir: Current directory
            
        Returns:
            Normalized absolute path
        """
        import os
        
        if path.startswith('~'):
            path = os.path.expanduser(path)
        
        if not os.path.isabs(path):
            path = os.path.join(current_dir, path)
        
        return os.path.normpath(path)