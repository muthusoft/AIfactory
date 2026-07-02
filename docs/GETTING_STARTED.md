# Getting Started with AI Software Factory

## 5-Minute Quick Start

### 1. Install

```bash
git clone <repo>
cd ai-factory
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

```bash
# Copy example config
cp config/config.example.yaml config/config.yaml

# Set your API key
export OPENAI_API_KEY=sk-xxx
```

### 3. Initialize

```bash
python main.py init
```

### 4. Create a Project

```bash
python main.py create-project \
  --name "my-app" \
  --requirement "Build a simple todo list app with user authentication"
```

### 5. Start Web UI

```bash
python ui/app.py
```

Visit `http://localhost:8000` to see the dashboard.

## Example Projects

### Example 1: Todo List Application

```bash
python main.py create-project \
  --name "todo-app" \
  --requirement "
    Build a web application for managing todo lists.
    Users should be able to:
    - Create an account and login
    - Create, read, update, delete todos
    - Mark todos as complete
    - Organize todos into categories
    - Set due dates and reminders
    - Share lists with other users
    
    Requirements:
    - Mobile-friendly responsive design
    - Real-time synchronization
    - Should support at least 10,000 users
    - All user data must be encrypted
  "
```

### Example 2: E-Commerce Platform

```bash
python main.py create-project \
  --name "ecommerce-platform" \
  --requirement "
    Build an e-commerce platform with:
    - Product catalog with search and filtering
    - Shopping cart and checkout
    - Payment processing (Stripe integration)
    - Order management
    - User accounts and profiles
    - Admin dashboard for inventory
    - Email notifications
    
    Non-functional requirements:
    - Support 100k concurrent users
    - 99.9% uptime SLA
    - GDPR compliant
  "
```

### Example 3: Analytics Dashboard

```bash
python main.py create-project \
  --name "analytics-dashboard" \
  --requirement "
    Create a real-time analytics dashboard:
    - Display website traffic metrics
    - User behavior analytics
    - Revenue tracking
    - Custom report generation
    - Data export to CSV/Excel
    - Real-time notifications for alerts
    
    Technology preferences:
    - Backend: Python/FastAPI
    - Database: PostgreSQL
    - Frontend: React with TypeScript
  "
```

## CLI Commands

### Project Management

```bash
# List all projects
python main.py list-projects

# Show project status
python main.py show-status --project "my-app"

# View project details
python main.py show-status --project "my-app" --detail
```

### Pipeline Execution

```bash
# Run entire pipeline
python main.py run-pipeline --project "my-app"

# Run specific phase
python main.py run-phase --project "my-app" --phase "requirements_analysis"

# Run specific phase and subsequent phases
python main.py run-phase --project "my-app" --phase "architecture_design" --and-next
```

### Configuration

```bash
# Show current configuration
python main.py show-config

# Switch LLM provider
python main.py set-config llm.provider anthropic

# Set API key
python main.py set-config llm.api_key ${ANTHROPIC_API_KEY}
```

## Web UI Guide

### Dashboard

The main dashboard shows:
- Quick project creation
- Recent projects
- Recent activities
- System status

### Projects View

View all projects with:
- Project name and ID
- Current status
- Created date
- Quick actions (view, execute, delete)

### Project Details

For each project, see:
- Business requirement
- Generated artifacts
  - Requirements document
  - Architecture diagram
  - Database schema
  - API specification
  - Task list
  - Generated code
  - Test cases
  - Documentation
- Execution history
  - Which phases have run
  - Execution status and duration
  - Any errors or warnings
- LLM call history
  - Prompts used
  - Responses received
  - Token usage
  - Costs

### Artifact Viewer

View generated artifacts:
- Syntax highlighted code
- Formatted documents
- Diagrams and charts
- Version history
- Diff viewer between versions

### Execution Pipeline

Visual pipeline execution:
- See which phases are running
- Monitor progress
- View logs in real-time
- Pause/resume/retry phases
- Estimate remaining time

