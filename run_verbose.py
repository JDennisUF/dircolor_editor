#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

print("🎨 Dircolor Editor - Verbose Launch")
print("=" * 40)

# Environment info
print(f"Display: {os.environ.get('DISPLAY', 'Not set')}")
print(f"Session: {os.environ.get('XDG_SESSION_TYPE', 'Not set')}")
print(f"Python: {sys.version.split()[0]}")

try:
    print("📦 Importing modules...")
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from gi.repository import Gtk, Adw, Gio
    print("   ✓ GTK4 and Libadwaita imported")
    
    from main import DirColorEditorApp
    print("   ✓ Main application imported")
    
    print("🚀 Creating application...")
    app = DirColorEditorApp()
    
    # Add some debugging to the app
    def on_window_shown():
        print("   ✓ Main window should now be visible!")
        
    def on_activate_debug(app):
        print("   ✓ Application activated")
        from ui.main_window import MainWindow
        
        print("   ✓ Creating main window...")
        app.window = MainWindow(application=app)
        
        # Force window to front
        app.window.set_title("Dircolor Editor - Starting...")
        print("   ✓ Window title set")
        
        app.window.present()
        print("   ✓ Window presented")
        
        # Try to ensure it's visible
        app.window.set_focus_visible(True)
        print("   ✓ Window focus set")
        
        # Update title after a moment
        from gi.repository import GLib
        def update_title():
            app.window.set_title("Dircolor Editor")
            print("   ✓ Window ready!")
            return False
            
        GLib.timeout_add(1000, update_title)
    
    # Replace the activate handler
    app.disconnect_by_func(app.on_activate)
    app.connect('activate', on_activate_debug)
    
    print("🎬 Starting application...")
    print("   (Window should appear shortly)")
    print("   Press Ctrl+C to exit")
    print()
    
    exit_code = app.run(sys.argv)
    print(f"👋 Application exited with code: {exit_code}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure PyGObject and GTK4 are installed:")
    print("  sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)