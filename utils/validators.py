"""
Data validation utilities.
"""

import re
from typing import Any, Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


def validate_email(email: str) -> bool:
    """Validate email address."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_url(url: str) -> bool:
    """Validate URL."""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None


def validate_uuid(uuid_str: str) -> bool:
    """Validate UUID format."""
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return re.match(pattern, uuid_str.lower()) is not None


def validate_python_syntax(code: str) -> bool:
    """Validate Python syntax."""
    try:
        compile(code, '<string>', 'exec')
        return True
    except SyntaxError:
        return False


def is_valid_json(text: str) -> bool:
    """Check if text is valid JSON."""
    try:
        import json
        json.loads(text)
        return True
    except:
        return False


def is_valid_yaml(text: str) -> bool:
    """Check if text is valid YAML."""
    try:
        import yaml
        yaml.safe_load(text)
        return True
    except:
        return False


class ProjectNameValidator:
    """Validate project names."""
    
    MIN_LENGTH = 3
    MAX_LENGTH = 255
    PATTERN = r'^[a-zA-Z][a-zA-Z0-9_-]*$'
    
    @classmethod
    def validate(cls, name: str) -> tuple[bool, Optional[str]]:
        """
        Validate project name.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name:
            return False, "Project name is required"
        
        if len(name) < cls.MIN_LENGTH:
            return False, f"Project name must be at least {cls.MIN_LENGTH} characters"
        
        if len(name) > cls.MAX_LENGTH:
            return False, f"Project name must be at most {cls.MAX_LENGTH} characters"
        
        if not re.match(cls.PATTERN, name):
            return False, "Project name must start with a letter and contain only letters, numbers, hyphens, and underscores"
        
        return True, None
