"""Rich formatting for conversation display."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from .models import Conversation, ConversationMetadata, ConversationStats, Message, MessageType, ToolCall


class ConversationFormatter:
    """Rich formatter for conversations and metadata."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize formatter with optional console."""
        self.console = console or Console()
    
    def format_conversation_list(self, conversations: List[ConversationMetadata]) -> None:
        """Display a table of conversations."""
        if not conversations:
            self.console.print("[yellow]No conversations found.[/yellow]")
            return
        
        table = Table(title="Conversation Transcripts")
        table.add_column("Session ID", style="cyan", no_wrap=True)
        table.add_column("Start Time", style="green")
        table.add_column("Duration", style="blue")
        table.add_column("Messages", style="yellow", justify="right")
        table.add_column("Tools", style="red", justify="right")
        table.add_column("Size", style="magenta", justify="right")
        
        for conv in conversations:
            session_id = conv.session_id[:12] + "..." if len(conv.session_id) > 15 else conv.session_id
            start_time = conv.start_time.strftime("%Y-%m-%d %H:%M")
            duration = self._format_duration(conv.duration_seconds)
            size = self._format_file_size(conv.file_size_bytes)
            
            table.add_row(
                session_id,
                start_time,
                duration,
                str(conv.message_count),
                str(conv.tool_call_count),
                size,
            )
        
        self.console.print(table)
    
    def format_conversation_details(self, conversation: Conversation) -> None:
        """Display detailed conversation information."""
        metadata = conversation.metadata
        
        # Header panel
        header_info = [
            f"Session: {metadata.session_id}",
            f"Started: {metadata.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Duration: {self._format_duration(metadata.duration_seconds)}",
            f"Messages: {len(conversation.messages)}",
            f"Tool Calls: {len(conversation.tool_calls)}",
        ]
        
        header_panel = Panel(
            "\n".join(header_info),
            title="Conversation Details",
            border_style="blue",
        )
        self.console.print(header_panel)
        
        # Tool usage summary
        if conversation.tool_calls:
            self.format_tool_summary(conversation.tool_calls)
        
        # Messages
        self.console.print("\n[bold]Messages:[/bold]")
        for i, message in enumerate(conversation.messages):
            self._format_message(message, i + 1)
    
    def format_tool_summary(self, tool_calls: List[ToolCall]) -> None:
        """Display tool usage summary."""
        if not tool_calls:
            return
        
        tool_table = Table(title="Tool Usage", show_header=True, header_style="bold magenta")
        tool_table.add_column("Tool", style="cyan")
        tool_table.add_column("Status", style="green")
        tool_table.add_column("Target", style="yellow")
        tool_table.add_column("Duration", style="blue")
        
        for tool in tool_calls:
            status_color = "green" if tool.status.value == "completed" else "red" if tool.status.value == "error" else "yellow"
            status = f"[{status_color}]{tool.status.value}[/{status_color}]"
            
            duration = ""
            if tool.end_time:
                duration = self._format_duration((tool.end_time - tool.start_time).total_seconds())
            
            target = tool.target or ""
            if len(target) > 40:
                target = target[:37] + "..."
            
            tool_table.add_row(tool.name, status, target, duration)
        
        self.console.print(tool_table)
    
    def format_stats(self, stats: ConversationStats) -> None:
        """Display conversation statistics."""
        # Basic stats
        basic_info = [
            f"Total Conversations: {stats.total_conversations}",
            f"Total Messages: {stats.total_messages}",
            f"Total Tool Calls: {stats.total_tool_calls}",
            f"Average Duration: {self._format_duration(stats.average_duration)}",
        ]
        
        if stats.date_range:
            start, end = stats.date_range
            basic_info.append(f"Date Range: {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
        
        basic_panel = Panel(
            "\n".join(basic_info),
            title="Statistics",
            border_style="green",
        )
        self.console.print(basic_panel)
        
        # Tool usage
        if stats.tool_usage_counts:
            tool_table = Table(title="Tool Usage", show_header=True)
            tool_table.add_column("Tool", style="cyan")
            tool_table.add_column("Count", style="yellow", justify="right")
            
            # Sort by usage count
            sorted_tools = sorted(stats.tool_usage_counts.items(), key=lambda x: x[1], reverse=True)
            for tool_name, count in sorted_tools:
                tool_table.add_row(tool_name, str(count))
            
            self.console.print(tool_table)
        
        # Daily activity (if available)
        if stats.conversations_by_date and len(stats.conversations_by_date) > 1:
            self._format_daily_activity(stats.conversations_by_date)
    
    def format_search_results(self, conversations: List[ConversationMetadata], query: str) -> None:
        """Display search results."""
        if not conversations:
            self.console.print(f"[yellow]No conversations found matching '{query}'[/yellow]")
            return
        
        self.console.print(f"[green]Found {len(conversations)} conversations matching '{query}':[/green]\n")
        self.format_conversation_list(conversations)
    
    def _format_message(self, message: Message, index: int) -> None:
        """Format a single message."""
        timestamp = message.timestamp.strftime("%H:%M:%S")
        
        if message.type == MessageType.USER:
            # User message
            content = str(message.content)
            if len(content) > 200:
                content = content[:197] + "..."
            
            panel = Panel(
                content,
                title=f"[bold cyan]User #{index}[/bold cyan] @ {timestamp}",
                border_style="cyan",
                padding=(0, 1),
            )
            self.console.print(panel)
        
        elif message.type == MessageType.ASSISTANT:
            # Assistant response
            content = str(message.content)
            if isinstance(message.content, list):
                # Handle content blocks
                content = self._format_content_blocks(message.content)
            
            if len(content) > 300:
                content = content[:297] + "..."
            
            panel = Panel(
                content,
                title=f"[bold green]Assistant #{index}[/bold green] @ {timestamp}",
                border_style="green",
                padding=(0, 1),
            )
            self.console.print(panel)
        
        elif message.type in (MessageType.TOOL_USE, MessageType.TOOL_RESULT):
            # Tool calls - show abbreviated info
            if isinstance(message.content, dict):
                data = message.content
                tool_name = data.get("tool_name", "unknown")
                
                if message.type == MessageType.TOOL_USE:
                    title = f"[bold yellow]Tool Use: {tool_name}[/bold yellow] @ {timestamp}"
                    color = "yellow"
                else:
                    title = f"[bold blue]Tool Result: {tool_name}[/bold blue] @ {timestamp}"
                    color = "blue"
                
                # Show abbreviated content
                content_preview = str(data)[:150] + "..." if len(str(data)) > 150 else str(data)
                
                panel = Panel(
                    content_preview,
                    title=title,
                    border_style=color,
                    padding=(0, 1),
                )
                self.console.print(panel)
    
    def _format_content_blocks(self, content_blocks: List[Any]) -> str:
        """Format content blocks into readable text."""
        if not content_blocks:
            return ""
        
        parts = []
        for block in content_blocks:
            if isinstance(block, dict):
                if block.get("type") == "text" and "text" in block:
                    parts.append(block["text"])
                else:
                    # Other block types
                    block_type = block.get("type", "unknown")
                    parts.append(f"[{block_type}]")
            else:
                parts.append(str(block))
        
        return " ".join(parts)
    
    def _format_daily_activity(self, conversations_by_date: Dict[str, int]) -> None:
        """Display daily activity chart."""
        activity_table = Table(title="Daily Activity", show_header=True)
        activity_table.add_column("Date", style="cyan")
        activity_table.add_column("Conversations", style="yellow", justify="right")
        activity_table.add_column("Activity", style="green")
        
        sorted_dates = sorted(conversations_by_date.items())
        max_count = max(conversations_by_date.values()) if conversations_by_date else 1
        
        for date, count in sorted_dates[-14:]:  # Show last 14 days
            # Simple bar chart
            bar_length = int((count / max_count) * 20)
            bar = "█" * bar_length
            
            activity_table.add_row(date, str(count), bar)
        
        self.console.print(activity_table)
    
    @staticmethod
    def _format_duration(seconds: Optional[float]) -> str:
        """Format duration in a human-readable way."""
        if seconds is None:
            return "Unknown"
        
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    @staticmethod
    def _format_file_size(bytes_size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes_size < 1024:
                return f"{bytes_size:.1f}{unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f}TB"