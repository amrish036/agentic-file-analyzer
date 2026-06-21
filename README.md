# Agentic File Analyzer

Imagine you have a big box of files on your computer, and you want to find something specific or understand what's inside. This tool is like having a smart assistant who can help you explore your files and answer questions about them.

## What Does This Tool Do?

Think of this as a digital librarian for your files. Instead of manually searching through folders, you can just ask questions in plain English, and the tool will help you find what you need.

### How It Works (Simple Explanation)

1. **You ask a question** - Like "Show me all Python files" or "Find where the login function is"
2. **The agent thinks** - It figures out what you need and which tools to use
3. **The agent uses tools** - It calls the right tools to get the information
4. **The agent answers** - It gives you a helpful response based on what it found

## Available Tools

### 📁 List Files
Shows you all the files and folders in a directory.

**Example:**
```
Show me all files in my project folder
```

### 📖 Read File
Opens and shows you the contents of a file.

**Example:**
```
Show me the contents of src/main.py
```

### 🔍 Search Files
Searches for specific words or patterns in files.

**Example:**
```
Find all places where "TODO" appears in my Python files
```

### 📋 List Code Definitions
Shows you all the classes, functions, and methods in your code.

**Example:**
```
List all the functions in my src directory
```

## How to Use

### Step 1: Install the Tool

Open your terminal and run:

```bash
pip install -r requirements.txt
```

### Step 2: Run the Tool

You can use the tool in two ways:

#### Option A: Interactive Mode (Easiest!)

Just run the tool and start chatting with it:

```bash
python3 agents/file_analyzer_agent.py
```

Then you can type questions like:
- "What files are in my project?"
- "Show me the main.py file"
- "Find all TODO comments in my code"
- "List all functions in my src folder"

#### Option B: Programmatic Mode

If you want to use it in your own code:

```python
from agents import FileAnalyzerAgent

# Create the agent
agent = FileAnalyzerAgent(
    llm_config={
        "host": "https://your-llm-api.com",
        "model": "your-model-name"
    },
    working_dir="/path/to/your/project"
)

# Ask the agent a question
response = agent.run("Show me all Python files in the src directory")
print(response)
```

## Example Conversations

### Example 1: Exploring Your Project

```
You: What files are in my project?
Agent: Here are all the files in your project:
       - src/main.py
       - src/utils.py
       - config/settings.json
       - README.md
```

### Example 2: Reading a Specific File

```
You: Show me the first 50 lines of src/main.py
Agent: Here's the content of src/main.py (lines 1-50):
       [file contents]
```

### Example 3: Finding Code

```
You: Find all functions that handle user authentication
Agent: I found these functions:
       - authenticate_user() in src/auth.py
       - validate_token() in src/auth.py
       - logout_user() in src/auth.py
```

## Project Structure

```
agentic-file-analyzer/
├── agents/
│   ├── __init__.py          # Makes the agent classes available
│   ├── base_agent.py        # The base class all agents inherit from
│   └── file_analyzer_agent.py # The main agent that uses tools
├── tools/
│   ├── __init__.py          # Makes the tools available
│   ├── list_files.py        # Tool to list directory contents
│   ├── read_file.py         # Tool to read file contents
│   ├── search_files.py      # Tool to search for patterns
│   └── list_code_definition_names.py # Tool to list code definitions
├── LICENSE
├── README.md                # This file!
└── requirements.txt        # List of Python packages needed
```

## How It All Works Together

```
┌─────────────────────────────────────────┐
│         You Type a Question             │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         File Analyzer Agent             │
│         (Your Smart Assistant)          │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         LLM (AI Brain)                  │
│         "What should I do?"             │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         Tools (The Hands)               │
│         - list_files                    │
│         - read_file                     │
│         - search_files                  │
│         - list_code_definitions         │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         LLM (AI Brain)                  │
│         "Now answer the question"       │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         Your Answer!                    │
└─────────────────────────────────────────┘
```

## Tips for Best Results

1. **Be specific** - "Show me Python files" is better than "Show me files"
2. **Use paths** - "Show me files in src/" is more helpful than just "Show me files"
3. **Ask follow-up questions** - The agent remembers what it already found
4. **Be natural** - Just talk to it like you would a person!

## License

This project is licensed under the MIT License - feel free to use it in your projects!

## Contributing

Want to help improve this tool? We'd love your help! Just submit a Pull Request or open an issue with your suggestions.