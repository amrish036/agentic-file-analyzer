"""Read file contents."""

import os
from typing import Dict, Any, Optional


class read_file:
    """Tool to read the contents of a file.
    
    Usage:
        read_file(file_path, start_line=1, end_line=None)
    """
    
    def __init__(self):
        """Initialize the read_file tool."""
        pass
    
    @staticmethod
    def execute(arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the read_file tool.
        
        Args:
            arguments: A dictionary containing:
                - file_path: The path to the file to read
                - start_line: The line number to start reading from (default: 1)
                - end_line: The line number to stop reading at (default: None, read to end)
            
        Returns:
            A dictionary containing the file contents and metadata.
        """
        file_path = arguments.get("file_path", "")
        start_line = arguments.get("start_line", 1)
        end_line = arguments.get("end_line", None)
        
        if not file_path:
            return {
                "success": False,
                "error": "No file path provided",
                "content": "",
                "lines": []
            }
        
        # Check if file_path is absolute
        if os.path.isabs(file_path):
            full_path = file_path
        else:
            # Resolve the path relative to the working directory
            working_dir = arguments.get("working_dir", os.getcwd())
            full_path = os.path.join(working_dir, file_path)
        
        if not os.path.exists(full_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "content": "",
                "lines": []
            }
        
        if not os.path.isfile(full_path):
            return {
                "success": False,
                "error": f"Not a file: {file_path}",
                "content": "",
                "lines": []
            }
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                
                # Calculate line indices
                start_idx = max(0, start_line - 1)
                end_idx = len(all_lines)
                
                if end_line is not None:
                    end_idx = min(end_line, len(all_lines))
                
                # Read the specified lines
                content_lines = all_lines[start_idx:end_idx]
                content = ''.join(content_lines)
                
                return {
                    "success": True,
                    "file_path": file_path,
                    "start_line": start_line,
                    "end_line": end_line,
                    "total_lines": len(all_lines),
                    "read_lines": end_idx - start_idx,
                    "content": content,
                    "lines": [line.rstrip('\n\r') for line in content_lines]
                }
        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "File is not a text file (cannot decode as UTF-8)",
                "content": "",
                "lines": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading file: {str(e)}",
                "content": "",
                "lines": []
            }
