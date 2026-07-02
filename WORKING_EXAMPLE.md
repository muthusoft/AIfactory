# AI Software Factory - Working Example

This document demonstrates how to use the AI Software Factory to convert a business requirement into a production-ready application.

---

## Example: Building a Todo Application

### Step 1: Initialize the System

```bash
cd /home/muthu/AIFactory
python main.py init
```

**Output**:
```
Initializing AI Software Factory...
✓ Database initialized: sqlite:///./factory.db
✓ AI Software Factory initialized successfully!
```

The system creates:
- SQLite database with 11 tables
- Project metadata storage
- Artifact versioning system
- Execution history tracking
- Logging framework

---

### Step 2: Create a Project

```bash
python main.py create-project \
  --name "todo-app" \
  --requirement "Build a task management application where users can create, organize, and track their daily todos with due dates and priorities. Users should be able to create categories, set reminders, and mark tasks as complete."
```

**Output**:
```
Creating project: todo-app
✓ Project created: todo-app
  Project ID: 03c9d53f-9c70-4b1a-9a81-0ecc5a7f9822
  Path: projects/todo-app

Next steps:
  1. List available phases: python main.py list-phases
  2. Run requirements analysis: python main.py run-phase --project "todo-app" --phase requirements_analysis
  3. Run full pipeline: python main.py run-pipeline --project "todo-app"
```

**What happened**:
- Project created in database
- Project directory created: `projects/todo-app/`
- Business requirement stored
- Project assigned unique ID for tracking

---

### Step 3: View All Available SDLC Phases

```bash
python main.py list-phases
```

**Output** (15 phases shown):
```
📋 Available SDLC Phases:

1. Requirements Analysis (requirements_analysis)
   Analyze and extract business requirements
   Produces: requirements_document, functional_requirements, non_functional_requirements

2. System Architecture Design (architecture_design)
   Design overall system architecture and components
   Depends on: requirements_analysis
   Produces: architecture_diagram, component_diagram, technology_stack, design_patterns

3. Business Analysis & Specification (business_analysis)
   Create detailed business specification and use cases
   Depends on: requirements_analysis
   Produces: business_specification, use_cases, actors_definition

4. Domain Model & Entities (domain_modeling)
   Create domain model with entities and relationships
   Depends on: business_analysis
   Produces: domain_model, entities_diagram, class_diagram

5. Database Schema Design (database_design)
   Design normalized database schema based on domain model
   Depends on: domain_modeling
   Produces: database_schema_json, database_schema_diagram, sql_create_script, migration_script

6. System Sequence Design (SSD) (system_sequence_design)
   Create sequence diagrams for system interactions
   Depends on: domain_modeling
   Produces: sequence_diagrams, system_flow_diagram, interaction_model

7. UI Wireframes & Mockups (wireframe_design)
   Create wireframes and UI mockups for all screens
   Depends on: requirements_analysis, domain_modeling
   Produces: wireframes, ui_mockups, navigation_flow, screen_specifications

8. API & Interface Specification (api_design)
   Design REST API endpoints and data contracts
   Depends on: database_design, architecture_design
   Produces: api_specification, openapi_spec, data_models, error_handling_spec

9. Implementation Planning (task_planning)
   Break down implementation into tasks and stories
   Depends on: architecture_design, database_design, api_design
   Produces: task_breakdown, epics, stories, sprint_plan

10. Code Generation (code_generation)
    Generate source code based on specifications
    Depends on: task_planning, database_design, api_design, wireframe_design
    Produces: backend_code, frontend_code, database_models, configuration_files

[... phases 11-15 shown similarly ...]
```

---

### Step 4: Run Individual Phases

You can run phases individually or in any order. Dependencies are checked but can be forced if needed.

#### Run Requirements Analysis
```bash
python main.py run-phase --project "todo-app" --phase requirements_analysis
```

**What this produces**:
- Functional requirements extracted from business requirement
- Non-functional requirements (performance, security, scalability)
- Identified stakeholders and constraints
- Assumptions and ambiguities documented

