# Conversation Explorer

A powerful tool for exploring and analyzing Claude conversation transcripts stored in JSONL format.

## Features

- **List conversations** with metadata (duration, message count, tool usage)
- **Search content** across all conversations
- **Filter by criteria** (date range, duration, message count, tools used)
- **View conversations** with detailed formatting and tool summaries
- **Statistics** showing usage patterns and activity over time
- **Advanced Analytics** with tool patterns, temporal analysis, and complexity scoring
- **Export** conversations to JSON or text format
- **Rich terminal UI** with colors and tables
- **Makefile Integration** with quick commands like `make conv`
- **Interactive Browser** for guided exploration

## Installation

The tool is already set up in your Claude workspace. Dependencies are managed with `uv`.

## Usage

### Quick Start with Makefile Commands

The fastest way to explore your conversations:

```bash
# Quick browsing
make conv                    # List recent conversations  
make conv-today             # Today's conversations
make conv-stats             # Show statistics
make conv-analytics         # Advanced insights

# Search and filter
make conv-search QUERY="rust"     # Search for content
make conv-tools TOOL=webfetch      # Find tool usage
make conv-long                     # Long conversations (>5min)
make conv-active                   # High-activity conversations

# Detailed analysis
make conv-show ID=3f78a75c1ffe     # View specific conversation
make conv-export ID=3f78a75c1ffe   # Export to JSON

# Interactive mode
make conv-browse            # Guided exploration
make conv-help              # Show all commands
```

### Full CLI Interface

For advanced usage, use the standalone CLI script:

```bash
# List recent conversations
uv run python scripts/conversation_explorer.py list --limit 10

# Show recent conversations from last 3 days
uv run python scripts/conversation_explorer.py recent --days 3

# Search for specific content
uv run python scripts/conversation_explorer.py search "error handling"

# Show conversation details
uv run python scripts/conversation_explorer.py show <session_id>

# Find conversations that used specific tools
uv run python scripts/conversation_explorer.py tools webfetch grep

# Show statistics
uv run python scripts/conversation_explorer.py stats --detailed

# Filter conversations with advanced criteria
uv run python scripts/conversation_explorer.py filter --start-date 2026-01-28 --min-messages 10

# Export a conversation
uv run python scripts/conversation_explorer.py export <session_id> --format json
```

### Available Commands

- `list` - List all conversations with sorting options
- `show` - Show details of a specific conversation
- `search` - Search conversations for text content
- `recent` - Show recent conversations from last N days
- `filter` - Advanced filtering with multiple criteria
- `tools` - Find conversations using specific tools
- `stats` - Show comprehensive statistics
- `export` - Export conversations to files

### Python API

You can also use the explorer programmatically:

```python
from conversation_explorer import ConversationExplorer, ConversationFormatter

# Initialize explorer
explorer = ConversationExplorer()
formatter = ConversationFormatter()

# List recent conversations
recent = explorer.get_recent_conversations(days=7, limit=10)
formatter.format_conversation_list(recent)

# Search for content
results = explorer.search_content("python code")

# Get conversation details
conversation = explorer.get_conversation(session_id)

# Generate statistics
stats = explorer.get_stats()
formatter.format_stats(stats)
```

## Data Format

The tool parses JSONL transcript files with the following structure:
- User messages: `{"type": "user", "timestamp": "...", "content": "..."}`
- Tool calls: `{"type": "tool_use", "timestamp": "...", "tool_name": "...", "tool_input": {...}}`
- Tool results: `{"type": "tool_result", "timestamp": "...", "tool_name": "...", "tool_output": {...}}`

## Architecture

- `models.py` - Pydantic data models for conversations and metadata
- `parser.py` - JSONL transcript parsing with error handling
- `explorer.py` - Core search, filter, and analysis functionality  
- `formatter.py` - Rich terminal formatting and display
- `cli.py` - Click-based command-line interface

## Performance

- Metadata caching for fast repeated operations
- Streaming JSONL parsing for large files
- Quick text search without full parsing for content queries
- Graceful handling of malformed transcript lines

## Examples

### Find long conversations about a specific topic
```bash
uv run python scripts/conversation_explorer.py filter --text "rust programming" --min-duration 300
```

### Show daily activity over time
```bash
uv run python scripts/conversation_explorer.py stats --detailed
```

### Export recent conversations
```bash
for session in $(uv run python scripts/conversation_explorer.py recent --days 1 | tail -n +4 | cut -d' ' -f2); do
  uv run python scripts/conversation_explorer.py export $session --format json --output "exports/$session.json"
done
```

The tool provides comprehensive insights into your Claude conversation history with powerful search and analysis capabilities.