#!/usr/bin/env python3

import sys
import os
sys.path.append('src')

from src.parser import DirColorsParser
from pathlib import Path

# Test the parser with the actual .dircolors file
parser = DirColorsParser()
parser.parse_file(Path.home() / '.dircolors')

# Check categories
categories = parser.get_categories()

print("Categories found:")
for cat_name, items in categories.items():
    print(f"  {cat_name}: {items[:5]}..." if len(items) > 5 else f"  {cat_name}: {items}")

# Specifically check if .cs is in code_extensions
if 'code_extensions' in categories:
    if '.cs' in categories['code_extensions']:
        print("\n✓ SUCCESS: .cs found in code_extensions")
    else:
        print(f"\n✗ PROBLEM: .cs not in code_extensions")
        print(f"code_extensions contains: {categories['code_extensions']}")
else:
    print("\n✗ PROBLEM: no code_extensions category found")

# Check if .cs is in other_extensions
if 'other_extensions' in categories:
    if '.cs' in categories['other_extensions']:
        print("✗ PROBLEM: .cs still in other_extensions")
        print(f"other_extensions contains: {categories['other_extensions'][:10]}...")
    else:
        print("✓ Good: .cs not in other_extensions")