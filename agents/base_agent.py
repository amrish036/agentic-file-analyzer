"""Base agent class for agentic file analyzer."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import os
from dotenv import load_dotenv, find_dotenv


# Local LLM imports (required)
try:
    import requests
except ImportError:
    raise ImportError("requests library is required for local LLM")


# Load environment variables from .env file
env_file = find_dotenv()
if env_file:
    load_dotenv(env_file)

# Get local LLM configuration from environment variables
LOCAL_LLM_HOST = os.getenv("LOCAL_LLM_HOST", "http://localhost:1234")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "your-local-model-name")


@dataclass
class Message:
    """Represents a message in a conversation."""
    role: str  # 'system', 'user', 'assistant'
    content: str
    name: Optional[str] = None


@dataclass
class ToolCall:
    """Represents a tool call."""
    name: str
    arguments: str
    call_id: Optional[str] = None


@dataclass
class ToolResponse:
    """Represents a tool response."""
    content: str
    tool_call_id: str


class LLM:
    """LLM wrapper that supports local LLM only."""
    
    def __init__(self, model: Optional[str] = None, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize the LLM.
        
        Args:
            model: The model name to use. Defaults to LOCAL_LLM_MODEL from environment.
            base_url: The base URL for the LLM API. Defaults to LOCAL_LLM_HOST from environment.
            api_key: Optional API key for authentication.
        """
        self.model = model or LOCAL_LLM_MODEL
        self.base_url = base_url or LOCAL_LLM_HOST
        self.api_key = api_key
        self.provider = "local"
        self.conversation_history: List[Message] = []
    
    def _call_local(self, messages: List[Message]) -> str:
        """Call local LLM (e.g., Ollama, LM Studio)."""
        import json
        import requests
        
        # Convert messages to the correct format for the local LLM API
        # The API expects: {"model": "...", "input": [{"type": "text", "content": "..."}]}
        api_messages = []
        for msg in messages:
            api_messages.append({
                "type": "text",
                "content": msg.content
            })
        
        url = f"{self.base_url}/chat"
        payload = {
            "model": self.model,
            "input": api_messages,
            "stream": False
        }
        
        response = requests.post(
            url,
            headers=self._get_headers() if self.api_key else {},
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"Local LLM error: {response.text}")
        
        result = response.json()
        
        # Handle different response formats from different LLM providers
        # Format: {"output": [{"type": "reasoning", "content": "..."}, {"type": "message", "content": "..."}]}
        if "output" in result and len(result["output"]) > 0:
            # Get the message content (skip reasoning if present)
            for item in result["output"]:
                if item.get("type") == "message":
                    return item.get("content", "")
            # If no message, return reasoning
            return result["output"][0].get("content", "")
        else:
            # Fallback: return the entire response as string
            return json.dumps(result)
    
    def _call(self, messages: List[Message]) -> str:
        """Call the LLM with the given messages.
        
        Args:
            messages: List of messages to send to the LLM.
            
            Returns:
                The LLM's response.
        """
        return self._call_local(messages)
    
    def _call_llm(self, messages: List[Message]) -> str:
        """Call the LLM with the given messages.
        
        Args:
            messages: List of messages to send to the LLM.
            
            Returns:
                The LLM's response.
        """
        return self._call(messages)
    
    def _call_llm_stream(self, messages: List[Message]) -> str:
        """Call the LLM with streaming.
        
        Args:
            messages: List of messages to send to the LLM.
            
            Returns:
                The LLM's response.
        """
        return self._call_llm(messages)  # Default to non-streaming for simplicity
    
    def _get_headers(self) -> Dict[str, str]:
        """Get the headers for API requests.
        
        Returns:
            Dictionary of headers.
        """
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def add_message(self, message: Message):
        """Add a message to the conversation history.
        
        Args:
            message: The message to add.
        """
        self.conversation_history.append(message)
    
    def get_conversation_history(self) -> List[Message]:
        """Get the conversation history.
        
        Returns:
            List of messages in the conversation.
        """
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []


# BaseAgent is actually the LLM class in base_agent.py
BaseAgent = LLM
