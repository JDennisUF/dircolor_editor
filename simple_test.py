#!/usr/bin/env python3

import sys
import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio

class SimpleApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.test.simple')
        
    def do_activate(self):
        print("✓ Application activated!")
        
        # Create window
        window = Gtk.ApplicationWindow(application=self)
        window.set_title("Simple Test")
        window.set_default_size(600, 400)
        
        # Create content
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        
        label = Gtk.Label()
        label.set_markup("<big><b>Dircolor Editor Test</b></big>\n\nIf you can see this window, GTK4 is working!")
        box.append(label)
        
        button = Gtk.Button(label="Close")
        button.connect("clicked", lambda b: self.quit())
        box.append(button)
        
        window.set_child(box)
        window.present()
        
        print("✓ Window created and presented")

def main():
    print("🧪 Simple GTK4 Test")
    app = SimpleApp()
    return app.run(sys.argv)

if __name__ == '__main__':
    sys.exit(main())