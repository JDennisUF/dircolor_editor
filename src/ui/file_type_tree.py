#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, GObject
from typing import Optional
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from parser import DirColorsParser

class FileTypeTreeView(Gtk.ScrolledWindow):
    """Tree view for displaying file types and extensions."""
    
    __gsignals__ = {
        'selection-changed': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    }
    
    def __init__(self):
        super().__init__()
        
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.set_vexpand(True)
        
        # Create tree store: [display_name, file_type, icon_name, is_category]
        self.store = Gtk.TreeStore(str, str, str, bool)
        
        # Create tree view
        self.tree_view = Gtk.TreeView(model=self.store)
        self.tree_view.set_headers_visible(True)
        self.tree_view.set_enable_tree_lines(True)
        
        # Create columns
        column = Gtk.TreeViewColumn("File Types")
        
        # Icon renderer
        icon_renderer = Gtk.CellRendererPixbuf()
        column.pack_start(icon_renderer, False)
        column.add_attribute(icon_renderer, "icon-name", 2)
        
        # Text renderer
        text_renderer = Gtk.CellRendererText()
        column.pack_start(text_renderer, True)
        column.add_attribute(text_renderer, "text", 0)
        
        self.tree_view.append_column(column)
        
        # Selection handling
        selection = self.tree_view.get_selection()
        selection.set_mode(Gtk.SelectionMode.SINGLE)
        selection.connect("changed", self.on_selection_changed)
        
        self.set_child(self.tree_view)
        
        # Category icons mapping
        self.category_icons = {
            'File System Objects': 'folder-symbolic',
            'Directories': 'folder-symbolic',
            'Links': 'emblem-symbolic-link',
            'Special Files': 'applications-system-symbolic',
            'Executables': 'application-x-executable',
            'Permissions': 'security-high-symbolic',
            'Basic Types': 'text-x-generic-symbolic',
            'File Extensions': 'document-properties-symbolic',
            'Archives': 'package-x-generic',
            'Documents': 'x-office-document',
            'Images': 'image-x-generic',
            'Audio': 'audio-x-generic',
            'Video': 'video-x-generic',
            'Code': 'text-x-script',
            'Config': 'preferences-system-symbolic',
            'Other': 'text-x-generic-symbolic'
        }
        
        # File type icons
        self.file_type_icons = {
            'DIR': 'folder-symbolic',
            'LINK': 'emblem-symbolic-link',
            'ORPHAN': 'emblem-important-symbolic',
            'EXEC': 'application-x-executable',
            'FIFO': 'preferences-system-symbolic',
            'SOCK': 'network-workgroup-symbolic',
            'BLK': 'drive-harddisk-symbolic',
            'CHR': 'input-keyboard-symbolic',
            'SETUID': 'security-high-symbolic',
            'SETGID': 'security-medium-symbolic'
        }
        
    def update_data(self, parser: DirColorsParser):
        """Update the tree view with data from parser."""
        self.store.clear()
        
        # Get categorized file types
        categories = parser.get_categories()
        
        # Add file system objects
        fs_iter = self.store.append(None, [
            "File System Objects", "", "folder-symbolic", True
        ])
        
        # Basic file types
        if 'basic' in categories:
            for file_type in categories['basic']:
                icon = self.file_type_icons.get(file_type, 'text-x-generic-symbolic')
                display_name = self._format_file_type_name(file_type)
                self.store.append(fs_iter, [display_name, file_type, icon, False])
        
        # Directories
        if 'directories' in categories:
            for file_type in categories['directories']:
                icon = self.file_type_icons.get(file_type, 'folder-symbolic')
                display_name = self._format_file_type_name(file_type)
                self.store.append(fs_iter, [display_name, file_type, icon, False])
                
        # Links
        if 'links' in categories:
            for file_type in categories['links']:
                icon = self.file_type_icons.get(file_type, 'emblem-symbolic-link')
                display_name = self._format_file_type_name(file_type)
                self.store.append(fs_iter, [display_name, file_type, icon, False])
                
        # Special files
        if 'special' in categories:
            for file_type in categories['special']:
                icon = self.file_type_icons.get(file_type, 'applications-system-symbolic')
                display_name = self._format_file_type_name(file_type)
                self.store.append(fs_iter, [display_name, file_type, icon, False])
                
        # Executables
        if 'executables' in categories:
            for file_type in categories['executables']:
                icon = self.file_type_icons.get(file_type, 'application-x-executable')
                display_name = self._format_file_type_name(file_type)
                self.store.append(fs_iter, [display_name, file_type, icon, False])
                
        # Permissions
        if 'permissions' in categories:
            for file_type in categories['permissions']:
                icon = self.file_type_icons.get(file_type, 'security-high-symbolic')
                display_name = self._format_file_type_name(file_type)
                self.store.append(fs_iter, [display_name, file_type, icon, False])
        
        # File Extensions
        ext_iter = self.store.append(None, [
            "File Extensions", "", "document-properties-symbolic", True
        ])
        
        # Extension categories
        ext_categories = {
            'archives_extensions': ('Archives', 'package-x-generic'),
            'documents_extensions': ('Documents', 'x-office-document'),
            'images_extensions': ('Images', 'image-x-generic'),
            'audio_extensions': ('Audio', 'audio-x-generic'),
            'video_extensions': ('Video', 'video-x-generic'),
            'code_extensions': ('Code', 'text-x-script'),
            'config_extensions': ('Config', 'preferences-system-symbolic'),
            'other_extensions': ('Other', 'text-x-generic-symbolic')
        }
        
        for category_key, (display_name, icon) in ext_categories.items():
            if category_key in categories:
                category_iter = self.store.append(ext_iter, [
                    display_name, "", icon, True
                ])
                
                for extension in sorted(categories[category_key]):
                    ext_icon = self._get_extension_icon(extension)
                    self.store.append(category_iter, [
                        extension, extension, ext_icon, False
                    ])
        
        # Expand file system objects by default
        path = self.store.get_path(fs_iter)
        self.tree_view.expand_row(path, False)
        
    def _format_file_type_name(self, file_type: str) -> str:
        """Format file type name for display."""
        display_names = {
            'DIR': 'Directories',
            'FILE': 'Regular Files',
            'LINK': 'Symbolic Links',
            'ORPHAN': 'Broken Links',
            'MISSING': 'Missing Files',
            'FIFO': 'Named Pipes',
            'SOCK': 'Sockets',
            'DOOR': 'Door Files',
            'BLK': 'Block Devices',
            'CHR': 'Character Devices',
            'EXEC': 'Executable Files',
            'SETUID': 'Setuid Files',
            'SETGID': 'Setgid Files',
            'CAPABILITY': 'Capability Files',
            'STICKY': 'Sticky Directories',
            'OTHER_WRITABLE': 'Other-Writable Dirs',
            'STICKY_OTHER_WRITABLE': 'Sticky+Other-Writable',
            'NORMAL': 'Normal Files',
            'RESET': 'Reset Code',
            'MULTIHARDLINK': 'Multi-Hard Links'
        }
        return display_names.get(file_type, file_type)
        
    def _get_extension_icon(self, extension: str) -> str:
        """Get appropriate icon for file extension."""
        ext_icons = {
            # Archives
            '.tar': 'package-x-generic',
            '.zip': 'package-x-generic', 
            '.gz': 'package-x-generic',
            '.bz2': 'package-x-generic',
            '.7z': 'package-x-generic',
            '.rar': 'package-x-generic',
            
            # Documents
            '.pdf': 'application-pdf',
            '.doc': 'x-office-document',
            '.docx': 'x-office-document',
            '.txt': 'text-x-generic',
            '.md': 'text-x-generic',
            
            # Images
            '.jpg': 'image-x-generic',
            '.png': 'image-x-generic',
            '.gif': 'image-x-generic',
            '.svg': 'image-x-generic',
            '.bmp': 'image-x-generic',
            
            # Audio
            '.mp3': 'audio-x-generic',
            '.wav': 'audio-x-generic',
            '.flac': 'audio-x-generic',
            '.ogg': 'audio-x-generic',
            
            # Video
            '.mp4': 'video-x-generic',
            '.avi': 'video-x-generic',
            '.mkv': 'video-x-generic',
            '.mov': 'video-x-generic',
            
            # Code
            '.py': 'text-x-python',
            '.js': 'text-x-javascript',
            '.html': 'text-html',
            '.css': 'text-css',
            '.c': 'text-x-csrc',
            '.cpp': 'text-x-c++src',
            '.java': 'text-x-java',
            '.php': 'text-x-php',
            
            # Config
            '.conf': 'preferences-system',
            '.cfg': 'preferences-system',
            '.ini': 'preferences-system',
            '.yaml': 'text-x-generic',
            '.json': 'application-json'
        }
        
        return ext_icons.get(extension.lower(), 'text-x-generic-symbolic')
        
    def on_selection_changed(self, selection):
        """Handle tree selection changes."""
        model, tree_iter = selection.get_selected()
        if tree_iter:
            display_name = model[tree_iter][0]  # display_name column
            file_type = model[tree_iter][1]     # file_type column
            is_category = model[tree_iter][3]   # is_category column
            
            print(f"DEBUG Tree: Selected '{display_name}', file_type='{file_type}', is_category={is_category}")
            
            if file_type and not is_category:
                print(f"DEBUG Tree: Emitting selection-changed for: {file_type}")
                self.emit('selection-changed', file_type)
            else:
                print(f"DEBUG Tree: Not emitting (empty file_type or category)")
                
    def get_selected_file_type(self) -> Optional[str]:
        """Get the currently selected file type."""
        selection = self.tree_view.get_selection()
        model, tree_iter = selection.get_selected()
        if tree_iter:
            file_type = model[tree_iter][1]
            is_category = model[tree_iter][3]
            if file_type and not is_category:
                return file_type
        return None