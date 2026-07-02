"""
Base agent class for all SDLC phase agents.

Provides common functionality for LLM interaction, artifact management,
and execution tracking.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from datetime import datetime
import uuid
import logging

from ai.llm import LLMProvider, LLMConfig
from ai.prompt_loader import PromptLoader
from ai.response_parser import ResponseParser, ResponseFormat
from ai.validator import OutputValidator
from ai.context_builder import ContextBuilder
from database.connection import SessionLocal
from database.schema import (
    Artifact, LLMCall, ProjectMetadata, ExecutionHistory
)

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all SDLC phase agents."""

    def __init__(
        self,
        project_id: str,
        llm_config: LLMConfig,
        phase_name: str
    ):
        """
        Initialize the agent.

        Args:
            project_id: ID of the project
            llm_config: LLM configuration
            phase_name: Name of this phase (e.g., 'requirements_analysis')
        """
        self.project_id = project_id
        self.phase_name = phase_name
        
        # Initialize LLM
        self.llm = LLMProvider(llm_config)
        
        # Initialize prompt loader
        self.prompts = PromptLoader("prompts")
        
        # Initialize validator
        self.validator = OutputValidator()
        self.validator.setup_standard_rules()
        
        # Initialize context builder
        self.context = ContextBuilder()
        
        logger.info(f"Agent initialized: phase={phase_name}, project={project_id}")

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main logic.

        Args:
            input_data: Input data for this phase

        Returns:
            Dictionary with results and artifacts
        """
        pass

    async def call_llm(
        self,
        prompt_name: str,
        variables: Optional[Dict[str, Any]] = None,
        response_format: ResponseFormat = ResponseFormat.JSON,
        system_prompt_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call the LLM with prompt handling and parsing.

        Args:
            prompt_name: Name of the prompt template to use
            variables: Variables to fill in the prompt
            response_format: Expected response format
            system_prompt_name: Optional system prompt template name

        Returns:
            Parsed response
        """
        variables = variables or {}
        
        # Load prompt
        try:
            prompt = self.prompts.load(prompt_name, variables)
        except Exception as e:
            logger.error(f"Failed to load prompt '{prompt_name}': {e}")
            raise

        # Load system prompt if provided
        system_prompt = None
        if system_prompt_name:
            try:
                system_prompt = self.prompts.get_system_prompt(system_prompt_name)
            except Exception as e:
                logger.warning(f"Failed to load system prompt: {e}")

        # Call LLM
        try:
            result = await self.llm.call(
                prompt=prompt,
                system_prompt=system_prompt
            )
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise

        # Log the call
        with SessionLocal() as session:
            llm_call_record = LLMCall(
                id=str(uuid.uuid4()),
                project_id=self.project_id,
                phase=self.phase_name,
                model=result.model,
                provider=result.provider,
                prompt=prompt[:1000],  # Store first 1000 chars
                system_prompt=system_prompt[:1000] if system_prompt else None,
                response=result.content[:1000],  # Store first 1000 chars
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                latency=result.latency,
                cost=result.cost,
                retry_count=result.retry_count,
                success=True
            )
            session.add(llm_call_record)
            session.commit()

        # Parse response
        try:
            parsed = ResponseParser.safe_extract(
                result.content,
                format=response_format,
                default={"raw": result.content}
            )
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            parsed = {"raw": result.content}

        return parsed

    def create_artifact(
        self,
        name: str,
        content: str,
        artifact_type: str = "artifact",
        file_path: Optional[str] = None,
        requirement_id: Optional[str] = None
    ) -> str:
        """
        Create and store an artifact.

        Args:
            name: Artifact name
            content: Artifact content
            artifact_type: Type of artifact
            file_path: Optional file path
            requirement_id: Optional requirement ID

        Returns:
            Artifact ID
        """
        artifact_id = str(uuid.uuid4())

        with SessionLocal() as session:
            artifact = Artifact(
                id=artifact_id,
                project_id=self.project_id,
                requirement_id=requirement_id,
                type=artifact_type,
                name=name,
                content=content,
                file_path=file_path,
                created_by_phase=self.phase_name,
                status="draft"
            )
            session.add(artifact)
            session.commit()

        logger.info(f"Created artifact: {artifact_id} ({name})")
        return artifact_id

    def get_project_context(self) -> Dict[str, Any]:
        """
        Get project context for LLM.

        Returns:
            Project context dictionary
        """
        with SessionLocal() as session:
            project = session.query(ProjectMetadata).filter(
                ProjectMetadata.id == self.project_id
            ).first()

            if not project:
                raise ValueError(f"Project not found: {self.project_id}")

            return {
                "name": project.name,
                "description": project.description,
                "requirement": project.business_requirement,
                "status": project.status
            }

    def update_execution_status(
        self,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> None:
        """
        Update execution history.

        Args:
            status: Execution status
            result: Optional result data
            error_message: Optional error message
        """
        with SessionLocal() as session:
            execution = ExecutionHistory(
                id=str(uuid.uuid4()),
                project_id=self.project_id,
                phase=self.phase_name,
                status=status,
                result=result,
                error_message=error_message
            )
            session.add(execution)
            session.commit()

        logger.info(f"Updated execution: phase={self.phase_name}, status={status}")

    def add_context_from_phase(self, phase_name: str, content: str) -> None:
        """
        Add context from a previous phase.

        Args:
            phase_name: Name of the previous phase
            content: Phase output
        """
        self.context.add_previous_phase_output(phase_name, content)
        logger.info(f"Added context from phase: {phase_name}")

    def validate_output(
        self,
        data: Any,
        pydantic_model=None
    ) -> tuple[bool, List[str]]:
        """
        Validate output.

        Args:
            data: Data to validate
            pydantic_model: Optional Pydantic model

        Returns:
            Tuple of (is_valid, errors)
        """
        return self.validator.validate(
            self.phase_name,
            data,
            pydantic_model
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(phase={self.phase_name}, project={self.project_id})"
