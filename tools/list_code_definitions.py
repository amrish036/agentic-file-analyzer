#!/usr/bin/env python3
"""Interactive CLI for listing code definition names in a directory."""

import sys
sys.path.insert(0, '.')
from tools.list_code_definition_names import ListCodeDefinitionNames


def main():
    """Run the interactive code definition list tool."""
    print("\n" + "=" * 60)
    print("  List Code Definitions")
    print("=" * 60)
    
    tool = ListCodeDefinitionNames()
    
    # Get directory path from user
    directory = input("\nDirectory path (default: .): ") or "."
    
    result = tool.execute({'directory_path': directory})
    
    if result['success']:
        definitions = result['definitions']
        total = len(definitions)
        
        # Count by type
        by_type = {}
        for defn in definitions:
            t = defn['type']
            by_type[t] = by_type.get(t, 0) + 1
        
        print(f"\nFound {total} definitions:")
        print("\nBy type:")
        
        for def_type in sorted(by_type.keys()):
            count = by_type[def_type]
            print(f"  {def_type:12} {count}")
        
        print("\nDefinitions:")
        
        for defn in definitions:
            print(f"  {defn['type']:12} {defn['name']:30} {defn['file']}")
    else:
        print(f"\nError: {result['error']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
