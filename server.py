from pathlib import Path
import subprocess

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from config import (
    ALLOWED_COMMANDS,
    CODE_EXTS,
    IGNORE_DIRS,
    IGNORE_EXTS,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    PROJECT_ROOT,
)

app = FastAPI(title="Lean Local Coding Assistant")


# -------------------------
# Request models
# -------------------------

class ChatRequest(BaseModel):
    prompt: str
    model: str | None = None
    context_files: list[str] = Field(default_factory=list)


class FileRequest(BaseModel):
    path: str


class WriteFileRequest(BaseModel):
    path: str
    content: str


class CommandRequest(BaseModel):
    command: list[str]


class ListFilesRequest(BaseModel):
    directory: str = "."
    max_files: int = 300


# -------------------------
# Helpers
# -------------------------

def safe_path(relative_path: str) -> Path:
    """Prevent reading/writing outside PROJECT_ROOT."""
    path = (PROJECT_ROOT / relative_path).resolve()

    try:
        path.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Unsafe path") from exc

    return path


def should_skip(path: Path) -> bool:
    parts = set(path.relative_to(PROJECT_ROOT).parts)
    if parts & IGNORE_DIRS:
        return True
    return path.suffix.lower() in IGNORE_EXTS


def read_context_files(paths: list[str]) -> str:
    blocks: list[str] = []

    for relative_path in paths:
        path = safe_path(relative_path)

        if not path.exists() or not path.is_file():
            raise HTTPException(status_code=404, detail=f"Context file not found: {relative_path}")

        if should_skip(path):
            raise HTTPException(status_code=400, detail=f"Context file is ignored: {relative_path}")

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise HTTPException(status_code=400, detail=f"Cannot read non-text file: {relative_path}") from exc

        blocks.append(f"--- FILE: {relative_path} ---\n{content}")

    return "\n\n".join(blocks)


def ollama_chat(prompt: str, model: str | None = None) -> str:
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={
            "model": model or OLLAMA_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a careful local coding assistant. "
                        "Help with code review, debugging, refactoring, tests, and explanations. "
                        "Use only the context explicitly provided by the user or tools."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        },
        timeout=180,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("message", {}).get("content", "")


# -------------------------
# Tool 1: Plain AI chat
# -------------------------

@app.post("/chat")
def chat(request: ChatRequest):
    context = read_context_files(request.context_files)

    prompt = request.prompt
    if context:
        prompt = f"Use these project files as context:\n\n{context}\n\nUser request:\n{request.prompt}"

    return {
        "model": request.model or OLLAMA_MODEL,
        "response": ollama_chat(prompt, request.model),
    }


# -------------------------
# Tool 2: List project files
# -------------------------

@app.post("/list-files")
def list_files(request: ListFilesRequest):
    directory = safe_path(request.directory)

    if not directory.exists():
        raise HTTPException(status_code=404, detail="Directory not found")

    if not directory.is_dir():
        raise HTTPException(status_code=400, detail="Path is not a directory")

    files: list[str] = []

    for path in directory.rglob("*"):
        if len(files) >= request.max_files:
            break

        if not path.is_file():
            continue

        if should_skip(path):
            continue

        if path.suffix.lower() not in CODE_EXTS:
            continue

        files.append(str(path.relative_to(PROJECT_ROOT)))

    return {
        "root": str(PROJECT_ROOT),
        "directory": request.directory,
        "count": len(files),
        "files": files,
    }


# -------------------------
# Tool 3: Read file
# -------------------------

@app.post("/read-file")
def read_file(request: FileRequest):
    path = safe_path(request.path)

    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if not path.is_file():
        raise HTTPException(status_code=400, detail="Path is not a file")

    if should_skip(path):
        raise HTTPException(status_code=400, detail="File is ignored")

    return {
        "path": request.path,
        "content": path.read_text(encoding="utf-8"),
    }


# -------------------------
# Tool 4: Write file
# -------------------------

@app.post("/write-file")
def write_file(request: WriteFileRequest):
    path = safe_path(request.path)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(request.content, encoding="utf-8")

    return {
        "status": "written",
        "path": request.path,
    }


# -------------------------
# Tool 5: Run safe command
# -------------------------

@app.post("/run-command")
def run_command(request: CommandRequest):
    if not request.command:
        raise HTTPException(status_code=400, detail="Empty command")

    executable = request.command[0]

    if executable not in ALLOWED_COMMANDS:
        raise HTTPException(status_code=403, detail=f"Command not allowed: {executable}")

    result = subprocess.run(
        request.command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )

    return {
        "command": request.command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
