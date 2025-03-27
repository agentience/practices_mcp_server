#!/usr/bin/env python
"""
License header templates for different file types.

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.1.0
"""

import os
from typing import Dict, Any, Optional, List

# Default header template
DEFAULT_HEADER = """filename: {filename}
description: {description}

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.1.0
"""

# Header comment style by file extension
COMMENT_STYLES = {
    # Python, Shell, Ruby, etc.
    ".py": {"start": '"""', "middle": "", "end": '"""'},
    ".sh": {"start": "# ", "middle": "# ", "end": "# "},
    ".rb": {"start": "# ", "middle": "# ", "end": "# "},
    
    # C-style
    ".c": {"start": "/*", "middle": " * ", "end": " */"},
    ".h": {"start": "/*", "middle": " * ", "end": " */"},
    ".cpp": {"start": "/*", "middle": " * ", "end": " */"},
    ".hpp": {"start": "/*", "middle": " * ", "end": " */"},
    ".cs": {"start": "/*", "middle": " * ", "end": " */"},
    ".java": {"start": "/*", "middle": " * ", "end": " */"},
    
    # JavaScript/TypeScript
    ".js": {"start": "/**", "middle": " * ", "end": " */"},
    ".jsx": {"start": "/**", "middle": " * ", "end": " */"},
    ".ts": {"start": "/**", "middle": " * ", "end": " */"},
    ".tsx": {"start": "/**", "middle": " * ", "end": " */"},
    
    # Web
    ".html": {"start": "<!--", "middle": "", "end": "-->"},
    ".xml": {"start": "<!--", "middle": "", "end": "-->"},
    ".css": {"start": "/*", "middle": " * ", "end": " */"},
    ".scss": {"start": "/*", "middle": " * ", "end": " */"},
    ".sass": {"start": "/*", "middle": " * ", "end": " */"},
    
    # Config files
    ".yaml": {"start": "# ", "middle": "# ", "end": "# "},
    ".yml": {"start": "# ", "middle": "# ", "end": "# "},
    ".toml": {"start": "# ", "middle": "# ", "end": "# "},
    ".json": {"start": "// ", "middle": "// ", "end": "// "},  # Technically invalid but used in comments
    
    # Others
    ".md": {"start": "<!--", "middle": "", "end": "-->"},
    ".rst": {"start": ".. ", "middle": ".. ", "end": ".. "},
    ".go": {"start": "/*", "middle": " * ", "end": " */"},
    ".rs": {"start": "/*", "middle": " * ", "end": " */"},
    ".swift": {"start": "/*", "middle": " * ", "end": " */"},
}

# Some files need the headers at a specific position (not the top)
SPECIAL_POSITIONS = {
    # Python files with shebang
    ".py": {"pattern": "^#!", "position": "after"},
    
    # Shell scripts with shebang
    ".sh": {"pattern": "^#!", "position": "after"},
    
    # XML/HTML files with declarations
    ".html": {"pattern": "^<!DOCTYPE", "position": "after"},
    ".xml": {"pattern": "^<\\?xml", "position": "after"},
}


def get_header_template(filename: str, description: str = "", 
                        custom_template: Optional[str] = None) -> str:
    """
    Get the appropriate license header template for a file.
    
    Args:
        filename: Name of the file
        description: Optional description of the file's purpose
        custom_template: Optional custom template to use
        
    Returns:
        Formatted header template as a string
    """
    # Get file extension
    _, ext = os.path.splitext(filename)
    
    # Use provided or default template
    template = custom_template or DEFAULT_HEADER
    
    # Format the template with filename and description
    content = template.format(
        filename=os.path.basename(filename),
        description=description
    )
    
    # Apply comment style based on file extension
    if ext in COMMENT_STYLES:
        style = COMMENT_STYLES[ext]
        lines = content.split("\n")
        
        formatted_lines = []
        if style["start"]:
            formatted_lines.append(style["start"])
        
        for line in lines:
            if line:
                formatted_lines.append(f"{style['middle']}{line}")
            else:
                formatted_lines.append(style["middle"].rstrip())
        
        if style["end"]:
            formatted_lines.append(style["end"])
            
        return "\n".join(formatted_lines)
    
    # Default for unknown extensions: use Python-style
    return f'"""\n{content}\n"""'


def get_comment_style(filename: str) -> Dict[str, str]:
    """
    Get the comment style for a file based on its extension.
    
    Args:
        filename: Name of the file
        
    Returns:
        Dictionary with start, middle, and end comment markers
    """
    _, ext = os.path.splitext(filename)
    
    if ext in COMMENT_STYLES:
        return COMMENT_STYLES[ext]
    
    # Default to Python-style
    return {"start": '"""', "middle": "", "end": '"""'}


def get_special_position(filename: str) -> Optional[Dict[str, str]]:
    """
    Check if the file requires special header positioning.
    
    Args:
        filename: Name of the file
        
    Returns:
        Dictionary with pattern and position, or None
    """
    _, ext = os.path.splitext(filename)
    
    if ext in SPECIAL_POSITIONS:
        return SPECIAL_POSITIONS[ext]
    
    return None
