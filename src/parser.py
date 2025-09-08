#!/usr/bin/env python3

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ColorEntry:
    """Represents a single color configuration entry."""
    file_type: str
    color_code: str
    comment: Optional[str] = None
    
    def __post_init__(self):
        """Validate and normalize the color code."""
        self.color_code = self.color_code.strip()
        if self.comment:
            self.comment = self.comment.strip()

class DirColorsParser:
    """Parser for .dircolors configuration files."""
    
    # File type categories for organization
    FILE_TYPES = {
        'directories': ['DIR'],
        'links': ['LINK', 'ORPHAN', 'MISSING'],
        'special': ['FIFO', 'SOCK', 'DOOR', 'BLK', 'CHR'],
        'executables': ['EXEC'],
        'permissions': ['SETUID', 'SETGID', 'CAPABILITY', 'STICKY', 'OTHER_WRITABLE', 'STICKY_OTHER_WRITABLE'],
        'basic': ['NORMAL', 'FILE', 'RESET', 'MULTIHARDLINK']
    }
    
    # File extension categories
    EXTENSION_CATEGORIES = {
        'archives': ['.tar', '.tgz', '.zip', '.gz', '.bz2', '.xz', '.7z', '.rar'],
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.md', '.rtf'],
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff'],
        'audio': ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'],
        'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.webm'],
        'code': ['.py', '.js', '.html', '.css', '.c', '.cpp', '.java', '.php'],
        'config': ['.conf', '.cfg', '.ini', '.yaml', '.yml', '.json']
    }
    
    def __init__(self):
        self.entries: Dict[str, ColorEntry] = {}
        self.terminal_types: List[str] = []
        self.comments: List[str] = []
        
    def infer_categories_from_file(self) -> None:
        """Infer extension categories based on how they're organized in the file."""
        # Reset to original categories first
        self.EXTENSION_CATEGORIES = {
            'archives': ['.tar', '.tgz', '.zip', '.gz', '.bz2', '.xz', '.7z', '.rar'],
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.md', '.rtf'],
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff'],
            'audio': ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'],
            'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.webm'],
            'code': ['.py', '.js', '.html', '.css', '.c', '.cpp', '.java', '.php'],
            'config': ['.conf', '.cfg', '.ini', '.yaml', '.yml', '.json']
        }
        
        # Now read through the entries and detect patterns by comment sections
        current_category = None
        
        # Parse the file content to detect category sections
        if hasattr(self, '_file_lines'):
            for line in self._file_lines:
                line = line.strip()
                if line.startswith('#') and 'files' in line.lower():
                    # Try to detect category from comment
                    if 'archive' in line.lower():
                        current_category = 'archives'
                    elif 'document' in line.lower():
                        current_category = 'documents'
                    elif 'image' in line.lower():
                        current_category = 'images'
                    elif 'audio' in line.lower():
                        current_category = 'audio'
                    elif 'video' in line.lower():
                        current_category = 'video'
                    elif 'code' in line.lower():
                        current_category = 'code'
                    elif 'config' in line.lower():
                        current_category = 'config'
                    else:
                        current_category = None
                        
                elif line and not line.startswith('#') and current_category:
                    # This is an extension line under a category
                    parts = line.split()
                    if len(parts) >= 2 and parts[0].startswith('.'):
                        extension = parts[0]
                        # Remove from other categories first
                        for cat_list in self.EXTENSION_CATEGORIES.values():
                            if extension in cat_list:
                                cat_list.remove(extension)
                        # Add to current category
                        if extension not in self.EXTENSION_CATEGORIES[current_category]:
                            self.EXTENSION_CATEGORIES[current_category].append(extension)
    
    def parse_file(self, filepath: Path) -> None:
        """Parse a .dircolors file."""
        self.entries.clear()
        self.terminal_types.clear()
        self.comments.clear()
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except (IOError, UnicodeDecodeError) as e:
            raise ValueError(f"Could not read file {filepath}: {e}")
            
        # Store lines for category inference
        self._file_lines = [line.rstrip('\n\r') for line in lines]
        
        for line_num, line in enumerate(lines, 1):
            try:
                self._parse_line(line.rstrip('\n\r'))
            except Exception as e:
                print(f"Warning: Error parsing line {line_num}: {e}")
                
        # Infer categories from the file structure after parsing
        self.infer_categories_from_file()
                
    def _parse_line(self, line: str) -> None:
        """Parse a single line from the .dircolors file."""
        # Remove leading/trailing whitespace
        line = line.strip()
        
        # Skip empty lines
        if not line:
            return
            
        # Handle full-line comments
        if line.startswith('#'):
            self.comments.append(line)
            return
            
        # Split line and comment
        if '#' in line:
            line_part, comment = line.split('#', 1)
            line_part = line_part.strip()
            comment = comment.strip()
        else:
            line_part = line
            comment = None
            
        if not line_part:
            return
            
        # Parse terminal type definitions
        if line_part.startswith('TERM '):
            term_type = line_part[5:].strip()
            if term_type:
                self.terminal_types.append(term_type)
            return
            
        # Parse color definitions
        # Format: TYPE color_code or *.ext color_code
        parts = line_part.split()
        if len(parts) >= 2:
            file_type = parts[0]
            color_code = ' '.join(parts[1:])  # Handle multi-part color codes
            
            self.entries[file_type] = ColorEntry(
                file_type=file_type,
                color_code=color_code,
                comment=comment
            )
            
    def write_file(self, filepath: Path) -> None:
        """Write the configuration to a .dircolors file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Write header comments
                f.write("# Configuration file for dircolors\n")
                f.write("# Generated by Dircolor Editor\n\n")
                
                # Write terminal types
                if self.terminal_types:
                    f.write("# Terminal type definitions\n")
                    for term_type in self.terminal_types:
                        f.write(f"TERM {term_type}\n")
                    f.write("\n")
                
                # Write file type definitions (basic types first)
                f.write("# Basic file types\n")
                for file_type in self.FILE_TYPES['basic']:
                    if file_type in self.entries:
                        entry = self.entries[file_type]
                        self._write_entry(f, entry)
                f.write("\n")
                
                # Write directory and link types
                f.write("# Directories and links\n")
                for category in ['directories', 'links']:
                    for file_type in self.FILE_TYPES[category]:
                        if file_type in self.entries:
                            entry = self.entries[file_type]
                            self._write_entry(f, entry)
                f.write("\n")
                
                # Write special file types
                f.write("# Special file types\n")
                for category in ['special', 'executables', 'permissions']:
                    for file_type in self.FILE_TYPES[category]:
                        if file_type in self.entries:
                            entry = self.entries[file_type]
                            self._write_entry(f, entry)
                f.write("\n")
                
                # Write file extensions by category
                for category_name, extensions in self.EXTENSION_CATEGORIES.items():
                    category_entries = []
                    for ext in extensions:
                        if ext in self.entries:
                            category_entries.append(self.entries[ext])
                    
                    if category_entries:
                        f.write(f"# {category_name.title()} files\n")
                        for entry in category_entries:
                            self._write_entry(f, entry)
                        f.write("\n")
                
                # Write remaining extensions (uncategorized)
                remaining = []
                for file_type, entry in self.entries.items():
                    if file_type.startswith('.') and not self._is_categorized(file_type):
                        remaining.append(entry)
                
                if remaining:
                    f.write("# Other file extensions\n")
                    for entry in sorted(remaining, key=lambda x: x.file_type):
                        self._write_entry(f, entry)
                        
        except IOError as e:
            raise ValueError(f"Could not write to file {filepath}: {e}")
            
    def _write_entry(self, f, entry: ColorEntry) -> None:
        """Write a single color entry to the file."""
        if entry.comment:
            f.write(f"{entry.file_type} {entry.color_code} # {entry.comment}\n")
        else:
            f.write(f"{entry.file_type} {entry.color_code}\n")
            
    def _is_categorized(self, extension: str) -> bool:
        """Check if an extension is already categorized."""
        for extensions in self.EXTENSION_CATEGORIES.values():
            if extension in extensions:
                return True
        return False
        
    def get_entry(self, file_type: str) -> Optional[ColorEntry]:
        """Get a color entry by file type."""
        return self.entries.get(file_type)
        
    def set_entry(self, file_type: str, color_code: str, comment: Optional[str] = None) -> None:
        """Set or update a color entry."""
        self.entries[file_type] = ColorEntry(
            file_type=file_type,
            color_code=color_code,
            comment=comment
        )
        
    def remove_entry(self, file_type: str) -> bool:
        """Remove a color entry. Returns True if entry existed."""
        return self.entries.pop(file_type, None) is not None
        
    def move_extension_to_category(self, extension: str, target_category: str) -> bool:
        """Move an extension to a different category."""
        print(f"DEBUG Parser: *** MOVE_EXTENSION_TO_CATEGORY: '{extension}' to '{target_category}' ***")
        
        if not extension.startswith('.'):
            print(f"DEBUG Parser: Extension doesn't start with dot: {extension}")
            return False
            
        # Get the current entry
        entry = self.get_entry(extension)
        if not entry:
            print(f"DEBUG Parser: No entry found for extension: {extension}")
            return False
            
        print(f"DEBUG Parser: Found entry for {extension}: {entry.color_code}")
        
        # Remove from current category if it exists in predefined categories
        found_in_category = None
        for category_name, extensions in self.EXTENSION_CATEGORIES.items():
            if extension in extensions:
                print(f"DEBUG Parser: Found {extension} in category {category_name}, removing...")
                extensions.remove(extension)
                found_in_category = category_name
                break
                
        if found_in_category:
            print(f"DEBUG Parser: Removed {extension} from {found_in_category}")
        else:
            print(f"DEBUG Parser: Extension {extension} was not in any predefined category")
                
        # Add to target category if it exists
        if target_category in self.EXTENSION_CATEGORIES:
            if extension not in self.EXTENSION_CATEGORIES[target_category]:
                self.EXTENSION_CATEGORIES[target_category].append(extension)
                print(f"DEBUG Parser: Added {extension} to {target_category}")
                return True
            else:
                print(f"DEBUG Parser: Extension {extension} already in {target_category}")
                return True
        elif target_category == 'other':
            # Handle 'other' category - just remove from predefined categories
            print(f"DEBUG Parser: Moved {extension} to 'other' category")
            return True
        else:
            print(f"DEBUG Parser: Unknown target category: {target_category}")
            
        return False
        
    def get_categories(self) -> Dict[str, List[str]]:
        """Get file types organized by categories."""
        categories = {}
        
        # Built-in file types
        for category, file_types in self.FILE_TYPES.items():
            existing = [ft for ft in file_types if ft in self.entries]
            if existing:
                categories[category] = existing
                
        # File extensions - organize by current EXTENSION_CATEGORIES state
        for category, extensions in self.EXTENSION_CATEGORIES.items():
            existing = [ext for ext in extensions if ext in self.entries]
            if existing:
                categories[f"{category}_extensions"] = existing
                
        # Uncategorized extensions - anything not in current EXTENSION_CATEGORIES
        uncategorized = []
        for file_type in self.entries:
            if file_type.startswith('.') and not self._is_categorized(file_type):
                uncategorized.append(file_type)
        if uncategorized:
            categories['other_extensions'] = sorted(uncategorized)
            
        return categories

# Utility functions
def load_default_dircolors() -> DirColorsParser:
    """Load the system default dircolors configuration."""
    import subprocess
    
    parser = DirColorsParser()
    
    try:
        # Get default dircolors database
        result = subprocess.run(['dircolors', '--print-database'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                parser._parse_line(line)
    except (subprocess.SubprocessError, FileNotFoundError):
        # Fallback to basic defaults if dircolors command fails
        parser.set_entry('DIR', '01;34')
        parser.set_entry('LINK', '01;36')
        parser.set_entry('EXEC', '01;32')
        
    return parser

def validate_color_code(color_code: str) -> Tuple[bool, str]:
    """
    Validate a color code string.
    Returns (is_valid, error_message).
    """
    if not color_code or not color_code.strip():
        return False, "Color code cannot be empty"
        
    code = color_code.strip()
    
    # Check for valid ANSI color code format
    # Basic format: numbers separated by semicolons
    if not re.match(r'^[\d;]+$', code):
        return False, "Color code must contain only digits and semicolons"
        
    # Split into components
    parts = code.split(';')
    
    for part in parts:
        if not part.isdigit():
            return False, f"Invalid color component: {part}"
            
        num = int(part)
        
        # Basic validation of common ranges
        if num < 0 or num > 255:
            return False, f"Color value {num} out of range (0-255)"
            
    return True, ""