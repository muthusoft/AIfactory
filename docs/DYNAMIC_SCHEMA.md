# Dynamic Schema Generation

## Overview

The AI Software Factory now uses **dynamic schema generation** instead of pre-defined schemas. Each project gets a database schema that is **specifically designed for its requirements**.

## Key Concepts

### 1. Project-Agnostic Factory Database

The factory itself uses a minimal database with just:
- **project_metadata** - Project information and tracking
- **artifacts** - Generated documents and artifacts
- **execution_history** - Pipeline execution records

### 2. Generated Application Database

Each project gets its own database schema generated during the **Database Design phase**, based on:
- Requirements analysis output
- Domain model
- Architecture decisions
- Business rules

### 3. Schema Stored as JSON

The generated schema is stored as JSON in the project metadata, allowing:
- Version control
- Easy modification
- Regeneration if needed
- Documentation
- Schema visualization

## Workflow

```
Business Requirement
    ↓
Requirements Analysis → Domain Model
    ↓
Database Design Phase → Generates Schema JSON
    ↓
Schema stored in ProjectMetadata.generated_schema
    ↓
API Design uses the generated schema
    ↓
Code Generation uses the generated schema
    ↓
Final application with custom database
```

## Schema Structure

Each generated schema contains:

```json
{
  "project_name": "todo-app",
  "description": "Schema for a task management application",
  "version": 1,
  "tables": [
    {
      "name": "users",
      "description": "User accounts",
      "columns": [
        {
          "name": "id",
          "type": "integer",
          "primary_key": true,
          "nullable": false
        },
        {
          "name": "email",
          "type": "string",
          "unique": true,
          "indexed": true
        }
      ],
      "relationships": [
        {
          "type": "many-to-one",
          "related_table": "users",
          "foreign_key": "user_id"
        }
      ],
      "indexes": [
        ["user_id", "completed"]
      ]
    }
  ]
}
```

## Running Individual Steps

Each phase can be run independently:

```bash
# List all available phases
python main.py list-phases

# Run just requirements analysis
python main.py run-phase --project "my-app" --phase requirements_analysis

# Run database design (depends on earlier phases)
python main.py run-phase --project "my-app" --phase database_design

# Force run even if dependencies not met
python main.py run-phase --project "my-app" --phase api_design --force

# Run specific phases in order
python main.py run-pipeline --project "my-app" --phases "requirements_analysis,database_design,api_design"
```

## Available Phases

| Phase ID | Name | Depends On | Produces |
|----------|------|-----------|----------|
| `requirements_analysis` | Requirements Analysis | - | requirements_document |
| `business_analysis` | Business Analysis | requirements_analysis | business_analysis_document |
| `domain_modeling` | Domain Modeling | business_analysis | domain_model |
| `database_design` | Database Design | domain_modeling | database_schema, sql_script |
| `architecture_design` | Architecture Design | requirements_analysis | architecture_design |
| `api_design` | API Design | database_design, architecture_design | api_specification, openapi_spec |
| `ui_design` | UI/UX Design | requirements_analysis, architecture_design | ui_design, wireframes |
| `task_planning` | Task Planning | architecture_design, database_design, api_design | task_breakdown, epics, stories |
| `code_generation` | Code Generation | task_planning, database_design, api_design | backend_code, frontend_code, database_code |
| `code_review` | Code Review | code_generation | review_report, issues_found |
| `test_generation` | Test Generation | code_generation | unit_tests, integration_tests |
| `bug_detection` | Bug Detection | code_review, test_generation | bugs_found, bug_report |
| `bug_fixing` | Bug Fixing | bug_detection | fixed_code |
| `documentation` | Documentation | code_generation, api_design | readme, api_docs, user_guide |
| `packaging` | Packaging | documentation, bug_fixing | deliverable |

## Database Design Phase

### Input
- Domain model (from Domain Modeling phase)
- Business rules
- Requirements
- Architecture decisions

### Process
1. Parse domain model
2. Identify entities and relationships
3. Normalize schema
4. Add indexes for performance
5. Define constraints
6. Generate SQL script

### Output
- Schema JSON
- SQL CREATE TABLE statements
- Migration scripts
- Documentation

### Example Output

```python
{
    "tables": [
        {
            "name": "users",
            "columns": [
                {"name": "id", "type": "integer", "primary_key": true},
                {"name": "email", "type": "string", "unique": true},
                {"name": "created_at", "type": "datetime"}
            ]
        },
        {
            "name": "todos",
            "columns": [
                {"name": "id", "type": "integer", "primary_key": true},
                {"name": "user_id", "type": "integer", "foreign_key": "users.id"},
                {"name": "title", "type": "string"},
                {"name": "completed", "type": "boolean", "default": false}
            ]
        }
    ]
}
```

## Phase Dependencies

Phases are automatically run in dependency order:

