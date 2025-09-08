# Dircolor Editor Project

## Project Overview
A Linux GUI application for editing .dircolors files with visual color selection and live preview.

## Current Understanding

### .dircolors File Format
- Configuration file for GNU `ls` command colors via `LS_COLORS` environment variable
- Located at `~/.dircolors` (user-specific) or `/etc/DIR_COLORS` (system-wide)
- Format: `FILE_TYPE=COLOR_CODE` or `*.extension COLOR_CODE`

### User's Current Configuration
- File location: `/home/jasondennis/.dircolors`
- Custom directory colors: `01;93;48;5;93` (bold yellow text, purple background)
- Extensive file extension mappings organized by category
- Uses both 8-bit and 256-color codes

### Color Code Format
- ANSI escape sequences: `STYLE;FG_COLOR;BG_COLOR`
- Style codes: 00=normal, 01=bold, 04=underline, 05=blink, 07=reverse, 08=concealed
- 8-bit colors: 30-37 (foreground), 40-47 (background)
- 256-color format: `38;5;N` (foreground), `48;5;N` (background)
- RGB format: `38;2;R;G;B` (foreground), `48;2;R;G;B` (background)

## File Types to Support
### Basic Types
- DIR: Directories
- FILE: Regular files  
- LINK: Symbolic links
- ORPHAN: Broken symlinks
- FIFO: Named pipes
- SOCK: Sockets
- DOOR: Door files
- BLK: Block devices
- CHR: Character devices
- EXEC: Executable files

### Special Permission Types
- SETUID: Setuid files
- SETGID: Setgid files
- CAPABILITY: Files with capabilities
- STICKY: Sticky directories
- OTHER_WRITABLE: Other-writable directories
- STICKY_OTHER_WRITABLE: Sticky + other-writable

### File Extensions
Current user config includes:
- Archives: .tar, .zip, .gz, .bz2, etc. (red)
- Documents: .pdf, .docx (blue)
- Text: .txt, .json, .csv, .html, .log, .md (green)
- Images: .jpg, .png, .gif, .svg, etc. (magenta)
- Audio: .mp3, .wav, .flac, etc. (cyan)
- Code: .php, .js, .cs, .ts (bright cyan)

## Technology Stack Considerations

### GUI Framework Options
1. **GTK4 + Python (PyGObject)**
   - Native Linux look/feel
   - Good Pop OS! integration
   - Color picker widgets available
   
2. **Qt6 + Python (PySide6)**  
   - Cross-platform
   - Rich color selection widgets
   - Professional appearance
   
3. **Electron + JavaScript/TypeScript**
   - Web technologies
   - Rich color libraries available
   - Larger footprint

4. **Tauri + Rust + HTML/CSS/JS**
   - Lightweight
   - Native performance
   - Modern web UI

### Recommended: GTK4 + Python
- Best Linux desktop integration
- Native file dialogs
- System theme awareness
- Built-in color chooser widgets

## Planned Features

### Core Features
1. **File Loading/Saving**
   - Load existing .dircolors files
   - Save/export configurations
   - Backup original files
   
2. **Visual Color Editor**
   - Color picker for foreground/background
   - Style toggles (bold, underline, etc.)
   - Live color preview
   
3. **File Type Management**
   - List all supported file types
   - Add/remove file extensions
   - Organize by categories
   
4. **Live Preview**
   - Simulated `ls` output preview
   - Real-time updates as colors change
   - Sample files display

### Advanced Features
1. **Color Schemes**
   - Predefined themes (dark, light, high contrast)
   - Import/export color schemes
   - Theme templates
   
2. **Validation**
   - Check terminal compatibility
   - Validate color codes
   - Conflict detection
   
3. **Integration**
   - Apply changes immediately to terminal
   - Generate dircolors command output
   - Test mode with temporary application

## Architecture Plan

### Main Components
1. **Configuration Parser**
   - Parse .dircolors file format
   - Handle comments and terminal compatibility
   - Validate color codes
   
