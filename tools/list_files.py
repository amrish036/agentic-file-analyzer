"""List files in a directory."""

import os
from typing import Dict, Any, Optional


class list_files:
    """Tool to list files in a directory.
    
    Usage:
        list_files(directory_path, recursive=False)
    """
    
    def __init__(self):
        """Initialize the list_files tool."""
        pass
    
    @staticmethod
    def execute(arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the list_files tool.
        
        Args:
            arguments: A dictionary containing:
                - directory_path: The path to the directory to list files from
                - recursive: Whether to list files recursively (default: False)
            
        Returns:
            A dictionary containing the list of files and directories.
        """
        directory_path = arguments.get("directory_path", ".")
        recursive = arguments.get("recursive", False)
        
        # Resolve the path relative to the working directory
        working_dir = arguments.get("working_dir", os.getcwd())
        full_path = os.path.join(working_dir, directory_path)
        
        # Check if directory_path is absolute
        if os.path.isabs(directory_path):
            full_path = directory_path
        
        if not os.path.exists(full_path):
            return {
                "success": False,
                "error": f"Directory not found: {directory_path}",
                "files": [],
                "directories": []
            }
        
        if not os.path.isdir(full_path):
            return {
                "success": False,
                "error": f"Not a directory: {directory_path}",
                "files": [],
                "directories": []
            }
        
        files = []
        directories = []
        
        if recursive:
            # List all files and directories recursively
            for root, dirs, filenames in os.walk(full_path):
                # Add directories (relative to working_dir)
                dir_name = os.path.relpath(root, working_dir)
                if dir_name != working_dir:
                    directories.append(dir_name)
                
                # Add files (relative to working_dir)
                for filename in filenames:
                    file_path = os.path.relpath(os.path.join(root, filename), working_dir)
                    files.append(file_path)
        else:
            # List only immediate children
            try:
                entries = os.listdir(full_path)
                for entry in entries:
                    entry_path = os.path.join(directory_path, entry)
                    if os.path.isdir(entry_path):
                        directories.append(entry)
                    else:
                        files.append(entry)
            except PermissionError:
                return {
                    "success": False,
                    "error": "Permission denied",
                    "files": [],
                    "directories": []
                }
        
        return {
            "success": True,
            "directory": directory_path,
            "recursive": recursive,
            "files": sorted(files),
            "directories": sorted(directories),
            "total_files": len(files),
            "total_directories": len(directories)
        }