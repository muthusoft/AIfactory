# AI Software Factory Architecture

## Overview

The AI Software Factory is a modular, extensible system that automates the software development lifecycle (SDLC) through AI agents. Each phase of development is implemented as an independent, composable module that can be executed individually or as part of a complete pipeline.

## Core Components

### 1. AI Layer (`ai/`)

Provides unified LLM access through LiteLLM, supporting multiple providers:

- **llm.py**: LiteLLM wrapper with unified interface
  - Multi-provider support (OpenAI, Anthropic, Gemini, Ollama, etc.)
  - Automatic retry with exponential backoff
  - Cost tracking and token counting
  - Structured response handling

- **prompt_loader.py**: Template-based prompt management
  - Jinja2 templating for dynamic prompts
  - Version control for prompt templates
  - Registry for organizing prompts by category

- **response_parser.py**: Structured output extraction
  - JSON/YAML parsing from markdown code blocks
  - Code block extraction by language
  - Section extraction from markdown
  - Safe extraction with fallbacks

- **validator.py**: Output validation framework
  - Custom validation rules per phase
  - Pydantic model integration
  - JSON schema validation
  - Python syntax validation

- **retry.py**: Resilient operation execution
  - Exponential backoff with jitter
  - Circuit breaker pattern
  - Configurable retry policies
  - Sync and async support

- **context_builder.py**: LLM context management
  - Artifact tracking and versioning
  - Token budget management
  - Context pruning for size limits
  - Traceability across phases

### 2. Database Layer (`database/`)

SQLite-based persistence with comprehensive schema:

- **connection.py**: Database connection management
  - Session factory pattern
  - Connection pooling
  - Context manager for transactions

- **schema.py**: Comprehensive data model
  - Projects and requirements
  - Artifacts with versioning
  - LLM call history and analytics
  - Execution history and logs
  - Code files and tests
  - Bugs and reviews

### 3. Agent Layer (`agents/`)

SDLC phase implementation as autonomous agents:

- **base_agent.py**: Base class for all agents
  - LLM interaction abstraction
  - Artifact management
  - Validation framework
  - Context building
  - Execution tracking

- **requirement_analyzer.py**: Phase 1 - Requirements Analysis
  - Extract business objectives
  - Identify actors and use cases
  - Define functional/non-functional requirements
  - Document constraints and assumptions
  - Flag ambiguities

- Additional agents for other phases (to be implemented):
  - Business analyzer
  - Architect
  - Database designer
  - API designer
  - UI designer
  - Task planner
  - Code generator
  - Code reviewer
  - Test generator
  - Bug fixer
  - Documentation generator
  - Packager

### 4. Web UI (`ui/`)

FastAPI-based modern web interface:

- **app.py**: FastAPI application
  - REST API for project management
  - HTML interface with HTMX
  - Real-time status updates
  - Dark mode support
  - Artifact viewer
  - Execution history
  - LLM call analytics

### 5. Utilities (`utils/`)

Supporting modules:

- **logger.py**: Structured logging with JSON support
- **config.py**: Configuration management with env var expansion
- **validators.py**: Data validation utilities
- **helpers.py**: Common helper functions
- **exceptions.py**: Custom exception hierarchy

## Data Flow

```
Business Requirement
    ↓
[RequirementAnalyzer Agent]
    - Calls LLM with prompt template
    - Parses structured JSON response
    - Validates output
    - Creates artifact in database
    ↓
Artifacts & Context
    ↓
[Next Phase Agent]
    - Loads context from database
    - Adds previous artifacts to context
    - Calls LLM with enhanced context
    - Parses and validates response
    - Creates new artifacts
    - Updates execution history
    ↓
Final Deliverable
```

## Key Design Patterns

### 1. Agent Pattern
- Each phase is an autonomous agent
- Agents inherit from `BaseAgent`
- Share common interfaces for LLM interaction
- Independently testable and deployable

### 2. Repository Pattern
- Database access through session/repository layer
- ORM-based queries
- Transaction management
- Separation of concerns

### 3. Strategy Pattern
- Pluggable LLM providers through LiteLLM
- Swappable validators
- Configurable retry policies
- Multiple response parsing strategies

### 4. Template Method Pattern
- Base agent defines execution skeleton
- Subclasses implement phase-specific logic
- Common artifact creation flow
- Unified validation pipeline