**Output stored in**:
- `projects/todo-app/specifications/requirements.json`
- `projects/todo-app/specifications/requirements_analysis_report.md`

#### Run Database Design (can run independently)
```bash
python main.py run-phase --project "todo-app" --phase database_design --force
```

**What this produces**:
- Normalized database schema in JSON
- SQL CREATE TABLE statements
- Entity-relationship diagram (SVG)
- Migration scripts

**Output stored in**:
- `projects/todo-app/database/schema.json`
- `projects/todo-app/database/create_tables.sql`
- `projects/todo-app/database/schema_diagram.svg`
- `projects/todo-app/database/migration.sql`

#### Run System Sequence Design (SSD)
```bash
python main.py run-phase --project "todo-app" --phase system_sequence_design
```

**What this produces**:
- Sequence diagrams showing system interactions
- Use case interaction flows
- Component communication diagrams
- System flow diagrams (SVG)

**Output stored in**:
- `projects/todo-app/design/sequence_diagrams/create_todo.svg`
- `projects/todo-app/design/sequence_diagrams/complete_todo.svg`
- `projects/todo-app/design/system_flow_diagram.svg`

#### Run Wireframe Design
```bash
python main.py run-phase --project "todo-app" --phase wireframe_design
```

**What this produces**:
- UI mockups for all screens
- Wireframes showing screen layouts
- Navigation flow diagrams
- Component specifications

**Output stored in**:
- `projects/todo-app/ui/wireframes/dashboard.png`
- `projects/todo-app/ui/wireframes/todo_details.png`
- `projects/todo-app/ui/navigation_flow.svg`

#### Run API Design
```bash
python main.py run-phase --project "todo-app" --phase api_design
```

**What this produces**:
- REST API endpoints specification
- OpenAPI/Swagger documentation
- Request/response data models
- Error handling specifications

**Output stored in**:
- `projects/todo-app/api/openapi.yaml`
- `projects/todo-app/api/api_specification.md`
- `projects/todo-app/api/data_models.json`

---

### Step 5: Run Multiple Specific Phases

Run only the specification phases before code generation:

```bash
python main.py run-pipeline --project "todo-app" \
  --phases "requirements_analysis,business_analysis,domain_modeling,system_sequence_design,database_design,wireframe_design,api_design"
```

This runs only specification phases, generating all design artifacts before any code.

---

### Step 6: Run Complete Pipeline

Run the entire SDLC from requirements to packaging:

```bash
python main.py run-pipeline --project "todo-app"
```

This executes all 15 phases in dependency order:

```
Phase 1/15: Requirements Analysis
Phase 2/15: Business Analysis & Specification
Phase 3/15: Domain Modeling
Phase 4/15: System Sequence Design (SSD)
Phase 5/15: Database Schema Design
Phase 6/15: System Architecture Design
Phase 7/15: UI Wireframes & Mockups
Phase 8/15: API & Interface Specification
Phase 9/15: Implementation Planning
Phase 10/15: Code Generation
Phase 11/15: Code Quality Review
Phase 12/15: Test Generation
Phase 13/15: Bug Detection & Analysis
Phase 14/15: Bug Fixing
Phase 15/15: Project Packaging
```

---

### Step 7: View Project Status

```bash
python main.py show-status --project "todo-app"
```

**Output**:
```
Project: todo-app
Status: in_progress
Created: 2026-07-03 00:57:03
Updated: 2026-07-03 01:05:42
```

---

### Step 8: List All Projects

```bash
python main.py list-projects
```

**Output**:
```
Projects:
────────────────────────────────────────────────────────────────────────────────
Name: todo-app
ID: 03c9d53f-9c70-4b1a-9a81-0ecc5a7f9822
Status: in_progress
Created: 2026-07-03 00:57:03
────────────────────────────────────────────────────────────────────────────────
```

---

### Step 9: Explore Generated Artifacts

