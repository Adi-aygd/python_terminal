"""
File Operations

This module handles file and directory operations like ls, mkdir, rm, cp, mv, etc.
"""

import os
import shutil
import stat
import time
from typing import List, Tuple, Optional
from pathlib import Path


class FileOperations:
    """
    Handles file and directory operations for the terminal.
    """
    
    def __init__(self):
        """Initialize file operations handler."""
        self.supported_commands = {
            'ls': self._handle_ls,
            'mkdir': self._handle_mkdir,
            'rmdir': self._handle_rmdir,
            'rm': self._handle_rm,
            'cp': self._handle_cp,
            'mv': self._handle_mv,
            'cat': self._handle_cat,
            'touch': self._handle_touch,
            'find': self._handle_find,
            'chmod': self._handle_chmod,
            'chown': self._handle_chown,
            'stat': self._handle_stat,
            'head': self._handle_head,
            'tail': self._handle_tail,
            'wc': self._handle_wc,
        }
    
    def get_supported_commands(self) -> List[str]:
        """Get list of supported file operation commands."""
        return list(self.supported_commands.keys())
    
    def execute_command(self, command: str, args: List[str], current_dir: str) -> Tuple[str, int]:
        """
        Execute a file operation command.
        
        Args:
            command: The command to execute
            args: Command arguments
            current_dir: Current working directory
            
        Returns:
            Tuple of (output_string, exit_code)
        """
        if command not in self.supported_commands:
            return f"Unknown file operation: {command}", 1
        
        try:
            return self.supported_commands[command](args, current_dir)
        except Exception as e:
            return f"Error executing {command}: {str(e)}", 1
    
    def _handle_ls(self, args: List[str], current_dir: str) -> Tuple[str, int]:
        """Handle ls command."""
        # Parse options
        show_all = False
        show_long = False
        show_human = False
        paths = []
        
        for arg in args:
            if arg.startswith('-'):
                if 'a' in arg:
                    show_all = True
                if 'l' in arg:
                    show_long = True
                if 'h' in arg:
                    show_human = True
            else:
                paths.append(arg)
        
        if not paths:
            paths = ['.']
        
        output = []
        
        for path_arg in paths:
            target_path = os.path.join(current_dir, path_arg) if not os.path.isabs(path_arg) else path_arg
            
            if not os.path.exists(target_path):
                output.append(f"ls: cannot access '{path_arg}': No such file or directory")
                continue
            
            if os.path.isfile(target_path):
                if show_long:
                    output.append(self._format_long_listing([target_path], show_human))
                else:
                    output.append(os.path.basename(target_path))
            else:
                try:
                    entries = os.listdir(target_path)
                    if not show_all:
                        entries = [e for e in entries if not e.startswith('.')]
                    
                    entries.sort()
                    
                    if show_long:
                        full_paths = [os.path.join(target_path, entry) for entry in entries]
                        output.append(self._format_long_listing(full_paths, show_human))
                    else:
                        if len(paths) > 1:
                            output.append(f"{path_arg}:")
                        output.append("  ".join(entries))
                        
                except PermissionError:
                    output.append(f"ls: cannot open directory '{path_arg}': Permission denied")
        
        return "\n".join(output), 0
    
    def _format_long_listing(self, paths: List[str], human_readable: bool = False) -> str:
        """Format files in long listing format (-l option)."""
        lines = []
        
        for path in paths:
            try:
                stat_info = os.stat(path)
                
                # File type and permissions
                mode = stat_info.st_mode
                if stat.S_ISDIR(mode):
                    file_type = 'd'
                elif stat.S_ISLNK(mode):
                    file_type = 'l'
                else:
                    file_type = '-'
                
                # Permissions
                perms = file_type
                perms += 'r' if mode & stat.S_IRUSR else '-'
                perms += 'w' if mode & stat.S_IWUSR else '-'
                perms += 'x' if mode & stat.S_IXUSR else '-'
                perms += 'r' if mode & stat.S_IRGRP else '-'
                perms += 'w' if mode & stat.S_IWGRP else '-'
                perms += 'x' if mode & stat.S_IXGRP else '-'
                perms += 'r' if mode & stat.S_IROTH else '-'
                perms += 'w' if mode & stat.S_IWOTH else '-'
                perms += 'x' if mode & stat.S_IXOTH else '-'
                
                # Links, owner, group (simplified)
                links = stat_info.st_nlink
                owner = stat_info.st_uid  # In a real system, you'd look up the username
                group = stat_info.st_gid  # In a real system, you'd look up the group name
                
                # Size
                size = stat_info.st_size
                if human_readable:
                    size_str = self._format_size_human(size)
                else:
                    size_str = str(size)
                
                # Modification time
                mtime = time.strftime('%b %d %H:%M', time.localtime(stat_info.st_mtime))
                
                # File name
                filename = os.path.basename(path)
                
                line = f"{perms} {links:3d} {owner:8d} {group:8d} {size_str:8s} {mtime} {filename}"
                lines.append(line)
                
            except (OSError, IOError) as e:
                lines.append(f"ls: cannot access '{path}': {str(e)}")
        
        return "\n".join(lines)
    
    def _format_size_human(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'K', 'M', 'G', 'T']:
            if size < 1024.0:
                return f"{size:3.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}P"
    
    def _handle_mkdir(self, args: List[str], current_dir: str) -> Tuple[str, int]:
        """Handle mkdir command."""
        if not args:
            return "mkdir: missing operand", 1
        
        create_parents = False
        dirs_to_create = []
        
        for arg in args:
            if arg == '-p':
                create_parents = True
            elif not arg.startswith('-'):
                dirs_to_create.append(arg)
        
        if not dirs_to_create:
            return "mkdir: missing operand", 1
        
        errors = []
        for dir_name in dirs_to_create:
            target_path = os.path.join(current_dir, dir_name) if not os.path.isabs(dir_name) else dir_name
            
            try:
                if create_parents:
                    os.makedirs(target_path, exist_ok=True)
                else:
                    os.mkdir(target_path)
            except FileExistsError:
                errors.append(f"mkdir: cannot create directory '{dir_name}': File exists")
            except PermissionError:
                errors.append(f"mkdir: cannot create directory '{dir_name}': Permission denied")
            except OSError as e:
                errors.append(f"mkdir: cannot create directory '{dir_name}': {str(e)}")
        
        if errors:
            return "\n".join(errors), 1
        
        return "", 0
    
    def _handle_rmdir(self, args: List[str], current_dir: str) -> Tuple[str, int]:
        """Handle rmdir command."""
        if not args:
            return "rmdir: missing operand", 1
        
        errors = []
        for dir_name in args:
            if dir_name.startswith('-'):
                continue
                
            target_path = os.path.join(current_dir, dir_name) if not os.path.isabs(dir_name) else dir_name
            
            try:
                os.rmdir(target_path)
            except FileNotFoundError:
                errors.append(f"rmdir: failed to remove '{dir_name}': No such file or directory")
            except OSError as e:
                if "Directory not empty" in str(e):
                    errors.append(f"rmdir: failed to remove '{dir_name}': Directory not empty")
                else:
                    errors.append(f"rmdir: failed to remove '{dir_name}': {str(e)}")
        
        if errors:
            return "\n".join(errors), 1
        
        return "", 0
    
    def _handle_rm(self, args: List[str], current_dir: str) -> Tuple[str, int]:
        """Handle rm command."""
        if not args:
            return "rm: missing operand", 1
        
        recursive = False
        force = False
        files_to_remove = []
        
        for arg in args:
            if arg.startswith('-'):
                if 'r' in arg or 'R' in arg:
                    recursive = True
                if 'f' in arg:
                    force = True
            else:
                files_to_remove.append(arg)
        
        if not files_to_remove:
            return "rm: missing operand", 1
        
        errors = []
        for file_name in files_to_remove:
            target_path = os.path.join(current_dir, file_name) if not os.path.isabs(file_name) else file_name
            
            try:
                if os.path.isdir(target_path):
                    if recursive:
                        shutil.rmtree(target_path)
                    else:
                        errors.append(f"rm: cannot remove '{file_name}': Is a directory")
                else:
                    os.remove(target_path)
            except FileNotFoundError:
                if not force:
                    errors.append(f"rm: cannot remove '{file_name}': No such file or directory")
            except PermissionError:
                if not force:
                    errors.append(f"rm: cannot remove '{file_name}': Permission denied")
            except OSError as e:
                if not force:
                    errors.append(f"rm: cannot remove '{file_name}': {str(e)}")
        
        if errors:
            return "\n".join(errors), 1
        
        return "", 0
    
    def _handle_cp(self, args: List[str], current_dir: str) -> Tuple[str, int]:
        """Handle cp command."""
        if len(args) < 2:
            return "cp: missing file operand", 1
        
        recursive = False
        preserve = False
        
        # Parse options
        files = []
        for arg in args:
            if arg.startswith('-'):
                if 'r' in arg or 'R' in arg:
                    recursive = True
                if 'p' in arg:
                    preserve = True
            else:
                files.append(arg)
        
        if len(files) < 2:
            return "cp: missing destination file operand", 1
        
        source_files = files[:-1]
        dest = files[-1]
        
        dest_path = os.path.join(current_dir, dest) if not os.path.isabs(dest) else dest
        
        try:
            # If destination is a directory and exists
            if os.path.isdir(dest_path):
                for source in source_files:
                    source_path = os.path.join(current_dir, source) if not os.path.isabs(source) else source
                    dest_file = os.path.join(dest_path, os.path.basename(source_path))
                    
                    if os.path.isdir(source_path):
                        if recursive:
                            shutil.copytree(source_path, dest_file)
                        else:
                            return f"cp: -r not specified; omitting directory '{source}'", 1
                    else:
                        shutil.copy2(source_path, dest_file) if preserve else shutil.copy(source_path, dest_file)
            else:
                # Single file copy
                if len(source_files) > 1:
                    return f"cp: target '{dest}' is not a directory", 1
                
                source_path = os.path.join(current_dir, source_files[0]) if not os.path.isabs(source_files[0]) else source_files[0]
                
                if os.path.isdir(source_path):
                    if recursive:
                        shutil.copytree(source_path, dest_path)
                    else:
                        return f"cp: -r not specified; omitting directory '{source_files[0]}'", 1
                else:
                    shutil.copy2(source_path, dest_path) if preserve else shutil.copy(source_path, dest_path)
        
        except Exception as e:
            return f"cp: {str(e)}", 1
        
        return "", 0
    
    def _handle_mv(self, args: List[str], current_dir: str) -> Tuple[str, int]:
        """Handle mv command."""
        if len(args) < 2:
            return "mv: missing file operand", 1
        
        source_files = args[:-1]
        dest = args[-1]
        
        dest_path = os.path.join(current_dir, dest) if not os.path.isabs(dest) else dest
        
        try:
            if os.path.isdir(dest_path):
                # Moving to directory
                for source in source_files:
                    source_path = os.path.join(current_dir, source) if not os.path.isabs(source) else source
                    dest_file = os.path.join(dest_path, os.path.basename(source_path))
                    shutil.move(source_path, dest_file)
            else:
                # Renaming or moving to new location
                if len(source_files) > 1:
                    return f"mv: target '{dest}' is not a directory", 1
                
                source_path = os.path.join(current_dir, source_files[0]) if not os.path.isabs(source_files[0]) else source_files[0]
                shutil.move(source_path, dest_path)
        
        except Exception as e:
            return f"mv: {str(e)}", 1
        
        return "", 0
    
    def _handle_cat(self, args: List[str], current_dir: str) -> Tuple[str, int]:
        """Handle cat command."""
        if not args:
            return "cat: missing file operand", 1
        
        output = []
        for file_name in args:
            if file_name.startswith('-'):
                continue
                
            file_path = os.path.join(current_dir, file_name) if not os.path.isabs(file_name) else file_name
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    output.append(content)
            except FileNotFoundError:
                return f"cat: {file_name}: No such file or directory", 1
            except PermissionError:
                return f"cat: {file_name}: Permission denied", 1
            except UnicodeDecodeError:
                return f"cat: {file_name}: Binary file", 1
        
        return "".join(output), 0
    
    def _handle_touch(self, args: List[str], current_dir: str) -> Tuple[str, int]:
        """Handle touch command."""
        if not args:
            return "touch: missing file operand", 1
        
        for file_name in args:
            if file_name.startswith('-'):
                continue
                
            file_path = os.path.join(current_dir, file_name) if not os.path.isabs(file_name) else file_name
            
            try:
                # Create file if it doesn't exist, update timestamp if it does
                Path(file_path).touch()
            except Exception as e:
                return f"touch: cannot touch '{file_name}': {str(e)}", 1
        
        return "", 0
    
    def _handle_find(self, args: List[str], current_dir: str) -> Tuple[str, int]:
        """Handle find command (simplified version)."""
        if not args:
            return "find: missing search path", 1
        
        search_path = args[0]
        pattern = args[1] if len(args) > 1 else "*"
        
        if not os.path.isabs(search_path):
            search_path = os.path.join(current_dir, search_path)
        
        import glob
        matches = []
        
        try:
            if os.path.isdir(search_path):
                search_pattern = os.path.join(search_path, "**", pattern)
                matches = glob.glob(search_pattern, recursive=True)
            else:
                return f"find: '{args[0]}': No such file or directory", 1
        
        except Exception as e:
            return f"find: {str(e)}", 1
        
        return "\n".join(sorted(matches)), 0
    
    def _handle_chmod(self, args: List[str], current_dir: str) -> Tuple[str, int]:
        """Handle chmod command (simplified)."""
        return "chmod: command not fully implemented in this terminal", 1
    
    def _handle_chown(self, args: List[str], current_dir: str) -> Tuple[str, int]:
        """Handle chown command (simplified)."""
        return "chown: command not fully implemented in this terminal", 1
    
    def _handle_stat(self, args: List[str], current_dir: str) -> Tuple[str, int]:
        """Handle stat command."""
        if not args:
            return "stat: missing operand", 1
        
        file_name = args[0]
        file_path = os.path.join(current_dir, file_name) if not os.path.isabs(file_name) else file_name
        
        try:
            stat_info = os.stat(file_path)
            output = f"""File: {file_name}
Size: {stat_info.st_size}
Blocks: {stat_info.st_blocks if hasattr(stat_info, 'st_blocks') else 'N/A'}
Device: {stat_info.st_dev}
Inode: {stat_info.st_ino}
Links: {stat_info.st_nlink}
Access: {oct(stat_info.st_mode)}
Uid: {stat_info.st_uid}
Gid: {stat_info.st_gid}
Access Time: {time.ctime(stat_info.st_atime)}
Modify Time: {time.ctime(stat_info.st_mtime)}
Change Time: {time.ctime(stat_info.st_ctime)}"""
            
            return output, 0
            
        except FileNotFoundError:
            return f"stat: cannot stat '{file_name}': No such file or directory", 1
        except Exception as e:
            return f"stat: {str(e)}", 1
    
    def _handle_head(self, args: List[str], current_dir: str) -> Tuple[str, int]:
        """Handle head command."""
        lines = 10  # default
        files = []
        
        i = 0
        while i < len(args):
            if args[i] == '-n' and i + 1 < len(args):
                try:
                    lines = int(args[i + 1])
                    i += 2
                except ValueError:
                    return f"head: invalid number of lines: '{args[i + 1]}'", 1
            elif args[i].startswith('-') and args[i][1:].isdigit():
                lines = int(args[i][1:])
                i += 1
            else:
                files.append(args[i])
                i += 1
        
        if not files:
            return "head: missing file operand", 1
        
        output = []
        for file_name in files:
            file_path = os.path.join(current_dir, file_name) if not os.path.isabs(file_name) else file_name
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_lines = f.readlines()
                    output.extend(file_lines[:lines])
            except FileNotFoundError:
                return f"head: cannot open '{file_name}' for reading: No such file or directory", 1
            except Exception as e:
                return f"head: {str(e)}", 1
        
        return "".join(output).rstrip('\n'), 0
    
    def _handle_tail(self, args: List[str], current_dir: str) -> Tuple[str, int]:
        """Handle tail command."""
        lines = 10  # default
        files = []
        
        i = 0
        while i < len(args):
            if args[i] == '-n' and i + 1 < len(args):
                try:
                    lines = int(args[i + 1])
                    i += 2
                except ValueError:
                    return f"tail: invalid number of lines: '{args[i + 1]}'", 1
            elif args[i].startswith('-') and args[i][1:].isdigit():
                lines = int(args[i][1:])
                i += 1
            else:
                files.append(args[i])
                i += 1
        
        if not files:
            return "tail: missing file operand", 1
        
        output = []
        for file_name in files:
            file_path = os.path.join(current_dir, file_name) if not os.path.isabs(file_name) else file_name
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_lines = f.readlines()
                    output.extend(file_lines[-lines:])
            except FileNotFoundError:
                return f"tail: cannot open '{file_name}' for reading: No such file or directory", 1
            except Exception as e:
                return f"tail: {str(e)}", 1
        
        return "".join(output).rstrip('\n'), 0
    
    def _handle_wc(self, args: List[str], current_dir: str) -> Tuple[str, int]:
        """Handle wc command."""
        if not args:
            return "wc: missing file operand", 1
        
        show_lines = True
        show_words = True
        show_chars = True
        files = []
        
        for arg in args:
            if arg.startswith('-'):
                if 'l' in arg:
                    show_lines, show_words, show_chars = True, False, False
                elif 'w' in arg:
                    show_lines, show_words, show_chars = False, True, False
                elif 'c' in arg:
                    show_lines, show_words, show_chars = False, False, True
            else:
                files.append(arg)
        
        if not files:
            return "wc: missing file operand", 1
        
        output = []
        for file_name in files:
            file_path = os.path.join(current_dir, file_name) if not os.path.isabs(file_name) else file_name
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.count('\n')
                    words = len(content.split())
                    chars = len(content)
                    
                    result = []
                    if show_lines:
                        result.append(str(lines))
                    if show_words:
                        result.append(str(words))
                    if show_chars:
                        result.append(str(chars))
                    
                    result.append(file_name)
                    output.append(" ".join(result))
                    
            except FileNotFoundError:
                return f"wc: {file_name}: No such file or directory", 1
            except Exception as e:
                return f"wc: {str(e)}", 1
        
        return "\n".join(output), 0