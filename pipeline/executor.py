"""
Pipeline executor for running SDLC phases independently or sequentially.

Each phase can be run independently with its output stored in the database.
Phases can be re-run, skipped, or reordered based on requirements.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PhaseDefinition:
    """Definition of an SDLC phase."""
    id: str
    name: str
    description: str
    agent_class: str
    depends_on: List[str]  # List of phase IDs this depends on
    required_input: List[str]  # What this phase needs
    produces_output: List[str]  # What this phase produces


class PipelineExecutor:
    """Executes SDLC phases independently or in sequence."""
    
    # Define all available phases
    PHASES = {
        "requirements_analysis": PhaseDefinition(
            id="requirements_analysis",
            name="Requirements Analysis",
            description="Analyze and extract business requirements",
            agent_class="RequirementAnalyzer",
            depends_on=[],
            required_input=["business_requirement"],
            produces_output=["requirements_document", "functional_requirements", "non_functional_requirements"],
        ),
        "business_analysis": PhaseDefinition(
            id="business_analysis",
            name="Business Analysis & Specification",
            description="Create detailed business specification and use cases",
            agent_class="BusinessAnalyzer",
            depends_on=["requirements_analysis"],
            required_input=["requirements_document"],
            produces_output=["business_specification", "use_cases", "actors_definition"],
        ),
        "domain_modeling": PhaseDefinition(
            id="domain_modeling",
            name="Domain Model & Entities",
            description="Create domain model with entities and relationships",
            agent_class="DomainModeler",
            depends_on=["business_analysis"],
            required_input=["business_specification"],
            produces_output=["domain_model", "entities_diagram", "class_diagram"],
        ),
        "system_sequence_design": PhaseDefinition(
            id="system_sequence_design",
            name="System Sequence Design (SSD)",
            description="Create sequence diagrams for system interactions",
            agent_class="SystemSequenceDesigner",
            depends_on=["domain_modeling"],
            required_input=["domain_model", "use_cases"],
            produces_output=["sequence_diagrams", "system_flow_diagram", "interaction_model"],
        ),
        "database_design": PhaseDefinition(
            id="database_design",
            name="Database Schema Design",
            description="Design normalized database schema based on domain model",
            agent_class="DatabaseDesigner",
            depends_on=["domain_modeling"],
            required_input=["domain_model"],
            produces_output=["database_schema_json", "database_schema_diagram", "sql_create_script", "migration_script"],
        ),
        "architecture_design": PhaseDefinition(
            id="architecture_design",
            name="System Architecture Design",
            description="Design overall system architecture and components",
            agent_class="Architect",
            depends_on=["requirements_analysis"],
            required_input=["requirements_document"],
            produces_output=["architecture_diagram", "component_diagram", "technology_stack", "design_patterns"],
        ),
        "wireframe_design": PhaseDefinition(
            id="wireframe_design",
            name="UI Wireframes & Mockups",
            description="Create wireframes and UI mockups for all screens",
            agent_class="WireframeDesigner",
            depends_on=["requirements_analysis", "domain_modeling"],
            required_input=["requirements_document", "domain_model"],
            produces_output=["wireframes", "ui_mockups", "navigation_flow", "screen_specifications"],
        ),
        "api_design": PhaseDefinition(
            id="api_design",
            name="API & Interface Specification",
            description="Design REST API endpoints and data contracts",
            agent_class="APIDesigner",
            depends_on=["database_design", "architecture_design"],
            required_input=["database_schema_json", "architecture_diagram"],
            produces_output=["api_specification", "openapi_spec", "data_models", "error_handling_spec"],
        ),
        "task_planning": PhaseDefinition(
            id="task_planning",
            name="Implementation Planning",
            description="Break down implementation into tasks and stories",
            agent_class="TaskPlanner",
            depends_on=["architecture_design", "database_design", "api_design"],
            required_input=["architecture_diagram", "database_schema_json", "api_specification"],
            produces_output=["task_breakdown", "epics", "stories", "sprint_plan"],
        ),
        "code_generation": PhaseDefinition(
            id="code_generation",
            name="Code Generation",
            description="Generate source code based on specifications",
            agent_class="CodeGenerator",
            depends_on=["task_planning", "database_design", "api_design", "wireframe_design"],
            required_input=["task_breakdown", "database_schema_json", "api_specification", "wireframes"],
            produces_output=["backend_code", "frontend_code", "database_models", "configuration_files"],
        ),
        "code_review": PhaseDefinition(
            id="code_review",
            name="Code Quality Review",
            description="Review generated code for quality and best practices",
            agent_class="CodeReviewer",
            depends_on=["code_generation"],
            required_input=["backend_code", "frontend_code"],
            produces_output=["review_report", "quality_metrics", "improvement_suggestions"],
        ),
        "test_generation": PhaseDefinition(
            id="test_generation",
            name="Test Generation",
            description="Generate unit and integration tests",
            agent_class="TestGenerator",
            depends_on=["code_generation"],
            required_input=["backend_code", "frontend_code", "api_specification"],
            produces_output=["unit_tests", "integration_tests", "test_fixtures", "test_documentation"],
        ),
        "bug_detection": PhaseDefinition(
            id="bug_detection",
            name="Bug Detection & Analysis",
            description="Detect potential bugs and security issues",
            agent_class="BugDetector",
            depends_on=["code_review", "test_generation"],
            required_input=["review_report", "unit_tests"],
            produces_output=["bugs_found", "bug_report", "security_issues", "performance_issues"],
        ),
        "bug_fixing": PhaseDefinition(
            id="bug_fixing",
            name="Bug Fixing",
            description="Fix detected bugs and issues",
            agent_class="BugFixer",
            depends_on=["bug_detection"],
            required_input=["bugs_found", "backend_code"],
            produces_output=["fixed_code", "fix_verification_report"],
        ),
        "documentation": PhaseDefinition(
            id="documentation",
            name="Documentation Generation",
            description="Generate comprehensive project documentation",
            agent_class="DocumentationGenerator",
            depends_on=["code_generation", "api_design", "database_design"],
            required_input=["backend_code", "api_specification", "database_schema_json"],
            produces_output=["readme", "api_documentation", "database_guide", "user_guide", "developer_guide", "architecture_guide"],
        ),
        "packaging": PhaseDefinition(
            id="packaging",
            name="Project Packaging",
            description="Package the project for delivery",
            agent_class="Packager",
            depends_on=["documentation", "bug_fixing"],
            required_input=["fixed_code", "documentation"],
            produces_output=["deliverable_package", "setup_scripts", "deployment_guide"],
        ),
    }
    
    def __init__(self, project_id: str):
        """Initialize executor."""
        self.project_id = project_id
        self.execution_results: Dict[str, Any] = {}
        self.phase_status: Dict[str, str] = {}  # phase_id -> status
        logger.info(f"Pipeline executor initialized for project {project_id}")
    
    def get_available_phases(self) -> Dict[str, PhaseDefinition]:
        """Get all available phases."""
        return self.PHASES
    
    def get_phase(self, phase_id: str) -> Optional[PhaseDefinition]:
        """Get a specific phase definition."""
        return self.PHASES.get(phase_id)
    
    def get_dependencies(self, phase_id: str) -> List[str]:
        """Get dependencies for a phase."""
        phase = self.get_phase(phase_id)
        if not phase:
            raise ValueError(f"Phase not found: {phase_id}")
        return phase.depends_on
    
    def check_dependencies(self, phase_id: str) -> tuple[bool, List[str]]:
        """
        Check if all dependencies are satisfied.
        
        Returns:
            (all_satisfied, missing_phases)
        """
        phase = self.get_phase(phase_id)
        if not phase:
            return False, [phase_id]
        
        missing = []
        for dep_id in phase.depends_on:
            if self.phase_status.get(dep_id) != "completed":
                missing.append(dep_id)
        
        return len(missing) == 0, missing
    
    async def run_phase(
        self,
        phase_id: str,
        input_data: Dict[str, Any],
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Run a single phase.
        
        Args:
            phase_id: Phase to run
            input_data: Input data for the phase
            force: Force execution even if dependencies not met
        
        Returns:
            Phase output
        """
        phase = self.get_phase(phase_id)
        if not phase:
            raise ValueError(f"Phase not found: {phase_id}")
        
        # Check dependencies
        deps_ok, missing = self.check_dependencies(phase_id)
        if not deps_ok and not force:
            missing_str = ", ".join(missing)
            raise ValueError(
                f"Cannot run {phase_id}. Missing dependencies: {missing_str}. "
                f"Use force=True to skip dependency check."
            )
        
        logger.info(f"Running phase: {phase_id}")
        self.phase_status[phase_id] = "running"
        
        try:
            # TODO: Load actual agent and run
            # For now, simulate execution
            result = {
                "phase_id": phase_id,
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "output": {f"mock_{output}": f"result_{output}" for output in phase.produces_output}
            }
            
            self.execution_results[phase_id] = result
            self.phase_status[phase_id] = "completed"
            
            logger.info(f"Phase completed: {phase_id}")
            return result
            
        except Exception as e:
            logger.error(f"Phase failed: {phase_id} - {str(e)}")
            self.phase_status[phase_id] = "failed"
            raise
    
    async def run_pipeline(
        self,
        phases: Optional[List[str]] = None,
        input_data: Optional[Dict[str, Any]] = None,
        stop_on_error: bool = True
    ) -> Dict[str, Any]:
        """
        Run multiple phases in sequence.
        
        Args:
            phases: List of phase IDs to run (None = run all)
            input_data: Initial input data
            stop_on_error: Stop if any phase fails
        
        Returns:
            All results
        """
        if phases is None:
            # Run all phases in dependency order
            phases = list(self.PHASES.keys())
        
        if input_data is None:
            input_data = {}
        
        logger.info(f"Starting pipeline execution with phases: {phases}")
        
        all_results = {}
        
        for phase_id in phases:
            try:
                result = await self.run_phase(phase_id, input_data)
                all_results[phase_id] = result
                
                # Update input data with outputs for next phase
                if "output" in result:
                    input_data.update(result["output"])
                
            except Exception as e:
                logger.error(f"Phase failed: {phase_id}")
                all_results[phase_id] = {
                    "status": "failed",
                    "error": str(e)
                }
                
                if stop_on_error:
                    logger.error("Stopping pipeline execution due to error")
                    break
        
        return all_results
    
    def get_execution_order(self, phases: List[str]) -> List[str]:
        """
        Get execution order based on dependencies.
        
        Args:
            phases: List of phase IDs
        
        Returns:
            Ordered list of phase IDs
        """
        ordered = []
        remaining = set(phases)
        
        while remaining:
            # Find phases with no unsatisfied dependencies
            ready = []
            for phase_id in remaining:
                deps = self.get_dependencies(phase_id)
                if all(d in ordered for d in deps):
                    ready.append(phase_id)
            
            if not ready:
                # Circular dependency
                raise ValueError(f"Circular dependency detected in phases: {remaining}")
            
            # Add ready phases in order
            for phase_id in sorted(ready):
                ordered.append(phase_id)
                remaining.remove(phase_id)
        
        return ordered
    
    def get_status(self) -> Dict[str, Any]:
        """Get current execution status."""
        return {
            "project_id": self.project_id,
            "phases": self.phase_status,
            "results": self.execution_results,
            "timestamp": datetime.now().isoformat(),
        }
    
    def save_results(self, path: str) -> None:
        """Save execution results to file."""
        results = self.get_status()
        with open(path, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {path}")
    
    def list_phases(self, dependency_order: bool = False) -> List[Dict[str, Any]]:
        """
        List all available phases.
        
        Args:
            dependency_order: Sort by dependency order
        
        Returns:
            List of phase information
        """
        phases_list = []
        
        for phase_id, phase in self.PHASES.items():
            phases_list.append({
                "id": phase.id,
                "name": phase.name,
                "description": phase.description,
                "depends_on": phase.depends_on,
                "required_input": phase.required_input,
                "produces_output": phase.produces_output,
                "status": self.phase_status.get(phase_id, "not_run"),
            })
        
        if dependency_order:
            try:
                ordered = self.get_execution_order(list(self.PHASES.keys()))
                phases_list = [
                    p for p in phases_list
                    if p["id"] in ordered
                ]
                phases_list.sort(key=lambda p: ordered.index(p["id"]))
            except ValueError as e:
                logger.warning(f"Could not order by dependencies: {e}")
        
        return phases_list
