"""Command-line interface for conversation explorer."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from .explorer import ConversationExplorer
from .formatter import ConversationFormatter
from .models import SearchFilter


@click.group()
@click.option(
    "--transcripts-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Directory containing transcript files",
)
@click.pass_context
def cli(ctx, transcripts_dir):
    """Explore conversation transcripts from Claude sessions."""
    ctx.ensure_object(dict)
    
    if transcripts_dir:
        transcripts_path = Path(transcripts_dir)
    else:
        transcripts_path = Path.home() / ".claude" / "transcripts"
    
    try:
        ctx.obj["explorer"] = ConversationExplorer(transcripts_path)
        ctx.obj["formatter"] = ConversationFormatter()
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.option("--limit", "-l", type=int, default=20, help="Limit number of results")
@click.option(
    "--sort-by",
    "-s",
    type=click.Choice(["timestamp", "duration", "messages", "size"]),
    default="timestamp",
    help="Sort conversations by field",
)
@click.option("--reverse/--no-reverse", default=True, help="Sort in reverse order")
@click.pass_context
def list(ctx, limit, sort_by, reverse):
    """List all conversations."""
    explorer = ctx.obj["explorer"]
    formatter = ctx.obj["formatter"]
    
    conversations = explorer.list_conversations(limit=limit, sort_by=sort_by, reverse=reverse)
    formatter.format_conversation_list(conversations)


@cli.command()
@click.argument("session_id")
@click.option("--full/--summary", default=False, help="Show full conversation or just summary")
@click.pass_context
def show(ctx, session_id, full):
    """Show details of a specific conversation."""
    explorer = ctx.obj["explorer"]
    formatter = ctx.obj["formatter"]
    
    conversation = explorer.get_conversation(session_id)
    if not conversation:
        click.echo(f"Conversation '{session_id}' not found.", err=True)
        return
    
    if full:
        formatter.format_conversation_details(conversation)
    else:
        # Show just metadata and tool summary
        formatter.console.print(f"[bold]Session: {conversation.metadata.session_id}[/bold]")
        formatter.console.print(f"Started: {conversation.metadata.start_time}")
        formatter.console.print(f"Duration: {formatter._format_duration(conversation.metadata.duration_seconds)}")
        formatter.console.print(f"Messages: {len(conversation.messages)}")
        
        if conversation.tool_calls:
            formatter.format_tool_summary(conversation.tool_calls)


@cli.command()
@click.argument("query")
@click.option("--case-sensitive/--ignore-case", default=False, help="Case sensitive search")
@click.option("--limit", "-l", type=int, help="Limit number of results")
@click.pass_context
def search(ctx, query, case_sensitive, limit):
    """Search conversations for text content."""
    explorer = ctx.obj["explorer"]
    formatter = ctx.obj["formatter"]
    
    conversations = explorer.search_content(query, case_sensitive=case_sensitive)
    
    if limit:
        conversations = conversations[:limit]
    
    formatter.format_search_results(conversations, query)


@cli.command()
@click.option("--days", "-d", type=int, default=7, help="Number of days to look back")
@click.option("--limit", "-l", type=int, default=10, help="Maximum number of conversations")
@click.pass_context
def recent(ctx, days, limit):
    """Show recent conversations from the last N days."""
    explorer = ctx.obj["explorer"]
    formatter = ctx.obj["formatter"]
    
    conversations = explorer.get_recent_conversations(days=days, limit=limit)
    
    if conversations:
        formatter.console.print(f"[green]Recent conversations (last {days} days):[/green]\n")
        formatter.format_conversation_list(conversations)
    else:
        formatter.console.print(f"[yellow]No conversations found in the last {days} days.[/yellow]")


@cli.command()
@click.option("--start-date", type=click.DateTime(["%Y-%m-%d"]), help="Start date (YYYY-MM-DD)")
@click.option("--end-date", type=click.DateTime(["%Y-%m-%d"]), help="End date (YYYY-MM-DD)")
@click.option("--min-duration", type=float, help="Minimum duration in seconds")
@click.option("--max-duration", type=float, help="Maximum duration in seconds")
@click.option("--min-messages", type=int, help="Minimum number of messages")
@click.option("--max-messages", type=int, help="Maximum number of messages")
@click.option("--tools", help="Comma-separated list of tools used")
@click.option("--text", help="Text query to search for")
@click.option("--errors/--no-errors", default=None, help="Filter conversations with/without errors")
@click.pass_context
def filter(ctx, start_date, end_date, min_duration, max_duration, min_messages, max_messages, tools, text, errors):
    """Filter conversations with advanced criteria."""
    explorer = ctx.obj["explorer"]
    formatter = ctx.obj["formatter"]
    
    # Build filter criteria
    filter_criteria = SearchFilter()
    
    if start_date:
        filter_criteria.start_date = start_date
    if end_date:
        filter_criteria.end_date = end_date
    if min_duration:
        filter_criteria.min_duration = min_duration
    if max_duration:
        filter_criteria.max_duration = max_duration
    if min_messages:
        filter_criteria.min_messages = min_messages
    if max_messages:
        filter_criteria.max_messages = max_messages
    if text:
        filter_criteria.text_query = text
    if tools:
        filter_criteria.tools_used = [t.strip() for t in tools.split(",")]
    if errors is not None:
        filter_criteria.has_errors = errors
    
    conversations = explorer.search_conversations(filter_criteria)
    
    if conversations:
        formatter.console.print(f"[green]Found {len(conversations)} matching conversations:[/green]\n")
        formatter.format_conversation_list(conversations)
    else:
        formatter.console.print("[yellow]No conversations match the specified criteria.[/yellow]")


@cli.command()
@click.argument("tool_names", nargs=-1, required=True)
@click.pass_context
def tools(ctx, tool_names):
    """Find conversations that used specific tools."""
    explorer = ctx.obj["explorer"]
    formatter = ctx.obj["formatter"]
    
    conversations = explorer.find_conversations_with_tools(list(tool_names))
    
    if conversations:
        formatter.console.print(f"[green]Conversations using tools {', '.join(tool_names)}:[/green]\n")
        formatter.format_conversation_list(conversations)
    else:
        formatter.console.print(f"[yellow]No conversations found using tools: {', '.join(tool_names)}[/yellow]")


@cli.command()
@click.option("--detailed/--summary", default=False, help="Show detailed statistics")
@click.pass_context
def stats(ctx, detailed):
    """Show conversation statistics."""
    explorer = ctx.obj["explorer"]
    formatter = ctx.obj["formatter"]
    
    stats = explorer.get_stats()
    formatter.format_stats(stats)
    
    if detailed:
        # Show additional detailed stats
        console = Console()
        console.print("\n[bold]Additional Details:[/bold]")
        
        # Most active days
        if stats.conversations_by_date:
            sorted_dates = sorted(stats.conversations_by_date.items(), key=lambda x: x[1], reverse=True)
            console.print(f"Most active day: {sorted_dates[0][0]} ({sorted_dates[0][1]} conversations)")
        
        # Tool analysis
        if stats.tool_usage_counts:
            total_tool_calls = sum(stats.tool_usage_counts.values())
            most_used_tool = max(stats.tool_usage_counts.items(), key=lambda x: x[1])
            console.print(f"Most used tool: {most_used_tool[0]} ({most_used_tool[1]} times)")
            console.print(f"Tool diversity: {len(stats.unique_tools_used)} unique tools")


@cli.command()
@click.argument("session_id")
@click.option("--output", "-o", help="Output file path")
@click.option("--format", "output_format", type=click.Choice(["json", "txt"]), default="txt", help="Output format")
@click.pass_context
def export(ctx, session_id, output, output_format):
    """Export a conversation to a file."""
    explorer = ctx.obj["explorer"]
    
    conversation = explorer.get_conversation(session_id)
    if not conversation:
        click.echo(f"Conversation '{session_id}' not found.", err=True)
        return
    
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = "json" if output_format == "json" else "txt"
        output = f"conversation_{session_id[:8]}_{timestamp}.{extension}"
    
    output_path = Path(output)
    
    if output_format == "json":
        # Export as JSON
        import json
        data = {
            "metadata": conversation.metadata.dict(),
            "messages": [msg.dict() for msg in conversation.messages],
            "tool_calls": [tool.dict() for tool in conversation.tool_calls],
        }
        
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    
    else:
        # Export as text
        with output_path.open("w", encoding="utf-8") as f:
            f.write(f"Conversation: {conversation.metadata.session_id}\n")
            f.write(f"Started: {conversation.metadata.start_time}\n")
            f.write(f"Duration: {conversation.metadata.duration_seconds}s\n")
            f.write(f"Messages: {len(conversation.messages)}\n")
            f.write(f"Tool Calls: {len(conversation.tool_calls)}\n")
            f.write("\n" + "="*60 + "\n\n")
            
            for i, message in enumerate(conversation.messages, 1):
                timestamp = message.timestamp.strftime("%H:%M:%S")
                f.write(f"[{i}] {message.type.value.upper()} @ {timestamp}\n")
                f.write("-" * 40 + "\n")
                f.write(str(message.content) + "\n\n")
    
    click.echo(f"Conversation exported to: {output_path}")


if __name__ == "__main__":
    cli()