import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("lean-coding-assistant")

API_BASE_URL = "http://127.0.0.1:8000"


@mcp.tool()
def ask_ai(prompt: str, context_files: list[str] | None = None, model: str | None = None) -> dict:
    """Ask the local AI a coding question. Optionally include specific project files as context."""
    response = requests.post(
        f"{API_BASE_URL}/chat",
        json={
            "prompt": prompt,
            "context_files": context_files or [],
            "model": model,
        },
        timeout=180,
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def list_project_files(directory: str = ".", max_files: int = 300) -> dict:
    """List code and text files in the project. No embeddings or vector database are used."""
    response = requests.post(
        f"{API_BASE_URL}/list-files",
        json={"directory": directory, "max_files": max_files},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def read_project_file(path: str) -> dict:
    """Read a project file using a relative path."""
    response = requests.post(
        f"{API_BASE_URL}/read-file",
        json={"path": path},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def write_project_file(path: str, content: str) -> dict:
    """Write a project file using a relative path."""
    response = requests.post(
        f"{API_BASE_URL}/write-file",
        json={"path": path, "content": content},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def run_project_command(command: list[str]) -> dict:
    """Run an allowed local project command such as drush, composer, phpunit, npm, or python."""
    response = requests.post(
        f"{API_BASE_URL}/run-command",
        json={"command": command},
        timeout=180,
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    mcp.run()
