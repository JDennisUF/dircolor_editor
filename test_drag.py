#!/usr/bin/env python3

import sys
import os
sys.path.append('src')

from src.main import main

if __name__ == '__main__':
    print("Starting dircolor editor with drag-and-drop test...")
    print("Try dragging .deb from Archives to Documents category")
    main()