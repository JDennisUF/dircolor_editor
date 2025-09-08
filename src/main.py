#!/usr/bin/env python3

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio
from pathlib import Path

from ui.main_window import MainWindow

class DirColorEditorApp(Adw.Application):
    """Main application class."""
    
    def __init__(self):
        super().__init__(
            application_id='com.example.dircolor-editor',
            flags=Gio.ApplicationFlags.HANDLES_OPEN
        )
        self.window = None
        
    def do_activate(self):
        """Called when the application is activated."""
        if not self.window:
            # Create main window
            self.window = MainWindow(application=self)
        self.window.present()
        
    def do_open(self, files, n_files, hint):
        """Called when files are opened with the application."""
        self.do_activate()
        
        # Load the first file if provided
        if files and n_files > 0:
            try:
                file_path = files[0].get_path()
                if file_path and Path(file_path).exists():
                    self.window.load_file(Path(file_path))
            except Exception as e:
                print(f"Warning: Could not open file: {e}")

def main():
    """Main entry point."""
    app = DirColorEditorApp()
    return app.run(sys.argv)

if __name__ == '__main__':
    sys.exit(main())