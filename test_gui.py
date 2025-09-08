#!/usr/bin/env python3

import sys
from pathlib import Path
import signal

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Test GTK imports
try:
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from gi.repository import Gtk, Adw
    print("✓ GTK4 and Libadwaita imports OK")
except ImportError as e:
    print(f"✗ GTK import error: {e}")
    sys.exit(1)

# Test our modules
try:
    from parser import DirColorsParser
    from color_utils import parse_color_code
    print("✓ Our modules import OK")
except ImportError as e:
    print(f"✗ Module import error: {e}")
    sys.exit(1)

# Test basic GTK window
def test_basic_window():
    """Test if we can create a basic GTK window."""
    print("Testing basic GTK window...")
    
    app = Adw.Application(application_id='test.app')
    
    def on_activate(app):
        window = Adw.ApplicationWindow(application=app)
        window.set_title("Test Window")
        window.set_default_size(400, 300)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        
        label = Gtk.Label(label="Dircolor Editor Test")
        box.append(label)
        
        button = Gtk.Button(label="Close")
        button.connect('clicked', lambda b: app.quit())
        box.append(button)
        
        window.set_content(box)
        window.present()
        
        # Auto-close after 3 seconds
        from gi.repository import GLib
        GLib.timeout_add_seconds(3, lambda: app.quit())
    
    app.connect('activate', on_activate)
    
    # Set up signal handler for clean exit
    def signal_handler(sig, frame):
        print("\nReceived interrupt, exiting...")
        app.quit()
        
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Opening test window (will auto-close in 3 seconds)...")
    try:
        app.run([])
        print("✓ Basic GTK window test passed")
        return True
    except Exception as e:
        print(f"✗ GTK window test failed: {e}")
        return False

if __name__ == '__main__':
    success = test_basic_window()
    if success:
        print("\nBasic GUI test passed! You can now run the full application:")
        print("python3 run.py")
    else:
        print("\nGUI test failed. Check your GTK4/Libadwaita installation.")
        sys.exit(1)