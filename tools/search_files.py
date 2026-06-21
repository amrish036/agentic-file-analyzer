"""Search for patterns in files."""

import os
import fnmatch
import re
from typing import Dict, Any, Optional, List


class search_files:
    """Tool to search for patterns in files.
    
    Usage:
        search_files(directory_path, regex_pattern, file_pattern=None)
    """
    
    def __init__(self):
        """Initialize the search_files tool."""
        pass
    
    @staticmethod
    def execute(arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the search_files tool.
        
        Args:
            arguments: A dictionary containing:
                - directory_path: The path to the directory to search in
                - regex_pattern: The regex pattern to search for
                - file_pattern: Optional glob pattern to filter files (default: None)
            
        Returns:
            A dictionary containing the search results.
        """
        directory_path = arguments.get("directory_path", ".")
        regex_pattern = arguments.get("regex_pattern", "")
        file_pattern = arguments.get("file_pattern", None)
        
        if not regex_pattern:
            return {
                "success": False,
                "error": "No regex pattern provided",
                "matches": [],
                "total_matches": 0
            }
        
        # Compile the regex pattern
        try:
            pattern = re.compile(regex_pattern)
        except re.error as e:
            return {
                "success": False,
                "error": f"Invalid regex pattern: {str(e)}",
                "matches": [],
                "total_matches": 0
            }
        
        # Resolve the path relative to the working directory
        working_dir = arguments.get("working_dir", ".")
        full_path = os.path.join(working_dir, directory_path)
        
        if not os.path.exists(full_path):
            return {
                "success": False,
                "error": f"Directory not found: {directory_path}",
                "matches": [],
                "total_matches": 0
            }
        
        if not os.path.isdir(full_path):
            return {
                "success": False,
                "error": f"Not a directory: {directory_path}",
                "matches": [],
                "total_matches": 0
            }
        
        matches = []
        total_matches = 0
        
        # Walk through the directory
        for root, dirs, files in os.walk(full_path):
            # Filter files if a file_pattern is specified
            if file_pattern:
                files = [f for f in files if fnmatch.fnmatch(f, file_pattern)]
            
            for filename in files:
                file_path = os.path.join(root, filename)
                
                # Skip binary files
                if not os.path.isfile(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            # Check if the line matches the pattern
                            match_obj = pattern.search(line)
                            if match_obj:
                                # Get the relative path
                                rel_path = os.path.relpath(file_path, working_dir)
                                
                                match_dict = {
                                    "file": rel_path,
                                    "line": line_num,
                                    "content": line.rstrip('\n\r'),
                                    "match": match_obj.group()
                                }
                                matches.append(match_dict)
                                total_matches += 1
                except Exception:
                    # Skip files that can't be read
                    continue
        
        return {
            "success": True,
            "directory": directory_path,
            "pattern": regex_pattern,
            "file_pattern": file_pattern,
            "matches": matches,
            "total_matches": total_matches
        }