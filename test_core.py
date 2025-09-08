#!/usr/bin/env python3

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_parser():
    """Test the dircolors parser."""
    print("Testing parser...")
    
    from parser import DirColorsParser, load_default_dircolors, validate_color_code
    
    # Test color code validation
    valid, msg = validate_color_code("01;31")
    print(f"Color code validation (01;31): {valid}, {msg}")
    
    # Test parser creation
    parser = DirColorsParser()
    parser.set_entry("DIR", "01;34")
    parser.set_entry(".txt", "00;32")
    
    entry = parser.get_entry("DIR")
    print(f"DIR entry: {entry.color_code if entry else 'None'}")
    
    # Test categories
    categories = parser.get_categories()
    print(f"Categories: {list(categories.keys())}")
    
    print("Parser test OK")

def test_color_utils():
    """Test color utilities."""
    print("Testing color utilities...")
    
    from color_utils import parse_color_code, build_color_code, ColorMode, Style
    
    # Test parsing
    color_info = parse_color_code("01;31")
    print(f"Parsed styles: {[s.name for s in color_info.styles]}")
    print(f"Foreground: {color_info.foreground}")
    
    # Test building
    code = build_color_code(
        foreground_rgb=(255, 0, 0),
        styles=[Style.BOLD],
        mode=ColorMode.RGB_TRUECOLOR
    )
    print(f"Built color code: {code}")
    
    print("Color utils test OK")

def test_file_operations():
    """Test file operations."""
    print("Testing file operations...")
    
    from parser import DirColorsParser
    
    # Test loading user's file
    parser = DirColorsParser()
    user_file = Path.home() / '.dircolors'
    
    if user_file.exists():
        parser.parse_file(user_file)
        print(f"Loaded {len(parser.entries)} entries from user file")
        
        # Show some entries
        for i, (file_type, entry) in enumerate(parser.entries.items()):
            if i >= 5:
                break
            print(f"  {file_type}: {entry.color_code}")
    else:
        print("No user .dircolors file found")
    
    print("File operations test OK")

if __name__ == '__main__':
    try:
        test_parser()
        print()
        test_color_utils()
        print()
        test_file_operations()
        print("\nAll tests passed!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)