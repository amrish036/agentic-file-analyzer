"""File analyzer agent for agentic file analyzer."""

import os
import sys
from typing import List, Optional, Dict, Any
from pathlib import Path

# Handle imports for both module and script execution
if __name__ == "__main__":
    # When running as a script, add parent directory to sys.path
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)

try:
    from .base_agent import Message, ToolCall, ToolResponse, LLM
    BaseAgent = LLM  # BaseAgent is actually the LLM class in base_agent.py
except ImportError:
    from base_agent import Message, ToolCall, ToolResponse, LLM
    BaseAgent = LLM

class FileAnalyzerAgent(BaseAgent):
    """Agent for analyzing files in a directory."""
    
    def __init__(self, llm_config: Optional[Dict[str, Any]] = None, working_dir: str = "."):
        """Initialize the file analyzer agent.
        
        Args:
            llm_config: Configuration for the LLM. If None, uses environment variables.
            working_dir: The working directory to analyze.
        """
        import os
        from dotenv import load_dotenv, find_dotenv
        
        # Load environment variables from .env file
        env_file = find_dotenv()
        if env_file:
            load_dotenv(env_file)
        
        # Use llm_config if provided, otherwise use environment variables
        if llm_config is None:
            llm_config = {}
        
        self.llm = LLM(
            model=llm_config.get("model", os.getenv("LOCAL_LLM_MODEL", "qwen3.5-9b")),
            base_url=llm_config.get("base_url", os.getenv("LOCAL_LLM_HOST", "http://localhost:1234/v1")),
            api_key=llm_config.get("api_key")
        )
        self.working_dir = working_dir
        self.file_content_cache: Dict[str, str] = {}
        self.tool_results: Dict[str, Any] = {}
        self.conversation_history: List[Message] = []
    
    def run(self, user_input: str) -> str:
        """Run the file analyzer agent.
        
        Args:
            user_input: The user's input message.
            
        Returns:
            The agent's response.
        """
        # Preprocess user input to handle "this directory" references
        # Convert "this directory" to "." for the working directory
        processed_input = user_input.replace("this directory", ".").replace("this directory.", ".")
        
        self.add_message(Message(role="user", content=processed_input))
        
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
                # LM Studio doesn't support 'tool' role, use 'assistant' instead
                self.add_message(Message(role="assistant", content=tool_response.content, name=tool_call.name))
            
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
- Specify the directory path (relative to working directory). Use "." for the current working directory or "this directory"
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
        import re
        tool_calls = []
        
        # LM Studio returns tool calls in a specific format with 'tool_calls' array
        # Format: {"tool_calls": [{"id": "...", "type": "function", "function": {"name": "...", "arguments": {...}}}, ...]}
        
        # Pattern to match the tool_calls array
        tool_calls_pattern = r'"tool_calls"\s*:\s*\[(.*?)\]'
        
        # Extract the tool_calls array content
        match = re.search(tool_calls_pattern, response, re.DOTALL)
        if match:
            tool_calls_content = match.group(1)
            
            # Parse each tool call in the array
            # Each tool call has: id, type, function (with name and arguments)
            tool_call_pattern = r'\{\s*"id"\s*:\s*"([^"]+)"\s*,\s*"type"\s*:\s*"([^"]+)"\s*,\s*"function"\s*:\s*\{\s*"name"\s*:\s*"([^"]+)"\s*,\s*"arguments"\s*:\s*"([^"]+)"\s*\}\s*\}'
            
            for tc_match in re.finditer(tool_call_pattern, tool_calls_content):
                tool_call = ToolCall(
                    name=tc_match.group(3),
                    arguments=tc_match.group(4),
                    call_id=tc_match.group(1)
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
        import json
        import sys
        from pathlib import Path
        
        # Get the working directory for tool execution
        working_dir = Path(self.working_dir).resolve()
        
        # Import tools here to avoid circular imports
        # Add the tools directory to the path
        tools_dir = working_dir / "tools"
        if tools_dir.exists():
            sys.path.insert(0, str(tools_dir))
        
        try:
            from tools import list_files, read_file, search_files
            from tools.list_code_definition_names import ListCodeDefinitionNames
        except ImportError as e:
            return ToolResponse(content=f"Error importing tools: {str(e)}", tool_call_id=tool_call.call_id or "unknown")
        
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
                # Add working_dir to arguments if not already present
                if "working_dir" not in arguments:
                    arguments["working_dir"] = self.working_dir
                result = list_files.execute(arguments)
            elif tool_name == "read_file":
                # Add working_dir to arguments if not already present
                if "working_dir" not in arguments:
                    arguments["working_dir"] = self.working_dir
                # Change 'path' to 'file_path' to match the read_file tool's expected parameter
                if "path" in arguments:
                    arguments["file_path"] = arguments.pop("path")
                result = read_file.execute(arguments)
            elif tool_name == "search_files":
                # Add working_dir to arguments if not already present
                if "working_dir" not in arguments:
                    arguments["working_dir"] = self.working_dir
                # Change 'path' to 'directory_path' and 'pattern' to 'regex_pattern' to match the search_files tool's expected parameters
                if "path" in arguments:
                    arguments["directory_path"] = arguments.pop("path")
                if "pattern" in arguments:
                    arguments["regex_pattern"] = arguments.pop("pattern")
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
        return self.llm._call_llm(messages)


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
        
        # Create agent with default config from environment variables
        agent = FileAnalyzerAgent(
            llm_config={
                "model": os.getenv("LOCAL_LLM_MODEL", "your-local-model-name"),
                "base_url": os.getenv("LOCAL_LLM_HOST", "http://localhost:1234/v1")
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
                "model": os.getenv("LOCAL_LLM_MODEL", "your-local-model-name"),
                "base_url": os.getenv("LOCAL_LLM_HOST", "http://localhost:1234/v1")
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
