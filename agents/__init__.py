# Agents package
from .base_agent import LLM

# BaseAgent is an alias for LLM (defined in file_analyzer_agent.py)
BaseAgent = LLM

from .file_analyzer_agent import FileAnalyzerAgent

__all__ = ['BaseAgent', 'FileAnalyzerAgent', 'LLM']
