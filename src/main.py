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
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS
        )
        
        self.connect('activate', self.on_activate)
        self.connect('open', self.on_open)
        
    def on_activate(self, app):
        """Called when the application is activated."""
        # Create main window
        self.window = MainWindow(application=self)
        self.window.present()
        
    def on_open(self, app, files, n_files, hint):
        """Called when files are opened with the application."""
        self.on_activate(app)
        
        # Load the first file if provided
        if files and len(files) > 0:
            file_path = files[0].get_path()
            if file_path:
                self.window.load_file(Path(file_path))

def main():
    """Main entry point."""
    app = DirColorEditorApp()
    return app.run(sys.argv)

if __name__ == '__main__':
    sys.exit(main())