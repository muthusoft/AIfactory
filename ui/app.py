"""
FastAPI web application for the AI Software Factory.

Provides a modern web UI for managing projects and executing pipelines.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import logging
from typing import List, Optional, Dict, Any
import uuid

from database.connection import DatabaseConnection
from database.schema import Project, Artifact, ExecutionHistory, LLMCall
from utils.logger import setup_logging
from utils.config import load_config
from database.connection import SessionLocal

# Setup logging
setup_logging(level="INFO")
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Software Factory",
    description="Convert business requirements into production-ready software",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    config = load_config()
    db_url = config.get("database", {}).get("url", "sqlite:///./factory.db")
    DatabaseConnection.initialize(db_url)
    logger.info("Application started")


@app.on_event("shutdown")
async def shutdown():
    """Close database on shutdown."""
    DatabaseConnection.close()
    logger.info("Application shutdown")


# ==================== HTML Routes ====================

@app.get("/", response_class=HTMLResponse)
async def index():
    """Dashboard home page."""
    return """
    <html>
        <head>
            <title>AI Software Factory</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { background-color: #0d1117; color: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; }
                .navbar { background-color: #161b22 !important; border-bottom: 1px solid #30363d; }
                .card { background-color: #0d1117; border-color: #30363d; }
                .btn-primary { background-color: #238636; border-color: #238636; }
                .btn-primary:hover { background-color: #2ea043; }
                .sidebar { background-color: #161b22; border-right: 1px solid #30363d; padding: 20px; }
                .project-card { cursor: pointer; transition: background-color 0.2s; }
                .project-card:hover { background-color: #161b22; }
                .status-badge { font-size: 0.85rem; padding: 0.35rem 0.65rem; }
                .status-created { background-color: #1f6feb; }
                .status-in_progress { background-color: #d29922; }
                .status-completed { background-color: #238636; }
            </style>
        </head>
        <body>
            <nav class="navbar navbar-dark">
                <div class="container-fluid">
                    <span class="navbar-brand mb-0 h1">🏭 AI Software Factory</span>
                </div>
            </nav>

            <div class="container-fluid">
                <div class="row mt-4">
                    <div class="col-md-3">
                        <div class="sidebar">
                            <h5>Navigation</h5>
                            <ul class="nav flex-column">
                                <li class="nav-item"><a class="nav-link" href="/">Dashboard</a></li>
                                <li class="nav-item"><a class="nav-link" href="/projects">Projects</a></li>
                                <li class="nav-item"><a class="nav-link" href="/create-project">New Project</a></li>
                                <li class="nav-item"><a class="nav-link" href="/execution-history">Execution History</a></li>
                                <li class="nav-item"><a class="nav-link" href="/logs">Logs</a></li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="col-md-9">
                        <div class="card">
                            <div class="card-body">
                                <h2>Dashboard</h2>
                                <p>Welcome to the AI Software Factory.</p>
                                <p>Create a new project or select an existing one to get started.</p>
                                <a href="/projects" class="btn btn-primary">View Projects</a>
                                <a href="/create-project" class="btn btn-success">Create Project</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
    </html>
    """


@app.get("/projects", response_class=HTMLResponse)
async def projects_page():
    """Projects list page."""
    return """
    <html>
        <head>
            <title>Projects - AI Software Factory</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { background-color: #0d1117; color: #c9d1d9; }
                .navbar { background-color: #161b22 !important; border-bottom: 1px solid #30363d; }
                .card { background-color: #0d1117; border-color: #30363d; }
                .table { color: #c9d1d9; border-color: #30363d; }
                .table-hover tbody tr:hover { background-color: #161b22; }
                .btn-primary { background-color: #238636; border-color: #238636; }
                .btn-primary:hover { background-color: #2ea043; }
            </style>
        </head>
        <body>
            <nav class="navbar navbar-dark">
                <div class="container-fluid">
                    <span class="navbar-brand mb-0 h1">🏭 AI Software Factory</span>
                </div>
            </nav>

            <div class="container mt-4">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h3>Projects</h3>
                        <a href="/create-project" class="btn btn-success btn-sm">+ New Project</a>
                    </div>
                    <div class="card-body">
                        <div id="projects-list">Loading...</div>
                    </div>
                </div>
            </div>

            <script>
                async function loadProjects() {
                    const response = await fetch('/api/projects');
                    const projects = await response.json();
                    
                    if (projects.length === 0) {
                        document.getElementById('projects-list').innerHTML = '<p>No projects found. Create one to get started.</p>';
                        return;
                    }
                    
                    let html = '<table class="table table-hover"><thead><tr><th>Name</th><th>Status</th><th>Created</th><th>Actions</th></tr></thead><tbody>';
                    
                    for (const project of projects) {
                        html += `<tr>
                            <td><a href="/project/${project.id}">${project.name}</a></td>
                            <td><span class="badge status-${project.status}">${project.status}</span></td>
                            <td>${new Date(project.created_at).toLocaleDateString()}</td>
                            <td>
                                <a href="/project/${project.id}" class="btn btn-sm btn-primary">View</a>
                                <button class="btn btn-sm btn-danger" onclick="deleteProject('${project.id}')">Delete</button>
                            </td>
                        </tr>`;
                    }
                    
                    html += '</tbody></table>';
                    document.getElementById('projects-list').innerHTML = html;
                }
                
                loadProjects();
            </script>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
    </html>
    """


# ==================== API Routes ====================

@app.get("/api/projects")
async def get_projects() -> List[Dict[str, Any]]:
    """Get all projects."""
    try:
        with SessionLocal() as session:
            projects = session.query(Project).all()
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "status": p.status,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                    "updated_at": p.updated_at.isoformat() if p.updated_at else None,
                }
                for p in projects
            ]
    except Exception as e:
        logger.error(f"Failed to get projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}")
async def get_project(project_id: str) -> Dict[str, Any]:
    """Get project details."""
    try:
        with SessionLocal() as session:
            project = session.query(Project).filter(Project.id == project_id).first()
            
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            return {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "business_requirement": project.business_requirement,
                "status": project.status,
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "updated_at": project.updated_at.isoformat() if project.updated_at else None,
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/artifacts")
async def get_project_artifacts(project_id: str) -> List[Dict[str, Any]]:
    """Get artifacts for a project."""
    try:
        with SessionLocal() as session:
            artifacts = session.query(Artifact).filter(
                Artifact.project_id == project_id
            ).all()
            
            return [
                {
                    "id": a.id,
                    "name": a.name,
                    "type": a.type,
                    "version": a.version,
                    "status": a.status,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in artifacts
            ]
    except Exception as e:
        logger.error(f"Failed to get artifacts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/execution-history")
async def get_execution_history(project_id: str) -> List[Dict[str, Any]]:
    """Get execution history for a project."""
    try:
        with SessionLocal() as session:
            executions = session.query(ExecutionHistory).filter(
                ExecutionHistory.project_id == project_id
            ).order_by(ExecutionHistory.started_at.desc()).limit(50).all()
            
            return [
                {
                    "id": e.id,
                    "phase": e.phase,
                    "status": e.status,
                    "started_at": e.started_at.isoformat() if e.started_at else None,
                    "completed_at": e.completed_at.isoformat() if e.completed_at else None,
                    "duration": e.duration,
                }
                for e in executions
            ]
    except Exception as e:
        logger.error(f"Failed to get execution history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/llm-calls")
async def get_llm_calls(project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get LLM calls for a project."""
    try:
        with SessionLocal() as session:
            calls = session.query(LLMCall).filter(
                LLMCall.project_id == project_id
            ).order_by(LLMCall.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": c.id,
                    "phase": c.phase,
                    "model": c.model,
                    "provider": c.provider,
                    "input_tokens": c.input_tokens,
                    "output_tokens": c.output_tokens,
                    "latency": c.latency,
                    "cost": c.cost,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in calls
            ]
    except Exception as e:
        logger.error(f"Failed to get LLM calls: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health check
@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    config = load_config()
    ui_config = config.get("ui", {})
    
    uvicorn.run(
        app,
        host=ui_config.get("host", "0.0.0.0"),
        port=ui_config.get("port", 8000),
        reload=ui_config.get("reload", True)
    )
