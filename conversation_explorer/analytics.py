"""Advanced analytics for conversation exploration."""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from .models import Conversation, ConversationMetadata, ToolCall


class ConversationAnalytics:
    """Advanced analytics for conversation patterns."""
    
    @staticmethod
    def analyze_tool_patterns(conversations: List[Conversation]) -> Dict:
        """Analyze tool usage patterns across conversations."""
        tool_sequences = []
        tool_cooccurrence = defaultdict(lambda: defaultdict(int))
        tool_success_rates = defaultdict(lambda: {"success": 0, "total": 0})
        
        for conv in conversations:
            if not conv.tool_calls:
                continue
                
            # Extract tool sequence for this conversation
            sequence = [tool.name for tool in conv.tool_calls]
            tool_sequences.append(sequence)
            
            # Analyze tool co-occurrence (tools used together)
            unique_tools = list(set(sequence))
            for i, tool1 in enumerate(unique_tools):
                for tool2 in unique_tools[i+1:]:
                    tool_cooccurrence[tool1][tool2] += 1
                    tool_cooccurrence[tool2][tool1] += 1
            
            # Track success rates
            for tool in conv.tool_calls:
                tool_success_rates[tool.name]["total"] += 1
                if tool.status.value == "completed":
                    tool_success_rates[tool.name]["success"] += 1
        
        # Find common tool sequences
        common_sequences = {}
        for seq in tool_sequences:
            if len(seq) >= 2:
                for i in range(len(seq) - 1):
                    pair = (seq[i], seq[i + 1])
                    common_sequences[pair] = common_sequences.get(pair, 0) + 1
        
        return {
            "tool_cooccurrence": dict(tool_cooccurrence),
            "common_sequences": sorted(common_sequences.items(), key=lambda x: x[1], reverse=True)[:10],
            "success_rates": {
                tool: round(stats["success"] / stats["total"] * 100, 1)
                for tool, stats in tool_success_rates.items()
                if stats["total"] >= 3  # Only include tools used at least 3 times
            }
        }
    
    @staticmethod
    def analyze_temporal_patterns(conversations: List[ConversationMetadata]) -> Dict:
        """Analyze temporal patterns in conversation activity."""
        hourly_activity = defaultdict(int)
        daily_activity = defaultdict(int)
        duration_distribution = defaultdict(int)
        
        for conv in conversations:
            if not conv.start_time:
                continue
                
            # Hour of day analysis
            hour = conv.start_time.hour
            hourly_activity[hour] += 1
            
            # Day of week analysis  
            day_name = conv.start_time.strftime("%A")
            daily_activity[day_name] += 1
            
            # Duration distribution
            if conv.duration_seconds:
                if conv.duration_seconds < 60:
                    duration_distribution["<1 min"] += 1
                elif conv.duration_seconds < 300:
                    duration_distribution["1-5 min"] += 1
                elif conv.duration_seconds < 900:
                    duration_distribution["5-15 min"] += 1
                elif conv.duration_seconds < 3600:
                    duration_distribution["15-60 min"] += 1
                else:
                    duration_distribution[">1 hour"] += 1
        
        # Find peak hours
        peak_hour = max(hourly_activity.items(), key=lambda x: x[1]) if hourly_activity else (0, 0)
        peak_day = max(daily_activity.items(), key=lambda x: x[1]) if daily_activity else ("", 0)
        
        return {
            "hourly_activity": dict(hourly_activity),
            "daily_activity": dict(daily_activity),
            "duration_distribution": dict(duration_distribution),
            "peak_hour": peak_hour,
            "peak_day": peak_day
        }
    
    @staticmethod
    def find_conversation_clusters(conversations: List[ConversationMetadata], 
                                 time_gap_hours: int = 2) -> List[List[str]]:
        """Find clusters of conversations that happened close together."""
        if not conversations:
            return []
        
        # Sort by start time
        sorted_convs = sorted(conversations, key=lambda x: x.start_time or datetime.min)
        
        clusters = []
        current_cluster = [sorted_convs[0].session_id]
        
        for i in range(1, len(sorted_convs)):
            prev_conv = sorted_convs[i-1]
            curr_conv = sorted_convs[i]
            
            if (not prev_conv.start_time or not curr_conv.start_time):
                continue
                
            time_diff = (curr_conv.start_time - prev_conv.start_time).total_seconds() / 3600
            
            if time_diff <= time_gap_hours:
                current_cluster.append(curr_conv.session_id)
            else:
                if len(current_cluster) > 1:
                    clusters.append(current_cluster)
                current_cluster = [curr_conv.session_id]
        
        # Don't forget the last cluster
        if len(current_cluster) > 1:
            clusters.append(current_cluster)
        
        return clusters
    
    @staticmethod
    def analyze_conversation_complexity(conversations: List[Conversation]) -> Dict:
        """Analyze complexity metrics of conversations."""
        complexity_metrics = {
            "avg_tools_per_conversation": 0,
            "avg_messages_per_conversation": 0,
            "conversations_with_errors": 0,
            "most_complex_conversations": [],
            "tool_diversity_scores": {}
        }
        
        if not conversations:
            return complexity_metrics
        
        total_tools = sum(len(conv.tool_calls) for conv in conversations)
        total_messages = sum(len(conv.messages) for conv in conversations)
        error_count = 0
        
        # Calculate complexity scores for each conversation
        complexity_scores = []
        
        for conv in conversations:
            # Complexity based on tools, messages, duration, and unique tools
            tool_count = len(conv.tool_calls)
            message_count = len(conv.messages)
            unique_tools = len(set(tool.name for tool in conv.tool_calls))
            duration = conv.duration or 0
            
            # Check for errors
            has_errors = any(tool.status.value == "error" for tool in conv.tool_calls)
            if has_errors:
                error_count += 1
            
            # Simple complexity score
            complexity_score = (
                tool_count * 2 +           # Tools are weighted heavily
                message_count * 1 +        # Messages contribute
                unique_tools * 3 +         # Tool diversity is important
                (duration / 60) * 0.5      # Duration contributes but less
            )
            
            complexity_scores.append({
                "session_id": conv.metadata.session_id,
                "score": complexity_score,
                "tools": tool_count,
                "messages": message_count,
                "unique_tools": unique_tools,
                "duration_minutes": duration / 60 if duration else 0
            })
        
        # Sort by complexity
        complexity_scores.sort(key=lambda x: x["score"], reverse=True)
        
        complexity_metrics.update({
            "avg_tools_per_conversation": round(total_tools / len(conversations), 1),
            "avg_messages_per_conversation": round(total_messages / len(conversations), 1),
            "conversations_with_errors": error_count,
            "error_rate": round(error_count / len(conversations) * 100, 1),
            "most_complex_conversations": complexity_scores[:5],
            "least_complex_conversations": complexity_scores[-3:] if len(complexity_scores) > 3 else []
        })
        
        return complexity_metrics