## Using Different LLM Providers

### OpenAI (Recommended for beginners)

```bash
export OPENAI_API_KEY=sk-xxx
```

```yaml
# config/config.yaml
llm:
  provider: openai
  model: gpt-4-turbo-preview
```

### Anthropic Claude (Great quality)

```bash
export ANTHROPIC_API_KEY=sk-ant-xxx
```

```yaml
llm:
  provider: anthropic
  model: claude-3-opus-20240229
```

### Google Gemini (Cost effective)

```bash
export GOOGLE_API_KEY=xxx
```

```yaml
llm:
  provider: gemini
  model: gemini-1.5-pro
```

### Ollama (Local & Free)

```bash
# 1. Install Ollama from https://ollama.ai
# 2. Pull a model
ollama pull mistral

# 3. Run Ollama server
ollama serve

# 4. Configure
```

```yaml
llm:
  provider: ollama
  model: mistral
```

## Common Workflows

### Workflow 1: Basic Full Pipeline

```bash
# Create project with clear requirements
python main.py create-project \
  --name "project-name" \
  --requirement "Your detailed requirement"

# Run everything
python main.py run-pipeline --project "project-name"

# View results in web UI
python ui/app.py
# Navigate to project in browser
```

### Workflow 2: Iterative Refinement

```bash
# Create project
python main.py create-project --name "app" --requirement "Initial requirement"

# Run requirements analysis only
python main.py run-phase --project "app" --phase "requirements_analysis"

# View and refine requirements in UI

# Then run architecture
python main.py run-phase --project "app" --phase "architecture_design"

# Continue with other phases
python main.py run-phase --project "app" --phase "code_generation"
```

### Workflow 3: Custom Architecture

```bash
# Create project
python main.py create-project --name "app" --requirement "..."

# Run requirements first
python main.py run-phase --project "app" --phase "requirements_analysis"

# Manually edit architecture in UI if needed

# Continue with remaining phases
python main.py run-pipeline --project "app" --start-from "database_design"
```

## Troubleshooting

### "API key not found"

```bash
# Check environment variable
echo $OPENAI_API_KEY

# Or set in config.yaml
vim config/config.yaml
# Add: api_key: sk-xxx
```

### "Database locked"

```bash
# Restart to release lock
python main.py init
```

### "LLM timeout"

```yaml
# Increase timeout in config.yaml
llm:
  retry:
    max_wait: 120
```

### Port 8000 already in use

```yaml
# Change port in config.yaml
ui:
  port: 8001
```

## Next Steps

1. **Read Full Documentation**
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design
   - [API_GUIDE.md](API_GUIDE.md) - API endpoints
   - [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide

2. **Try More Complex Projects**
   - E-commerce platform
   - Analytics dashboard
   - Real-time chat application
   - Machine learning pipeline

3. **Customize**
   - Add custom agents
   - Create custom prompts
   - Implement validation rules
   - Add integrations

4. **Deploy**
   - Export generated code
   - Set up CI/CD pipeline
   - Deploy to production
   - Monitor and maintain

## Support & Resources

- **Issues**: Check GitHub Issues
- **Documentation**: See `docs/` folder
- **Examples**: Check `projects/` folder for examples
- **Community**: Join our community forums

## Tips for Best Results

1. **Be Specific in Requirements**
   - Clearly define what the system must do
   - Specify technology preferences
   - List non-functional requirements
   - Mention constraints and assumptions

2. **Use Clarification Questions**
   - The system will ask clarifying questions
   - Answer them thoroughly
   - Provide context and examples

3. **Review Generated Artifacts**
   - Check requirements analysis
   - Review architecture before code generation
   - Validate API design
   - Test generated code

4. **Iterate and Refine**
   - Regenerate phases if needed
   - Try different LLM models
   - Adjust temperature for consistency vs. creativity
   - Use feedback to improve prompts

5. **Version Control**
   - All artifacts are versioned
   - Can compare between versions
   - Full audit trail of changes
   - Can revert to previous versions
