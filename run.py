#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

try:
    from main import main
    sys.exit(main())
except ImportError as e:
    print(f"Error importing application: {e}")
    print("Make sure PyGObject is installed:")
    print("  sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1")
    print("  pip install PyGObject pycairo")
    sys.exit(1)
except Exception as e:
    print(f"Error running application: {e}")
    sys.exit(1)