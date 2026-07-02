"""
Context management for AI agents.

Builds and manages context for LLM calls including previous artifacts,
conversation history, and domain information.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ContextItem:
    """A single item in the execution context."""
    name: str
    content: str
    type: str  # "artifact", "requirement", "design", "code", etc.
    source: Optional[str] = None
    timestamp: Optional[datetime] = None


class ContextBuilder:
    """Builds execution context for AI agents."""

    def __init__(self, max_context_tokens: int = 8000):
        """
        Initialize context builder.

        Args:
            max_context_tokens: Maximum tokens to include in context
        """
        self.max_context_tokens = max_context_tokens
        self.items: List[ContextItem] = []
        self.current_tokens = 0

    def add_artifact(
        self,
        name: str,
        content: str,
        source: Optional[str] = None
    ) -> None:
        """
        Add an artifact to the context.

        Args:
            name: Artifact name
            content: Artifact content
            source: Optional source identifier
        """
        item = ContextItem(
            name=name,
            content=content,
            type="artifact",
            source=source,
            timestamp=datetime.now()
        )
        
        self.items.append(item)
        self.current_tokens += self._estimate_tokens(content)
        
        logger.info(f"Added artifact '{name}' to context")

    def add_requirement(
        self,
        name: str,
        content: str,
        source: Optional[str] = None
    ) -> None:
        """Add a requirement to the context."""
        item = ContextItem(
            name=name,
            content=content,
            type="requirement",
            source=source,
            timestamp=datetime.now()
        )
        
        self.items.append(item)
        self.current_tokens += self._estimate_tokens(content)
        
        logger.info(f"Added requirement '{name}' to context")

    def add_design(
        self,
        name: str,
        content: str,
        source: Optional[str] = None
    ) -> None:
        """Add a design artifact to the context."""
        item = ContextItem(
            name=name,
            content=content,
            type="design",
            source=source,
            timestamp=datetime.now()
        )
        
        self.items.append(item)
        self.current_tokens += self._estimate_tokens(content)
        
        logger.info(f"Added design '{name}' to context")

    def add_code(
        self,
        name: str,
        content: str,
        language: str = "python",
        source: Optional[str] = None
    ) -> None:
        """Add code to the context."""
        item = ContextItem(
            name=name,
            content=content,
            type=f"code_{language}",
            source=source,
            timestamp=datetime.now()
        )
        
        self.items.append(item)
        self.current_tokens += self._estimate_tokens(content)
        
        logger.info(f"Added {language} code '{name}' to context")

    def add_previous_phase_output(
        self,
        phase_name: str,
        content: str
    ) -> None:
        """
        Add output from a previous phase.

        Args:
            phase_name: Name of the previous phase
            content: Phase output content
        """
        item = ContextItem(
            name=f"previous_{phase_name}",
            content=content,
            type="phase_output",
            source=phase_name,
            timestamp=datetime.now()
        )
        
        self.items.append(item)
        self.current_tokens += self._estimate_tokens(content)
        
        logger.info(f"Added output from phase '{phase_name}' to context")

    def add_conversation_history(
        self,
        messages: List[Dict[str, str]]
    ) -> None:
        """
        Add conversation history.

        Args:
            messages: List of messages with 'role' and 'content'
        """
        for i, message in enumerate(messages):
            item = ContextItem(
                name=f"message_{i}",
                content=message.get("content", ""),
                type="conversation",
                source=message.get("role", "unknown"),
                timestamp=datetime.now()
            )
            self.items.append(item)
            self.current_tokens += self._estimate_tokens(message.get("content", ""))
        
        logger.info(f"Added {len(messages)} message(s) to context")

    def build_system_prompt(self) -> str:
        """
        Build a system prompt incorporating all context.

        Returns:
            System prompt string
        """
        prompt_parts = [
            "You are an expert software architect and developer.",
            "You are part of an AI Software Factory that converts business requirements",
            "into production-ready software through an automated SDLC pipeline.",
            "",
            "CONTEXT FROM PREVIOUS PHASES:"
        ]
        
        # Add artifacts in reverse chronological order (most recent first)
        for item in reversed(self.items):
            if item.type == "artifact":
                prompt_parts.append(f"\n## {item.name}")
                prompt_parts.append(item.content[:500])  # Limit size
        
        return "\n".join(prompt_parts)

    def get_all_context(self) -> str:
        """
        Get all context as a formatted string.

        Returns:
            Formatted context string
        """
        lines = ["=== EXECUTION CONTEXT ===\n"]
        
        for i, item in enumerate(self.items, 1):
            lines.append(f"{i}. [{item.type}] {item.name}")
            if item.source:
                lines.append(f"   Source: {item.source}")
            if item.timestamp:
                lines.append(f"   Added: {item.timestamp.isoformat()}")
            lines.append(f"   Content preview: {item.content[:100]}...\n")
        
        return "\n".join(lines)

    def get_context_by_type(self, type_filter: str) -> List[ContextItem]:
        """
        Get context items of a specific type.

        Args:
            type_filter: Type to filter for

        Returns:
            List of matching context items
        """
        return [item for item in self.items if item.type == type_filter]

    def clear(self) -> None:
        """Clear all context."""
        self.items = []
        self.current_tokens = 0
        logger.info("Context cleared")

    def prune_to_limit(self) -> None:
        """
        Remove oldest items to stay within token limit.

        Keeps recent items and removes older ones if over limit.
        """
        if self.current_tokens <= self.max_context_tokens:
            return
        
        # Remove oldest items until under limit
        while self.current_tokens > self.max_context_tokens and self.items:
            removed_item = self.items.pop(0)
            self.current_tokens -= self._estimate_tokens(removed_item.content)
            logger.warning(f"Removed '{removed_item.name}' from context to stay under token limit")

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """
        Estimate token count for text.

        Uses simple heuristic: ~4 characters per token.

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        return len(text) // 4

    def get_stats(self) -> Dict[str, Any]:
        """
        Get context statistics.

        Returns:
            Dictionary with context stats
        """
        type_counts = {}
        for item in self.items:
            type_counts[item.type] = type_counts.get(item.type, 0) + 1
        
        return {
            "total_items": len(self.items),
            "total_tokens": self.current_tokens,
            "max_tokens": self.max_context_tokens,
            "items_by_type": type_counts,
            "oldest_item": self.items[0].timestamp if self.items else None,
            "newest_item": self.items[-1].timestamp if self.items else None,
        }

    def __repr__(self) -> str:
        stats = self.get_stats()
        return (
            f"ContextBuilder(items={stats['total_items']}, "
            f"tokens={stats['total_tokens']}/{self.max_context_tokens})"
        )
