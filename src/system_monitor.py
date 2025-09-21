"""
System Monitor

This module handles system monitoring commands like ps, top, free, df, etc.
"""

import psutil
import os
import time
from typing import List, Tuple, Dict, Any
from tabulate import tabulate


class SystemMonitor:
    """
    Handles system monitoring commands for the terminal.
    """
    
    def __init__(self):
        """Initialize system monitor."""
        self.supported_commands = {
            'ps': self._handle_ps,
            'top': self._handle_top,
            'free': self._handle_free,
            'df': self._handle_df,
            'uptime': self._handle_uptime,
            'kill': self._handle_kill,
            'killall': self._handle_killall,
            'jobs': self._handle_jobs,
            'who': self._handle_who,
            'whoami': self._handle_whoami,
            'uname': self._handle_uname,
        }
    
    def get_supported_commands(self) -> List[str]:
        """Get list of supported system monitoring commands."""
        return list(self.supported_commands.keys())
    
    def execute_command(self, command: str, args: List[str]) -> Tuple[str, int]:
        """
        Execute a system monitoring command.
        
        Args:
            command: The command to execute
            args: Command arguments
            
        Returns:
            Tuple of (output_string, exit_code)
        """
        if command not in self.supported_commands:
            return f"Unknown system command: {command}", 1
        
        try:
            return self.supported_commands[command](args)
        except Exception as e:
            return f"Error executing {command}: {str(e)}", 1
    
    def _handle_ps(self, args: List[str]) -> Tuple[str, int]:
        """Handle ps command."""
        show_all = False
        show_full = False
        show_user = False
        
        # Parse options
        for arg in args:
            if arg.startswith('-'):
                if 'a' in arg:
                    show_all = True
                if 'u' in arg:
                    show_user = True
                if 'x' in arg:
                    show_all = True
                if 'f' in arg:
                    show_full = True
            elif arg in ['aux', 'axu']:
                show_all = True
                show_user = True
        
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'ppid', 'name', 'username', 'status', 'cpu_percent', 'memory_percent', 'create_time', 'cmdline']):
                try:
                    pinfo = proc.info
                    
                    # Filter processes based on options
                    if not show_all:
                        # Only show processes from the current user and with a controlling terminal
                        if pinfo['username'] != psutil.Process().username():
                            continue
                    
                    # Calculate CPU and memory usage
                    try:
                        cpu_percent = proc.cpu_percent(interval=0.1)
                        memory_percent = proc.memory_percent()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        cpu_percent = 0.0
                        memory_percent = 0.0
                    
                    # Format command
                    if show_full and pinfo['cmdline']:
                        command = ' '.join(pinfo['cmdline'])
                    else:
                        command = pinfo['name']
                    
                    if len(command) > 60:
                        command = command[:57] + "..."
                    
                    # Format creation time
                    if pinfo['create_time']:
                        start_time = time.strftime('%H:%M', time.localtime(pinfo['create_time']))
                    else:
                        start_time = "?"
                    
                    process_data = {
                        'PID': pinfo['pid'],
                        'PPID': pinfo['ppid'] or 0,
                        'USER': pinfo['username'] or '?',
                        'STAT': pinfo['status'] or '?',
                        '%CPU': f"{cpu_percent:.1f}",
                        '%MEM': f"{memory_percent:.1f}",
                        'TIME': start_time,
                        'COMMAND': command
                    }
                    
                    processes.append(process_data)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # Process may have terminated or we don't have access
                    pass
            
            # Sort by PID
            processes.sort(key=lambda x: x['PID'])
            
            # Format output
            if show_user:
                headers = ['USER', 'PID', 'PPID', '%CPU', '%MEM', 'STAT', 'TIME', 'COMMAND']
                table_data = [[p[h] for h in headers] for p in processes]
            else:
                headers = ['PID', 'PPID', 'STAT', 'TIME', 'COMMAND']
                table_data = [[p[h] for h in headers] for p in processes]
            
            output = tabulate(table_data, headers=headers, tablefmt='plain')
            return output, 0
            
        except Exception as e:
            return f"ps: {str(e)}", 1
    
    def _handle_top(self, args: List[str]) -> Tuple[str, int]:
        """Handle top command (snapshot version)."""
        try:
            # Get system info
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
            
            # Header information
            output_lines = []
            output_lines.append(f"System Load: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}")
            output_lines.append(f"CPU Usage: {cpu_percent:.1f}%")
            output_lines.append(f"Memory Usage: {memory.percent:.1f}% ({self._format_bytes(memory.used)}/{self._format_bytes(memory.total)})")
            output_lines.append("")
            
            # Process table
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    pinfo = proc.info
                    cpu_percent = proc.cpu_percent(interval=0.1)
                    
                    processes.append({
                        'PID': pinfo['pid'],
                        'USER': (pinfo['username'] or '?')[:10],
                        'CPU%': f"{cpu_percent:.1f}",
                        'MEM%': f"{pinfo['memory_percent']:.1f}",
                        'STAT': pinfo['status'] or '?',
                        'COMMAND': (pinfo['name'] or '?')[:20]
                    })
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort by CPU usage (descending)
            processes.sort(key=lambda x: float(x['CPU%']), reverse=True)
            
            # Take top 20 processes
            processes = processes[:20]
            
            headers = ['PID', 'USER', 'CPU%', 'MEM%', 'STAT', 'COMMAND']
            table_data = [[p[h] for h in headers] for p in processes]
            
            output_lines.append(tabulate(table_data, headers=headers, tablefmt='plain'))
            
            return "\n".join(output_lines), 0
            
        except Exception as e:
            return f"top: {str(e)}", 1
    
    def _handle_free(self, args: List[str]) -> Tuple[str, int]:
        """Handle free command."""
        human_readable = '-h' in args
        
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            if human_readable:
                total_mem = self._format_bytes(memory.total)
                used_mem = self._format_bytes(memory.used)
                free_mem = self._format_bytes(memory.available)
                
                total_swap = self._format_bytes(swap.total)
                used_swap = self._format_bytes(swap.used)
                free_swap = self._format_bytes(swap.free)
            else:
                total_mem = memory.total // 1024  # KB
                used_mem = memory.used // 1024
                free_mem = memory.available // 1024
                
                total_swap = swap.total // 1024
                used_swap = swap.used // 1024
                free_swap = swap.free // 1024
            
            headers = ['', 'total', 'used', 'free']
            data = [
                ['Mem:', total_mem, used_mem, free_mem],
                ['Swap:', total_swap, used_swap, free_swap]
            ]
            
            output = tabulate(data, headers=headers, tablefmt='plain')
            return output, 0
            
        except Exception as e:
            return f"free: {str(e)}", 1
    
    def _handle_df(self, args: List[str]) -> Tuple[str, int]:
        """Handle df command."""
        human_readable = '-h' in args
        path = args[0] if args and not args[0].startswith('-') else None
        
        try:
            disk_partitions = psutil.disk_partitions()
            data = []
            
            for partition in disk_partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    if path and partition.mountpoint != path:
                        continue
                    
                    if human_readable:
                        total = self._format_bytes(usage.total)
                        used = self._format_bytes(usage.used)
                        free = self._format_bytes(usage.free)
                    else:
                        total = usage.total // 1024  # KB
                        used = usage.used // 1024
                        free = usage.free // 1024
                    
                    use_percent = f"{(usage.used / usage.total * 100):.1f}%"
                    
                    data.append([
                        partition.device,
                        total,
                        used,
                        free,
                        use_percent,
                        partition.mountpoint
                    ])
                    
                except PermissionError:
                    # Skip partitions we can't access
                    pass
            
            headers = ['Filesystem', 'Size', 'Used', 'Available', 'Use%', 'Mounted on']
            output = tabulate(data, headers=headers, tablefmt='plain')
            return output, 0
            
        except Exception as e:
            return f"df: {str(e)}", 1
    
    def _handle_uptime(self, args: List[str]) -> Tuple[str, int]:
        """Handle uptime command."""
        try:
            boot_time = psutil.boot_time()
            current_time = time.time()
            uptime_seconds = current_time - boot_time
            
            # Convert to days, hours, minutes
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            # Current time
            current_str = time.strftime('%H:%M:%S', time.localtime(current_time))
            
            # Load average (if available)
            try:
                load_avg = os.getloadavg()
                load_str = f", load average: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}"
            except (OSError, AttributeError):
                load_str = ""
            
            # Number of users (simplified - just count unique usernames of running processes)
            users = set()
            for proc in psutil.process_iter(['username']):
                try:
                    if proc.info['username']:
                        users.add(proc.info['username'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            user_count = len(users)
            
            if days > 0:
                uptime_str = f"{days} day{'s' if days != 1 else ''}, {hours:02d}:{minutes:02d}"
            else:
                uptime_str = f"{hours:02d}:{minutes:02d}"
            
            output = f" {current_str} up {uptime_str}, {user_count} user{'s' if user_count != 1 else ''}{load_str}"
            return output, 0
            
        except Exception as e:
            return f"uptime: {str(e)}", 1
    
    def _handle_kill(self, args: List[str]) -> Tuple[str, int]:
        """Handle kill command."""
        if not args:
            return "kill: usage: kill [-s sigspec | -n signum | -sigspec] pid | jobspec ... or kill -l [sigspec]", 1
        
        signal_num = 15  # SIGTERM by default
        pids = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg.startswith('-') and len(arg) > 1:
                try:
                    if arg[1:].isdigit():
                        signal_num = int(arg[1:])
                    else:
                        # Handle signal names like -TERM, -KILL, etc.
                        signal_names = {'TERM': 15, 'KILL': 9, 'HUP': 1, 'INT': 2, 'QUIT': 3, 'USR1': 10, 'USR2': 12}
                        signal_name = arg[1:].upper()
                        signal_num = signal_names.get(signal_name, 15)
                except ValueError:
                    return f"kill: invalid signal specification '{arg}'", 1
            else:
                try:
                    pids.append(int(arg))
                except ValueError:
                    return f"kill: '{arg}': arguments must be process or job IDs", 1
            i += 1
        
        if not pids:
            return "kill: usage: kill [-s sigspec | -n signum | -sigspec] pid | jobspec ... or kill -l [sigspec]", 1
        
        errors = []
        for pid in pids:
            try:
                proc = psutil.Process(pid)
                proc.send_signal(signal_num)
            except psutil.NoSuchProcess:
                errors.append(f"kill: ({pid}) - No such process")
            except psutil.AccessDenied:
                errors.append(f"kill: ({pid}) - Operation not permitted")
            except Exception as e:
                errors.append(f"kill: ({pid}) - {str(e)}")
        
        if errors:
            return "\n".join(errors), 1
        
        return "", 0
    
    def _handle_killall(self, args: List[str]) -> Tuple[str, int]:
        """Handle killall command."""
        if not args:
            return "killall: usage: killall [-s signal] process_name", 1
        
        signal_num = 15  # SIGTERM by default
        process_names = []
        
        i = 0
        while i < len(args):
            if args[i] == '-s' and i + 1 < len(args):
                try:
                    signal_num = int(args[i + 1])
                    i += 2
                except ValueError:
                    return f"killall: invalid signal '{args[i + 1]}'", 1
            else:
                process_names.append(args[i])
                i += 1
        
        if not process_names:
            return "killall: usage: killall [-s signal] process_name", 1
        
        killed_count = 0
        errors = []
        
        for process_name in process_names:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] == process_name:
                        proc.send_signal(signal_num)
                        killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        
        if killed_count == 0:
            return f"killall: no process found", 1
        
        return f"Killed {killed_count} process(es)", 0
    
    def _handle_jobs(self, args: List[str]) -> Tuple[str, int]:
        """Handle jobs command (simplified - no actual job control)."""
        return "No active jobs", 0
    
    def _handle_who(self, args: List[str]) -> Tuple[str, int]:
        """Handle who command."""
        try:
            users = psutil.users()
            if not users:
                return "No users currently logged in", 0
            
            data = []
            for user in users:
                started = time.strftime('%Y-%m-%d %H:%M', time.localtime(user.started))
                data.append([user.name, user.terminal or 'console', started])
            
            output = tabulate(data, headers=['USER', 'TTY', 'LOGIN'], tablefmt='plain')
            return output, 0
            
        except Exception as e:
            return f"who: {str(e)}", 1
    
    def _handle_whoami(self, args: List[str]) -> Tuple[str, int]:
        """Handle whoami command."""
        try:
            import getpass
            return getpass.getuser(), 0
        except Exception as e:
            return f"whoami: {str(e)}", 1
    
    def _handle_uname(self, args: List[str]) -> Tuple[str, int]:
        """Handle uname command."""
        import platform
        
        show_all = '-a' in args
        show_system = '-s' in args or not args or show_all
        show_node = '-n' in args or show_all
        show_release = '-r' in args or show_all
        show_version = '-v' in args or show_all
        show_machine = '-m' in args or show_all
        
        parts = []
        
        if show_system:
            parts.append(platform.system())
        if show_node:
            parts.append(platform.node())
        if show_release:
            parts.append(platform.release())
        if show_version:
            parts.append(platform.version())
        if show_machine:
            parts.append(platform.machine())
        
        return " ".join(parts), 0
    
    def _format_bytes(self, bytes_val: int) -> str:
        """Format bytes in human-readable format."""
        for unit in ['B', 'K', 'M', 'G', 'T']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f}{unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f}P"