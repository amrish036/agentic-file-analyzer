"""Example usage of the Agentic File Analyzer tools."""

import sys
sys.path.insert(0, '.')

from tools import list_files, read_file, search_files, list_code_definition_names

print("=" * 60)
print("Agentic File Analyzer - Example Usage")
print("=" * 60)

# Example 1: List files in the current directory
print("\n--- Example 1: List Files ---")
result = list_files.execute({
    "directory_path": ".",
    "recursive": True,
    "working_dir": "."
})
print(f"Success: {result.get('success', False)}")
print(f"Files: {result.get('files', [])[:10]}...")  # Show first 10 files
print(f"Directories: {result.get('directories', [])[:10]}...")  # Show first 10 directories

# Example 2: Read a file
print("\n--- Example 2: Read File ---")
result = read_file.execute({
    "file_path": "README.md",
    "start_line": 1,
    "end_line": 30,
    "working_dir": "."
})
print(f"Success: {result.get('success', False)}")
print(f"Content preview:\n{result.get('content', '')[:200]}...")

# Example 3: Search for patterns in files
print("\n--- Example 3: Search Files ---")
result = search_files.execute({
    "directory_path": ".",
    "regex_pattern": "def |class |import |from ",
    "file_pattern": "*.py",
    "working_dir": "."
})
print(f"Success: {result.get('success', False)}")
print(f"Total matches: {result.get('total_matches', 0)}")
print(f"First 5 matches:")
for match in result.get('matches', [])[:5]:
    print(f"  - {match['file']}:{match['line']}: {match['content']}")

# Example 4: List code definition names
print("\n--- Example 4: List Code Definitions ---")
result = list_code_definition_names.execute({
    "directory_path": "agents",
    "working_dir": "."
})
print(f"Success: {result.get('success', False)}")
print(f"Found {len(result.get('definitions', []))} definitions:")
for defn in result.get('definitions', [])[:10]:
    print(f"  - {defn['type']}: {defn['name']}")

print("\n" + "=" * 60)
print("Done!")
print("=" * 60)