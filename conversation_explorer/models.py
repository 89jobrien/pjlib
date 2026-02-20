"""Data models for conversation exploration."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Types of messages in a conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"


class ToolStatus(str, Enum):
    """Status of tool execution."""
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class ContentBlock(BaseModel):
    """A content block within a message."""
    type: str
    text: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    input: Optional[Dict[str, Any]] = None
    tool_use_id: Optional[str] = None
    content: Optional[str] = None
    is_error: Optional[bool] = False


class Message(BaseModel):
    """A message in a conversation."""
    type: MessageType
    timestamp: datetime
    content: Any  # Allow any content type for flexibility
    role: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


class ToolCall(BaseModel):
    """Information about a tool call."""
    id: str
    name: str
    input: Optional[Dict[str, Any]] = None
    status: ToolStatus = ToolStatus.RUNNING
    start_time: datetime
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    target: Optional[str] = None  # Extracted target like file path


class ConversationMetadata(BaseModel):
    """Metadata about a conversation."""
    session_id: str
    file_path: str
    start_time: datetime
    end_time: Optional[datetime] = None
    message_count: int = 0
    tool_call_count: int = 0
    file_size_bytes: int = 0
    duration_seconds: Optional[float] = None


class Conversation(BaseModel):
    """A complete conversation with messages and metadata."""
    metadata: ConversationMetadata
    messages: List[Message] = Field(default_factory=list)
    tool_calls: List[ToolCall] = Field(default_factory=list)
    
    @property
    def duration(self) -> Optional[float]:
        """Get conversation duration in seconds."""
        if self.metadata.end_time and self.metadata.start_time:
            return (self.metadata.end_time - self.metadata.start_time).total_seconds()
        return None
    
    @property
    def user_message_count(self) -> int:
        """Count of user messages."""
        return sum(1 for msg in self.messages if msg.type == MessageType.USER)
    
    @property
    def assistant_message_count(self) -> int:
        """Count of assistant messages."""
        return sum(1 for msg in self.messages if msg.type == MessageType.ASSISTANT)


class SearchFilter(BaseModel):
    """Filter criteria for searching conversations."""
    text_query: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_duration: Optional[float] = None
    max_duration: Optional[float] = None
    tools_used: Optional[List[str]] = None
    min_messages: Optional[int] = None
    max_messages: Optional[int] = None
    has_errors: Optional[bool] = None


class ConversationStats(BaseModel):
    """Statistics about conversations."""
    total_conversations: int
    total_messages: int
    total_tool_calls: int
    unique_tools_used: List[str]
    average_duration: Optional[float] = None
    date_range: Optional[tuple[datetime, datetime]] = None
    tool_usage_counts: Dict[str, int] = Field(default_factory=dict)
    conversations_by_date: Dict[str, int] = Field(default_factory=dict)