2. **Color Management**
   - Color code conversion (8-bit ↔ 256-color ↔ RGB)
   - Color space utilities
   - Palette management
   
3. **UI Components**
   - Main window with file tree
   - Color picker dialogs
   - Preview panel
   - Menu/toolbar
   
4. **File Operations**
   - Safe file backup/restore
   - Configuration validation
   - Export functionality

### Development Phases
1. **Phase 1: Core Parser & Basic UI**
   - Parse/write .dircolors format
   - Basic GTK application shell
   - Simple color editing
   
2. **Phase 2: Advanced UI & Preview**
   - Rich color picker interface
   - Live preview functionality
   - File type management
   
3. **Phase 3: Polish & Features**
   - Color schemes
   - Import/export
   - Documentation

## Dependencies
- Python 3.8+
- GTK4
- PyGObject (gi)
- Optional: python-magic for file type detection

## File Structure
```
dircolor_editor/
├── src/
│   ├── main.py              # Application entry point
│   ├── parser.py            # .dircolors file parser
│   ├── color_utils.py       # Color conversion utilities
│   ├── ui/
│   │   ├── main_window.py   # Main application window
│   │   ├── color_picker.py  # Color selection widget
│   │   └── preview_panel.py # Live preview widget
│   └── config.py            # Configuration management
├── data/
│   ├── default.dircolors    # Default configuration
│   └── themes/              # Predefined themes
├── tests/
├── requirements.txt
└── setup.py
```

## Detailed UI Design

### Main Window Layout (GTK4 ApplicationWindow)
```
[Menu Bar]
┌─────────────────┬──────────────────┬─────────────────┐
│  File Types     │  Color Editor    │  Live Preview   │
│  (TreeView)     │  (Properties)    │  (Terminal View)│
│                 │                  │                 │
│ 📁 Directories  │ ┌─ Foreground ─┐ │ 📁 Documents    │
│ 🔗 Links        │ │ ████████████ │ │ 📄 file.txt     │
│ ⚙️  Executables │ │ [Color Btn]  │ │ 🗂️  folder      │
│                 │ └──────────────┘ │ 📦 archive.zip  │
│ 📦 Archives     │ ┌─ Background ─┐ │ 🎵 music.mp3    │
│   └ .zip        │ │ ████████████ │ │ 🖼️  image.jpg   │
│   └ .tar        │ │ [Color Btn]  │ │ ⚡ script.sh    │
│   └ .gz         │ └──────────────┘ │                 │
│                 │                  │                 │
│ 🖼️ Images        │ ┌─── Styles ───┐ │                 │
│   └ .jpg        │ │ ☑ Bold       │ │                 │
│   └ .png        │ │ ☐ Underline  │ │                 │
│   └ .gif        │ │ ☐ Blink      │ │                 │
│                 │ │ ☐ Reverse    │ │                 │
│ 🎵 Audio         │ └──────────────┘ │                 │
│ 💻 Code          │                  │                 │
│ + Add Extension │ [Apply] [Reset]  │ [↻ Refresh]     │
└─────────────────┴──────────────────┴─────────────────┘
[Status Bar: "Editing: ~/.dircolors" | "Terminal: gnome-terminal"]
```

### Color Editor Component Details

#### Color Mode Selector
- Radio buttons: "8-bit" | "256-color" | "RGB"
- Auto-detect current mode from selected item
- Convert between modes with visual feedback

#### Color Picker Integration
- GTK ColorChooser for RGB selection
- Custom 256-color palette grid
- 8-bit color dropdown with labels
- Live color preview square
- Color code text entry (e.g., "01;31" or "38;5;196")

#### Style Toggles
- Checkboxes for each style attribute
- Tooltips explaining each style
- Visual preview showing effect