```
requirements_analysis
├── business_analysis
│   └── domain_modeling
│       └── database_design ──┐
├── architecture_design ──────┼──┐
│   └── api_design ───────────┤──┼──┐
│   └── ui_design ────────────┤──┼──┼──┐
└── task_planning ───────────┐│  │  │  │
    └── code_generation ─────┼┘  │  │  │
        ├── code_review ─┐   │   │  │  │
        │                └─┐ │   │  │  │
        ├── test_generation ┤ │   │  │  │
        │                    │ │   │  │  │
        └── bug_detection ───┘─┼───┘  │  │
            └── bug_fixing ────┘      │  │
                └── documentation ────┴──┘
                    └── packaging
```

## Running Phases

### Sequential Execution (Default)

```bash
# Run all phases in dependency order
python main.py run-pipeline --project "my-app"

# Runs: requirements_analysis → business_analysis → domain_modeling → ...
```

### Selective Execution

```bash
# Run only specific phases
python main.py run-pipeline --project "my-app" \
  --phases "requirements_analysis,database_design,api_design"

# Runs: requirements_analysis → database_design → api_design
```

### Individual Phase Execution

```bash
# Run single phase (may skip if dependencies not met)
python main.py run-phase --project "my-app" --phase database_design

# Force run without dependency check
python main.py run-phase --project "my-app" --phase api_design --force
```

## Schema Versioning

Each project tracks schema versions:

```python
# Schema is stored with version
project.generated_schema_version = 1
project.generated_schema = {schema_json}

# When regenerated
project.generated_schema_version = 2
project.generated_schema = {new_schema_json}
```

## Benefits

### 1. **Flexibility**
- Each project gets exactly the database it needs
- No pre-defined constraints
- Can evolve with requirements

### 2. **Traceability**
- Schema is stored and versioned
- Can see how it was derived
- Full change history

### 3. **Automation**
- Database design is automated
- Schema generation from requirements
- SQL script generation

### 4. **Independence**
- Each phase is independent
- Can re-run any phase
- Can skip unnecessary phases
- Can run in any order (if forcing)

### 5. **Visibility**
- Schema as JSON is human-readable
- Can be version controlled
- Can be reviewed before generation
- Can be modified manually if needed

## Example Workflow

### Step 1: Create Project

```bash
python main.py create-project \
  --name "todo-app" \
  --requirement "A task management app with users, todos, and categories"
```

### Step 2: List Available Phases

```bash
python main.py list-phases
```

Output:
```
📋 Available SDLC Phases:

1. Requirements Analysis (requirements_analysis)
   Analyze and extract business requirements
   Produces: requirements_document

2. Business Analysis (business_analysis)
   Detailed business analysis and specifications
   Depends on: requirements_analysis
   Produces: business_analysis_document

...
```

### Step 3: Run Requirements Analysis

```bash
python main.py run-phase --project "todo-app" --phase requirements_analysis
```

Output:
```
Running phase 'requirements_analysis' for project 'todo-app'...
✓ Phase completed: requirements_analysis
  Status: completed
  Outputs: requirements_document
```

### Step 4: Run Database Design

```bash
python main.py run-phase --project "todo-app" --phase database_design
```

Output:
```
Running phase 'database_design' for project 'todo-app'...
✓ Phase completed: database_design
  Status: completed
  Outputs: database_schema, sql_script
```

### Step 5: Run Full Pipeline

```bash
python main.py run-pipeline --project "todo-app"
```

Output:
```
Running pipeline for project 'todo-app'...
✓ Pipeline execution completed
  ✓ requirements_analysis: completed
  ✓ business_analysis: completed
  ✓ domain_modeling: completed
  ✓ database_design: completed
  ✓ architecture_design: completed
  ✓ api_design: completed
  ✓ code_generation: completed
  ✓ documentation: completed
  ✓ packaging: completed
```

## Advanced Usage

### Retry Failed Phase

```bash
# If a phase fails, retry it
python main.py run-phase --project "todo-app" --phase code_generation --force
```

### Skip to Later Phase

```bash
# Skip earlier phases and jump to a later one
python main.py run-phase --project "todo-app" --phase api_design --force
```

### Run Multiple Phases

```bash
# Run specific phases in order
python main.py run-pipeline --project "todo-app" \
  --phases "database_design,api_design,code_generation"
```

### Check Current Status

```bash
# See which phases have run
python main.py show-status --project "todo-app"
```

## Schema Export

Generated schemas can be exported:

```bash
# Export to JSON
python -c "
from database.schema_generator import SchemaGenerator
gen = SchemaGenerator()
schema = gen.example_todo_app_schema()
gen.save_schema(schema, 'schema.json')
"

# Export to SQL
python -c "
from database.schema_generator import SchemaGenerator
gen = SchemaGenerator()
schema = gen.example_todo_app_schema()
sql = gen.generate_sql_script(schema)
print(sql)
"
```

## Next Steps

1. **Requirements Analysis Phase** will parse the business requirement and create a domain model
2. **Database Design Phase** will automatically generate the database schema
3. Each subsequent phase uses the generated schema
4. Final code is customized for the specific database

This ensures each generated application has the optimal database structure for its unique requirements.
