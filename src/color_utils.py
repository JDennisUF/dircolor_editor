#!/usr/bin/env python3

import re
from typing import Tuple, Optional, Dict, List
from enum import Enum

class ColorMode(Enum):
    """Color mode enumeration."""
    BASIC_8 = "8-bit"
    EXTENDED_256 = "256-color"
    RGB_TRUECOLOR = "RGB"

class Style(Enum):
    """Text style enumeration."""
    NORMAL = 0
    BOLD = 1
    DIM = 2
    ITALIC = 3
    UNDERLINE = 4
    BLINK = 5
    REVERSE = 7
    STRIKETHROUGH = 9

class ColorInfo:
    """Information about a parsed color code."""
    
    def __init__(self, code: str):
        self.original_code = code
        self.styles: List[Style] = []
        self.foreground: Optional[Tuple[int, int, int]] = None
        self.background: Optional[Tuple[int, int, int]] = None
        self.fg_256: Optional[int] = None
        self.bg_256: Optional[int] = None
        self.mode = ColorMode.BASIC_8
        
        self._parse_code(code)
        
    def _parse_code(self, code: str) -> None:
        """Parse an ANSI color code into components."""
        if not code or not code.strip():
            return
            
        # Split by semicolon
        parts = [int(p) for p in code.split(';') if p.isdigit()]
        
        i = 0
        while i < len(parts):
            part = parts[i]
            
            # Style codes
            if part in [0, 1, 2, 3, 4, 5, 7, 9]:
                if part == 0:
                    self.styles.clear()  # Reset
                else:
                    try:
                        self.styles.append(Style(part))
                    except ValueError:
                        pass
                        
            # 8-bit foreground colors (30-37, 90-97)
            elif 30 <= part <= 37:
                self.foreground = self._basic_color_to_rgb(part - 30)
                
            elif 90 <= part <= 97:
                self.foreground = self._basic_color_to_rgb(part - 90, bright=True)
                
            # 8-bit background colors (40-47, 100-107)
            elif 40 <= part <= 47:
                self.background = self._basic_color_to_rgb(part - 40)
                
            elif 100 <= part <= 107:
                self.background = self._basic_color_to_rgb(part - 100, bright=True)
                
            # 256-color or RGB mode
            elif part == 38:  # Foreground
                if i + 2 < len(parts) and parts[i + 1] == 5:
                    # 256-color mode: 38;5;n
                    self.fg_256 = parts[i + 2]
                    self.foreground = self._color_256_to_rgb(parts[i + 2])
                    self.mode = ColorMode.EXTENDED_256
                    i += 2
                elif i + 4 < len(parts) and parts[i + 1] == 2:
                    # RGB mode: 38;2;r;g;b
                    self.foreground = (parts[i + 2], parts[i + 3], parts[i + 4])
                    self.mode = ColorMode.RGB_TRUECOLOR
                    i += 4
                    
            elif part == 48:  # Background
                if i + 2 < len(parts) and parts[i + 1] == 5:
                    # 256-color mode: 48;5;n
                    self.bg_256 = parts[i + 2]
                    self.background = self._color_256_to_rgb(parts[i + 2])
                    self.mode = ColorMode.EXTENDED_256
                    i += 2
                elif i + 4 < len(parts) and parts[i + 1] == 2:
                    # RGB mode: 48;2;r;g;b
                    self.background = (parts[i + 2], parts[i + 3], parts[i + 4])
                    self.mode = ColorMode.RGB_TRUECOLOR
                    i += 4
                    
            i += 1
    
    def _basic_color_to_rgb(self, color_index: int, bright: bool = False) -> Tuple[int, int, int]:
        """Convert basic 8-color index to RGB."""
        basic_colors = [
            (0, 0, 0),       # Black
            (128, 0, 0),     # Red
            (0, 128, 0),     # Green
            (128, 128, 0),   # Yellow
            (0, 0, 128),     # Blue
            (128, 0, 128),   # Magenta
            (0, 128, 128),   # Cyan
            (192, 192, 192), # White
        ]
        
        bright_colors = [
            (128, 128, 128), # Bright Black (Gray)
            (255, 0, 0),     # Bright Red
            (0, 255, 0),     # Bright Green
            (255, 255, 0),   # Bright Yellow
            (0, 0, 255),     # Bright Blue
            (255, 0, 255),   # Bright Magenta
            (0, 255, 255),   # Bright Cyan
            (255, 255, 255), # Bright White
        ]
        
        if 0 <= color_index <= 7:
            return bright_colors[color_index] if bright else basic_colors[color_index]
        return (128, 128, 128)  # Default gray
        
    def _color_256_to_rgb(self, color_index: int) -> Tuple[int, int, int]:
        """Convert 256-color index to RGB."""
        if color_index < 16:
            # Standard colors (0-15)
            if color_index < 8:
                return self._basic_color_to_rgb(color_index, False)
            else:
                return self._basic_color_to_rgb(color_index - 8, True)
                
        elif color_index < 232:
            # 216 color cube (16-231): 6x6x6
            index = color_index - 16
            r = (index // 36) % 6
            g = (index // 6) % 6
            b = index % 6
            
            # Convert 0-5 to 0-255
            def component_to_rgb(c):
                return 0 if c == 0 else 55 + c * 40
                
            return (component_to_rgb(r), component_to_rgb(g), component_to_rgb(b))
            
        else:
            # Grayscale (232-255)
            gray = 8 + (color_index - 232) * 10
            return (gray, gray, gray)

def parse_color_code(code: str) -> ColorInfo:
    """Parse a color code string and return color information."""
    return ColorInfo(code)

def rgb_to_256_color(r: int, g: int, b: int) -> int:
    """Convert RGB values to the closest 256-color index."""
    # Check grayscale first
    if r == g == b:
        if r < 8:
            return 16  # Black
        elif r > 238:
            return 231  # White
        else:
            return 232 + int((r - 8) / 10)
    
    # Convert to 6x6x6 color cube
    def rgb_to_6(val):
        if val < 48:
            return 0
        elif val < 115:
            return 1
        else:
            return int((val - 35) / 40)
    
    r6 = rgb_to_6(r)
    g6 = rgb_to_6(g)
    b6 = rgb_to_6(b)
    
    return 16 + (36 * r6) + (6 * g6) + b6

def color_256_to_rgb(color_index: int) -> Tuple[int, int, int]:
    """Convert 256-color index to RGB."""
    info = ColorInfo(f"38;5;{color_index}")
    return info.foreground or (128, 128, 128)

def build_color_code(foreground_rgb: Optional[Tuple[int, int, int]] = None,
                    background_rgb: Optional[Tuple[int, int, int]] = None,
                    styles: List[Style] = None,
                    mode: ColorMode = ColorMode.RGB_TRUECOLOR) -> str:
    """Build an ANSI color code from RGB values and styles."""
    parts = []
    
    # Add styles
    if styles:
        for style in styles:
            parts.append(str(style.value))
    
    # Add foreground color
    if foreground_rgb:
        r, g, b = foreground_rgb
        if mode == ColorMode.RGB_TRUECOLOR:
            parts.extend(['38', '2', str(r), str(g), str(b)])
        elif mode == ColorMode.EXTENDED_256:
            color_256 = rgb_to_256_color(r, g, b)
            parts.extend(['38', '5', str(color_256)])
        else:  # Basic 8-bit
            # Find closest basic color
            basic_color = _rgb_to_basic_color(r, g, b)
            parts.append(str(basic_color))
    
    # Add background color
    if background_rgb:
        r, g, b = background_rgb
        if mode == ColorMode.RGB_TRUECOLOR:
            parts.extend(['48', '2', str(r), str(g), str(b)])
        elif mode == ColorMode.EXTENDED_256:
            color_256 = rgb_to_256_color(r, g, b)
            parts.extend(['48', '5', str(color_256)])
        else:  # Basic 8-bit
            # Find closest basic color
            basic_color = _rgb_to_basic_color(r, g, b) + 10  # Background offset
            parts.append(str(basic_color))
    
    return ';'.join(parts) if parts else '00'

def _rgb_to_basic_color(r: int, g: int, b: int) -> int:
    """Convert RGB to closest basic 8-color."""
    # Simple distance-based matching
    basic_colors = [
        (0, 0, 0),       # 30 - Black
        (128, 0, 0),     # 31 - Red
        (0, 128, 0),     # 32 - Green
        (128, 128, 0),   # 33 - Yellow
        (0, 0, 128),     # 34 - Blue
        (128, 0, 128),   # 35 - Magenta
        (0, 128, 128),   # 36 - Cyan
        (192, 192, 192), # 37 - White
    ]
    
    bright_colors = [
        (128, 128, 128), # 90 - Bright Black
        (255, 0, 0),     # 91 - Bright Red
        (0, 255, 0),     # 92 - Bright Green
        (255, 255, 0),   # 93 - Bright Yellow
        (0, 0, 255),     # 94 - Bright Blue
        (255, 0, 255),   # 95 - Bright Magenta
        (0, 255, 255),   # 96 - Bright Cyan
        (255, 255, 255), # 97 - Bright White
    ]
    
    def color_distance(c1, c2):
        return sum((a - b) ** 2 for a, b in zip(c1, c2))
    
    # Check basic colors
    min_dist = float('inf')
    best_color = 30
    
    for i, color in enumerate(basic_colors):
        dist = color_distance((r, g, b), color)
        if dist < min_dist:
            min_dist = dist
            best_color = 30 + i
    
    # Check bright colors
    for i, color in enumerate(bright_colors):
        dist = color_distance((r, g, b), color)
        if dist < min_dist:
            min_dist = dist
            best_color = 90 + i
    
    return best_color

def get_color_palette_256() -> List[Tuple[int, int, int]]:
    """Get the full 256-color palette as RGB tuples."""
    palette = []
    
    for i in range(256):
        palette.append(color_256_to_rgb(i))
        
    return palette

def format_color_code_display(code: str) -> str:
    """Format a color code for display with description."""
    info = parse_color_code(code)
    
    parts = []
    
    # Add styles
    if info.styles:
        style_names = []
        for style in info.styles:
            style_names.append(style.name.lower().replace('_', ' '))
        parts.append(f"Styles: {', '.join(style_names)}")
    
    # Add colors
    if info.foreground:
        r, g, b = info.foreground
        parts.append(f"FG: rgb({r}, {g}, {b})")
        
    if info.background:
        r, g, b = info.background
        parts.append(f"BG: rgb({r}, {g}, {b})")
        
    if info.mode != ColorMode.BASIC_8:
        parts.append(f"Mode: {info.mode.value}")
    
    return " | ".join(parts) if parts else "Default"

# Color scheme presets
COLOR_SCHEMES = {
    'default': {
        'DIR': '01;34',
        'LINK': '01;36',
        'EXEC': '01;32',
        '.tar': '01;31',
        '.txt': '00;32'
    },
    'dark_theme': {
        'DIR': '01;94',
        'LINK': '01;96',
        'EXEC': '01;92',
        '.tar': '01;91',
        '.txt': '00;93'
    },
    'high_contrast': {
        'DIR': '01;93;40',
        'LINK': '01;95;40',
        'EXEC': '01;92;40',
        '.tar': '01;91;40',
        '.txt': '01;97;40'
    }
}