"""
Output Formatter

This module provides utilities for formatting terminal output consistently.
"""

import os
import shutil
from typing import List, Dict, Any, Optional
from colorama import Fore, Back, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class OutputFormatter:
    """
    Handles formatting and colorization of terminal output.
    """
    
    def __init__(self, use_colors: bool = True):
        """
        Initialize output formatter.
        
        Args:
            use_colors: Whether to use colored output
        """
        self.use_colors = use_colors and self._supports_color()
        self.terminal_width = self._get_terminal_width()
    
    def _supports_color(self) -> bool:
        """Check if the terminal supports colored output."""
        # Check if stdout is a terminal and supports colors
        if not hasattr(os.sys.stdout, 'isatty') or not os.sys.stdout.isatty():
            return False
        
        # Check common terminal color support environment variables
        term = os.environ.get('TERM', '').lower()
        colorterm = os.environ.get('COLORTERM', '').lower()
        
        if 'color' in colorterm or term in ['xterm', 'xterm-color', 'xterm-256color', 'screen', 'screen-256color']:
            return True
        
        return False
    
    def _get_terminal_width(self) -> int:
        """Get the terminal width."""
        try:
            return shutil.get_terminal_size().columns
        except (OSError, AttributeError):
            return 80  # Default width
    
    def colorize(self, text: str, color: str, style: str = None) -> str:
        """
        Colorize text if colors are enabled.
        
        Args:
            text: Text to colorize
            color: Color name (red, green, blue, yellow, magenta, cyan, white)
            style: Style name (bright, dim, normal)
            
        Returns:
            Colorized text or original text if colors disabled
        """
        if not self.use_colors:
            return text
        
        color_map = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'blue': Fore.BLUE,
            'yellow': Fore.YELLOW,
            'magenta': Fore.MAGENTA,
            'cyan': Fore.CYAN,
            'white': Fore.WHITE,
            'black': Fore.BLACK,
        }
        
        style_map = {
            'bright': Style.BRIGHT,
            'dim': Style.DIM,
            'normal': Style.NORMAL,
        }
        
        color_code = color_map.get(color.lower(), '')
        style_code = style_map.get(style.lower(), '') if style else ''
        
        return f"{style_code}{color_code}{text}{Style.RESET_ALL}"
    
    def format_error(self, message: str) -> str:
        """
        Format an error message.
        
        Args:
            message: Error message to format
            
        Returns:
            Formatted error message
        """
        return self.colorize(f"Error: {message}", 'red', 'bright')
    
    def format_warning(self, message: str) -> str:
        """
        Format a warning message.
        
        Args:
            message: Warning message to format
            
        Returns:
            Formatted warning message
        """
        return self.colorize(f"Warning: {message}", 'yellow', 'bright')
    
    def format_success(self, message: str) -> str:
        """
        Format a success message.
        
        Args:
            message: Success message to format
            
        Returns:
            Formatted success message
        """
        return self.colorize(message, 'green')
    
    def format_info(self, message: str) -> str:
        """
        Format an info message.
        
        Args:
            message: Info message to format
            
        Returns:
            Formatted info message
        """
        return self.colorize(message, 'cyan')
    
    def format_prompt(self, username: str, hostname: str, current_dir: str) -> str:
        """
        Format the terminal prompt.
        
        Args:
            username: Current username
            hostname: System hostname
            current_dir: Current directory path
            
        Returns:
            Formatted prompt string
        """
        # Shorten directory path if it's too long
        if len(current_dir) > 30:
            dir_parts = current_dir.split(os.sep)
            if len(dir_parts) > 3:
                current_dir = os.sep.join(['...'] + dir_parts[-2:])
        
        # Replace home directory with ~
        home_dir = os.path.expanduser('~')
        if current_dir.startswith(home_dir):
            current_dir = current_dir.replace(home_dir, '~', 1)
        
        if self.use_colors:
            user_host = self.colorize(f"{username}@{hostname}", 'green', 'bright')
            directory = self.colorize(current_dir, 'blue', 'bright')
            prompt_symbol = self.colorize('$', 'white', 'bright')
            return f"{user_host}:{directory}{prompt_symbol} "
        else:
            return f"{username}@{hostname}:{current_dir}$ "
    
    def format_file_listing(self, files: List[Dict[str, Any]]) -> str:
        """
        Format file listing with colors based on file types.
        
        Args:
            files: List of file dictionaries with name, type, size, etc.
            
        Returns:
            Formatted file listing
        """
        if not files:
            return ""
        
        formatted_files = []
        
        for file_info in files:
            name = file_info.get('name', '')
            file_type = file_info.get('type', 'file')
            
            if self.use_colors:
                if file_type == 'directory':
                    formatted_name = self.colorize(name, 'blue', 'bright')
                elif file_type == 'executable':
                    formatted_name = self.colorize(name, 'green', 'bright')
                elif file_type == 'symlink':
                    formatted_name = self.colorize(name, 'cyan')
                elif name.startswith('.'):
                    formatted_name = self.colorize(name, 'white', 'dim')
                else:
                    formatted_name = name
            else:
                formatted_name = name
            
            formatted_files.append(formatted_name)
        
        return "  ".join(formatted_files)
    
    def format_table(self, headers: List[str], rows: List[List[str]], 
                    max_width: Optional[int] = None) -> str:
        """
        Format data as a table.
        
        Args:
            headers: Table column headers
            rows: Table data rows
            max_width: Maximum width for the table
            
        Returns:
            Formatted table string
        """
        if not rows:
            return ""
        
        max_width = max_width or self.terminal_width
        
        # Calculate column widths
        col_widths = []
        for i, header in enumerate(headers):
            max_col_width = len(header)
            for row in rows:
                if i < len(row):
                    max_col_width = max(max_col_width, len(str(row[i])))
            col_widths.append(min(max_col_width, max_width // len(headers)))
        
        # Format header
        if self.use_colors:
            formatted_headers = [self.colorize(h[:w], 'white', 'bright').ljust(w + 10) 
                               for h, w in zip(headers, col_widths)]
        else:
            formatted_headers = [h[:w].ljust(w) for h, w in zip(headers, col_widths)]
        
        table_lines = [" ".join(formatted_headers)]
        
        # Add separator
        if self.use_colors:
            separator = self.colorize("-" * min(sum(col_widths) + len(headers) - 1, max_width), 'white', 'dim')
        else:
            separator = "-" * min(sum(col_widths) + len(headers) - 1, max_width)
        table_lines.append(separator)
        
        # Format data rows
        for row in rows:
            formatted_row = []
            for i, (cell, width) in enumerate(zip(row, col_widths)):
                cell_str = str(cell)[:width].ljust(width)
                formatted_row.append(cell_str)
            table_lines.append(" ".join(formatted_row))
        
        return "\n".join(table_lines)
    
    def format_progress_bar(self, percentage: float, width: int = 50, 
                          label: str = "") -> str:
        """
        Format a progress bar.
        
        Args:
            percentage: Progress percentage (0-100)
            width: Width of the progress bar
            label: Optional label for the progress bar
            
        Returns:
            Formatted progress bar string
        """
        filled_width = int(width * percentage / 100)
        bar_filled = "█" * filled_width
        bar_empty = "░" * (width - filled_width)
        
        if self.use_colors:
            bar_filled = self.colorize(bar_filled, 'green')
            bar_empty = self.colorize(bar_empty, 'white', 'dim')
        
        progress_bar = f"[{bar_filled}{bar_empty}] {percentage:.1f}%"
        
        if label:
            progress_bar = f"{label}: {progress_bar}"
        
        return progress_bar
    
    def format_columns(self, items: List[str], columns: int = None) -> str:
        """
        Format items in columns.
        
        Args:
            items: List of items to format
            columns: Number of columns (auto-calculate if None)
            
        Returns:
            Formatted column output
        """
        if not items:
            return ""
        
        if columns is None:
            # Auto-calculate columns based on terminal width and item lengths
            max_item_length = max(len(item) for item in items)
            columns = max(1, self.terminal_width // (max_item_length + 2))
        
        formatted_lines = []
        for i in range(0, len(items), columns):
            row_items = items[i:i + columns]
            # Pad items to equal width within the row
            if len(row_items) > 1:
                max_width = max(len(item) for item in row_items)
                padded_items = [item.ljust(max_width + 2) for item in row_items[:-1]]
                padded_items.append(row_items[-1])  # Don't pad the last item
                formatted_lines.append("".join(padded_items))
            else:
                formatted_lines.append(row_items[0])
        
        return "\n".join(formatted_lines)
    
    def wrap_text(self, text: str, width: Optional[int] = None, 
                  indent: str = "") -> str:
        """
        Wrap text to fit within specified width.
        
        Args:
            text: Text to wrap
            width: Maximum width (uses terminal width if None)
            indent: String to indent wrapped lines
            
        Returns:
            Wrapped text
        """
        import textwrap
        
        width = width or self.terminal_width
        wrapper = textwrap.TextWrapper(
            width=width,
            subsequent_indent=indent,
            break_long_words=False,
            break_on_hyphens=False
        )
        
        return wrapper.fill(text)
    
    def format_size(self, size_bytes: int, human_readable: bool = True) -> str:
        """
        Format file size.
        
        Args:
            size_bytes: Size in bytes
            human_readable: Whether to use human-readable format
            
        Returns:
            Formatted size string
        """
        if not human_readable:
            return str(size_bytes)
        
        for unit in ['B', 'K', 'M', 'G', 'T']:
            if size_bytes < 1024.0:
                if unit == 'B':
                    return f"{size_bytes:.0f}{unit}"
                else:
                    return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.1f}P"
    
    def format_duration(self, seconds: float) -> str:
        """
        Format duration in human-readable format.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m{secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h{minutes}m"
    
    def center_text(self, text: str, width: Optional[int] = None, 
                   fill_char: str = " ") -> str:
        """
        Center text within specified width.
        
        Args:
            text: Text to center
            width: Width to center within (uses terminal width if None)
            fill_char: Character to use for padding
            
        Returns:
            Centered text
        """
        width = width or self.terminal_width
        return text.center(width, fill_char)
    
    def set_colors_enabled(self, enabled: bool) -> None:
        """
        Enable or disable colored output.
        
        Args:
            enabled: Whether to enable colors
        """
        self.use_colors = enabled and self._supports_color()