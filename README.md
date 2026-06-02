# Lean Local Coding Assistant

MCP tools for VS Code-compatible clients

## Architecture

```text
VS Code / MCP Client
    ↓
mcp_server.py
    ↓
server.py
    ↓
Ollama + project files you explicitly read/provide
```

## Environment

Create a `.env` file:

```bash
PROJECT_ROOT=/absolute/path/to/your/project
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3
```

`PROJECT_ROOT` replaces `DRUPAL_ROOT`, but the config still falls back to `DRUPAL_ROOT` if you already use that variable.

## Install

```bash
pip install -r requirements.txt
```

## Run Ollama

```bash
brew services start ollama
ollama pull qwen3
```

## Start the API server

```bash
uvicorn server:app --reload --port 8000
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Start the MCP server

In another terminal:

```bash
python mcp_server.py
```

## Tools

```text
ask_ai
list_project_files
read_project_file
write_project_file
run_project_command
```

## Example prompts

```text
List files in modules/custom.
Read modules/custom/example/example.module and explain it.
Ask AI to refactor this file using context_files=["modules/custom/example/example.module"].
Run drush cr.
Run composer validate.
```

## Important difference from RAG

This assistant does not search a vector database. It only knows:

1. what the user asks,
2. files explicitly read or passed as `context_files`,
3. command output returned by tools.

That keeps it lean and predictable.
