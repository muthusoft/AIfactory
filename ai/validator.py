"""
Output validation and constraint checking.

Ensures that AI-generated outputs meet requirements and constraints.
"""

from typing import Any, Dict, List, Optional, Callable
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger(__name__)


class ValidationRule:
    """A single validation rule."""

    def __init__(
        self,
        name: str,
        validator: Callable[[Any], bool],
        error_message: str
    ):
        """
        Initialize validation rule.

        Args:
            name: Rule name
            validator: Function that returns True if valid
            error_message: Message if validation fails
        """
        self.name = name
        self.validator = validator
        self.error_message = error_message

    def validate(self, data: Any) -> tuple[bool, str]:
        """
        Run validation.

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            is_valid = self.validator(data)
            if is_valid:
                return True, ""
            else:
                return False, self.error_message
        except Exception as e:
            return False, f"Validation error: {str(e)}"


class OutputValidator:
    """Validates AI-generated outputs."""

    def __init__(self):
        """Initialize validator."""
        self.rules: Dict[str, List[ValidationRule]] = {}

    def register_rule(
        self,
        phase: str,
        name: str,
        validator: Callable[[Any], bool],
        error_message: str
    ) -> None:
        """
        Register a validation rule for a phase.

        Args:
            phase: Pipeline phase name
            name: Rule name
            validator: Validation function
            error_message: Error message if validation fails
        """
        if phase not in self.rules:
            self.rules[phase] = []
        
        rule = ValidationRule(name, validator, error_message)
        self.rules[phase].append(rule)
        logger.info(f"Registered validation rule: {phase}/{name}")

    def validate(
        self,
        phase: str,
        data: Any,
        pydantic_model: Optional[type[BaseModel]] = None
    ) -> tuple[bool, List[str]]:
        """
        Validate output from a phase.

        Args:
            phase: Pipeline phase name
            data: Data to validate
            pydantic_model: Optional Pydantic model for validation

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []
        
        # Pydantic validation
        if pydantic_model:
            try:
                pydantic_model.model_validate(data)
                logger.info(f"Pydantic validation passed for {phase}")
            except ValidationError as e:
                for error in e.errors():
                    errors.append(f"Pydantic: {error['msg']}")
                logger.warning(f"Pydantic validation failed for {phase}: {errors}")

        # Custom rules validation
        if phase in self.rules:
            for rule in self.rules[phase]:
                is_valid, error_msg = rule.validate(data)
                if not is_valid:
                    errors.append(f"{rule.name}: {error_msg}")
                    logger.warning(f"Rule '{rule.name}' failed for {phase}")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info(f"All validations passed for {phase}")
        else:
            logger.error(f"Validation failed for {phase} with {len(errors)} error(s)")
        
        return is_valid, errors

    def validate_json_schema(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        """
        Validate data against JSON schema.

        Args:
            data: Data to validate
            schema: JSON schema

        Returns:
            Tuple of (is_valid, errors)
        """
        try:
            from jsonschema import validate, ValidationError
        except ImportError:
            logger.error("jsonschema not installed")
            return False, ["jsonschema library required"]
        
        errors = []
        
        try:
            validate(instance=data, schema=schema)
            logger.info("JSON schema validation passed")
            return True, []
        except ValidationError as e:
            errors.append(str(e.message))
            logger.error(f"JSON schema validation failed: {e.message}")
            return False, errors

    def setup_standard_rules(self) -> None:
        """Setup standard validation rules for common phases."""
        
        # Requirements analysis rules
        self.register_rule(
            "requirements_analysis",
            "has_business_objectives",
            lambda d: isinstance(d, dict) and "business_objectives" in d,
            "Missing business_objectives field"
        )
        
        self.register_rule(
            "requirements_analysis",
            "has_actors",
            lambda d: isinstance(d, dict) and "actors" in d and len(d.get("actors", [])) > 0,
            "Missing or empty actors field"
        )
        
        # Architecture design rules
        self.register_rule(
            "architecture_design",
            "has_components",
            lambda d: isinstance(d, dict) and "components" in d,
            "Missing components field"
        )
        
        self.register_rule(
            "architecture_design",
            "has_technology_stack",
            lambda d: isinstance(d, dict) and "technology_stack" in d,
            "Missing technology_stack field"
        )
        
        # Database design rules
        self.register_rule(
            "database_design",
            "has_entities",
            lambda d: isinstance(d, dict) and "entities" in d and len(d.get("entities", [])) > 0,
            "Missing or empty entities field"
        )
        
        # API design rules
        self.register_rule(
            "api_design",
            "has_endpoints",
            lambda d: isinstance(d, dict) and "endpoints" in d and len(d.get("endpoints", [])) > 0,
            "Missing or empty endpoints field"
        )
        
        # Code generation rules
        self.register_rule(
            "code_generation",
            "valid_python_syntax",
            self._validate_python_syntax,
            "Invalid Python syntax"
        )
        
        logger.info("Standard validation rules setup complete")

    @staticmethod
    def _validate_python_syntax(code: str) -> bool:
        """Validate Python syntax."""
        try:
            compile(code, '<string>', 'exec')
            return True
        except SyntaxError:
            return False

    def get_rule_names(self, phase: str) -> List[str]:
        """Get names of all rules for a phase."""
        if phase not in self.rules:
            return []
        return [rule.name for rule in self.rules[phase]]
