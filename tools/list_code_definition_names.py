"""List code definition names in a directory."""

import os
import ast
import re
from typing import Dict, Any, Optional, List
from pathlib import Path


class ListCodeDefinitionNames:
    """Tool to list code definition names in a directory.
    
    Usage:
        list_code_definition_names(directory_path)
    """
    
    def __init__(self):
        """Initialize the list_code_definition_names tool."""
        pass
    
    @staticmethod
    def execute(arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the list_code_definition_names tool.
        
        Args:
            arguments: A dictionary containing:
                - directory_path: The path to the directory to analyze
                
        Returns:
            A dictionary containing the list of code definitions.
        """
        directory_path = arguments.get("directory_path", ".")
        
        if not directory_path:
            return {
                "success": False,
                "error": "No directory path provided",
                "definitions": []
            }
        
        # Resolve the path relative to the working directory
        working_dir = arguments.get("working_dir", ".")
        full_path = os.path.join(working_dir, directory_path)
        
        if not os.path.exists(full_path):
            return {
                "success": False,
                "error": f"Directory not found: {directory_path}",
                "definitions": []
            }
        
        if not os.path.isdir(full_path):
            return {
                "success": False,
                "error": f"Not a directory: {directory_path}",
                "definitions": []
            }
        
        definitions = []
        
        # Supported file extensions for code analysis
        supported_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.cs', '.vb', '.fs', '.lua', '.pl', '.pm', '.r', '.R', '.m', '.mm', '.clj', '.cljs', '.edn', '.ex', '.exs', '.elixir', '.hcl', '.tf', '.tfvars', '.yml', '.yaml', '.json', '.toml', '.ini', '.cfg', '.conf', '.properties', '.xml', '.xsd', '.sql', '.md', '.rst', '.txt', '.csv', '.log', '.sh', '.bash', '.zsh', '.ps1', '.psm1', '.psd1', '.bat', '.cmd', '.env', '.gitignore', '.dockerfile', '.Dockerfile', '.gitattributes', '.gitconfig', '.gitmodules', '.gitremote'}
        
        # Walk through the directory
        for root, dirs, files in os.walk(full_path):
            for filename in files:
                _, ext = os.path.splitext(filename)
                if ext.lower() in supported_extensions:
                    file_path = os.path.join(root, filename)
                    
                    try:
                        # Try to parse as Python file
                        if ext == '.py':
                            definitions.extend(ListCodeDefinitionNames._parse_python(file_path))
                        # Try to parse as JavaScript/TypeScript file
                        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
                            definitions.extend(ListCodeDefinitionNames._parse_javascript(file_path))
                        # Try to parse as Java file
                        elif ext == '.java':
                            definitions.extend(ListCodeDefinitionNames._parse_java(file_path))
                        # For other file types, just list the filename
                        else:
                            definitions.append({
                                "type": "other",
                                "name": filename,
                                "file": os.path.relpath(file_path, working_dir)
                            })
                    except Exception as e:
                        # If parsing fails, just list the filename
                        definitions.append({
                            "type": "other",
                            "name": filename,
                            "file": os.path.relpath(file_path, working_dir),
                            "error": str(e)
                        })
        
        return {
            "success": True,
            "directory": directory_path,
            "definitions": definitions
        }
    
    @staticmethod
    def _parse_python(file_path: str) -> List[Dict[str, Any]]:
        """Parse a Python file to extract class and function definitions."""
        definitions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            try:
                tree = ast.parse(content)
            except SyntaxError:
                return definitions
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    definitions.append({
                        "type": "class",
                        "name": node.name,
                        "file": os.path.relpath(file_path, os.path.dirname(file_path))
                    })
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    definitions.append({
                        "type": "function",
                        "name": node.name,
                        "file": os.path.relpath(file_path, os.path.dirname(file_path))
                    })
                elif isinstance(node, ast.Lambda):
                    definitions.append({
                        "type": "lambda",
                        "name": "<anonymous>",
                        "file": os.path.relpath(file_path, os.path.dirname(file_path))
                    })
                elif isinstance(node, ast.Module):
                    definitions.append({
                        "type": "module",
                        "name": os.path.basename(file_path),
                        "file": os.path.relpath(file_path, os.path.dirname(file_path))
                    })
        except Exception:
            pass
        
        return definitions
    
    @staticmethod
    def _parse_javascript(file_path: str) -> List[Dict[str, Any]]:
        """Parse a JavaScript/TypeScript file to extract class and function definitions."""
        definitions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Simple regex-based parsing for JavaScript/TypeScript
            # Match class declarations
            class_pattern = r'class\s+(\w+)(?:\s+extends\s+\w+)?'
            for match in re.finditer(class_pattern, content):
                definitions.append({
                    "type": "class",
                    "name": match.group(1),
                    "file": os.path.relpath(file_path, os.path.dirname(file_path))
                })
            
            # Match function declarations
            function_pattern = r'(?:function\s+|async\s+)(\w+)\s*\('
            for match in re.finditer(function_pattern, content):
                definitions.append({
                    "type": "function",
                    "name": match.group(1),
                    "file": os.path.relpath(file_path, os.path.dirname(file_path))
                })
            
            # Match arrow functions assigned to variables
            arrow_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>\s*\{'
            for match in re.finditer(arrow_pattern, content):
                definitions.append({
                    "type": "function",
                    "name": match.group(1),
                    "file": os.path.relpath(file_path, os.path.dirname(file_path))
                })
            
            # Match method definitions in classes
            method_pattern = r'(?:public\s+|private\s+|protected\s+|static\s+)?(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{'
            for match in re.finditer(method_pattern, content):
                definitions.append({
                    "type": "method",
                    "name": match.group(1),
                    "file": os.path.relpath(file_path, os.path.dirname(file_path))
                })
            
            # Match interface declarations
            interface_pattern = r'interface\s+(\w+)'
            for match in re.finditer(interface_pattern, content):
                definitions.append({
                    "type": "interface",
                    "name": match.group(1),
                    "file": os.path.relpath(file_path, os.path.dirname(file_path))
                })
            
            # Match type aliases
            type_pattern = r'type\s+(\w+)\s*='
            for match in re.finditer(type_pattern, content):
                definitions.append({
                    "type": "type",
                    "name": match.group(1),
                    "file": os.path.relpath(file_path, os.path.dirname(file_path))
                })
            
            # Match namespace declarations
            namespace_pattern = r'namespace\s+(\w+)'
            for match in re.finditer(namespace_pattern, content):
                definitions.append({
                    "type": "namespace",
                    "name": match.group(1),
                    "file": os.path.relpath(file_path, os.path.dirname(file_path))
                })
            
            # Match enum declarations
            enum_pattern = r'enum\s+(\w+)'
            for match in re.finditer(enum_pattern, content):
                definitions.append({
                    "type": "enum",
                    "name": match.group(1),
                    "file": os.path.relpath(file_path, os.path.dirname(file_path))
                })
            
        except Exception:
            pass
        
        return definitions
    
    @staticmethod
    def _parse_java(file_path: str) -> List[Dict[str, Any]]:
        """Parse a Java file to extract class and method definitions."""
        definitions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Match class declarations
            class_pattern = r'(?:public\s+|private\s+|protected\s+|abstract\s+|final\s+)?class\s+(\w+)'
            for match in re.finditer(class_pattern, content):
                definitions.append({
                    "type": "class",
                    "name": match.group(1),
                    "file": os.path.relpath(file_path, os.path.dirname(file_path))
                })
            
            # Match method declarations
            method_pattern = r'(?:public\s+|private\s+|protected\s+|static\s+|final\s+|abstract\s+|synchronized\s+|native\s+|strictfp\s+)?(\w+)\s*\([^)]*\)\s*\{'
            for match in re.finditer(method_pattern, content):
                definitions.append({
                    "type": "method",
                    "name": match.group(1),
                    "file": os.path.relpath(file_path, os.path.dirname(file_path))
                })
            
        except Exception:
            pass
        
        return definitions


# Export with lowercase name for compatibility with __init__.py
list_code_definition_names = ListCodeDefinitionNames