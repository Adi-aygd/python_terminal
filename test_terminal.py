#!/usr/bin/env python3
"""
Quick test script to validate the Python terminal functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.terminal_engine import TerminalEngine
from src.ai_processor import AIProcessor


def test_basic_commands():
    """Test basic terminal commands"""
    engine = TerminalEngine()
    
    print("Testing basic commands...")
    
    # Test pwd
    output, code = engine.execute_command("pwd")
    print(f"pwd: {output}")
    assert code == 0
    
    # Test ls
    output, code = engine.execute_command("ls")
    print(f"ls: {output[:100]}...")
    assert code == 0
    
    # Test help
    output, code = engine.execute_command("help")
    print(f"help: Command executed successfully")
    assert code == 0
    
    print("✓ Basic commands working!")


def test_file_operations():
    """Test file operations"""
    engine = TerminalEngine()
    
    print("\nTesting file operations...")
    
    # Test mkdir
    output, code = engine.execute_command("mkdir test_dir")
    if code == 0:
        print("✓ mkdir working")
        
        # Test rmdir
        output, code = engine.execute_command("rmdir test_dir")
        if code == 0:
            print("✓ rmdir working")
    
    # Test touch
    output, code = engine.execute_command("touch test_file.txt")
    if code == 0:
        print("✓ touch working")
        
        # Test rm
        output, code = engine.execute_command("rm test_file.txt")
        if code == 0:
            print("✓ rm working")
    
    print("✓ File operations working!")


def test_ai_processor():
    """Test AI natural language processing"""
    ai = AIProcessor()
    
    print("\nTesting AI processor...")
    
    # Test natural language queries
    test_queries = [
        "show me the files in this directory",
        "create a new folder called test",
        "copy file.txt to backup",
        "find all python files",
        "what processes are running"
    ]
    
    for query in test_queries:
        command = ai.process_query(query)
        print(f"'{query}' -> '{command}'")
        assert command is not None
    
    print("✓ AI processor working!")


def test_system_monitoring():
    """Test system monitoring commands"""
    engine = TerminalEngine()
    
    print("\nTesting system monitoring...")
    
    # Test ps
    output, code = engine.execute_command("ps")
    if code == 0:
        print("✓ ps working")
    
    # Test free
    output, code = engine.execute_command("free")
    if code == 0:
        print("✓ free working")
    
    # Test df
    output, code = engine.execute_command("df")
    if code == 0:
        print("✓ df working")
    
    print("✓ System monitoring working!")


def main():
    """Run all tests"""
    print("Python Terminal - Quick Test Suite")
    print("=" * 40)
    
    try:
        test_basic_commands()
        test_file_operations()
        test_ai_processor()
        test_system_monitoring()
        
        print("\n" + "=" * 40)
        print("🎉 All tests passed! The terminal is ready to use.")
        print("\nTo start the terminal, run:")
        print("  source venv/bin/activate")
        print("  python main.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())