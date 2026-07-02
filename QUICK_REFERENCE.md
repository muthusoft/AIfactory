# AI Software Factory - Quick Reference

## Installation (2 minutes)

```bash
# 1. Setup Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
export OPENAI_API_KEY=sk-xxx

# 4. Initialize database
python main.py init
```

## Basic Commands

```bash
# Create project
python main.py create-project --name "app-name" --requirement "Your requirement"

# List projects
python main.py list-projects

# Show project status
python main.py show-status --project "app-name"

# Start web UI
python ui/app.py
# Open http://localhost:8000
```

## Configuration

### Set LLM Provider

```yaml
# config/config.yaml
llm:
  provider: openai              # openai, anthropic, gemini, ollama
  api_key: ${OPENAI_API_KEY}   # Use env vars
  model: gpt-4-turbo-preview
```

### Database

```yaml
database:
  url: sqlite:///./factory.db   # SQLite database path
```

### Web UI

```yaml
ui:
  host: 0.0.0.0               # Interface to bind
  port: 8000                  # Port number
```

## LLM Providers Quick Setup

### OpenAI
```bash
export OPENAI_API_KEY=sk-xxx
```

### Anthropic
```bash
export ANTHROPIC_API_KEY=sk-ant-xxx
```

### Google Gemini
```bash
export GOOGLE_API_KEY=xxx
```

### Ollama (Local)
```bash
ollama pull mistral
ollama serve
# No API key needed
```

## Project Workflow

### 1. Create with Clear Requirement
```bash
python main.py create-project \
  --name "project" \
  --requirement "Build X with features Y and Z"
```

### 2. View in Dashboard
```bash
python ui/app.py
# Open http://localhost:8000/projects
```

### 3. See Generated Artifacts
- Requirements analysis
- Architecture design
- Database schema
- API specification
- Tasks and stories
- Generated code
- Tests
- Documentation

## File Organization

```
config/
  config.yaml          ← Your main configuration
  config.example.yaml  ← Reference
  models.yaml          ← LLM model definitions

prompts/
  registry.yaml        ← Prompt index
  requirements/        ← Requirements phase templates
  system_prompts/      ← System prompts

projects/
  project_name/
    artifacts/         ← Generated documents
    code/             ← Generated code
    tests/            ← Generated tests
    logs/             ← Execution logs

database/
  schema.py            ← Database structure
  factory.db           ← SQLite database file
```

## Key Concepts

### Artifacts
- Versioned documents (requirements, design, code)
- Stored in database and as files
- Traceable to source requirements
- Status: draft → reviewed → approved

### Agents
- SDLC phase implementations (requirements, architecture, code generation)
- Inherit from `BaseAgent`
- Use shared LLM interface
- Validate outputs
- Create versioned artifacts

### Context
- Previous phase outputs passed to next phase
- LLM has full project context
- Token-budgeted for efficiency
- Pruned automatically if too large

### Validation
- Custom rules per phase
- Pydantic model validation
- JSON schema validation
- Python syntax checking

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API key not found | Set `export OPENAI_API_KEY=sk-xxx` |
| Database locked | `python main.py init` to reset |
| Port 8000 in use | Change `ui.port` in config.yaml |
| LLM timeout | Increase `llm.retry.max_wait` in config |
| Out of memory | Reduce `llm.max_tokens` or increase token limit |

## Common Customizations

### Change Default Model
```yaml
llm:
  model: gpt-4o  # or claude-3-opus, gemini-1.5-pro
```

### Adjust Temperature
```yaml
llm:
  temperature: 0.5  # Lower = deterministic, Higher = creative
```

### Change Database Location
```yaml
database:
  url: sqlite:////data/factory.db
```

### Increase Retry Attempts
```yaml
llm:
  retry:
    max_retries: 5
    max_wait: 120
```

## API Endpoints

```
GET  /api/health                              Health check
GET  /api/projects                            List projects
POST /api/projects                            Create project
GET  /api/projects/{id}                       Get project
GET  /api/projects/{id}/artifacts             List artifacts
GET  /api/projects/{id}/execution-history     Execution history
GET  /api/projects/{id}/llm-calls             LLM call history
```

## Environment Variables

```bash
# LLM API Keys
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
GOOGLE_API_KEY=xxx
OPENROUTER_API_KEY=xxx

# Database
DATABASE_URL=sqlite:///./factory.db

# Logging
LOG_LEVEL=INFO
```

## Project Structure Tips

### Adding New Agent
1. Create `agents/my_agent.py`
2. Inherit from `BaseAgent`
3. Implement `async def execute(input_data)`
4. Create prompts in `prompts/my_phase/`
5. Register in CLI

### Adding New Prompt Template
1. Create `prompts/category/name.jinja2`
2. Add to `prompts/registry.yaml`
3. Use: `await agent.call_llm("category/name", variables={...})`

### Adding Validation Rule
```python
validator.register_rule(
    "phase_name",
    "rule_name",
    lambda data: condition(data),
    "Error message"
)
```

## Performance Tips

1. **Faster responses**: Lower temperature, smaller max_tokens
2. **Better quality**: Higher temperature, increase max_tokens
3. **Cost savings**: Use smaller models (GPT-3.5, Claude Haiku, Gemini Flash)
4. **Local only**: Use Ollama or LM Studio with local models

## Debug Commands

```bash
# Check configuration
cat config/config.yaml

# View logs
tail -f logs/factory.log

# Database stats
python -c "from database import DatabaseConnection; print(DatabaseConnection.get_session().query(Project).count())"

# List artifacts for project
python -c "from database import *; from database.connection import SessionLocal; s = SessionLocal(); print(len(s.query(Artifact).filter(Artifact.project_id=='ID').all()))"
```

## URLs & Ports

```
Web UI:          http://localhost:8000
API Base:        http://localhost:8000/api
Health Check:    http://localhost:8000/api/health
Projects View:   http://localhost:8000/projects
```

## File Limits

| Item | Limit | Config Key |
|------|-------|-----------|
| Max tokens per call | 4000 | `llm.max_tokens` |
| Context tokens | 8000 | `ai.max_context_tokens` |
| Max prompt size | 1000 chars | `artifacts.max_prompt_size` |
| Max artifact size | No limit | Database stored |

## Best Practices

1. ✅ Always provide detailed requirements
2. ✅ Use specific technology preferences
3. ✅ Include non-functional requirements
4. ✅ Review generated artifacts
5. ✅ Keep configuration in version control
6. ✅ Use environment variables for secrets
7. ✅ Monitor LLM costs and token usage
8. ✅ Backup projects directory regularly

## Resources

| Resource | Location |
|----------|----------|
| Documentation | `docs/` |
| Architecture | `docs/ARCHITECTURE.md` |
| Getting Started | `docs/GETTING_STARTED.md` |
| Installation | `INSTALLATION.md` |
| Examples | Project creation examples |
| Configuration | `config/config.example.yaml` |

## Support

- **Logs**: Check `logs/factory.log`
- **Config**: Review `config/config.yaml`
- **Documentation**: See `docs/` folder
- **GitHub Issues**: Report bugs and request features
