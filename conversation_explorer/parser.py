"""Parser for JSONL conversation transcripts."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from .models import (
    Conversation,
    ConversationMetadata,
    ContentBlock,
    Message,
    MessageType,
    ToolCall,
    ToolStatus,
)


class TranscriptParser:
    """Parser for JSONL transcript files."""
    
    @staticmethod
    def extract_session_id(file_path: Path) -> str:
        """Extract session ID from transcript filename."""
        # Extract from pattern like ses_3f8a7b247ffeGcVIx09Dza7mBa.jsonl
        match = re.search(r'ses_([a-zA-Z0-9_]+)\.jsonl$', file_path.name)
        return match.group(1) if match else file_path.stem
    
    @staticmethod
    def extract_target(tool_name: str, tool_input: Optional[Dict[str, Any]]) -> Optional[str]:
        """Extract target information from tool input."""
        if not tool_input:
            return None
            
        # Common patterns based on the TypeScript implementation
        if tool_name in ("read_files", "edit_files", "create_file"):
            # Check for various file path fields
            for field in ("file_path", "path", "files"):
                if field in tool_input:
                    value = tool_input[field]
                    if isinstance(value, str):
                        return value
                    elif isinstance(value, list) and value:
                        return str(value[0])  # First file if list
        elif tool_name in ("grep", "file_glob"):
            # Pattern-based tools
            for field in ("queries", "patterns", "query", "pattern"):
                if field in tool_input:
                    value = tool_input[field]
                    if isinstance(value, str):
                        return value
                    elif isinstance(value, list) and value:
                        return str(value[0])
        elif tool_name == "run_shell_command":
            # Shell commands - truncate for readability
            cmd = tool_input.get("command", "")
            if isinstance(cmd, str):
                return cmd[:50] + ("..." if len(cmd) > 50 else "")
        
        return None
    
    @classmethod
    def parse_transcript(cls, file_path: Path) -> Conversation:
        """Parse a JSONL transcript file into a Conversation object."""
        if not file_path.exists():
            raise FileNotFoundError(f"Transcript file not found: {file_path}")
        
        # Initialize metadata
        session_id = cls.extract_session_id(file_path)
        file_size = file_path.stat().st_size
        
        metadata = ConversationMetadata(
            session_id=session_id,
            file_path=str(file_path),
            start_time=datetime.now(),  # Will be updated from first message
            file_size_bytes=file_size,
        )
        
        conversation = Conversation(metadata=metadata)
        tool_map: Dict[str, ToolCall] = {}
        
        # Parse each line
        line_count = 0
        for line_data in cls._parse_jsonl_file(file_path):
            line_count += 1
            
            try:
                message = cls._parse_message_line(line_data)
                if message:
                    conversation.messages.append(message)
                    
                    # Update metadata with first timestamp
                    if line_count == 1:
                        metadata.start_time = message.timestamp
                    
                    # Track latest timestamp
                    metadata.end_time = message.timestamp
                    
                    # Process tool calls and results
                    cls._process_tool_calls(message, tool_map, conversation.tool_calls)
                    
            except Exception as e:
                # Log but continue parsing other lines
                print(f"Warning: Failed to parse line {line_count} in {file_path}: {e}")
                continue
        
        # Update final metadata
        metadata.message_count = len(conversation.messages)
        metadata.tool_call_count = len(conversation.tool_calls)
        if metadata.end_time and metadata.start_time:
            metadata.duration_seconds = (
                metadata.end_time - metadata.start_time
            ).total_seconds()
        
        return conversation
    
    @staticmethod
    def _parse_jsonl_file(file_path: Path) -> Generator[Dict[str, Any], None, None]:
        """Parse JSONL file line by line."""
        try:
            with file_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError as e:
                        print(f"Warning: Invalid JSON in {file_path}: {e}")
                        continue
        except UnicodeDecodeError as e:
            print(f"Warning: Encoding error in {file_path}: {e}")
            return
    
    @classmethod
    def _parse_message_line(cls, line_data: Dict[str, Any]) -> Optional[Message]:
        """Parse a single line into a Message object."""
        if "type" not in line_data:
            return None
        
        msg_type = line_data["type"]
        timestamp_str = line_data.get("timestamp")
        
        if not timestamp_str:
            return None
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
        
        # Handle different message types based on actual format
        if msg_type == "user":
            content = line_data.get("content", "")
            return Message(
                type=MessageType.USER,
                timestamp=timestamp,
                content=content,
            )
        
        elif msg_type == "tool_use":
            # Tool use messages - store as dict for tool processing
            return Message(
                type=MessageType.TOOL_USE,
                timestamp=timestamp,
                content=line_data,
            )
        
        elif msg_type == "tool_result":
            # Tool result messages - store as dict for tool processing
            return Message(
                type=MessageType.TOOL_RESULT,
                timestamp=timestamp,
                content=line_data,
            )
        
        else:
            # Assistant or other message types
            content = line_data.get("content", "")
            return Message(
                type=MessageType.ASSISTANT,
                timestamp=timestamp,
                content=content,
                role=line_data.get("role"),
            )
    
    @classmethod
    def _process_tool_calls(
        cls,
        message: Message,
        tool_map: Dict[str, ToolCall],
        tool_calls: List[ToolCall],
    ) -> None:
        """Process tool calls and results from messages."""
        if message.type == MessageType.TOOL_USE:
            # Extract tool use information from actual format
            if isinstance(message.content, dict):
                data = message.content
                tool_name = data.get("tool_name")
                tool_input = data.get("tool_input", {})
                
                if tool_name:
                    # Use a composite key since actual format doesn't have tool_use_id
                    tool_id = f"{tool_name}_{message.timestamp.isoformat()}"
                    target = cls.extract_target(tool_name, tool_input)
                    
                    tool_call = ToolCall(
                        id=tool_id,
                        name=tool_name,
                        input=tool_input,
                        start_time=message.timestamp,
                        target=target,
                    )
                    
                    tool_map[tool_id] = tool_call
                    tool_calls.append(tool_call)
        
        elif message.type == MessageType.TOOL_RESULT:
            # Update tool call with result - match by tool name and find most recent
            if isinstance(message.content, dict):
                data = message.content
                tool_name = data.get("tool_name")
                
                if tool_name:
                    # Find the most recent tool call with this name that doesn't have an end time
                    matching_tool = None
                    for tool_call in reversed(tool_calls):
                        if tool_call.name == tool_name and tool_call.end_time is None:
                            matching_tool = tool_call
                            break
                    
                    if matching_tool:
                        matching_tool.end_time = message.timestamp
                        matching_tool.status = (
                            ToolStatus.ERROR if data.get("is_error") else ToolStatus.COMPLETED
                        )
                        
                        if data.get("is_error") or data.get("tool_output", {}).get("error"):
                            error_msg = data.get("tool_output", {}).get("error", "Unknown error")
                            matching_tool.error = str(error_msg)
    
    @classmethod
    def get_transcript_metadata(cls, file_path: Path) -> ConversationMetadata:
        """Get metadata for a transcript without full parsing."""
        if not file_path.exists():
            raise FileNotFoundError(f"Transcript file not found: {file_path}")
        
        session_id = cls.extract_session_id(file_path)
        file_size = file_path.stat().st_size
        
        # Quick scan for basic info
        start_time = None
        end_time = None
        message_count = 0
        tool_count = 0
        
        for line_data in cls._parse_jsonl_file(file_path):
            message_count += 1
            timestamp_str = line_data.get("timestamp")
            
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    if start_time is None:
                        start_time = timestamp
                    end_time = timestamp
                except (ValueError, AttributeError):
                    pass
            
            if line_data.get("type") == "tool_use":
                tool_count += 1
        
        duration_seconds = None
        if start_time and end_time:
            duration_seconds = (end_time - start_time).total_seconds()
        
        return ConversationMetadata(
            session_id=session_id,
            file_path=str(file_path),
            start_time=start_time or datetime.now(),
            end_time=end_time,
            message_count=message_count,
            tool_call_count=tool_count,
            file_size_bytes=file_size,
            duration_seconds=duration_seconds,
        )