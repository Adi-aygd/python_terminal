#!/usr/bin/env python3
"""
Test script to demonstrate the AI deletion fix
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.terminal_engine import TerminalEngine
from src.ai_processor import AIProcessor
from src.utils.formatter import OutputFormatter


def main():
    formatter = OutputFormatter()
    engine = TerminalEngine()
    
    print(formatter.colorize("=== Testing AI Deletion Fix ===", 'cyan', 'bright'))
    
    # Change to home directory for testing
    home_dir = os.path.expanduser("~")
    os.chdir(home_dir)
    engine.current_directory = home_dir
    
    print(f"\nWorking in: {home_dir}")
    
    # Test commands
    test_cases = [
        # Create test directories
        ("mkdir ai_test_folder", "Creating test folder"),
        ("ls | grep ai_test", "Verify folder exists"),
        
        # Test various AI deletion commands
        ("delete ai_test_folder", "AI: Delete using 'delete <name>'"),
        ("ls | grep ai_test", "Verify deletion worked"),
        
        # Test more cases
        ("mkdir ai_test_dir", "Creating another test folder"),
        ("remove ai_test_dir", "AI: Remove using 'remove <name>'"),
        
        ("mkdir 'folder with spaces'", "Creating folder with spaces"),
        ("delete folder with spaces", "AI: Delete folder with spaces"),
        
        ("mkdir test_directory", "Creating test_directory"),
        ("remove folder called test_directory", "AI: Remove using full phrase"),
    ]
    
    for command, description in test_cases:
        print(f"\n{formatter.colorize('$', 'green', 'bright')} {command}")
        print(f"  # {description}")
        
        output, exit_code = engine.execute_command(command)
        
        if output:
            print(f"  Output: {output}")
        
        if exit_code == 0:
            print(f"  {formatter.colorize('✓ Success', 'green')}")
        else:
            print(f"  {formatter.colorize('✗ Failed', 'red')} (exit code: {exit_code})")
    
    print(f"\n{formatter.colorize('=== AI Processor Pattern Test ===', 'cyan', 'bright')}")
    
    ai = AIProcessor()
    
    # Test AI pattern matching directly
    test_queries = [
        "delete project",
        "remove folder called test", 
        "delete directory named backup",
        "remove the project folder",
        "delete test_folder",
        "remove ai_test",
    ]
    
    for query in test_queries:
        result = ai.process_query(query)
        print(f"'{query}' → '{result}'")
    
    print(f"\n{formatter.colorize('=== Summary ===', 'yellow', 'bright')}")
    print("The AI processor has been updated with better deletion patterns:")
    print("• 'delete <name>' → 'rm -rf <name>'")
    print("• 'remove <name>' → 'rm -rf <name>'")  
    print("• 'delete folder called <name>' → 'rm -r <name>'")
    print("• 'remove directory named <name>' → 'rm -r <name>'")
    print("\nThis should fix the issue where directories weren't being deleted properly!")


if __name__ == "__main__":
    main()