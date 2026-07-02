"""
AI Software Factory - Main CLI entry point.

Provides command-line interface for project management and pipeline execution.
"""

import typer
import logging
from typing import Optional
from pathlib import Path
import yaml
import uuid
from datetime import datetime
import asyncio

from database.connection import DatabaseConnection
from database.schema import create_database, ProjectMetadata, Requirement
from utils.logger import setup_logging
from utils.config import load_config

app = typer.Typer(help="AI Software Factory - Convert requirements to production code")

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def load_app_config(config_path: str = "config/config.yaml") -> dict:
    """Load application configuration."""
    if not Path(config_path).exists():
        typer.echo(f"Config file not found: {config_path}")
        typer.echo("Please copy config/config.yaml.example to config/config.yaml")
        raise typer.Exit(1)
    
    with open(config_path) as f:
        return yaml.safe_load(f)


@app.command()
def init(
    config_file: str = typer.Option(
        "config/config.yaml",
        "--config",
        help="Path to config file"
    )
):
    """Initialize the AI Software Factory."""
    typer.echo("Initializing AI Software Factory...")
    
    try:
        # Load config
        config = load_app_config(config_file)
        
        # Initialize database
        db_url = config.get("database", {}).get("url", "sqlite:///./factory.db")
        DatabaseConnection.initialize(db_url)
        create_database(db_url)
        
        typer.echo(f"✓ Database initialized: {db_url}")
        typer.echo("✓ AI Software Factory initialized successfully!")
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        typer.echo(f"✗ Initialization failed: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def create_project(
    name: str = typer.Option(..., "--name", "-n", help="Project name"),
    requirement: str = typer.Option(..., "--requirement", "-r", help="Business requirement"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Project description"),
    config_file: str = typer.Option("config/config.yaml", "--config", help="Config file path")
):
    """Create a new project."""
    typer.echo(f"Creating project: {name}")
    
    try:
        # Load config and initialize DB
        config = load_app_config(config_file)
        db_url = config.get("database", {}).get("url", "sqlite:///./factory.db")
        DatabaseConnection.initialize(db_url)
        
        # Create project
        project_id = str(uuid.uuid4())
        project_path = Path(config.get("project", {}).get("base_path", "./projects")) / name
        project_path.mkdir(parents=True, exist_ok=True)
        
        from database.connection import SessionLocal
        from database.schema import ProjectMetadata
        
        with SessionLocal() as session:
            project = ProjectMetadata(
                id=project_id,
                name=name,
                description=description or "",
                business_requirement=requirement,
                base_path=str(project_path),
                status="created"
            )
            session.add(project)
            session.commit()
        
        typer.echo(f"✓ Project created: {name}")
        typer.echo(f"  Project ID: {project_id}")
        typer.echo(f"  Path: {project_path}")
        typer.echo(f"\nNext steps:")
        typer.echo(f"  1. List available phases: python main.py list-phases")
        typer.echo(f"  2. Run requirements analysis: python main.py run-phase --project \"{name}\" --phase requirements_analysis")
        typer.echo(f"  3. Run full pipeline: python main.py run-pipeline --project \"{name}\"")
        
    except Exception as e:
        logger.error(f"Project creation failed: {e}")
        typer.echo(f"✗ Project creation failed: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def list_projects(
    config_file: str = typer.Option("config/config.yaml", "--config", help="Config file path")
):
    """List all projects."""
    try:
        config = load_app_config(config_file)
        db_url = config.get("database", {}).get("url", "sqlite:///./factory.db")
        DatabaseConnection.initialize(db_url)
        
        from database.connection import SessionLocal
        from database.schema import ProjectMetadata
        
        with SessionLocal() as session:
            projects = session.query(ProjectMetadata).all()
            # Create a list to avoid session issues
            project_list = [
                {
                    "name": p.name,
                    "id": p.id,
                    "status": p.status,
                    "created_at": p.created_at
                }
                for p in projects
            ]
        
        if not project_list:
            typer.echo("No projects found.")
            return
        
        typer.echo("\nProjects:")
        typer.echo("-" * 80)
        
        for project in project_list:
            typer.echo(f"Name: {project['name']}")
            typer.echo(f"ID: {project['id']}")
            typer.echo(f"Status: {project['status']}")
            typer.echo(f"Created: {project['created_at']}")
            typer.echo("-" * 80)
        
    except Exception as e:
        logger.error(f"Failed to list projects: {e}")
        typer.echo(f"✗ Failed to list projects: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def run_phase(
    project_name: str = typer.Option(..., "--project", "-p", help="Project name"),
    phase: str = typer.Option(..., "--phase", help="Phase to run"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip dependency checks"),
    config_file: str = typer.Option("config/config.yaml", "--config", help="Config file path")
):
    """Run a specific SDLC phase."""
    typer.echo(f"Running phase '{phase}' for project '{project_name}'...")
    
    try:
        config = load_app_config(config_file)
        db_url = config.get("database", {}).get("url", "sqlite:///./factory.db")
        DatabaseConnection.initialize(db_url)
        
        from database.connection import SessionLocal
        from database.schema import ProjectMetadata
        from pipeline.executor import PipelineExecutor
        
        # Find project
        with SessionLocal() as session:
            project = session.query(ProjectMetadata).filter(ProjectMetadata.name == project_name).first()
        
        if not project:
            typer.echo(f"✗ Project not found: {project_name}", err=True)
            raise typer.Exit(1)
        
        # Create executor and run phase
        executor = PipelineExecutor(project.id)
        
        # Check if phase exists
        phase_def = executor.get_phase(phase)
        if not phase_def:
            typer.echo(f"✗ Phase not found: {phase}", err=True)
            typer.echo(f"Available phases:", err=False)
            for p in executor.list_phases():
                typer.echo(f"  - {p['id']}: {p['name']}", err=False)
            raise typer.Exit(1)
        
        # Check dependencies
        deps_ok, missing = executor.check_dependencies(phase)
        if not deps_ok and not force:
            typer.echo(f"⚠ Phase dependencies not satisfied: {', '.join(missing)}", err=False)
            typer.echo(f"Use --force to skip dependency check", err=False)
            raise typer.Exit(1)
        
        # Load project input data
        input_data = {"business_requirement": project.business_requirement}
        
        # Run the phase
        result = asyncio.run(executor.run_phase(phase, input_data, force=force))
        
        typer.echo(f"✓ Phase completed: {phase}")
        typer.echo(f"  Status: {result.get('status')}")
        typer.echo(f"  Outputs: {', '.join(phase_def.produces_output)}")
        
    except Exception as e:
        logger.error(f"Phase execution failed: {e}")
        typer.echo(f"✗ Phase execution failed: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def run_pipeline(
    project_name: str = typer.Option(..., "--project", "-p", help="Project name"),
    phases: Optional[str] = typer.Option(None, "--phases", help="Comma-separated list of phases (default: all)"),
    config_file: str = typer.Option("config/config.yaml", "--config", help="Config file path")
):
    """Run the complete or partial SDLC pipeline."""
    typer.echo(f"Running pipeline for project '{project_name}'...")
    
    try:
        config = load_app_config(config_file)
        db_url = config.get("database", {}).get("url", "sqlite:///./factory.db")
        DatabaseConnection.initialize(db_url)
        
        from database.connection import SessionLocal
        from database.schema import ProjectMetadata
        from pipeline.executor import PipelineExecutor
        
        # Find project
        with SessionLocal() as session:
            project = session.query(ProjectMetadata).filter(ProjectMetadata.name == project_name).first()
        
        if not project:
            typer.echo(f"✗ Project not found: {project_name}", err=True)
            raise typer.Exit(1)
        
        # Create executor
        executor = PipelineExecutor(project.id)
        
        # Parse phases if provided
        phase_list = None
        if phases:
            phase_list = [p.strip() for p in phases.split(",")]
        
        # Run pipeline
        input_data = {"business_requirement": project.business_requirement}
        results = asyncio.run(executor.run_pipeline(phases=phase_list, input_data=input_data))
        
        typer.echo(f"✓ Pipeline execution completed")
        
        # Show results
        for phase_id, result in results.items():
            status = result.get('status', 'unknown')
            status_icon = "✓" if status == "completed" else "✗" if status == "failed" else "⏸"
            typer.echo(f"  {status_icon} {phase_id}: {status}")
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        typer.echo(f"✗ Pipeline execution failed: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def show_status(
    project_name: str = typer.Option(..., "--project", "-p", help="Project name"),
    config_file: str = typer.Option("config/config.yaml", "--config", help="Config file path")
):
    """Show project status."""
    try:
        config = load_app_config(config_file)
        db_url = config.get("database", {}).get("url", "sqlite:///./factory.db")
        DatabaseConnection.initialize(db_url)
        
        from database.connection import SessionLocal
        from database.schema import ProjectMetadata
        
        with SessionLocal() as session:
            project = session.query(ProjectMetadata).filter(ProjectMetadata.name == project_name).first()
        
        if not project:
            typer.echo(f"✗ Project not found: {project_name}", err=True)
            raise typer.Exit(1)
        
        typer.echo(f"\nProject: {project.name}")
        typer.echo(f"Status: {project.status}")
        typer.echo(f"Created: {project.created_at}")
        typer.echo(f"Updated: {project.updated_at}")
        
    except Exception as e:
        logger.error(f"Failed to show status: {e}")
        typer.echo(f"✗ Failed to show status: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def list_phases(
    config_file: str = typer.Option("config/config.yaml", "--config", help="Config file path")
):
    """List all available SDLC phases."""
    try:
        from pipeline.executor import PipelineExecutor
        
        executor = PipelineExecutor("temp")
        phases = executor.list_phases(dependency_order=True)
        
        typer.echo("\n📋 Available SDLC Phases:\n")
        
        for i, phase in enumerate(phases, 1):
            typer.echo(f"{i}. {phase['name']} ({phase['id']})")
            typer.echo(f"   {phase['description']}")
            if phase['depends_on']:
                typer.echo(f"   Depends on: {', '.join(phase['depends_on'])}")
            typer.echo(f"   Produces: {', '.join(phase['produces_output'])}\n")
        
    except Exception as e:
        logger.error(f"Failed to list phases: {e}")
        typer.echo(f"✗ Failed to list phases: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
