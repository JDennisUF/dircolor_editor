#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib
from pathlib import Path
import os

import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from parser import DirColorsParser, load_default_dircolors
from ui.file_type_tree import FileTypeTreeView
from ui.color_editor import ColorEditor
from ui.preview_panel import PreviewPanel

class MainWindow(Adw.ApplicationWindow):
    """Main application window with three-panel layout."""
    
    def __init__(self, application):
        super().__init__(application=application)
        
        self.parser = DirColorsParser()
        self.current_file = None
        self.modified = False
        
        self.setup_ui()
        self.setup_actions()
        self.load_default_config()
        
    def setup_ui(self):
        """Set up the user interface."""
        self.set_title("Dircolor Editor")
        self.set_default_size(1200, 800)
        
        # Header bar
        header = Adw.HeaderBar()
        self.set_titlebar(header)
        
        # Menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        header.pack_end(menu_button)
        
        # Create menu
        menu_model = Gio.Menu()
        
        file_menu = Gio.Menu()
        file_menu.append("New", "win.new")
        file_menu.append("Open...", "win.open")
        file_menu.append("Save", "win.save")
        file_menu.append("Save As...", "win.save_as")
        menu_model.append_submenu("File", file_menu)
        
        edit_menu = Gio.Menu()
        edit_menu.append("Add Extension...", "win.add_extension")
        edit_menu.append("Remove Selected", "win.remove_selected")
        edit_menu.append("Reset to Default", "win.reset")
        menu_model.append_submenu("Edit", edit_menu)
        
        help_menu = Gio.Menu()
        help_menu.append("About", "win.about")
        menu_model.append_submenu("Help", help_menu)
        
        menu_button.set_menu_model(menu_model)
        
        # Save button in header
        self.save_button = Gtk.Button.new_from_icon_name("document-save-symbolic")
        self.save_button.set_tooltip_text("Save")
        self.save_button.connect("clicked", lambda btn: self.save_file())
        self.save_button.set_sensitive(False)
        header.pack_start(self.save_button)
        
        # Main content area
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)
        
        # Three-panel layout using Paned widgets
        h_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.append(h_paned)
        
        # Left panel: File type tree
        left_frame = Gtk.Frame()
        left_frame.set_size_request(300, -1)
        self.file_tree = FileTypeTreeView()
        self.file_tree.connect("selection-changed", self.on_file_type_selected)
        left_frame.set_child(self.file_tree)
        h_paned.set_start_child(left_frame)
        
        # Right side: Color editor and preview
        right_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        h_paned.set_end_child(right_paned)
        
        # Center panel: Color editor
        center_frame = Gtk.Frame()
        center_frame.set_size_request(350, -1)
        self.color_editor = ColorEditor()
        self.color_editor.connect("color-changed", self.on_color_changed)
        center_frame.set_child(self.color_editor)
        right_paned.set_start_child(center_frame)
        
        # Right panel: Preview
        right_frame = Gtk.Frame()
        right_frame.set_size_request(300, -1)
        self.preview_panel = PreviewPanel()
        right_frame.set_child(self.preview_panel)
        right_paned.set_end_child(right_frame)
        
        # Status bar
        self.status_bar = Gtk.StatusBar()
        main_box.append(self.status_bar)
        self.status_context = self.status_bar.get_context_id("main")
        
    def setup_actions(self):
        """Set up application actions."""
        # File actions
        new_action = Gio.SimpleAction.new("new", None)
        new_action.connect("activate", lambda a, p: self.new_file())
        self.add_action(new_action)
        
        open_action = Gio.SimpleAction.new("open", None)
        open_action.connect("activate", lambda a, p: self.open_file())
        self.add_action(open_action)
        
        save_action = Gio.SimpleAction.new("save", None)
        save_action.connect("activate", lambda a, p: self.save_file())
        self.add_action(save_action)
        
        save_as_action = Gio.SimpleAction.new("save_as", None)
        save_as_action.connect("activate", lambda a, p: self.save_as_file())
        self.add_action(save_as_action)
        
        # Edit actions
        add_ext_action = Gio.SimpleAction.new("add_extension", None)
        add_ext_action.connect("activate", lambda a, p: self.add_extension())
        self.add_action(add_ext_action)
        
        remove_action = Gio.SimpleAction.new("remove_selected", None)
        remove_action.connect("activate", lambda a, p: self.remove_selected())
        self.add_action(remove_action)
        
        reset_action = Gio.SimpleAction.new("reset", None)
        reset_action.connect("activate", lambda a, p: self.reset_to_default())
        self.add_action(reset_action)
        
        # Help actions
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", lambda a, p: self.show_about())
        self.add_action(about_action)
        
        # Keyboard shortcuts
        self.set_help_overlay(self.create_shortcuts())
        
    def create_shortcuts(self):
        """Create keyboard shortcuts overlay."""
        builder = Gtk.Builder()
        builder.add_from_string("""
        <interface>
          <object class="GtkShortcutsWindow" id="shortcuts">
            <property name="modal">True</property>
            <child>
              <object class="GtkShortcutsSection">
                <property name="section-name">general</property>
                <property name="title">General</property>
                <child>
                  <object class="GtkShortcutsGroup">
                    <property name="title">File Operations</property>
                    <child>
                      <object class="GtkShortcutsShortcut">
                        <property name="title">New file</property>
                        <property name="accelerator">&lt;Primary&gt;n</property>
                      </object>
                    </child>
                    <child>
                      <object class="GtkShortcutsShortcut">
                        <property name="title">Open file</property>
                        <property name="accelerator">&lt;Primary&gt;o</property>
                      </object>
                    </child>
                    <child>
                      <object class="GtkShortcutsShortcut">
                        <property name="title">Save</property>
                        <property name="accelerator">&lt;Primary&gt;s</property>
                      </object>
                    </child>
                  </object>
                </child>
              </object>
            </child>
          </object>
        </interface>
        """)
        return builder.get_object("shortcuts")
        
    def load_default_config(self):
        """Load the user's default .dircolors file."""
        user_dircolors = Path.home() / '.dircolors'
        if user_dircolors.exists():
            self.load_file(user_dircolors)
        else:
            # Load system defaults
            self.parser = load_default_dircolors()
            self.refresh_ui()
            self.update_status("Loaded system defaults")
            
    def load_file(self, filepath: Path):
        """Load a .dircolors file."""
        try:
            self.parser.parse_file(filepath)
            self.current_file = filepath
            self.modified = False
            self.refresh_ui()
            self.update_status(f"Loaded: {filepath}")
            self.update_title()
        except Exception as e:
            self.show_error(f"Failed to load file: {e}")
            
    def save_file(self):
        """Save the current configuration."""
        if self.current_file:
            try:
                self.parser.write_file(self.current_file)
                self.modified = False
                self.save_button.set_sensitive(False)
                self.update_status(f"Saved: {self.current_file}")
                self.update_title()
            except Exception as e:
                self.show_error(f"Failed to save file: {e}")
        else:
            self.save_as_file()
            
    def save_as_file(self):
        """Save the configuration to a new file."""
        dialog = Gtk.FileChooserNative(
            title="Save .dircolors file",
            transient_for=self,
            action=Gtk.FileChooserAction.SAVE
        )
        
        # Add file filter
        filter_dircolors = Gtk.FileFilter()
        filter_dircolors.set_name("Dircolors files")
        filter_dircolors.add_pattern("*.dircolors")
        filter_dircolors.add_pattern(".dircolors")
        dialog.add_filter(filter_dircolors)
        
        dialog.connect("response", self.on_save_dialog_response)
        dialog.show()
        
    def on_save_dialog_response(self, dialog, response):
        """Handle save dialog response."""
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            if file:
                filepath = Path(file.get_path())
                try:
                    self.parser.write_file(filepath)
                    self.current_file = filepath
                    self.modified = False
                    self.save_button.set_sensitive(False)
                    self.update_status(f"Saved: {filepath}")
                    self.update_title()
                except Exception as e:
                    self.show_error(f"Failed to save file: {e}")
        dialog.destroy()
        
    def new_file(self):
        """Create a new configuration."""
        if self.modified:
            # TODO: Ask to save changes
            pass
            
        self.parser = load_default_dircolors()
        self.current_file = None
        self.modified = False
        self.refresh_ui()
        self.update_status("New configuration created")
        self.update_title()
        
    def open_file(self):
        """Open a .dircolors file."""
        dialog = Gtk.FileChooserNative(
            title="Open .dircolors file",
            transient_for=self,
            action=Gtk.FileChooserAction.OPEN
        )
        
        # Add file filter
        filter_dircolors = Gtk.FileFilter()
        filter_dircolors.set_name("Dircolors files")
        filter_dircolors.add_pattern("*.dircolors")
        filter_dircolors.add_pattern(".dircolors")
        dialog.add_filter(filter_dircolors)
        
        # Set default location
        dialog.set_current_folder(Gio.File.new_for_path(str(Path.home())))
        
        dialog.connect("response", self.on_open_dialog_response)
        dialog.show()
        
    def on_open_dialog_response(self, dialog, response):
        """Handle open dialog response."""
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            if file:
                filepath = Path(file.get_path())
                self.load_file(filepath)
        dialog.destroy()
        
    def refresh_ui(self):
        """Refresh all UI components."""
        self.file_tree.update_data(self.parser)
        self.preview_panel.update_preview(self.parser)
        
    def on_file_type_selected(self, tree_view, file_type):
        """Handle file type selection in the tree."""
        entry = self.parser.get_entry(file_type)
        if entry:
            self.color_editor.set_color_code(entry.color_code)
            self.color_editor.set_sensitive(True)
        else:
            self.color_editor.clear()
            self.color_editor.set_sensitive(False)
            
    def on_color_changed(self, editor, color_code):
        """Handle color changes from the editor."""
        selected_type = self.file_tree.get_selected_file_type()
        if selected_type:
            self.parser.set_entry(selected_type, color_code)
            self.preview_panel.update_preview(self.parser)
            self.set_modified(True)
            
    def set_modified(self, modified: bool):
        """Set the modified state."""
        self.modified = modified
        self.save_button.set_sensitive(modified)
        self.update_title()
        
    def update_title(self):
        """Update the window title."""
        title = "Dircolor Editor"
        if self.current_file:
            title += f" - {self.current_file.name}"
        if self.modified:
            title += " •"
        self.set_title(title)
        
    def update_status(self, message: str):
        """Update the status bar."""
        self.status_bar.remove_all(self.status_context)
        self.status_bar.push(self.status_context, message)
        
    def show_error(self, message: str):
        """Show an error dialog."""
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading="Error",
            body=message
        )
        dialog.add_response("ok", "OK")
        dialog.present()
        
    def show_about(self):
        """Show the about dialog."""
        about = Adw.AboutWindow(
            transient_for=self,
            application_name="Dircolor Editor",
            application_icon="applications-graphics",
            developer_name="Developer",
            version="0.1.0",
            website="https://github.com/example/dircolor-editor",
            issue_url="https://github.com/example/dircolor-editor/issues",
            license_type=Gtk.License.MIT_X11,
            copyright="© 2024 Developer"
        )
        about.present()
        
    def add_extension(self):
        """Add a new file extension."""
        # TODO: Implement add extension dialog
        pass
        
    def remove_selected(self):
        """Remove the selected file type."""
        selected_type = self.file_tree.get_selected_file_type()
        if selected_type:
            self.parser.remove_entry(selected_type)
            self.refresh_ui()
            self.set_modified(True)
            
    def reset_to_default(self):
        """Reset to default configuration."""
        self.parser = load_default_dircolors()
        self.refresh_ui()
        self.set_modified(True)
        self.update_status("Reset to default configuration")