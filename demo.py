#!/usr/bin/env python3
"""
Python Terminal Demo

This script demonstrates the key capabilities of the Python Terminal
by running a series of commands and showing the output.
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.terminal_engine import TerminalEngine
from src.utils.formatter import OutputFormatter


def demo_section(title: str, description: str = ""):
    """Print a formatted section header."""
    formatter = OutputFormatter()
    print("\n" + "=" * 60)
    print(formatter.colorize(f" {title}", 'green', 'bright'))
    if description:
        print(f" {description}")
    print("=" * 60)


def run_command_demo(engine: TerminalEngine, command: str, description: str = ""):
    """Run a command and display the results."""
    formatter = OutputFormatter()
    
    print(f"\n{formatter.colorize('$', 'blue', 'bright')} {command}")
    if description:
        print(f"  # {description}")
    
    output, exit_code = engine.execute_command(command)
    
    if output:
        # Limit output length for demo purposes
        if len(output) > 500:
            output = output[:500] + "..."
        print(output)
    
    if exit_code != 0:
        print(formatter.colorize(f"[Exit code: {exit_code}]", 'red'))
    
    time.sleep(0.5)  # Small delay for better readability


def main():
    """Run the demonstration."""
    formatter = OutputFormatter()
    
    # Welcome message
    print(formatter.colorize("""
╔══════════════════════════════════════════════════════════════╗
║                    Python Terminal Demo                     ║
║           Showcasing Terminal Capabilities                  ║  
╚══════════════════════════════════════════════════════════════╝
    """, 'cyan', 'bright'))
    
    print("This demo showcases the key features of the Python Terminal.")
    print("Watch as we execute various commands and demonstrate AI capabilities!")
    
    input(formatter.colorize("\nPress Enter to start the demo...", 'yellow'))
    
    # Initialize the terminal engine
    engine = TerminalEngine()
    
    # Basic Commands Demo
    demo_section("Basic Terminal Commands", "Standard file and directory operations")
    
    run_command_demo(engine, "pwd", "Show current directory")
    run_command_demo(engine, "ls", "List directory contents") 
    run_command_demo(engine, "ls -la", "List all files with details")
    
    # File Operations Demo
    demo_section("File Operations", "Creating, copying, and managing files")
    
    run_command_demo(engine, "mkdir demo_folder", "Create a test directory")
    run_command_demo(engine, "touch demo_folder/test_file.txt", "Create a test file")
    run_command_demo(engine, "ls demo_folder", "List contents of demo folder")
    run_command_demo(engine, "cat README.md | head -5", "Show first 5 lines of README")
    
    # System Monitoring Demo
    demo_section("System Monitoring", "Process and system information")
    
    run_command_demo(engine, "ps", "Show running processes")
    run_command_demo(engine, "free -h", "Show memory usage")
    run_command_demo(engine, "df -h", "Show disk usage")
    run_command_demo(engine, "uptime", "Show system uptime")
    run_command_demo(engine, "whoami", "Show current user")
    
    # AI Natural Language Demo
    demo_section("AI Natural Language Processing", "Plain English commands")
    
    print(formatter.colorize("\\n🤖 Now let's try some natural language commands:", 'magenta', 'bright'))
    
    ai_commands = [
        "show me the files in this directory",
        "what processes are running",
        "show system memory usage",
        "create a new folder called ai_test",
        "show me the current directory",
    ]
    
    for cmd in ai_commands:
        run_command_demo(engine, cmd, "Natural language command")
    
    # AI Examples Demo
    demo_section("AI Examples and Help", "Getting help with natural language")
    
    run_command_demo(engine, "ai examples", "Show natural language examples")
    run_command_demo(engine, "help", "Show all available commands")
    
    # Cleanup
    demo_section("Cleanup", "Removing demo files")
    
    run_command_demo(engine, "ls demo_folder", "Check demo folder contents")
    run_command_demo(engine, "rm demo_folder/test_file.txt", "Remove test file")
    run_command_demo(engine, "rmdir demo_folder", "Remove demo directory")
    run_command_demo(engine, "rmdir ai_test", "Remove AI test directory")
    
    # Conclusion
    print("\n" + "=" * 60)
    print(formatter.colorize(" Demo Complete!", 'green', 'bright'))
    print("=" * 60)
    
    print(f"""
{formatter.colorize('🎉 Congratulations!', 'green', 'bright')} You've seen the key features of the Python Terminal:

✅ Standard terminal commands (ls, cd, pwd, mkdir, rm, etc.)
✅ System monitoring (ps, top, free, df, uptime)
✅ File operations with proper error handling
✅ Natural language AI commands
✅ Colored output and user-friendly interface
✅ Comprehensive help and examples

{formatter.colorize('🚀 Ready to try it yourself?', 'cyan', 'bright')}
Start the terminal with: {formatter.colorize('python main.py', 'yellow')}

{formatter.colorize('💡 Pro Tips:', 'blue', 'bright')}
• Type 'help' for all available commands
• Type 'ai examples' for natural language examples  
• Try speaking naturally: "show me all python files"
• Use 'history' to see your previous commands
• Press Ctrl+C to interrupt, Ctrl+D or 'exit' to quit
    """)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nDemo error: {e}")
        sys.exit(1)