"""
Prompt template management and loading system.

Prompts are stored as template files and can include variables that are
filled in at runtime using Jinja2 templating.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Any
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import yaml
import logging

logger = logging.getLogger(__name__)


class PromptLoader:
    """Loads and manages prompt templates."""

    def __init__(self, template_dir: str = "prompts"):
        """
        Initialize the prompt loader.

        Args:
            template_dir: Directory containing prompt templates
        """
        self.template_dir = Path(template_dir)
        
        # Create Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Load prompt registry if it exists
        self.registry = self._load_registry()
        
        logger.info(f"PromptLoader initialized with directory: {self.template_dir}")

    def _load_registry(self) -> Dict[str, Dict[str, Any]]:
        """
        Load prompt registry from config.

        Returns:
            Dictionary mapping prompt names to metadata
        """
        registry_path = self.template_dir / "registry.yaml"
        
        if not registry_path.exists():
            logger.warning(f"Prompt registry not found at {registry_path}")
            return {}
        
        try:
            with open(registry_path, 'r') as f:
                registry = yaml.safe_load(f) or {}
            logger.info(f"Loaded prompt registry with {len(registry)} prompts")
            return registry
        except Exception as e:
            logger.error(f"Failed to load prompt registry: {e}")
            return {}

    def load(
        self,
        name: str,
        variables: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None
    ) -> str:
        """
        Load and render a prompt template.

        Args:
            name: Name of the prompt template (e.g., 'requirements/analysis')
            variables: Variables to fill in the template
            version: Specific version to load (if not provided, uses latest)

        Returns:
            Rendered prompt string

        Raises:
            TemplateNotFound: If the prompt template doesn't exist
        """
        variables = variables or {}
        
        # Build template path
        template_path = f"{name}.jinja2"
        
        try:
            # Load template
            template = self.env.get_template(template_path)
            logger.info(f"Loaded prompt template: {template_path}")
            
            # Render template
            rendered = template.render(**variables)
            logger.debug(f"Rendered prompt with {len(variables)} variables")
            
            return rendered
            
        except TemplateNotFound:
            logger.error(f"Prompt template not found: {template_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to render prompt template: {e}")
            raise

    def load_raw(self, name: str) -> str:
        """
        Load a raw prompt template without rendering variables.

        Args:
            name: Name of the prompt template

        Returns:
            Raw template string
        """
        template_path = f"{name}.jinja2"
        
        try:
            template_file = self.template_dir / template_path
            with open(template_file, 'r') as f:
                content = f.read()
            logger.info(f"Loaded raw prompt template: {template_path}")
            return content
        except FileNotFoundError:
            logger.error(f"Prompt template file not found: {template_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to load raw prompt template: {e}")
            raise

    def get_metadata(self, name: str) -> Dict[str, Any]:
        """
        Get metadata for a prompt template.

        Args:
            name: Name of the prompt template

        Returns:
            Metadata dictionary
        """
        return self.registry.get(name, {})

    def list_prompts(self, category: Optional[str] = None) -> list:
        """
        List available prompt templates.

        Args:
            category: Optional category filter (e.g., 'requirements')

        Returns:
            List of prompt names
        """
        prompts = []
        
        for root, dirs, files in os.walk(self.template_dir):
            for file in files:
                if file.endswith('.jinja2'):
                    # Get relative path
                    rel_path = os.path.relpath(
                        os.path.join(root, file),
                        self.template_dir
                    )
                    
                    # Remove .jinja2 extension
                    prompt_name = rel_path[:-7]
                    
                    # Filter by category if provided
                    if category is None or prompt_name.startswith(category):
                        prompts.append(prompt_name)
        
        return sorted(prompts)

    def validate_template(self, name: str) -> bool:
        """
        Validate that a template can be loaded.

        Args:
            name: Name of the prompt template

        Returns:
            True if template is valid, False otherwise
        """
        try:
            template_path = f"{name}.jinja2"
            self.env.get_template(template_path)
            return True
        except Exception as e:
            logger.error(f"Template validation failed for {name}: {e}")
            return False

    def get_system_prompt(
        self,
        name: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Load a system prompt template.

        System prompts are typically used to set the behavior and context
        for an AI agent.

        Args:
            name: Name of the system prompt template
            variables: Variables to fill in the template

        Returns:
            Rendered system prompt string
        """
        system_prompt_name = f"system_prompts/{name}"
        return self.load(system_prompt_name, variables)

    def create_template(
        self,
        name: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Create a new prompt template.

        Args:
            name: Name for the template
            content: Template content
            metadata: Optional metadata to store in registry
        """
        # Create directory if needed
        template_path = self.template_dir / f"{name}.jinja2"
        template_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write template
        with open(template_path, 'w') as f:
            f.write(content)
        
        logger.info(f"Created prompt template: {name}")
        
        # Update registry if metadata provided
        if metadata:
            if 'prompts' not in self.registry:
                self.registry['prompts'] = {}
            self.registry['prompts'][name] = metadata
            self._save_registry()

    def _save_registry(self) -> None:
        """Save registry to file."""
        registry_path = self.template_dir / "registry.yaml"
        
        with open(registry_path, 'w') as f:
            yaml.dump(self.registry, f, default_flow_style=False)
        
        logger.info("Saved prompt registry")
