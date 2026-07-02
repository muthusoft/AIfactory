"""
Dynamic database schema generation for the AI Software Factory.

Instead of pre-defined schemas, the database schema is generated based on
the requirements of each project. This allows each generated application
to have exactly the database structure it needs.
"""

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey,
    JSON, UniqueConstraint, Index, create_engine, MetaData
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, List, Any

Base = declarative_base()


class ProjectMetadata(Base):
    """Metadata about the project (not the generated app database)."""
    __tablename__ = "project_metadata"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    business_requirement = Column(Text, nullable=False)
    status = Column(String(50), default="created")  # created, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    base_path = Column(String(255))
    config = Column(JSON)  # Project-specific config
    
    # Schema information
    generated_schema = Column(JSON)  # The schema that was generated for this project
    generated_schema_version = Column(Integer, default=1)
    
    # Relationships
    artifacts = relationship("Artifact", back_populates="project")
    execution_history = relationship("ExecutionHistory", back_populates="project")
    requirements = relationship("Requirement", back_populates="project")
    tasks = relationship("Task", back_populates="project")
    
    __table_args__ = (
        Index("idx_project_status", "status"),
    )


class Requirement(Base):
    """Stores project requirements."""
    __tablename__ = "requirements"
    
    id = Column(String(50), primary_key=True)
    project_id = Column(String(50), ForeignKey("project_metadata.id"), nullable=False)
    type = Column(String(50), nullable=False)  # functional, non_functional, constraint
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20))  # high, medium, low
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("ProjectMetadata", back_populates="requirements")
    artifacts = relationship("Artifact", back_populates="requirement")
    
    __table_args__ = (
        Index("idx_requirement_project", "project_id"),
        Index("idx_requirement_type", "type"),
    )
    artifacts = relationship("Artifact", back_populates="requirement")
    
    __table_args__ = (
        Index("idx_requirement_project", "project_id"),
        Index("idx_requirement_type", "type"),
    )


class Artifact(Base):
    """Stores all generated artifacts."""
    __tablename__ = "artifacts"
    
    id = Column(String(50), primary_key=True)
    project_id = Column(String(50), ForeignKey("project_metadata.id"), nullable=False)
    requirement_id = Column(String(50), ForeignKey("requirements.id"), nullable=True)
    type = Column(String(50), nullable=False)  # requirement, design, architecture, api, code, test, doc
    name = Column(String(255), nullable=False)
    version = Column(Integer, default=1)
    content = Column(Text)
    file_path = Column(String(255))
    status = Column(String(50), default="draft")  # draft, reviewed, approved, deployed
    created_by_phase = Column(String(100))
    created_by_llm_call = Column(String(50), ForeignKey("llm_calls.id"), nullable=True)
    parent_artifact_id = Column(String(50), nullable=True)  # For versioning
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("ProjectMetadata", back_populates="artifacts")
    requirement = relationship("Requirement", back_populates="artifacts")
    llm_call = relationship("LLMCall", back_populates="artifact")
    
    __table_args__ = (
        UniqueConstraint("project_id", "name", "version", name="uq_artifact_version"),
        Index("idx_artifact_project", "project_id"),
        Index("idx_artifact_type", "type"),
        Index("idx_artifact_status", "status"),
    )


class LLMCall(Base):
    """Stores all LLM interactions."""
    __tablename__ = "llm_calls"
    
    id = Column(String(50), primary_key=True)
    project_id = Column(String(50), ForeignKey("project_metadata.id"), nullable=True)
    phase = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)
    prompt = Column(Text, nullable=False)
    system_prompt = Column(Text)
    response = Column(Text, nullable=False)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    latency = Column(Float)
    cost = Column(Float, default=0.0)
    temperature = Column(Float)
    max_tokens = Column(Integer)
    retry_count = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    artifact = relationship("Artifact", back_populates="llm_call")
    
    __table_args__ = (
        Index("idx_llm_call_phase", "phase"),
        Index("idx_llm_call_model", "model"),
        Index("idx_llm_call_project", "project_id"),
    )


