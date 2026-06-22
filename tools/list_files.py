"""List files in a directory."""

import os
from typing import Dict, Any, Optional


class list_files:
    """Tool to list files in a directory.
    
    Usage:
        list_files(directory, recursive=False)
    """
    
    def __init__(self):
        """Initialize the list_files tool."""
        pass
    
    @staticmethod
    def execute(arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the list_files tool.
        
        Args:
            arguments: A dictionary containing:
                - directory: The path to the directory to list files from (default: ".")
                - recursive: Whether to list files recursively (default: False)
            
        Returns:
            A dictionary containing the list of files and directories.
        """
        directory = arguments.get("directory", ".")
        recursive = arguments.get("recursive", False)
        
        target_dir = directory
        
        # Resolve the path relative to the working directory
        working_dir = arguments.get("working_dir", os.getcwd())
        
        # Strip leading slash if present for relative paths
        if target_dir.startswith('/'):
            target_dir = target_dir.lstrip('/')
        
        # Check if target_dir is absolute (starts with /)
        if os.path.isabs(target_dir):
            full_path = target_dir
        else:
            # Relative path
            full_path = os.path.join(working_dir, target_dir)
        
        # Check if the resolved path exists
        if not os.path.exists(full_path):
            return {
                "success": False,
                "error": f"Directory not found: {full_path}",
                "files": [],
                "directories": [],
                "total_files": 0,
                "total_directories": 0
            }
        
        files = []
        directories = []
        
        if recursive:
            # List all files and directories recursively
            for root, dirs, filenames in os.walk(full_path):
                # Add directories (relative to target_dir)
                dir_name = os.path.relpath(root, full_path)
                if dir_name != '.':
                    directories.append(dir_name)
                
                # Add files (relative to target_dir)
                for filename in filenames:
                    file_path = os.path.relpath(os.path.join(root, filename), full_path)
                    files.append(file_path)
        else:
            # List only immediate children
            try:
                entries = os.listdir(full_path)
                for entry in entries:
                    entry_path = os.path.join(full_path, entry)
                    if os.path.isdir(entry_path):
                        directories.append(os.path.relpath(entry_path, full_path))
                    else:
                        files.append(os.path.relpath(entry_path, full_path))
            except PermissionError:
                return {
                    "success": False,
                    "error": "Permission denied",
                    "files": [],
                    "directories": [],
                    "total_files": 0,
                    "total_directories": 0
                }
        
        return {
            "success": True,
            "directory": target_dir,
            "recursive": recursive,
            "files": sorted(files),
            "directories": sorted(directories),
            "total_files": len(files),
            "total_directories": len(directories),
            "error": None
        }