#### View Generated Specifications

```bash
# Check what was generated
ls -la projects/todo-app/specifications/
cat projects/todo-app/specifications/requirements.json
cat projects/todo-app/specifications/business_specification.md
```

#### View Database Schema

```bash
# View the JSON schema
cat projects/todo-app/database/schema.json

# View the SQL
cat projects/todo-app/database/create_tables.sql
```

**Example schema.json content**:
```json
{
  "entities": [
    {
      "name": "users",
      "fields": [
        {"name": "id", "type": "UUID", "primary_key": true},
        {"name": "email", "type": "VARCHAR(255)", "unique": true},
        {"name": "name", "type": "VARCHAR(255)"},
        {"name": "created_at", "type": "TIMESTAMP", "default": "NOW()"}
      ],
      "indexes": ["email"]
    },
    {
      "name": "todos",
      "fields": [
        {"name": "id", "type": "UUID", "primary_key": true},
        {"name": "user_id", "type": "UUID", "foreign_key": "users.id"},
        {"name": "title", "type": "VARCHAR(255)"},
        {"name": "description", "type": "TEXT"},
        {"name": "due_date", "type": "DATE"},
        {"name": "priority", "type": "ENUM(HIGH,MEDIUM,LOW)"},
        {"name": "completed_at", "type": "TIMESTAMP", "nullable": true},
        {"name": "created_at", "type": "TIMESTAMP", "default": "NOW()"}
      ],
      "indexes": ["user_id", "due_date"]
    }
  ]
}
```

#### View Generated Code

```bash
ls -la projects/todo-app/code/
ls -la projects/todo-app/code/backend/
ls -la projects/todo-app/code/frontend/
```

#### View Generated Tests

```bash
ls -la projects/todo-app/tests/
cat projects/todo-app/tests/unit_tests.py
cat projects/todo-app/tests/integration_tests.py
```

#### View System Sequence Diagrams

```bash
ls -la projects/todo-app/design/sequence_diagrams/
# Can open SVG files in browser to visualize
```

#### View Wireframes

```bash
ls -la projects/todo-app/ui/wireframes/
# PNG/SVG files can be opened with image viewer
```

#### View API Specification

```bash
cat projects/todo-app/api/openapi.yaml
```

---

### Step 10: Start Web UI

```bash
python ui/app.py
```

Visit `http://localhost:8000` in browser to see:
- Dashboard with project overview
- Project list
- Artifact viewer
- Execution history
- Phase status
- Generated code viewer
- Test results
- Performance metrics

---

### Step 11: Export Project

```bash
python main.py export-project --project "todo-app" --format zip
```

Creates: `projects/todo-app/exports/todo-app_complete.zip`

Contains:
- All source code
- All specifications
- All databases schema
- All documentation
- All tests
- All configuration
- Ready to deploy

---

## Complete Project Structure

After running the full pipeline, the project directory looks like:

