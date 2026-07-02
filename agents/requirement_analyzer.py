"""
Requirements Analysis Agent.

Analyzes business requirements and extracts structured information.
This is the first phase of the SDLC pipeline.
"""

from typing import Any, Dict, Optional
import asyncio
import json
import logging
from pydantic import BaseModel, Field

from agents.base_agent import BaseAgent
from ai.llm import LLMConfig
from ai.response_parser import ResponseFormat

logger = logging.getLogger(__name__)


class RequirementInput(BaseModel):
    """Input for requirement analysis."""
    business_requirement: str
    additional_context: Optional[str] = None
    clarification_responses: Optional[Dict[str, str]] = None


class BusinessObjective(BaseModel):
    """Business objective."""
    title: str
    description: str
    success_metric: Optional[str] = None


class Actor(BaseModel):
    """Actor in the system."""
    name: str
    type: str  # user, system, external
    description: str
    responsibilities: Optional[list] = None


class UseCase(BaseModel):
    """Use case."""
    name: str
    description: str
    actors: list[str]
    preconditions: Optional[list[str]] = None
    steps: Optional[list[str]] = None
    postconditions: Optional[list[str]] = None


class Requirement(BaseModel):
    """Functional requirement."""
    id: str
    title: str
    description: str
    priority: str  # high, medium, low
    acceptance_criteria: Optional[list[str]] = None


class NonFunctionalRequirement(BaseModel):
    """Non-functional requirement."""
    id: str
    title: str
    description: str
    category: str  # performance, security, scalability, reliability, usability
    metric: Optional[str] = None


class RequirementAnalysisResult(BaseModel):
    """Result of requirement analysis."""
    business_objectives: list[BusinessObjective] = Field(default_factory=list)
    stakeholders: list[str] = Field(default_factory=list)
    actors: list[Actor] = Field(default_factory=list)
    use_cases: list[UseCase] = Field(default_factory=list)
    functional_requirements: list[Requirement] = Field(default_factory=list)
    non_functional_requirements: list[NonFunctionalRequirement] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)
    glossary: Dict[str, str] = Field(default_factory=dict)


class RequirementAnalyzer(BaseAgent):
    """Analyzes business requirements."""

    def __init__(self, project_id: str, llm_config: LLMConfig):
        """
        Initialize the requirement analyzer.

        Args:
            project_id: Project ID
            llm_config: LLM configuration
        """
        super().__init__(
            project_id=project_id,
            llm_config=llm_config,
            phase_name="requirements_analysis"
        )

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute requirement analysis.

        Args:
            input_data: Input containing business_requirement

        Returns:
            Analysis result with extracted requirements
        """
        try:
            # Validate input
            req_input = RequirementInput(**input_data)
            
            logger.info(f"Analyzing requirements for project {self.project_id}")
            
            # Call LLM to analyze requirements
            result = await self.call_llm(
                prompt_name="requirements/analyze_requirements",
                variables={
                    "business_requirement": req_input.business_requirement,
                    "clarification_questions": req_input.clarification_responses or {}
                },
                response_format=ResponseFormat.JSON,
                system_prompt_name="requirements_analyzer"
            )
            
            # Parse and validate response
            analysis = self._parse_analysis_response(result)
            
            # Create artifact
            artifact_id = self.create_artifact(
                name="business_requirements_analysis",
                content=json.dumps(analysis, indent=2),
                artifact_type="requirement",
                requirement_id=None
            )
            
            logger.info(f"Requirement analysis completed: {artifact_id}")
            
            return {
                "status": "success",
                "artifact_id": artifact_id,
                "analysis": analysis,
                "business_objectives_count": len(analysis.get("business_objectives", [])),
                "functional_requirements_count": len(analysis.get("functional_requirements", [])),
                "non_functional_requirements_count": len(analysis.get("non_functional_requirements", [])),
            }
            
        except Exception as e:
            logger.error(f"Requirement analysis failed: {e}")
            self.update_execution_status("failed", error_message=str(e))
            raise

    def _parse_analysis_response(self, response: Any) -> Dict[str, Any]:
        """
        Parse LLM response into structured format.

        Args:
            response: LLM response

        Returns:
            Parsed analysis
        """
        # Extract content if it's wrapped
        if isinstance(response, dict):
            if "raw" in response:
                content = response["raw"]
            else:
                content = response
        else:
            content = str(response)
        
        # Try to parse as JSON if string
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                logger.warning("Could not parse response as JSON, returning as-is")
                return {"raw_response": content}
        
        # Ensure required fields exist
        analysis = {
            "business_objectives": content.get("business_objectives", []),
            "stakeholders": content.get("stakeholders", []),
            "actors": content.get("actors", []),
            "use_cases": content.get("use_cases", []),
            "functional_requirements": content.get("functional_requirements", []),
            "non_functional_requirements": content.get("non_functional_requirements", []),
            "constraints": content.get("constraints", []),
            "assumptions": content.get("assumptions", []),
            "ambiguities": content.get("ambiguities", []),
            "glossary": content.get("glossary", {}),
        }
        
        return analysis

    async def ask_clarification_questions(
        self,
        business_requirement: str,
        max_questions: int = 5
    ) -> list[str]:
        """
        Generate clarification questions for ambiguous requirements.

        Args:
            business_requirement: Business requirement text
            max_questions: Maximum number of questions

        Returns:
            List of clarification questions
        """
        try:
            result = await self.call_llm(
                prompt_name="requirements/ask_clarifications",
                variables={
                    "business_requirement": business_requirement,
                    "max_questions": max_questions
                },
                response_format=ResponseFormat.TEXT,
                system_prompt_name="requirements_analyzer"
            )
            
            # Parse questions from response
            if isinstance(result, dict) and "raw" in result:
                content = result["raw"]
            else:
                content = str(result)
            
            # Split by newlines and filter
            questions = [
                q.strip().lstrip("-•").strip()
                for q in content.split("\n")
                if q.strip()
            ]
            
            return questions[:max_questions]
            
        except Exception as e:
            logger.error(f"Failed to generate clarification questions: {e}")
            return []
