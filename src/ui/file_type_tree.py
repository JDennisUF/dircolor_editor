#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, GObject, Gdk
from typing import Optional
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from parser import DirColorsParser

class FileTypeTreeView(Gtk.ScrolledWindow):
    """Tree view for displaying file types and extensions."""
    
    __gsignals__ = {
        'selection-changed': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'extension-moved': (GObject.SIGNAL_RUN_FIRST, None, (str, str)),
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
        
        # Enable drag and drop for GTK4
        self.setup_drag_and_drop()
        
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
        
        # Right-click context menu
        gesture = Gtk.GestureClick()
        gesture.set_button(3)  # Right mouse button
        gesture.connect("pressed", self.on_right_click)
        self.tree_view.add_controller(gesture)
        
        self.set_child(self.tree_view)
        
        # Track expansion state
        self.expanded_paths = set()
        
        # Icon mappings
        self.setup_icon_mappings()
        
    def setup_icon_mappings(self):
        """Set up icon mappings for different file types."""
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
        
    def setup_drag_and_drop(self):
        """Set up drag and drop functionality for GTK4."""
        # For now, let's disable drag-and-drop and add it as a menu option instead
        # GTK4 drag-and-drop is complex and needs more testing
        
        # TODO: Implement working GTK4 drag-and-drop
        # The current implementation has event handling issues
        print("DEBUG: Drag-and-drop temporarily disabled, use context menu instead")
        
    def on_right_click(self, gesture, n_press, x, y):
        """Handle right-click for context menu."""
        print(f"DEBUG: Right-click at coordinates ({x}, {y})")
        
        # Instead of using click coordinates, use the currently selected item
        # This is more reliable than coordinate detection
        selection = self.tree_view.get_selection()
        model, tree_iter = selection.get_selected()
        
        if not tree_iter:
            print("DEBUG: No item selected")
            return
            
        display_name = model[tree_iter][0]  # display_name column
        file_type = model[tree_iter][1]     # file_type column  
        is_category = model[tree_iter][3]   # is_category column
        
        print(f"DEBUG: Selected item details - display_name: '{display_name}', file_type: '{file_type}', is_category: {is_category}")
        
        # Only show menu for file extensions (not categories)
        if not file_type or is_category or not file_type.startswith('.'):
            print(f"DEBUG: Not showing menu - file_type: '{file_type}', is_category: {is_category}")
            return
            
        print(f"DEBUG: Right-click on extension: {file_type}")
        self.show_move_menu(file_type, x, y)
        
    def show_move_menu(self, extension, x, y):
        """Show context menu to move extension to different category."""
        # Create popover menu
        popover = Gtk.PopoverMenu()
        
        # Create menu model
        from gi.repository import Gio
        menu_model = Gio.Menu()
        
        # Add move options
        categories = ['archives', 'documents', 'images', 'audio', 'video', 'code', 'config', 'other']
        
        for category in categories:
            menu_model.append(f"Move to {category.title()}", f"move.{category}")
            
        popover.set_menu_model(menu_model)
        popover.set_parent(self.tree_view)
        
        # Store the extension for the action handlers
        self.context_extension = extension
        
        # Create action group for move actions
        action_group = Gio.SimpleActionGroup()
        
        for category in categories:
            action = Gio.SimpleAction.new(category, None)
            action.connect("activate", lambda a, p, cat=category: self.move_extension_to_category(extension, cat))
            action_group.add_action(action)
            
        popover.insert_action_group("move", action_group)
        
        # Position and show
        rect = Gdk.Rectangle()
        rect.x = int(x)
        rect.y = int(y)
        rect.width = 1
        rect.height = 1
        popover.set_pointing_to(rect)
        popover.popup()
        
    def move_extension_to_category(self, extension, category):
        """Move extension to specified category."""
        print(f"DEBUG: *** MOVING EXTENSION: '{extension}' to category '{category}' ***")
        self.emit('extension-moved', extension, category)
        
    def on_drag_begin(self, source, drag):
        """Handle drag begin."""
        print(f"DEBUG: Drag begin - {getattr(self, 'dragged_extension', 'unknown')}")
        
    def on_drag_end(self, source, drag, delete_data):
        """Handle drag end."""
        print(f"DEBUG: Drag end")
        if hasattr(self, 'dragged_extension'):
            delattr(self, 'dragged_extension')
            
    def on_drag_enter(self, target, x, y):
        """Handle drag enter."""
        print(f"DEBUG: Drag enter at {x}, {y}")
        # Highlight valid drop targets
        path_info = self.tree_view.get_path_at_pos(int(x), int(y))
        if path_info:
            path, column, cell_x, cell_y = path_info
            tree_iter = self.store.get_iter(path)
            is_category = self.store[tree_iter][3]
            
            print(f"DEBUG: Drag over {'category' if is_category else 'item'}")
            
            if is_category:
                # Valid drop target - add visual feedback
                self.tree_view.set_drag_dest_row(path, Gtk.TreeViewDropPosition.INTO_OR_AFTER)
                return Gdk.DragAction.MOVE
                
        return 0  # No action
        
    def on_drag_leave(self, target):
        """Handle drag leave."""
        # Remove visual feedback
        self.tree_view.set_drag_dest_row(None, Gtk.TreeViewDropPosition.INTO_OR_AFTER)
        
    def on_drop(self, target, value, x, y):
        """Handle drop operation."""
        # Clear visual feedback first
        self.tree_view.set_drag_dest_row(None, Gtk.TreeViewDropPosition.INTO_OR_AFTER)
        
        if not hasattr(self, 'dragged_extension'):
            return False
            
        dragged_ext = self.dragged_extension
        print(f"DEBUG: Drop received for {dragged_ext}")
        
        # Find the drop target
        path_info = self.tree_view.get_path_at_pos(int(x), int(y))
        if not path_info:
            print("DEBUG: No drop target found")
            return False
            
        path, column, cell_x, cell_y = path_info
        tree_iter = self.store.get_iter(path)
        
        target_file_type = self.store[tree_iter][1]
        target_is_category = self.store[tree_iter][3]
        
        # Only allow dropping on categories
        if not target_is_category:
            return False
            
        print(f"DEBUG: Dropping {dragged_ext} on category at path {path}")
        
        # Find which category this represents
        target_category = self.get_category_from_path(path)
        if target_category:
            self.emit('extension-moved', dragged_ext, target_category)
            return True
            
        return False
        
    def get_category_from_path(self, path):
        """Get the category name from a tree path."""
        # Map tree positions to category names
        # This is a simplified approach - in a real implementation you'd want
        # to store category info in the tree model
        
        if len(path.get_indices()) == 1:
            # Top level category
            index = path.get_indices()[0]
            if index == 0:
                return None  # File System Objects - not for extensions
            elif index == 1:
                return None  # File Extensions parent - not specific
        elif len(path.get_indices()) == 2:
            # Sub-category under File Extensions
            parent_index = path.get_indices()[0]
            child_index = path.get_indices()[1]
            
            if parent_index == 1:  # File Extensions
                categories = ['archives', 'documents', 'images', 'audio', 'video', 'code', 'config']
                if child_index < len(categories):
                    return categories[child_index]
                    
        return 'other'  # Default category
        
    def update_data(self, parser: DirColorsParser):
        """Update the tree view with data from parser."""
        # Save current expansion state
        self.save_expansion_state()
        
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
        
        # Restore previous expansion state
        self.restore_expansion_state()
        
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
        
    def save_expansion_state(self):
        """Save the current expansion state of the tree."""
        self.expanded_paths.clear()
        
        def save_expanded_row(tree_view, path, user_data):
            # Convert path to string representation for storage
            path_str = path.to_string()
            self.expanded_paths.add(path_str)
            return False  # Continue traversal
            
        self.tree_view.map_expanded_rows(save_expanded_row, None)
        
    def restore_expansion_state(self):
        """Restore the previously saved expansion state."""
        for path_str in self.expanded_paths:
            try:
                path = Gtk.TreePath.new_from_string(path_str)
                self.tree_view.expand_to_path(path)
            except:
                # Path might not be valid anymore, skip it
                pass
        
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