### File Type Tree Organization
```
📂 File System Objects
  📁 Directories (DIR)
  📄 Regular Files (FILE) 
  🔗 Symbolic Links (LINK)
  💔 Broken Links (ORPHAN)
  📡 Named Pipes (FIFO)
  🔌 Sockets (SOCK)
  🚪 Door Files (DOOR)
  🔲 Block Devices (BLK)
  ⚡ Character Devices (CHR)
  🏃 Executable Files (EXEC)

📂 Permission Types
  🔒 Setuid Files (SETUID)
  👥 Setgid Files (SETGID)
  ⚡ Capability Files (CAPABILITY)
  📌 Sticky Directories (STICKY)
  ✍️  Other-Writable (OTHER_WRITABLE)
  📌✍️ Sticky+Other-Writable (STICKY_OTHER_WRITABLE)

📂 File Extensions
  📦 Archives (.tar, .zip, .gz, .bz2, ...)
  📄 Documents (.pdf, .doc, .txt, .md, ...)
  🖼️ Images (.jpg, .png, .gif, .svg, ...)
  🎵 Audio (.mp3, .wav, .flac, .ogg, ...)
  🎬 Video (.mp4, .avi, .mkv, .webm, ...)
  💻 Code (.py, .js, .html, .css, .c, ...)
  ⚙️ Config (.conf, .cfg, .ini, .yaml, ...)
  🗜️ Compressed (.7z, .rar, .ace, .lz4, ...)
```

### Dialogs & Secondary Windows

#### New Extension Dialog
- File extension input (.ext)
- Color/style selection
- Category assignment
- Description field (optional)

#### Import/Export Dialog
- File chooser for .dircolors files
- Format options (standard, with comments, minimal)
- Backup options
- Terminal compatibility warnings

#### Preferences Dialog
- Default backup behavior
- Color picker preferences
- Preview update frequency
- Terminal emulator detection

### Menu Structure
```
File
├── New Configuration
├── Open Configuration...
├── ─────────────
├── Save
├── Save As...
├── ─────────────
├── Import Theme...
├── Export Theme...
├── ─────────────
├── Quit

Edit
├── Undo
├── Redo
├── ─────────────
├── Add Extension...
├── Remove Selected
├── ─────────────
├── Reset to Default
├── ─────────────
├── Preferences...

View
├── Refresh Preview
├── ─────────────
├── Show File Types
├── Show Extensions Only
├── Group by Category
├── ─────────────
├── Zoom In Preview
├── Zoom Out Preview

Tools
├── Apply to Terminal
├── Test Configuration
├── ─────────────
├── Validate Colors
├── Check Compatibility
├── ─────────────
├── Generate Command...

Help
├── User Guide
├── Keyboard Shortcuts
├── ─────────────
├── About
```

### Keyboard Shortcuts
- Ctrl+N: New configuration
- Ctrl+O: Open file
- Ctrl+S: Save
- Ctrl+Z/Y: Undo/Redo
- Delete: Remove selected extension
- F5: Refresh preview
- Ctrl+A: Apply to terminal
- F1: Help

### Status Indicators
- File modification status (●/○)
- Terminal compatibility (✓/⚠)
- Color validation status
- Current file path
- Number of configured extensions

## Error Handling & Validation

### File Operations
- Backup original files before modification
- Validate file permissions before writing
- Handle corrupted .dircolors files gracefully
- Confirm destructive operations

### Color Validation
- Check color code syntax
- Warn about unsupported colors in terminal
- Validate RGB ranges (0-255)
- Check 256-color index bounds (0-255)

### Terminal Compatibility
- Detect terminal emulator capabilities
- Warn about unsupported features
- Provide fallback color suggestions
- Test mode for safe experimentation

## Next Steps
1. Set up Python GTK4 development environment
2. Implement basic .dircolors parser
3. Create minimal GTK application shell
4. Build color picker component
5. Implement tree view for file types
6. Add live preview functionality
7. Create import/export features
8. Add validation and error handling
9. Package for distribution