class Task(Base):
    """Represents implementation tasks."""
    __tablename__ = "tasks"
    
    id = Column(String(50), primary_key=True)
    project_id = Column(String(50), ForeignKey("project_metadata.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(50))  # feature, bug_fix, refactor, documentation
    status = Column(String(50), default="pending")  # pending, in_progress, completed, blocked
    priority = Column(String(20))
    complexity = Column(String(20))  # simple, medium, complex
    estimated_hours = Column(Float)
    parent_task_id = Column(String(50), nullable=True)  # For subtasks
    dependencies = Column(JSON)  # List of task IDs this depends on
    assigned_to = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    project = relationship("ProjectMetadata", back_populates="tasks")
    
    __table_args__ = (
        Index("idx_task_project", "project_id"),
        Index("idx_task_status", "status"),
    )


class CodeFile(Base):
    """Stores generated code files."""
    __tablename__ = "code_files"
    
    id = Column(String(50), primary_key=True)
    project_id = Column(String(50), ForeignKey("project_metadata.id"), nullable=False)
    file_path = Column(String(255), nullable=False)
    language = Column(String(50))
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    checksum = Column(String(64))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint("project_id", "file_path", "version", name="uq_code_file_version"),
        Index("idx_code_file_project", "project_id"),
    )


class TestCase(Base):
    """Stores generated test cases."""
    __tablename__ = "test_cases"
    
    id = Column(String(50), primary_key=True)
    project_id = Column(String(50), ForeignKey("project_metadata.id"), nullable=False)
    type = Column(String(50))  # unit, integration, e2e
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(50), default="generated")  # generated, executed, passed, failed
    result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime)
    
    __table_args__ = (
        Index("idx_test_case_project", "project_id"),
        Index("idx_test_case_type", "type"),
    )


class Bug(Base):
    """Stores detected bugs."""
    __tablename__ = "bugs"
    
    id = Column(String(50), primary_key=True)
    project_id = Column(String(50), ForeignKey("project_metadata.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20))  # critical, high, medium, low
    status = Column(String(50), default="detected")  # detected, fixed, verified, closed
    file_path = Column(String(255))
    line_number = Column(Integer)
    error_message = Column(Text)
    fix_applied = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    fixed_at = Column(DateTime)
    
    __table_args__ = (
        Index("idx_bug_project", "project_id"),
        Index("idx_bug_status", "status"),
    )


class Review(Base):
    """Stores code and design reviews."""
    __tablename__ = "reviews"
    
    id = Column(String(50), primary_key=True)
    project_id = Column(String(50), ForeignKey("project_metadata.id"), nullable=False)
    artifact_id = Column(String(50), ForeignKey("artifacts.id"), nullable=True)
    type = Column(String(50))  # code_review, design_review, architecture_review
    reviewer = Column(String(100))
    content = Column(Text, nullable=False)
    issues = Column(JSON)  # List of issues found
    status = Column(String(50))  # approved, approved_with_changes, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_review_project", "project_id"),
        Index("idx_review_artifact", "artifact_id"),
    )


class ExecutionHistory(Base):
    """Stores pipeline execution history."""
    __tablename__ = "execution_history"
    
    id = Column(String(50), primary_key=True)
    project_id = Column(String(50), ForeignKey("project_metadata.id"), nullable=False)
    phase = Column(String(100), nullable=False)
    status = Column(String(50))  # running, completed, failed, skipped
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration = Column(Float)  # seconds
    result = Column(JSON)
    error_message = Column(Text)
    logs = Column(Text)
    
    # Relationships
    project = relationship("ProjectMetadata", back_populates="execution_history")
    
    __table_args__ = (
        Index("idx_execution_project", "project_id"),
        Index("idx_execution_phase", "phase"),
    )


class Log(Base):
    """Stores execution logs."""
    __tablename__ = "logs"
    
    id = Column(String(50), primary_key=True)
    project_id = Column(String(50), ForeignKey("project_metadata.id"), nullable=True)
    level = Column(String(20))  # DEBUG, INFO, WARNING, ERROR
    component = Column(String(100))
    message = Column(Text, nullable=False)
    context = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_log_project", "project_id"),
        Index("idx_log_level", "level"),
        Index("idx_log_component", "component"),
    )


def create_database(database_url: str) -> None:
    """
    Create database schema.

    Args:
        database_url: SQLAlchemy database URL
    """
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    print(f"Database schema created at {database_url}")
