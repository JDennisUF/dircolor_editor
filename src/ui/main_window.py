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
from config import app_config

class MainWindow(Gtk.ApplicationWindow):
    """Main application window with three-panel layout."""
    
    def __init__(self, application):
        super().__init__(application=application)
        
        self.parser = DirColorsParser()
        self.current_file = None
        self.modified = False
        
        self.setup_ui()
        self.setup_actions()
        self.load_default_config()
        
        # Connect to window close event to save settings
        self.connect("close-request", self.on_close_request)
        
    def on_close_request(self, window):
        """Handle window close request."""
        # Save window size
        width = self.get_width()
        height = self.get_height()
        app_config.set_window_size(width, height)
        
        # Allow the window to close
        return False
        
    def setup_ui(self):
        """Set up the user interface."""
        self.set_title("Dircolor Editor")
        
        # Restore window size from config
        width, height = app_config.get_window_size()
        self.set_default_size(width, height)
        
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
        
        view_menu = Gio.Menu()
        view_menu.append("Refresh Preview", "win.refresh_preview")
        view_menu.append("Set Background Color...", "win.set_bg_color")
        menu_model.append_submenu("View", view_menu)
        
        help_menu = Gio.Menu()
        help_menu.append("About", "win.about")
        menu_model.append_submenu("Help", help_menu)
        
        menu_button.set_menu_model(menu_model)
        
        # Save button in header - make it more prominent
        save_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        self.save_button = Gtk.Button()
        self.save_button.set_tooltip_text("Save to ~/.dircolors")
        self.save_button.connect("clicked", lambda btn: self.save_file())
        self.save_button.set_sensitive(False)
        
        # Create button content with icon and text
        save_content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        save_icon = Gtk.Image.new_from_icon_name("document-save-symbolic")
        save_label = Gtk.Label(label="Save .dircolors")
        save_content.append(save_icon)
        save_content.append(save_label)
        self.save_button.set_child(save_content)
        
        # Store references for updating
        self.save_button_label = save_label
        self.save_button_icon = save_icon
        
        save_box.append(self.save_button)
        header.pack_start(save_box)
        
        # Main content area
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(main_box)
        
        # Three-panel layout using simple Box with fixed widths
        content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        main_box.append(content_box)
        
        # Left panel: File type tree - Fixed width
        left_frame = Gtk.Frame()
        left_frame.set_size_request(280, -1)
        left_frame.set_hexpand(False)  # Don't expand horizontally
        self.file_tree = FileTypeTreeView()
        self.file_tree.connect("selection-changed", self.on_file_type_selected)
        left_frame.set_child(self.file_tree)
        content_box.append(left_frame)
        
        # Center panel: Color editor - Expandable
        center_frame = Gtk.Frame()
        center_frame.set_size_request(320, -1)
        center_frame.set_hexpand(True)  # Expand when window widens
        center_frame.set_hexpand_set(True)
        self.color_editor = ColorEditor()
        self.color_editor.connect("color-changed", self.on_color_changed)
        # Make color editor initially sensitive for testing
        self.color_editor.set_sensitive(True)
        self.color_editor.set_vexpand(True)
        
        print("DEBUG MainWindow: Created color editor, adding to frame...")
        center_frame.set_child(self.color_editor)
        content_box.append(center_frame)
        print("DEBUG MainWindow: Color editor panel setup complete")
        
        # Right panel: Preview - Expandable and larger
        right_frame = Gtk.Frame()
        right_frame.set_size_request(480, -1)  # Increased base size
        right_frame.set_hexpand(True)  # Expand when window widens
        right_frame.set_hexpand_set(True)
        self.preview_panel = PreviewPanel()
        right_frame.set_child(self.preview_panel)
        content_box.append(right_frame)
        
        # Status bar (using a simple label in GTK4)
        status_frame = Gtk.Frame()
        status_frame.add_css_class("statusbar")
        self.status_label = Gtk.Label(label="Ready")
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.set_margin_start(6)
        self.status_label.set_margin_end(6)
        self.status_label.set_margin_top(3)
        self.status_label.set_margin_bottom(3)
        status_frame.set_child(self.status_label)
        main_box.append(status_frame)
        
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
        
        # View actions
        refresh_action = Gio.SimpleAction.new("refresh_preview", None)
        refresh_action.connect("activate", lambda a, p: self.preview_panel.update_preview(self.parser))
        self.add_action(refresh_action)
        
        bg_color_action = Gio.SimpleAction.new("set_bg_color", None)
        bg_color_action.connect("activate", lambda a, p: self.set_background_color())
        self.add_action(bg_color_action)
        
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
        """Load the user's default .dircolors file and app settings."""
        user_dircolors = Path.home() / '.dircolors'
        if user_dircolors.exists():
            self.load_file(user_dircolors)
        else:
            # Load system defaults
            self.parser = load_default_dircolors()
            self.refresh_ui()
            self.update_status("Loaded system defaults")
            
        # Restore preview background color
        bg_color = app_config.get_background_color()
        from gi.repository import Gdk
        rgba = Gdk.RGBA()
        rgba.red = bg_color['r']
        rgba.green = bg_color['g']
        rgba.blue = bg_color['b']
        rgba.alpha = bg_color['a']
        self.preview_panel.set_background_color(rgba)
            
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
        print(f"DEBUG: File type selected: {file_type}")
        entry = self.parser.get_entry(file_type)
        if entry:
            print(f"DEBUG: Found entry with color code: {entry.color_code}")
            self.color_editor.set_color_code(entry.color_code)
            self.color_editor.set_sensitive(True)
            self.update_status(f"Editing: {file_type} = {entry.color_code}")
        else:
            print(f"DEBUG: No entry found for: {file_type}")
            self.color_editor.clear()
            self.color_editor.set_sensitive(False)
            self.update_status(f"No color defined for: {file_type}")
            
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
        
        # Update button appearance based on modified state
        if modified:
            # Indicate unsaved changes
            self.save_button.add_css_class("suggested-action")
            self.save_button_label.set_text("Save Changes")
            self.save_button_icon.set_from_icon_name("document-save-as-symbolic")
            self.save_button.set_tooltip_text("You have unsaved changes - Click to save to ~/.dircolors")
        else:
            # Normal state
            self.save_button.remove_css_class("suggested-action")
            self.save_button_label.set_text("Save .dircolors")
            self.save_button_icon.set_from_icon_name("document-save-symbolic")
            self.save_button.set_tooltip_text("Save to ~/.dircolors")
            
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
        self.status_label.set_text(message)
        
    def show_error(self, message: str):
        """Show an error dialog."""
        dialog = Gtk.AlertDialog()
        dialog.set_message("Error")
        dialog.set_detail(message)
        dialog.show(self)
        
    def set_background_color(self):
        """Set the preview background color to match terminal."""
        dialog = Gtk.ColorChooserDialog(title="Choose Background Color")
        dialog.set_transient_for(self)
        dialog.set_use_alpha(False)
        
        # Set default to common terminal background colors
        from gi.repository import Gdk
        default_color = Gdk.RGBA()
        default_color.red = 0.1  # Dark gray
        default_color.green = 0.1
        default_color.blue = 0.1
        default_color.alpha = 1.0
        dialog.set_rgba(default_color)
        
        # Add some preset colors for common terminals
        presets = [
            (0.0, 0.0, 0.0, 1.0),      # Black
            (0.1, 0.1, 0.1, 1.0),      # Dark gray
            (0.15, 0.15, 0.15, 1.0),   # Medium dark gray
            (0.2, 0.2, 0.2, 1.0),      # Light dark gray
            (1.0, 1.0, 1.0, 1.0),      # White
            (0.95, 0.95, 0.87, 1.0),   # Cream
        ]
        
        for r, g, b, a in presets:
            color = Gdk.RGBA()
            color.red, color.green, color.blue, color.alpha = r, g, b, a
            dialog.add_palette(Gtk.Orientation.HORIZONTAL, 6, [color])
        
        def on_response(dialog, response):
            if response == Gtk.ResponseType.OK:
                color = dialog.get_rgba()
                # Apply the color to the preview panel
                self.preview_panel.set_background_color(color)
                
                # Save the color to config
                app_config.set_background_color(
                    color.red, color.green, color.blue, color.alpha
                )
                
                self.update_status(f"Background color updated and saved")
            dialog.destroy()
        
        dialog.connect("response", on_response)
        dialog.present()
        
    def show_about(self):
        """Show the about dialog."""
        dialog = Gtk.AboutDialog()
        dialog.set_transient_for(self)
        dialog.set_program_name("Dircolor Editor")
        dialog.set_version("0.1.0")
        dialog.set_comments("A visual editor for .dircolors files")
        dialog.set_website("https://github.com/example/dircolor-editor")
        dialog.set_copyright("© 2025 Jason Dennis")
        dialog.set_license_type(Gtk.License.MIT_X11)
        dialog.present()
        
    def add_extension(self):
        """Add a new file extension."""
        dialog = Gtk.Dialog(title="Add File Extension")
        dialog.set_transient_for(self)
        dialog.set_modal(True)
        dialog.set_default_size(400, 300)
        
        # Add buttons
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        add_button = dialog.add_button("Add", Gtk.ResponseType.OK)
        add_button.add_css_class("suggested-action")
        
        # Create dialog content
        content_area = dialog.get_content_area()
        content_area.set_spacing(12)
        content_area.set_margin_start(12)
        content_area.set_margin_end(12)
        content_area.set_margin_top(12)
        content_area.set_margin_bottom(12)
        
        # Extension input
        ext_frame = Gtk.Frame(label="File Extension")
        ext_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        ext_box.set_margin_start(6)
        ext_box.set_margin_end(6)
        ext_box.set_margin_top(6)
        ext_box.set_margin_bottom(6)
        
        ext_entry = Gtk.Entry()
        ext_entry.set_placeholder_text("e.g., .myext")
        ext_entry.set_text(".")
        ext_box.append(Gtk.Label(label="Extension (including the dot):"))
        ext_box.append(ext_entry)
        ext_frame.set_child(ext_box)
        content_area.append(ext_frame)
        
        # Color code input
        color_frame = Gtk.Frame(label="Color Code")
        color_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        color_box.set_margin_start(6)
        color_box.set_margin_end(6)
        color_box.set_margin_top(6)
        color_box.set_margin_bottom(6)
        
        color_entry = Gtk.Entry()
        color_entry.set_placeholder_text("e.g., 01;32")
        color_entry.set_text("00;37")
        color_box.append(Gtk.Label(label="ANSI Color Code:"))
        color_box.append(color_entry)
        
        # Quick color buttons
        quick_colors = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        quick_colors.append(Gtk.Label(label="Quick colors:"))
        
        color_presets = [
            ("Red", "01;31"),
            ("Green", "01;32"),
            ("Yellow", "01;33"),
            ("Blue", "01;34"),
            ("Magenta", "01;35"),
            ("Cyan", "01;36"),
        ]
        
        for name, code in color_presets:
            btn = Gtk.Button(label=name)
            btn.connect("clicked", lambda b, c=code: color_entry.set_text(c))
            quick_colors.append(btn)
            
        color_box.append(quick_colors)
        color_frame.set_child(color_box)
        content_area.append(color_frame)
        
        # Description input
        desc_frame = Gtk.Frame(label="Description (Optional)")
        desc_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        desc_box.set_margin_start(6)
        desc_box.set_margin_end(6)
        desc_box.set_margin_top(6)
        desc_box.set_margin_bottom(6)
        
        desc_entry = Gtk.Entry()
        desc_entry.set_placeholder_text("e.g., My custom file type")
        desc_box.append(desc_entry)
        desc_frame.set_child(desc_box)
        content_area.append(desc_frame)
        
        # Focus the extension entry
        ext_entry.grab_focus()
        
        def on_response(dialog, response):
            if response == Gtk.ResponseType.OK:
                extension = ext_entry.get_text().strip()
                color_code = color_entry.get_text().strip()
                description = desc_entry.get_text().strip()
                
                # Validate input
                if not extension:
                    self.show_error("Extension cannot be empty")
                    return
                    
                if not extension.startswith('.'):
                    extension = '.' + extension
                    
                if not color_code:
                    self.show_error("Color code cannot be empty")
                    return
                    
                from parser import validate_color_code
                valid, error = validate_color_code(color_code)
                if not valid:
                    self.show_error(f"Invalid color code: {error}")
                    return
                    
                # Add the extension
                comment = description if description else None
                self.parser.set_entry(extension, color_code, comment)
                
                # Refresh UI
                self.refresh_ui()
                self.set_modified(True)
                self.update_status(f"Added extension: {extension} = {color_code}")
                
            dialog.destroy()
        
        dialog.connect("response", on_response)
        dialog.present()
        
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