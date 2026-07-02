# Installation Guide

## Prerequisites

- Python 3.12 or higher
- pip package manager
- Git (for version control)

## Step 1: Clone or Download the Project

```bash
git clone <repository-url>
cd ai-factory
```

## Step 2: Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Configure LLM Provider

Copy the example config and update with your API keys:

```bash
cp config/config.yaml.example config/config.yaml
```

Edit `config/config.yaml` and set:

```yaml
llm:
  provider: openai  # or anthropic, gemini, openrouter, ollama
  api_key: ${OPENAI_API_KEY}  # Or set environment variable
  model: gpt-4-turbo-preview
  temperature: 0.7
  max_tokens: 4000
```

### Setting up Environment Variables

```bash
# OpenAI
export OPENAI_API_KEY=sk-xxx

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-xxx

# Google Gemini
export GOOGLE_API_KEY=xxx

# OpenRouter
export OPENROUTER_API_KEY=xxx
```

## Step 5: Initialize the Database

```bash
python main.py init
```

This will create a SQLite database at `factory.db`.

## Step 6: Verify Installation

```bash
python main.py list-projects
```

You should see "No projects found." if the database is properly initialized.

## Starting the Web UI

```bash
python ui/app.py
```

The UI will be available at `http://localhost:8000`

## Quick Start

### Create a New Project

```bash
python main.py create-project \
  --name "todo-app" \
  --requirement "Build a simple task management application with authentication"
```

### List Projects

```bash
python main.py list-projects
```

### Show Project Status

```bash
python main.py show-status --project "todo-app"
```

## Using Different LLM Providers

### OpenAI (GPT-4, GPT-3.5-turbo)

```yaml
llm:
  provider: openai
  api_key: ${OPENAI_API_KEY}
  model: gpt-4-turbo-preview
```

### Anthropic (Claude)

```yaml
llm:
  provider: anthropic
  api_key: ${ANTHROPIC_API_KEY}
  model: claude-3-opus-20240229
```

### Google Gemini

```yaml
llm:
  provider: gemini
  api_key: ${GOOGLE_API_KEY}
  model: gemini-1.5-pro
```

### Ollama (Local)

```bash
# First, install and run Ollama
ollama pull mistral
ollama serve

# Then configure:
```

```yaml
llm:
  provider: ollama
  model: mistral
  api_key: null  # Not needed for local
```

### LM Studio (Local)

```bash
# Download and run LM Studio
# https://lmstudio.ai/

# Configure:
```

```yaml
llm:
  provider: lm-studio
  model: local-model
  api_key: null
```

## Troubleshooting

### Database Connection Error

```bash
rm factory.db
python main.py init
```

### Import Errors

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### LLM API Errors

Check that:
1. API key is correctly set in `config/config.yaml` or environment
2. API key has appropriate permissions
3. Rate limits are not exceeded
4. Model name is correct for the provider

### Port Already in Use (Web UI)

The default port is 8000. Change it in `config/config.yaml`:

```yaml
ui:
  host: 0.0.0.0
  port: 8001  # Use a different port
```

## Next Steps

1. Read [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
2. Read [API_GUIDE.md](docs/API_GUIDE.md) for API documentation
3. Explore [DEVELOPMENT.md](docs/DEVELOPMENT.md) for development setup
4. Check out example projects in `projects/` directory

## Getting Help

- Check the logs in `logs/factory.log`
- Review configuration in `config/config.yaml`
- Check LLM provider documentation for API-specific issues