### 5. Factory Pattern
- Agent factory for creating phase agents
- Artifact factory for versioning
- Session factory for database access

## Module Dependencies

```
main.py
├── utils (config, logging, exceptions)
├── database (SQLite, ORM)
└── agents
    └── base_agent
        ├── ai (LLM, prompts, validation)
        ├── database (repositories)
        └── utils
```

## Configuration Architecture

```yaml
config/
├── config.yaml          # Runtime configuration
├── models.yaml          # LLM model definitions
├── prompts.yaml         # Prompt registry
└── settings.yaml        # Application settings
```

### Configuration Hierarchy
1. Default values in code
2. YAML configuration files
3. Environment variables (override YAML)
4. Runtime configuration

## Artifact Management

### Versioning Strategy
- Every artifact is versioned
- Previous versions are retained
- Parent-child relationships tracked
- Immutable artifact history
- Traceability to source requirements

### Artifact Lifecycle
```
Draft → Reviewed → Approved → Used in Next Phase → Archived
```

## Execution Pipeline

### Linear Execution (Default)
```
Phase 1 → Phase 2 → Phase 3 → ... → Phase N
```

### Parallel Execution (Future)
```
       Phase 2a
      /         \
Phase 1         → Phase 4
      \         /
       Phase 2b
```

### Resumable Execution
- Checkpoints after each phase
- Can resume from any phase
- State preserved in database
- Full execution history maintained

## Security Considerations

1. **API Key Management**
   - Environment variables for sensitive data
   - No hardcoded credentials
   - Encrypted storage for stored keys

2. **Database Access**
   - SQLite with file-level permissions
   - Transaction management
   - Data validation on input

3. **LLM Interaction**
   - Prompt injection prevention
   - Response validation
   - Rate limiting via retry policy

4. **File Access**
   - Restricted to project directories
   - Path traversal prevention
   - File permission checks

## Extensibility

### Adding a New SDLC Phase

1. Create new agent in `agents/`
   ```python
   class NewPhaseAgent(BaseAgent):
       def __init__(self, project_id, llm_config):
           super().__init__(project_id, llm_config, "new_phase_name")
       
       async def execute(self, input_data):
           # Phase logic here
           pass
   ```

2. Create prompt templates in `prompts/new_phase/`
3. Create system prompt in `prompts/system_prompts/`
4. Register in pipeline
5. Add to CLI in `main.py`

### Adding a New LLM Provider

1. LiteLLM already supports it (no code changes needed)
2. Update `config/models.yaml` with model definitions
3. Set API key in environment or config
4. Test with existing agents

### Adding Validation Rules

```python
validator.register_rule(
    "phase_name",
    "rule_name",
    lambda data: check_condition(data),
    "Error message"
)
```

## Performance Considerations

1. **Token Optimization**
   - Context pruning to stay within limits
   - Efficient prompt design
   - Response compression

2. **Parallel Processing**
   - Async/await for I/O operations
   - Connection pooling
   - Batch operations where possible

3. **Caching**
   - Artifact caching
   - Prompt template caching
   - Response caching for identical inputs

4. **Scalability**
   - Database indexing on frequently queried columns
   - Artifact pagination
   - Lazy loading of large artifacts

## Testing Strategy

1. **Unit Tests**
   - Individual components in isolation
   - Mock LLM responses
   - Validation rules

2. **Integration Tests**
   - Phase interactions
   - Database transactions
   - End-to-end pipelines

3. **Performance Tests**
   - LLM response times
   - Database query performance
   - Memory usage under load

## Monitoring and Observability

1. **Logging**
   - Structured JSON logging
   - Phase execution logs
   - LLM call logs with metrics
   - Error tracking

2. **Metrics**
   - LLM tokens per phase
   - Cost tracking
   - Latency monitoring
   - Success/failure rates

3. **Traceability**
   - Requirement → Artifact → Code mapping
   - LLM call provenance
   - Execution audit trail
   - Version history

## Future Enhancements

1. **Parallel Phase Execution**
   - Dependencies between phases
   - Concurrent agent execution
   - Resource management

2. **Interactive Refinement**
   - User feedback loops
   - Artifact modification workflows
   - Iterative improvement

3. **Advanced Analytics**
   - Cost optimization
   - Quality metrics
   - Performance predictions

4. **Integration with External Tools**
   - Git repository integration
   - CI/CD pipeline integration
   - Project management tools
   - Code collaboration platforms
