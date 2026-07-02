"""
Helper utilities.
"""

import uuid
import hashlib
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID.

    Args:
        prefix: Optional prefix for the ID

    Returns:
        Unique ID string
    """
    uid = str(uuid.uuid4())
    if prefix:
        return f"{prefix}_{uid}"
    return uid


def calculate_checksum(content: str) -> str:
    """
    Calculate SHA256 checksum for content.

    Args:
        content: Content to checksum

    Returns:
        Hex checksum string
    """
    return hashlib.sha256(content.encode()).hexdigest()


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format datetime as ISO string.

    Args:
        dt: Datetime to format (uses current time if not provided)

    Returns:
        ISO formatted timestamp
    """
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat()


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to max length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def merge_dicts(base: Dict, override: Dict) -> Dict:
    """
    Merge override dict into base dict (recursively).

    Args:
        base: Base dictionary
        override: Override dictionary

    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """
    Flatten nested dictionary.

    Args:
        d: Dictionary to flatten
        parent_key: Parent key (for recursion)
        sep: Separator for nested keys

    Returns:
        Flattened dictionary
    """
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Split list into chunks.

    Args:
        lst: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def ensure_list(value: Any) -> List:
    """
    Ensure value is a list.

    Args:
        value: Value to convert

    Returns:
        List value
    """
    if value is None:
        return []
    elif isinstance(value, list):
        return value
    else:
        return [value]


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """
    Safely dump object to JSON string.

    Args:
        obj: Object to dump
        default: Default value if serialization fails

    Returns:
        JSON string
    """
    try:
        return json.dumps(obj)
    except (TypeError, ValueError) as e:
        logger.warning(f"Failed to serialize to JSON: {e}")
        return default


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"
