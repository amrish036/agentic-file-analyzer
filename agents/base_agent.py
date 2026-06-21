"""Base agent class for agentic file analyzer."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


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


class BaseAgent(ABC):
    """Abstract base class for agents."""
    
    def __init__(self, llm_config: Dict[str, Any]):
        """Initialize the agent with LLM configuration.
        
        Args:
            llm_config: Configuration for the LLM including host, model, etc.
        """
        self.llm_config = llm_config
        self.conversation_history: List[Message] = []
        self.tool_results: Dict[str, Any] = {}
    
    @abstractmethod
    def run(self, user_input: str) -> str:
        """Run the agent with user input.
        
        Args:
            user_input: The user's input message.
            
        Returns:
            The agent's response.
        """
        pass
    
    @abstractmethod
    def _call_llm(self, messages: List[Message]) -> str:
        """Call the LLM with the given messages.
        
        Args:
            messages: List of messages to send to the LLM.
            
        Returns:
            The LLM's response.
        """
        pass
    
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