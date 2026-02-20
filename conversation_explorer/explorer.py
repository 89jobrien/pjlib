"""Core conversation exploration functionality."""

import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .models import Conversation, ConversationMetadata, ConversationStats, SearchFilter
from .parser import TranscriptParser


class ConversationExplorer:
    """Main interface for exploring conversation transcripts."""
    
    def __init__(self, transcripts_dir: Path = None):
        """Initialize explorer with transcripts directory."""
        if transcripts_dir is None:
            transcripts_dir = Path.home() / ".claude" / "transcripts"
        
        self.transcripts_dir = Path(transcripts_dir)
        if not self.transcripts_dir.exists():
            raise FileNotFoundError(f"Transcripts directory not found: {transcripts_dir}")
        
        self.parser = TranscriptParser()
        self._metadata_cache: Dict[str, ConversationMetadata] = {}
    
    def list_conversations(
        self,
        limit: Optional[int] = None,
        sort_by: str = "timestamp",
        reverse: bool = True,
    ) -> List[ConversationMetadata]:
        """List available conversations with metadata."""
        transcript_files = list(self.transcripts_dir.glob("ses_*.jsonl"))
        
        if not transcript_files:
            return []
        
        # Get metadata for all files
        conversations = []
        for file_path in transcript_files:
            try:
                if str(file_path) not in self._metadata_cache:
                    metadata = self.parser.get_transcript_metadata(file_path)
                    self._metadata_cache[str(file_path)] = metadata
                else:
                    metadata = self._metadata_cache[str(file_path)]
                
                conversations.append(metadata)
            except Exception as e:
                print(f"Warning: Failed to get metadata for {file_path}: {e}")
                continue
        
        # Sort conversations
        if sort_by == "timestamp":
            conversations.sort(key=lambda x: x.start_time, reverse=reverse)
        elif sort_by == "duration":
            conversations.sort(key=lambda x: x.duration_seconds or 0, reverse=reverse)
        elif sort_by == "messages":
            conversations.sort(key=lambda x: x.message_count, reverse=reverse)
        elif sort_by == "size":
            conversations.sort(key=lambda x: x.file_size_bytes, reverse=reverse)
        
        if limit:
            conversations = conversations[:limit]
        
        return conversations
    
    def search_conversations(self, filter_criteria: SearchFilter) -> List[ConversationMetadata]:
        """Search conversations based on filter criteria."""
        all_conversations = self.list_conversations(sort_by="timestamp", reverse=True)
        matched_conversations = []
        
        for metadata in all_conversations:
            if self._matches_filter(metadata, filter_criteria):
                matched_conversations.append(metadata)
        
        return matched_conversations
    
    def get_conversation(self, session_id: str) -> Optional[Conversation]:
        """Get full conversation by session ID."""
        # Find the transcript file
        transcript_files = list(self.transcripts_dir.glob(f"ses_{session_id}*.jsonl"))
        
        if not transcript_files:
            return None
        
        try:
            return self.parser.parse_transcript(transcript_files[0])
        except Exception as e:
            print(f"Error parsing conversation {session_id}: {e}")
            return None
    
    def search_content(self, query: str, case_sensitive: bool = False) -> List[ConversationMetadata]:
        """Search conversation content for text."""
        if not query.strip():
            return []
        
        matched_conversations = []
        pattern = re.compile(query if case_sensitive else query, re.IGNORECASE if not case_sensitive else 0)
        
        for file_path in self.transcripts_dir.glob("ses_*.jsonl"):
            try:
                # Quick text search in file
                content = file_path.read_text(encoding="utf-8")
                if pattern.search(content):
                    metadata = self.parser.get_transcript_metadata(file_path)
                    matched_conversations.append(metadata)
            except Exception as e:
                print(f"Warning: Failed to search {file_path}: {e}")
                continue
        
        return matched_conversations
    
    def get_stats(self, conversations: Optional[List[ConversationMetadata]] = None) -> ConversationStats:
        """Generate statistics for conversations."""
        if conversations is None:
            conversations = self.list_conversations()
        
        if not conversations:
            return ConversationStats(
                total_conversations=0,
                total_messages=0,
                total_tool_calls=0,
                unique_tools_used=[],
            )
        
        total_messages = sum(conv.message_count for conv in conversations)
        total_tool_calls = sum(conv.tool_call_count for conv in conversations)
        
        # Calculate average duration
        durations = [conv.duration_seconds for conv in conversations if conv.duration_seconds]
        avg_duration = sum(durations) / len(durations) if durations else None
        
        # Date range
        start_times = [conv.start_time for conv in conversations if conv.start_time]
        date_range = None
        if start_times:
            date_range = (min(start_times), max(start_times))
        
        # Conversations by date
        conversations_by_date = defaultdict(int)
        for conv in conversations:
            if conv.start_time:
                date_key = conv.start_time.strftime("%Y-%m-%d")
                conversations_by_date[date_key] += 1
        
        # Tool usage analysis (requires parsing conversations)
        tool_usage_counts = defaultdict(int)
        unique_tools = set()
        
        # Sample a few conversations to get tool usage patterns
        sample_size = min(10, len(conversations))
        for metadata in conversations[:sample_size]:
            try:
                file_path = Path(metadata.file_path)
                conversation = self.parser.parse_transcript(file_path)
                
                for tool_call in conversation.tool_calls:
                    tool_usage_counts[tool_call.name] += 1
                    unique_tools.add(tool_call.name)
            except Exception:
                # Skip failed parses for stats
                continue
        
        return ConversationStats(
            total_conversations=len(conversations),
            total_messages=total_messages,
            total_tool_calls=total_tool_calls,
            unique_tools_used=list(unique_tools),
            average_duration=avg_duration,
            date_range=date_range,
            tool_usage_counts=dict(tool_usage_counts),
            conversations_by_date=dict(conversations_by_date),
        )
    
    def get_recent_conversations(self, days: int = 7, limit: int = 10) -> List[ConversationMetadata]:
        """Get recent conversations from the last N days."""
        from datetime import timezone, timedelta
        
        # Create timezone-aware cutoff time
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(days=days)
        
        filter_criteria = SearchFilter(start_date=cutoff_time)
        recent = self.search_conversations(filter_criteria)
        
        # Sort by timestamp descending
        recent.sort(key=lambda x: x.start_time, reverse=True)
        
        return recent[:limit] if limit else recent
    
    def find_conversations_with_tools(self, tool_names: List[str]) -> List[ConversationMetadata]:
        """Find conversations that used specific tools."""
        matched_conversations = []
        
        for file_path in self.transcripts_dir.glob("ses_*.jsonl"):
            try:
                # Quick scan for tool names in file
                content = file_path.read_text(encoding="utf-8")
                if any(tool_name in content for tool_name in tool_names):
                    metadata = self.parser.get_transcript_metadata(file_path)
                    matched_conversations.append(metadata)
            except Exception as e:
                print(f"Warning: Failed to scan {file_path}: {e}")
                continue
        
        return matched_conversations
    
    def _matches_filter(self, metadata: ConversationMetadata, filter_criteria: SearchFilter) -> bool:
        """Check if conversation metadata matches filter criteria."""
        # Date filters
        if filter_criteria.start_date and metadata.start_time < filter_criteria.start_date:
            return False
        
        if filter_criteria.end_date and metadata.start_time > filter_criteria.end_date:
            return False
        
        # Duration filters
        if filter_criteria.min_duration and (
            metadata.duration_seconds is None or metadata.duration_seconds < filter_criteria.min_duration
        ):
            return False
        
        if filter_criteria.max_duration and (
            metadata.duration_seconds is None or metadata.duration_seconds > filter_criteria.max_duration
        ):
            return False
        
        # Message count filters
        if filter_criteria.min_messages and metadata.message_count < filter_criteria.min_messages:
            return False
        
        if filter_criteria.max_messages and metadata.message_count > filter_criteria.max_messages:
            return False
        
        # Text query filter (requires full file search)
        if filter_criteria.text_query:
            try:
                file_path = Path(metadata.file_path)
                content = file_path.read_text(encoding="utf-8")
                if filter_criteria.text_query.lower() not in content.lower():
                    return False
            except Exception:
                return False
        
        # Tool usage filter (requires scanning file content)
        if filter_criteria.tools_used:
            try:
                file_path = Path(metadata.file_path)
                content = file_path.read_text(encoding="utf-8")
                if not any(tool_name in content for tool_name in filter_criteria.tools_used):
                    return False
            except Exception:
                return False
        
        return True