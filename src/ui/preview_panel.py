#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Pango
from typing import Dict, List, Tuple
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from parser import DirColorsParser
from color_utils import parse_color_code

class PreviewPanel(Gtk.ScrolledWindow):
    """Preview panel showing simulated terminal output."""
    
    def __init__(self):
        super().__init__()
        
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.set_vexpand(True)
        
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_box.set_margin_start(12)
        main_box.set_margin_end(12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        
        # Title
        title = Gtk.Label(label="Live Preview")
        title.set_markup("<b>Live Preview</b>")
        title.set_halign(Gtk.Align.START)
        main_box.append(title)
        
        # Preview area
        self.preview_text = Gtk.TextView()
        self.preview_text.set_editable(False)
        self.preview_text.set_cursor_visible(False)
        self.preview_text.set_monospace(True)
        self.preview_text.set_wrap_mode(Gtk.WrapMode.NONE)
        
        # Set background color to simulate terminal
        self.preview_text.override_background_color(
            Gtk.StateFlags.NORMAL, 
            Gtk.Gdk.RGBA(0.1, 0.1, 0.1, 1.0)  # Dark background
        )
        
        buffer = self.preview_text.get_buffer()
        
        # Refresh button
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_halign(Gtk.Align.END)
        
        refresh_button = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        refresh_button.set_tooltip_text("Refresh Preview")
        refresh_button.connect("clicked", lambda b: self.refresh_preview())
        button_box.append(refresh_button)
        
        main_box.append(button_box)
        main_box.append(self.preview_text)
        
        self.set_child(main_box)
        
        # Sample files for preview
        self.sample_files = [
            ("📁", "Documents", "DIR"),
            ("📁", "Pictures", "DIR"), 
            ("📁", "Downloads", "DIR"),
            ("📄", "readme.txt", ".txt"),
            ("📄", "config.json", ".json"),
            ("📄", "document.pdf", ".pdf"),
            ("🖼️", "photo.jpg", ".jpg"),
            ("🖼️", "image.png", ".png"),
            ("🎵", "song.mp3", ".mp3"),
            ("🎵", "audio.wav", ".wav"),
            ("🎬", "movie.mp4", ".mp4"),
            ("🎬", "video.avi", ".avi"),
            ("📦", "archive.zip", ".zip"),
            ("📦", "backup.tar.gz", ".tar"),
            ("⚡", "script.py", ".py"),
            ("⚡", "program.js", ".js"),
            ("⚡", "webpage.html", ".html"),
            ("🔗", "link", "LINK"),
            ("💔", "broken_link", "ORPHAN"),
            ("🏃", "executable", "EXEC"),
        ]
        
    def update_preview(self, parser: DirColorsParser):
        """Update the preview with current color configuration."""
        buffer = self.preview_text.get_buffer()
        buffer.delete(buffer.get_start_iter(), buffer.get_end_iter())
        
        # Clear existing tags
        tag_table = buffer.get_tag_table()
        tag_table.foreach(lambda tag, data: tag_table.remove(tag), None)
        
        # Add header
        header_text = "Terminal Color Preview (simulated ls output)\n"
        header_text += "=" * 50 + "\n\n"
        
        iter_start = buffer.get_end_iter()
        buffer.insert(iter_start, header_text)
        
        # Add sample files with colors
        for icon, filename, file_type in self.sample_files:
            # Get color entry for this file type
            entry = parser.get_entry(file_type)
            
            if entry:
                color_info = parse_color_code(entry.color_code)
                
                # Create text tag for this file
                tag = buffer.create_tag()
                
                # Apply foreground color
                if color_info.foreground:
                    r, g, b = color_info.foreground
                    rgba = Gtk.Gdk.RGBA(r/255.0, g/255.0, b/255.0, 1.0)
                    tag.set_property("foreground-rgba", rgba)
                    
                # Apply background color
                if color_info.background:
                    r, g, b = color_info.background
                    rgba = Gtk.Gdk.RGBA(r/255.0, g/255.0, b/255.0, 1.0)
                    tag.set_property("background-rgba", rgba)
                    
                # Apply text styles
                from color_utils import Style
                if Style.BOLD in color_info.styles:
                    tag.set_property("weight", Pango.Weight.BOLD)
                if Style.ITALIC in color_info.styles:
                    tag.set_property("style", Pango.Style.ITALIC)
                if Style.UNDERLINE in color_info.styles:
                    tag.set_property("underline", Pango.Underline.SINGLE)
                    
                # Insert filename with formatting
                text = f"{icon}  {filename}\n"
                iter_start = buffer.get_end_iter()
                iter_end = buffer.get_end_iter()
                buffer.insert(iter_end, text)
                iter_end = buffer.get_end_iter()
                
                # Apply the tag to the inserted text
                buffer.apply_tag(tag, iter_start, iter_end)
            else:
                # No color defined, use default
                text = f"{icon}  {filename}\n"
                iter_start = buffer.get_end_iter()
                buffer.insert(iter_start, text)
                
        # Add color code reference
        buffer.insert(buffer.get_end_iter(), "\n" + "=" * 50 + "\n")
        buffer.insert(buffer.get_end_iter(), "Color Code Reference:\n\n")
        
        # Show active color codes
        for file_type in ["DIR", "LINK", "EXEC"]:
            entry = parser.get_entry(file_type)
            if entry:
                ref_text = f"{file_type:15} = {entry.color_code}\n"
                buffer.insert(buffer.get_end_iter(), ref_text)
                
        # Show some extensions
        for ext in [".txt", ".zip", ".jpg", ".mp3"]:
            entry = parser.get_entry(ext)
            if entry:
                ref_text = f"{ext:15} = {entry.color_code}\n"
                buffer.insert(buffer.get_end_iter(), ref_text)
                
    def refresh_preview(self):
        """Refresh the preview display."""
        # This would be called from the main window with current parser
        pass
        
    def create_color_demonstration(self, parser: DirColorsParser):
        """Create a comprehensive color demonstration."""
        buffer = self.preview_text.get_buffer()
        
        # Add color palette demonstration
        buffer.insert(buffer.get_end_iter(), "\nColor Palette Demo:\n")
        
        # Basic 8 colors
        basic_colors = [
            ("Black", "30"),
            ("Red", "31"),
            ("Green", "32"),
            ("Yellow", "33"),
            ("Blue", "34"),
            ("Magenta", "35"),
            ("Cyan", "36"),
            ("White", "37"),
        ]
        
        for color_name, color_code in basic_colors:
            tag = buffer.create_tag()
            color_info = parse_color_code(color_code)
            
            if color_info.foreground:
                r, g, b = color_info.foreground
                rgba = Gtk.Gdk.RGBA(r/255.0, g/255.0, b/255.0, 1.0)
                tag.set_property("foreground-rgba", rgba)
                
            text = f"■ {color_name} ({color_code})  "
            iter_start = buffer.get_end_iter()
            iter_end = buffer.get_end_iter()
            buffer.insert(iter_end, text)
            iter_end = buffer.get_end_iter()
            buffer.apply_tag(tag, iter_start, iter_end)
            
        buffer.insert(buffer.get_end_iter(), "\n\n")
        
        # Style demonstration
        buffer.insert(buffer.get_end_iter(), "Style Demo:\n")
        
        styles_demo = [
            ("Normal", "00"),
            ("Bold", "01"),
            ("Dim", "02"),
            ("Italic", "03"),
            ("Underline", "04"),
            ("Reverse", "07"),
        ]
        
        for style_name, style_code in styles_demo:
            tag = buffer.create_tag()
            color_info = parse_color_code(style_code)
            
            # Apply styles based on code
            from color_utils import Style
            if Style.BOLD in color_info.styles:
                tag.set_property("weight", Pango.Weight.BOLD)
            if Style.ITALIC in color_info.styles:
                tag.set_property("style", Pango.Style.ITALIC)
            if Style.UNDERLINE in color_info.styles:
                tag.set_property("underline", Pango.Underline.SINGLE)
                
            text = f"{style_name} text ({style_code})\n"
            iter_start = buffer.get_end_iter()
            iter_end = buffer.get_end_iter()
            buffer.insert(iter_end, text)
            iter_end = buffer.get_end_iter()
            buffer.apply_tag(tag, iter_start, iter_end)