```
projects/todo-app/
├── specifications/
│   ├── requirements.json              # ✅ Generated
│   ├── requirements_analysis_report.md
│   ├── business_specification.md      # ✅ Generated
│   ├── functional_requirements.md
│   └── non_functional_requirements.md
│
├── design/
│   ├── domain_model.json              # ✅ Generated
│   ├── entity_diagram.svg
│   ├── sequence_diagrams/             # ✅ Generated (SSD)
│   │   ├── create_todo.svg
│   │   ├── complete_todo.svg
│   │   └── delete_todo.svg
│   ├── system_flow.svg
│   ├── architecture.md                # ✅ Generated
│   └── architecture_diagram.svg
│
├── database/                           # ✅ Generated
│   ├── schema.json
│   ├── schema_diagram.svg
│   ├── create_tables.sql
│   └── migration.sql
│
├── ui/                                 # ✅ Generated
│   ├── wireframes/
│   │   ├── dashboard.png
│   │   ├── todo_details.png
│   │   └── settings.png
│   ├── screen_specifications.md
│   ├── navigation_flow.svg
│   └── component_library.md
│
├── api/                                # ✅ Generated
│   ├── openapi.yaml
│   ├── api_specification.md
│   ├── data_models.json
│   └── error_codes.md
│
├── code/                               # ✅ Generated
│   ├── backend/
│   │   ├── app.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routes/
│   │   └── services/
│   ├── frontend/
│   │   ├── package.json
│   │   ├── src/
│   │   ├── components/
│   │   └── pages/
│   └── database/
│       └── models/
│
├── tests/                              # ✅ Generated
│   ├── unit_tests.py
│   ├── integration_tests.py
│   ├── fixtures/
│   └── test_config.yaml
│
├── docs/                               # ✅ Generated
│   ├── README.md
│   ├── SETUP.md
│   ├── API_GUIDE.md
│   ├── DATABASE_GUIDE.md
│   ├── USER_GUIDE.md
│   ├── DEVELOPER_GUIDE.md
│   └── DEPLOYMENT_GUIDE.md
│
└── exports/
    └── todo-app_complete.zip           # ✅ Generated (ready to deploy)
```

---

## Key Features Demonstrated

✅ **Requirements-Driven**: Business requirement → All specifications  
✅ **Specification-First**: All specs before code generation  
✅ **Complete SDLC**: 15 phases covering entire lifecycle  
✅ **Independent Phases**: Run any phase separately  
✅ **Dynamic Schemas**: Database schema generated from requirements  
✅ **SSD Generation**: System sequence diagrams automatically created  
✅ **Wireframe Creation**: UI mockups and navigation flows  
✅ **API Specs**: OpenAPI documentation auto-generated  
✅ **Code Generation**: Production code from all specifications  
✅ **Testing**: Unit and integration tests auto-generated  
✅ **Documentation**: Complete guides auto-generated  
✅ **Quality**: Code review and bug detection phases  
✅ **Packaging**: Deployable package created  

---

## Commands Reference

```bash
# Initialize
python main.py init

# Create project
python main.py create-project --name "project-name" --requirement "requirement text"

# List projects
python main.py list-projects

# List phases
python main.py list-phases

# Run specific phase
python main.py run-phase --project "project-name" --phase requirements_analysis

# Run multiple phases
python main.py run-pipeline --project "project-name" \
  --phases "requirements_analysis,database_design,api_design"

# Run full pipeline
python main.py run-pipeline --project "project-name"

# Skip dependencies
python main.py run-phase --project "project-name" --phase api_design --force

# Check status
python main.py show-status --project "project-name"

# Start web UI
python ui/app.py
```

---

## Configuration

Edit `config/config.yaml` to:

```yaml
# Set LLM provider
llm:
  provider: "openai"  # or anthropic, gemini, ollama, etc.
  model: "gpt-4"
  api_key: "${OPENAI_API_KEY}"
  temperature: 0.7
  max_tokens: 4096

# Set database location
database:
  url: "sqlite:///./factory.db"

# Set project base path
project:
  base_path: "./projects"
```

---

## What You Get

A complete, production-ready application including:

✅ Backend source code (FastAPI/Django/Flask)  
✅ Frontend source code (React/Vue/HTML)  
✅ Database schema (SQL + migration scripts)  
✅ API specification (OpenAPI/Swagger)  
✅ UI wireframes and mockups  
✅ System sequence diagrams  
✅ Unit & integration tests  
✅ Security considerations  
✅ Performance optimization notes  
✅ Deployment guides  
✅ Developer documentation  
✅ User guides  

---

## Next Steps

1. Configure your LLM provider in `config/config.yaml`
2. Create a project with your business requirement
3. Run the specification phases to generate all designs
4. Review the generated specifications
5. Run code generation to create the application
6. Deploy using the generated deployment guide

**The system is ready to convert your business requirements into production code!**

---

Generated: 2026-07-03  
AI Software Factory v2.0  
Status: ✅ Operational
