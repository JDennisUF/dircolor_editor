#!/usr/bin/env python3

import sys
import os
import subprocess
from pathlib import Path

def check_environment():
    """Check if the environment is suitable for GUI applications."""
    print("🔍 Environment Check")
    print("=" * 30)
    
    # Check display variables
    display = os.environ.get('DISPLAY')
    wayland = os.environ.get('WAYLAND_DISPLAY')
    xdg_session = os.environ.get('XDG_SESSION_TYPE')
    
    print(f"DISPLAY: {display or 'Not set'}")
    print(f"WAYLAND_DISPLAY: {wayland or 'Not set'}")
    print(f"XDG_SESSION_TYPE: {xdg_session or 'Not set'}")
    
    if not display and not wayland:
        print("❌ No display environment detected")
        return False
    else:
        print("✅ Display environment detected")
        
    # Check if we can import GTK
    try:
        import gi
        gi.require_version('Gtk', '4.0')
        from gi.repository import Gtk
        print("✅ GTK4 imports successfully")
    except Exception as e:
        print(f"❌ GTK4 import failed: {e}")
        return False
        
    return True

def test_simple_window():
    """Test if we can create a simple GTK window."""
    print("\n🪟 Simple Window Test")
    print("=" * 30)
    
    try:
        import gi
        gi.require_version('Gtk', '4.0')
        from gi.repository import Gtk, GLib
        
        def on_activate(app):
            window = Gtk.ApplicationWindow(application=app)
            window.set_title("Test Window")
            window.set_default_size(400, 200)
            
            label = Gtk.Label(label="If you see this, GTK4 is working!")
            window.set_child(label)
            window.present()
            
            # Auto close after 3 seconds
            GLib.timeout_add_seconds(3, lambda: app.quit())
            print("✅ Test window should be visible now...")
            
        app = Gtk.Application(application_id='test.window')
        app.connect('activate', on_activate)
        
        print("Opening test window (will auto-close in 3 seconds)...")
        result = app.run([])
        print(f"✅ Test window completed with exit code: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Simple window test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dircolor_app():
    """Test our dircolor application specifically."""
    print("\n🎨 Dircolor App Test")
    print("=" * 30)
    
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    
    try:
        # Test basic imports
        from main import DirColorEditorApp
        print("✅ App imports successfully")
        
        # Try to create the app
        app = DirColorEditorApp()
        print("✅ App created successfully")
        
        # Try a very short run
        import signal
        
        def timeout_handler(signum, frame):
            print("⏰ Timeout reached, exiting...")
            app.quit()
            
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)  # 5 second timeout
        
        print("🚀 Running app for 5 seconds...")
        try:
            result = app.run([])
            print(f"✅ App completed with exit code: {result}")
            return True
        except KeyboardInterrupt:
            print("⏰ App timed out (this might be normal)")
            return True
            
    except Exception as e:
        print(f"❌ Dircolor app test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🧪 Dircolor Editor Debug Launcher")
    print("=" * 40)
    
    # Step 1: Environment check
    if not check_environment():
        print("\n💡 Try running this from a terminal within your desktop environment")
        return 1
        
    # Step 2: Simple GTK test
    if not test_simple_window():
        print("\n💡 GTK4 may not be properly installed or configured")
        return 1
        
    # Step 3: Our app test
    if not test_dircolor_app():
        print("\n💡 There may be an issue with the dircolor editor code")
        return 1
        
    print("\n🎉 All tests passed! The app should work.")
    print("If you didn't see windows, try:")
    print("1. Make sure you're in a desktop environment (not SSH)")
    print("2. Try: DISPLAY=:0 python3 run.py")
    print("3. Check if your compositor/window manager is running")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())