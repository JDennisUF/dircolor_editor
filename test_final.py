#!/usr/bin/env python3

import sys
import subprocess
import time
from pathlib import Path

def test_application():
    """Final test of the dircolor editor application."""
    print("🎨 Dircolor Editor - Final Test")
    print("=" * 40)
    
    # Test 1: Core modules
    print("✅ Testing core modules...")
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    
    try:
        from parser import DirColorsParser, load_default_dircolors
        from color_utils import parse_color_code, ColorMode, Style
        print("   ✓ Parser and color utilities loaded")
    except Exception as e:
        print(f"   ✗ Module loading failed: {e}")
        return False
    
    # Test 2: Parse user's dircolors file
    print("✅ Testing file parsing...")
    parser = DirColorsParser()
    user_file = Path.home() / '.dircolors'
    
    if user_file.exists():
        parser.parse_file(user_file)
        print(f"   ✓ Loaded {len(parser.entries)} color entries")
        
        # Show some examples
        dir_entry = parser.get_entry("DIR")
        if dir_entry:
            print(f"   ✓ Directory color: {dir_entry.color_code}")
            
        txt_entry = parser.get_entry(".txt")
        if txt_entry:
            print(f"   ✓ Text file color: {txt_entry.color_code}")
    else:
        print("   ⚠ No user .dircolors file found (will use defaults)")
    
    # Test 3: Color parsing
    print("✅ Testing color parsing...")
    color_info = parse_color_code("01;93;48;5;93")  # User's dir color
    print(f"   ✓ Parsed styles: {[s.name for s in color_info.styles]}")
    print(f"   ✓ Foreground RGB: {color_info.foreground}")
    print(f"   ✓ Background RGB: {color_info.background}")
    
    # Test 4: Try launching GUI (non-blocking)
    print("✅ Testing GUI launch...")
    try:
        # Start application in background
        process = subprocess.Popen(
            [sys.executable, "run.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=Path(__file__).parent
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check if still running
        if process.poll() is None:
            print("   ✓ GUI application launched successfully")
            print("   ✓ Process is running (PID: {})".format(process.pid))
            
            # Terminate the test instance
            process.terminate()
            process.wait(timeout=5)
            print("   ✓ Test instance terminated cleanly")
            
        else:
            stdout, stderr = process.communicate()
            print(f"   ✗ Application exited with code: {process.returncode}")
            if stderr:
                print(f"   ✗ Errors: {stderr.decode()[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ✗ GUI test failed: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("\nYour Dircolor Editor is ready to use:")
    print(f"   python3 {Path(__file__).parent}/run.py")
    print("\nFeatures available:")
    print("   • Three-panel interface (file types, color editor, preview)")
    print("   • Visual RGB color picker")
    print("   • Support for 8-bit, 256-color, and RGB modes")
    print("   • Text style toggles (bold, italic, underline, etc.)")
    print("   • Auto-loads your ~/.dircolors file")
    print("   • Save/load dircolors files")
    print("   • Live preview of terminal colors")
    
    return True

if __name__ == '__main__':
    success = test_application()
    sys.exit(0 if success else 1)