"""File analyzer agent for agentic file analyzer."""

import os
import sys
from typing import List, Optional, Dict, Any
from pathlib import Path

from agents.base_agent import BaseAgent, Message, ToolCall, ToolResponse


class FileAnalyzerAgent(BaseAgent):
    """Agent for analyzing files in a directory."""
    
    def __init__(self, llm_config: Dict[str, Any], working_dir: str = "."):
        """Initialize the file analyzer agent.
        
        Args:
            llm_config: Configuration for the LLM.
            working_dir: The working directory to analyze.
        """
        super().__init__(llm_config)
        self.working_dir = working_dir
        self.file_content_cache: Dict[str, str] = {}
        self.tool_results: Dict[str, Any] = {}
    
    def run(self, user_input: str) -> str:
        """Run the file analyzer agent.
        
        Args:
            user_input: The user's input message.
            
        Returns:
            The agent's response.
        """
        self.add_message(Message(role="user", content=user_input))
        
        # Add system message
        system_message = Message(
            role="system",
            content=self._get_system_message()
        )
        self.add_message(system_message)
        
        # Call LLM with initial messages
        response = self._call_llm([system_message, Message(role="user", content=user_input)])
        
        # Process the response for tool calls
        tool_calls = self._extract_tool_calls(response)
        
        if tool_calls:
            # Initialize tool_responses list
            tool_responses = []
            
            # Execute tool calls and add responses to conversation
            for tool_call in tool_calls:
                tool_response = self._execute_tool_call(tool_call)
                tool_responses.append(tool_response)
                self.add_message(Message(role="tool", content=tool_response.content, name=tool_call.name))
            
            # Call LLM again with tool responses
            final_response = self._call_llm(self.get_conversation_history())
            
            return final_response
        else:
            return response
    
    def _get_system_message(self) -> str:
        """Get the system message for the file analyzer agent."""
        return f"""You are a file analyzer agent. Your task is to help users analyze files in the working directory.

Working directory: {self.working_dir}

Available tools:
- list_files: List files in a directory
- read_file: Read the contents of a file
- search_files: Search for patterns in files
- list_code_definition_names: List code definition names in a directory

Rules:
1. Always think step by step before using tools
2. Use tools to gather information when needed
3. Provide clear and concise responses
4. If you need more information, ask the user questions
5. Don't use tools unnecessarily

When using list_files:
- Specify the directory path (relative to working directory)
- Use recursive=true if you want to list all files recursively

When using read_file:
- Specify the file path (relative to working directory)
- You can specify start_line and end_line to read specific line ranges

When using search_files:
- Specify the directory path
- Provide a regex pattern to search for
- Optionally specify a file pattern to filter files

When using list_code_definition_names:
- Specify the directory path
- This will list classes, functions, methods, etc. in source code files

Remember to be helpful and provide useful information about the files."""
    
    def _extract_tool_calls(self, response: str) -> List[ToolCall]:
        """Extract tool calls from the LLM response.
        
        Args:
            response: The LLM's response string.
            
        Returns:
            List of tool calls.
        """
        tool_calls = []
        
        # Simple regex to extract tool calls
        # This is a basic implementation - you may need to adjust based on the LLM's output format
        import re
        
        # Pattern to match tool calls in format: {"name": "...", "arguments": "..."}
        tool_call_pattern = r'\{\s*"name"\s*:\s*"([^"]+)"\s*,\s*"arguments"\s*:\s*"([^"]+)"\s*\}'
        
        for match in re.finditer(tool_call_pattern, response):
            tool_call = ToolCall(
                name=match.group(1),
                arguments=match.group(2),
                call_id=f"call_{len(tool_calls)}"
            )
            tool_calls.append(tool_call)
        
        return tool_calls
    
    def _execute_tool_call(self, tool_call: ToolCall) -> ToolResponse:
        """Execute a tool call.
        
        Args:
            tool_call: The tool call to execute.
            
        Returns:
            The tool response.
        """
        # Import tools here to avoid circular imports
        from tools import list_files, read_file, search_files
        from tools.list_code_definition_names import ListCodeDefinitionNames
        import json
        
        tool_name = tool_call.name
        arguments_str = tool_call.arguments
        
        # Get a valid tool_call_id (fallback to "unknown" if None)
        tool_call_id = tool_call.call_id or "unknown"
        
        # Parse the arguments string into a dictionary
        try:
            arguments = json.loads(arguments_str)
        except json.JSONDecodeError as e:
            return ToolResponse(content=f"Error parsing arguments: {str(e)}", tool_call_id=tool_call_id)
        
        try:
            if tool_name == "list_files":
                result = list_files.execute(arguments)
            elif tool_name == "read_file":
                result = read_file.execute(arguments)
            elif tool_name == "search_files":
                result = search_files.execute(arguments)
            elif tool_name == "list_code_definition_names":
                result = ListCodeDefinitionNames().execute(arguments)
            else:
                return ToolResponse(content=f"Unknown tool: {tool_name}", tool_call_id=tool_call_id)
            
            # Cache the result
            self.tool_results[tool_call_id] = result
            
            return ToolResponse(content=str(result), tool_call_id=tool_call_id)
        except Exception as e:
            return ToolResponse(content=f"Error executing tool {tool_name}: {str(e)}", tool_call_id=tool_call_id)
    
    def _call_llm(self, messages: List[Message]) -> str:
        """Call the LLM with the given messages.
        
        Args:
            messages: List of messages to send to the LLM.
            
        Returns:
            The LLM's response.
        """
        # This is a placeholder implementation
        # You should replace this with actual LLM integration
        import json
        
        # Convert messages to JSON format for the LLM
        messages_json = [
            {"role": msg.role, "content": msg.content, "name": msg.name}
            for msg in messages
        ]
        
        # For now, just return a placeholder response
        # In production, you would call the actual LLM API
        return json.dumps(messages_json)


if __name__ == "__main__":
    import sys
    
    # Add parent directory to path for imports
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    sys.path.insert(0, os.path.join(parent_dir, 'agents'))
    
    # Check if running as main script
    if len(sys.argv) > 1:
        # Run with specific input
        user_input = " ".join(sys.argv[1:])
        
        # Create agent with default config
        agent = FileAnalyzerAgent(
            llm_config={
                "host": "https://api.example.com",
                "model": "your-model-name"
            },
            working_dir="."
        )
        
        # Run the agent
        response = agent.run(user_input)
        print(response)
    else:
        # Interactive mode
        print("Agentic File Analyzer")
        print("=" * 40)
        print("Type your questions and press Enter to submit.")
        print("Type 'exit' to quit.\n")
        
        agent = FileAnalyzerAgent(
            llm_config={
                "host": "https://api.example.com",
                "model": "your-model-name"
            },
            working_dir="."
        )
        
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            
            if not user_input.strip():
                continue
            
            print("Agent: ")
            response = agent.run(user_input)
            print(response)
            print()
