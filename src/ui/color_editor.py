#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, GObject, Gdk
from typing import Optional, List
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from color_utils import (
    ColorInfo, parse_color_code, build_color_code, 
    ColorMode, Style, rgb_to_256_color
)

class ColorEditor(Gtk.Box):
    """Color editor widget for editing ANSI color codes."""
    
    __gsignals__ = {
        'color-changed': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    }
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        
        # Set minimum size and expansion
        self.set_size_request(300, 400)
        self.set_vexpand(True)
        self.set_hexpand(True)
        
        # Add background color for visual debugging
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        .color-editor-debug {
            background-color: #f0f0f0;
            border: 2px solid #ff0000;
        }
        """)
        self.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.add_css_class("color-editor-debug")
        
        self.color_info: Optional[ColorInfo] = None
        self.updating = False  # Prevent recursion during updates
        
        print("DEBUG ColorEditor: Initializing color editor...")
        self.setup_ui()
        print("DEBUG ColorEditor: Color editor setup complete")
        
    def setup_ui(self):
        """Set up the color editor interface."""
        # Title
        title = Gtk.Label(label="Color Editor")
        title.set_markup("<big><b>Color Editor</b></big>")
        title.set_halign(Gtk.Align.START)
        self.append(title)
        
        # Add a separator for visual clarity
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.append(separator)
        
        # Color mode selector
        mode_frame = Gtk.Frame(label="Color Mode")
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        mode_box.set_margin_start(6)
        mode_box.set_margin_end(6)
        mode_box.set_margin_top(6)
        mode_box.set_margin_bottom(6)
        
        self.mode_basic = Gtk.CheckButton(label="8-bit")
        self.mode_256 = Gtk.CheckButton(label="256-color", group=self.mode_basic)
        self.mode_rgb = Gtk.CheckButton(label="RGB", group=self.mode_basic)
        
        self.mode_basic.connect("toggled", self.on_mode_changed)
        self.mode_256.connect("toggled", self.on_mode_changed)
        self.mode_rgb.connect("toggled", self.on_mode_changed)
        
        mode_box.append(self.mode_basic)
        mode_box.append(self.mode_256)
        mode_box.append(self.mode_rgb)
        mode_frame.set_child(mode_box)
        self.append(mode_frame)
        
        # Style toggles
        style_frame = Gtk.Frame(label="Text Styles")
        style_grid = Gtk.Grid()
        style_grid.set_row_spacing(6)
        style_grid.set_column_spacing(12)
        style_grid.set_margin_start(6)
        style_grid.set_margin_end(6)
        style_grid.set_margin_top(6)
        style_grid.set_margin_bottom(6)
        
        self.style_bold = Gtk.CheckButton(label="Bold")
        self.style_dim = Gtk.CheckButton(label="Dim")
        self.style_italic = Gtk.CheckButton(label="Italic")
        self.style_underline = Gtk.CheckButton(label="Underline")
        self.style_blink = Gtk.CheckButton(label="Blink")
        self.style_reverse = Gtk.CheckButton(label="Reverse")
        
        # Connect style signals
        for style_check in [self.style_bold, self.style_dim, self.style_italic,
                           self.style_underline, self.style_blink, self.style_reverse]:
            style_check.connect("toggled", self.on_style_changed)
        
        # Layout style checkboxes in grid
        style_grid.attach(self.style_bold, 0, 0, 1, 1)
        style_grid.attach(self.style_dim, 1, 0, 1, 1)
        style_grid.attach(self.style_italic, 0, 1, 1, 1)
        style_grid.attach(self.style_underline, 1, 1, 1, 1)
        style_grid.attach(self.style_blink, 0, 2, 1, 1)
        style_grid.attach(self.style_reverse, 1, 2, 1, 1)
        
        style_frame.set_child(style_grid)
        self.append(style_frame)
        
        # Foreground color
        fg_frame = Gtk.Frame(label="Foreground Color")
        fg_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        fg_box.set_margin_start(6)
        fg_box.set_margin_end(6)
        fg_box.set_margin_top(6)
        fg_box.set_margin_bottom(6)
        
        self.fg_color_button = Gtk.ColorButton()
        self.fg_color_button.set_use_alpha(False)
        self.fg_color_button.connect("color-set", self.on_fg_color_changed)
        
        fg_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        fg_button_box.append(self.fg_color_button)
        
        self.fg_clear_button = Gtk.Button(label="Clear")
        self.fg_clear_button.connect("clicked", self.on_fg_clear)
        fg_button_box.append(self.fg_clear_button)
        
        fg_box.append(fg_button_box)
        
        # RGB values display
        self.fg_rgb_label = Gtk.Label(label="RGB: (0, 0, 0)")
        self.fg_rgb_label.set_halign(Gtk.Align.START)
        fg_box.append(self.fg_rgb_label)
        
        fg_frame.set_child(fg_box)
        self.append(fg_frame)
        
        # Background color
        bg_frame = Gtk.Frame(label="Background Color")
        bg_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        bg_box.set_margin_start(6)
        bg_box.set_margin_end(6)
        bg_box.set_margin_top(6)
        bg_box.set_margin_bottom(6)
        
        self.bg_color_button = Gtk.ColorButton()
        self.bg_color_button.set_use_alpha(False)
        self.bg_color_button.connect("color-set", self.on_bg_color_changed)
        
        bg_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        bg_button_box.append(self.bg_color_button)
        
        self.bg_clear_button = Gtk.Button(label="Clear")
        self.bg_clear_button.connect("clicked", self.on_bg_clear)
        bg_button_box.append(self.bg_clear_button)
        
        bg_box.append(bg_button_box)
        
        # RGB values display
        self.bg_rgb_label = Gtk.Label(label="RGB: (0, 0, 0)")
        self.bg_rgb_label.set_halign(Gtk.Align.START)
        bg_box.append(self.bg_rgb_label)
        
        bg_frame.set_child(bg_box)
        self.append(bg_frame)
        
        # Preview and code
        preview_frame = Gtk.Frame(label="Preview")
        preview_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        preview_box.set_margin_start(6)
        preview_box.set_margin_end(6)
        preview_box.set_margin_top(6)
        preview_box.set_margin_bottom(6)
        
        # Color code entry
        self.code_entry = Gtk.Entry()
        self.code_entry.set_placeholder_text("Color code (e.g., 01;31)")
        self.code_entry.connect("changed", self.on_code_entry_changed)
        preview_box.append(self.code_entry)
        
        # Preview label
        self.preview_label = Gtk.Label(label="Sample Text")
        self.preview_label.set_margin_top(6)
        self.preview_label.set_margin_bottom(6)
        preview_box.append(self.preview_label)
        
        preview_frame.set_child(preview_box)
        self.append(preview_frame)
        
        # Action buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_halign(Gtk.Align.CENTER)
        
        self.apply_button = Gtk.Button(label="Apply")
        self.apply_button.connect("clicked", self.on_apply)
        self.apply_button.add_css_class("suggested-action")
        button_box.append(self.apply_button)
        
        self.reset_button = Gtk.Button(label="Reset")
        self.reset_button.connect("clicked", self.on_reset)
        button_box.append(self.reset_button)
        
        self.append(button_box)
        
    def set_color_code(self, color_code: str):
        """Set the color code to edit."""
        print(f"DEBUG ColorEditor: set_color_code called with: '{color_code}'")
        self.updating = True
        
        self.color_info = parse_color_code(color_code)
        print(f"DEBUG ColorEditor: Parsed color info - styles: {[s.name for s in self.color_info.styles]}, fg: {self.color_info.foreground}, bg: {self.color_info.background}")
        
        # Update mode
        if self.color_info.mode == ColorMode.BASIC_8:
            self.mode_basic.set_active(True)
        elif self.color_info.mode == ColorMode.EXTENDED_256:
            self.mode_256.set_active(True)
        else:
            self.mode_rgb.set_active(True)
            
        # Update styles
        self.style_bold.set_active(Style.BOLD in self.color_info.styles)
        self.style_dim.set_active(Style.DIM in self.color_info.styles)
        self.style_italic.set_active(Style.ITALIC in self.color_info.styles)
        self.style_underline.set_active(Style.UNDERLINE in self.color_info.styles)
        self.style_blink.set_active(Style.BLINK in self.color_info.styles)
        self.style_reverse.set_active(Style.REVERSE in self.color_info.styles)
        
        # Update colors
        if self.color_info.foreground:
            rgba = Gdk.RGBA()
            r, g, b = self.color_info.foreground
            rgba.red = r / 255.0
            rgba.green = g / 255.0
            rgba.blue = b / 255.0
            rgba.alpha = 1.0
            self.fg_color_button.set_rgba(rgba)
            self.fg_color_button.set_sensitive(True)
            self.fg_rgb_label.set_text(f"RGB: {self.color_info.foreground}")
        else:
            # Set to a default grey and disable
            rgba = Gdk.RGBA()
            rgba.red = rgba.green = rgba.blue = 0.5
            rgba.alpha = 1.0
            self.fg_color_button.set_rgba(rgba)
            self.fg_color_button.set_sensitive(False)
            self.fg_rgb_label.set_text("RGB: (none)")
            
        if self.color_info.background:
            rgba = Gdk.RGBA()
            r, g, b = self.color_info.background
            rgba.red = r / 255.0
            rgba.green = g / 255.0
            rgba.blue = b / 255.0
            rgba.alpha = 1.0
            self.bg_color_button.set_rgba(rgba)
            self.bg_color_button.set_sensitive(True)
            self.bg_rgb_label.set_text(f"RGB: {self.color_info.background}")
        else:
            # Set to a default grey and disable
            rgba = Gdk.RGBA()
            rgba.red = rgba.green = rgba.blue = 0.5
            rgba.alpha = 1.0
            self.bg_color_button.set_rgba(rgba)
            self.bg_color_button.set_sensitive(False)
            self.bg_rgb_label.set_text("RGB: (none)")
            
        # Update code entry
        self.code_entry.set_text(color_code)
        print(f"DEBUG ColorEditor: Set code entry text to: '{color_code}'")
        
        # Update preview
        self.update_preview()
        print("DEBUG ColorEditor: Preview updated")
        
        self.updating = False
        print("DEBUG ColorEditor: set_color_code complete")
        
    def clear(self):
        """Clear the editor."""
        self.updating = True
        
        self.color_info = None
        
        # Reset all controls
        self.mode_basic.set_active(True)
        
        for style_check in [self.style_bold, self.style_dim, self.style_italic,
                           self.style_underline, self.style_blink, self.style_reverse]:
            style_check.set_active(False)
            
        self.code_entry.set_text("")
        self.fg_rgb_label.set_text("RGB: (none)")
        self.bg_rgb_label.set_text("RGB: (none)")
        
        # Set color buttons to grey and disabled
        rgba = Gdk.RGBA()
        rgba.red = rgba.green = rgba.blue = 0.5
        rgba.alpha = 1.0
        self.fg_color_button.set_rgba(rgba)
        self.fg_color_button.set_sensitive(False)
        self.bg_color_button.set_rgba(rgba)
        self.bg_color_button.set_sensitive(False)
        
        # Clear preview
        self.preview_label.set_markup("Sample Text")
        
        self.updating = False
        
    def get_current_styles(self) -> List[Style]:
        """Get currently selected styles."""
        styles = []
        if self.style_bold.get_active():
            styles.append(Style.BOLD)
        if self.style_dim.get_active():
            styles.append(Style.DIM)
        if self.style_italic.get_active():
            styles.append(Style.ITALIC)
        if self.style_underline.get_active():
            styles.append(Style.UNDERLINE)
        if self.style_blink.get_active():
            styles.append(Style.BLINK)
        if self.style_reverse.get_active():
            styles.append(Style.REVERSE)
        return styles
        
    def get_current_mode(self) -> ColorMode:
        """Get currently selected color mode."""
        if self.mode_256.get_active():
            return ColorMode.EXTENDED_256
        elif self.mode_rgb.get_active():
            return ColorMode.RGB_TRUECOLOR
        else:
            return ColorMode.BASIC_8
            
    def rebuild_color_code(self):
        """Rebuild color code from current settings."""
        if self.updating:
            return
            
        styles = self.get_current_styles()
        mode = self.get_current_mode()
        
        # Get colors from color buttons
        fg_rgba = self.fg_color_button.get_rgba()
        bg_rgba = self.bg_color_button.get_rgba()
        
        fg_rgb = (
            int(fg_rgba.red * 255),
            int(fg_rgba.green * 255),
            int(fg_rgba.blue * 255)
        ) if self.color_info and self.color_info.foreground else None
        
        bg_rgb = (
            int(bg_rgba.red * 255),
            int(bg_rgba.green * 255),
            int(bg_rgba.blue * 255)
        ) if self.color_info and self.color_info.background else None
        
        # Build new color code
        new_code = build_color_code(fg_rgb, bg_rgb, styles, mode)
        
        self.updating = True
        self.code_entry.set_text(new_code)
        self.updating = False
        
        self.update_preview()
        
    def update_preview(self):
        """Update the preview display."""
        code = self.code_entry.get_text()
        if code:
            # Create markup with ANSI-style formatting
            markup = f'<span font_family="monospace">{code}</span>\n'
            markup += '<span font_family="monospace">Sample Text</span>'
            self.preview_label.set_markup(markup)
        else:
            self.preview_label.set_markup('<span font_family="monospace">Sample Text</span>')
            
    def on_mode_changed(self, button):
        """Handle color mode changes."""
        if button.get_active():
            self.rebuild_color_code()
            
    def on_style_changed(self, button):
        """Handle style changes."""
        self.rebuild_color_code()
        
    def on_fg_color_changed(self, button):
        """Handle foreground color changes."""
        if self.updating:
            return
            
        rgba = button.get_rgba()
        rgb = (
            int(rgba.red * 255),
            int(rgba.green * 255),
            int(rgba.blue * 255)
        )
        
        if not self.color_info:
            self.color_info = parse_color_code("")
        self.color_info.foreground = rgb
        
        self.fg_rgb_label.set_text(f"RGB: {rgb}")
        self.rebuild_color_code()
        
    def on_bg_color_changed(self, button):
        """Handle background color changes."""
        if self.updating:
            return
            
        rgba = button.get_rgba()
        rgb = (
            int(rgba.red * 255),
            int(rgba.green * 255),
            int(rgba.blue * 255)
        )
        
        if not self.color_info:
            self.color_info = parse_color_code("")
        self.color_info.background = rgb
        
        self.bg_rgb_label.set_text(f"RGB: {rgb}")
        self.rebuild_color_code()
        
    def on_fg_clear(self, button):
        """Clear foreground color."""
        if self.color_info:
            self.color_info.foreground = None
        self.fg_rgb_label.set_text("RGB: (none)")
        self.rebuild_color_code()
        
    def on_bg_clear(self, button):
        """Clear background color."""
        if self.color_info:
            self.color_info.background = None
        self.bg_rgb_label.set_text("RGB: (none)")
        self.rebuild_color_code()
        
    def on_code_entry_changed(self, entry):
        """Handle manual code entry changes."""
        if self.updating:
            return
            
        code = entry.get_text()
        try:
            # Parse and update UI
            self.set_color_code(code)
        except:
            # Invalid code, just update preview
            self.update_preview()
            
    def on_apply(self, button):
        """Apply the current color code."""
        code = self.code_entry.get_text()
        self.emit('color-changed', code)
        
    def on_reset(self, button):
        """Reset to original color code."""
        if self.color_info:
            self.set_color_code(self.color_info.original_code)