# AI Software Factory

A modular AI-powered software development lifecycle (SDLC) automation system that converts business requirements into production-ready software through automated analysis, design, implementation, testing, and deployment phases.

## Architecture

```
Business Requirement
    ↓
Requirements Analysis (AI Agent)
    ↓
Business Analysis (AI Agent)
    ↓
Functional Specification (AI Agent)
    ↓
Non-Functional Specification (AI Agent)
    ↓
Domain Model (AI Agent)
    ↓
Data Model (AI Agent)
    ↓
System Architecture (AI Agent)
    ↓
API Design (AI Agent)
    ↓
UI/UX Design (AI Agent)
    ↓
Database Design (AI Agent)
    ↓
Implementation Planning (AI Agent)
    ↓
Task Breakdown (AI Agent)
    ↓
Code Generation (AI Agent)
    ↓
Code Review (AI Agent)
    ↓
Unit Test Generation (AI Agent)
    ↓
Integration Test Generation (AI Agent)
    ↓
Bug Detection (AI Agent)
    ↓
Bug Fixing (AI Agent)
    ↓
Documentation (AI Agent)
    ↓
Packaging (AI Agent)
    ↓
Final Deliverable
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure LLM provider
cp config/config.example.yaml config/config.yaml

# Create a new project
python main.py create-project --name "my-app" --requirement "Build a task management application"

# Run the complete pipeline
python main.py run-pipeline --project "my-app"

# Start the web UI
python ui/app.py
```

## Features

- ✅ Modular SDLC phase execution
- ✅ LiteLLM integration for multi-provider LLM support
- ✅ SQLite-based artifact and state management
- ✅ Comprehensive artifact versioning and traceability
- ✅ Local FastAPI + HTMX web UI
- ✅ Configuration-driven design
- ✅ Type-safe with Pydantic models

## Documentation

See docs/ folder for detailed documentation.
