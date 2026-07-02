"""
Response parsing and extraction utilities.

Handles parsing structured responses from LLM outputs, including JSON,
YAML, and code blocks.
"""

import json
import re
from typing import Any, Dict, Optional, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ResponseFormat(str, Enum):
    """Supported response formats."""
    JSON = "json"
    YAML = "yaml"
    CODE = "code"
    TEXT = "text"
    MARKDOWN = "markdown"


class ResponseParser:
    """Parses and extracts structured data from LLM responses."""

    @staticmethod
    def extract_json(text: str) -> Dict[str, Any]:
        """
        Extract JSON from text, handling markdown code blocks.

        Args:
            text: Text potentially containing JSON

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If no valid JSON found
        """
        # Try to find JSON in code blocks
        json_pattern = r'```json\s*(.*?)\s*```'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            json_text = matches[0]
        else:
            # Try to find raw JSON
            json_pattern = r'\{.*\}'
            matches = re.findall(json_pattern, text, re.DOTALL)
            if matches:
                json_text = matches[0]
            else:
                json_text = text
        
        try:
            parsed = json.loads(json_text)
            logger.info("Successfully parsed JSON from response")
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            # Try cleaning up common issues
            cleaned = ResponseParser._clean_json_text(json_text)
            try:
                parsed = json.loads(cleaned)
                logger.info("Successfully parsed cleaned JSON")
                return parsed
            except json.JSONDecodeError as e2:
                logger.error(f"Failed to parse cleaned JSON: {e2}")
                raise ValueError(f"Invalid JSON in response: {str(e2)}")

    @staticmethod
    def extract_code(
        text: str,
        language: Optional[str] = None
    ) -> str:
        """
        Extract code from text, optionally for a specific language.

        Args:
            text: Text potentially containing code blocks
            language: Optional language filter (e.g., 'python', 'sql')

        Returns:
            Extracted code string
        """
        if language:
            # Look for language-specific code block
            pattern = f'```{language}\\s*(.*?)\\s*```'
        else:
            # Look for any code block
            pattern = r'```(?:\w+)?\s*(.*?)\s*```'
        
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            code = matches[0]
            logger.info(f"Extracted {language or 'unknown'} code block")
            return code
        
        logger.warning("No code block found in response")
        return ""

    @staticmethod
    def extract_code_blocks(text: str) -> Dict[str, str]:
        """
        Extract all code blocks, grouped by language.

        Args:
            text: Text containing code blocks

        Returns:
            Dictionary mapping language to code
        """
        pattern = r'```(\w*)\s*(.*?)\s*```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        code_blocks = {}
        for language, code in matches:
            lang = language or 'unknown'
            if lang not in code_blocks:
                code_blocks[lang] = []
            code_blocks[lang].append(code)
        
        logger.info(f"Extracted {len(code_blocks)} code block(s)")
        return code_blocks

    @staticmethod
    def extract_yaml(text: str) -> Dict[str, Any]:
        """
        Extract YAML from text.

        Args:
            text: Text potentially containing YAML

        Returns:
            Parsed YAML dictionary
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            raise ImportError("PyYAML required for YAML parsing")
        
        # Try to find YAML in code blocks
        yaml_pattern = r'```yaml\s*(.*?)\s*```'
        matches = re.findall(yaml_pattern, text, re.DOTALL)
        
        if matches:
            yaml_text = matches[0]
        else:
            yaml_text = text
        
        try:
            parsed = yaml.safe_load(yaml_text)
            logger.info("Successfully parsed YAML from response")
            return parsed or {}
        except Exception as e:
            logger.error(f"Failed to parse YAML: {e}")
            raise ValueError(f"Invalid YAML in response: {str(e)}")

    @staticmethod
    def extract_sections(
        text: str,
        section_pattern: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Extract sections from markdown text.

        Args:
            text: Markdown text with sections
            section_pattern: Optional regex pattern for section headers

        Returns:
            Dictionary mapping section names to content
        """
        if section_pattern is None:
            # Use standard markdown headers
            section_pattern = r'^#+\s+(.+?)$'
        
        sections = {}
        lines = text.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            match = re.match(section_pattern, line, re.IGNORECASE)
            if match:
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = match.group(1).strip()
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        logger.info(f"Extracted {len(sections)} section(s)")
        return sections

    @staticmethod
    def extract_list_items(text: str) -> List[str]:
        """
        Extract list items from text.

        Args:
            text: Text containing list items

        Returns:
            List of extracted items
        """
        # Match bullet points and numbered lists
        pattern = r'^[-*•]\s+(.+?)$|^\d+\.\s+(.+?)$'
        matches = re.findall(pattern, text, re.MULTILINE)
        
        items = []
        for match in matches:
            # match is a tuple of (bullet_item, numbered_item)
            item = match[0] or match[1]
            items.append(item.strip())
        
        logger.info(f"Extracted {len(items)} list item(s)")
        return items

    @staticmethod
    def _clean_json_text(text: str) -> str:
        """
        Clean up common JSON issues.

        Args:
            text: Raw JSON text

        Returns:
            Cleaned JSON text
        """
        # Remove trailing commas
        text = re.sub(r',(\s*[}\]])', r'\1', text)
        
        # Handle single quotes (replace with double quotes if not in value)
        # This is risky but helps with common issues
        
        return text

    @staticmethod
    def validate_structure(
        data: Any,
        schema: Dict[str, Any]
    ) -> bool:
        """
        Validate data against a simple schema.

        Args:
            data: Data to validate
            schema: Schema specification

        Returns:
            True if data matches schema
        """
        if isinstance(schema, dict):
            if not isinstance(data, dict):
                return False
            
            for key, value_schema in schema.items():
                if key not in data:
                    return False
                
                if not ResponseParser.validate_structure(data[key], value_schema):
                    return False
        
        elif isinstance(schema, list) and schema:
            if not isinstance(data, list):
                return False
            
            for item in data:
                if not ResponseParser.validate_structure(item, schema[0]):
                    return False
        
        return True

    @staticmethod
    def safe_extract(
        text: str,
        format: ResponseFormat = ResponseFormat.TEXT,
        default: Any = None
    ) -> Any:
        """
        Safely extract data from response with fallback.

        Args:
            text: Response text
            format: Expected response format
            default: Default value if extraction fails

        Returns:
            Extracted data or default
        """
        try:
            if format == ResponseFormat.JSON:
                return ResponseParser.extract_json(text)
            elif format == ResponseFormat.CODE:
                return ResponseParser.extract_code(text)
            elif format == ResponseFormat.YAML:
                return ResponseParser.extract_yaml(text)
            else:
                return text
        except Exception as e:
            logger.warning(f"Safe extraction failed, returning default: {e}")
            return default
