from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", os.getenv("DRUPAL_ROOT", "."))).expanduser().resolve()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3")

CODE_EXTS = {
    ".php", ".module", ".inc", ".install", ".theme",
    ".yml", ".yaml", ".twig", ".js", ".ts", ".css", ".scss",
    ".py", ".json", ".md", ".txt", ".rst", ".html", ".xml",
}

IGNORE_EXTS = {
    ".sqlite", ".gz", ".zip", ".tar", ".jpg", ".jpeg", ".png",
    ".gif", ".pdf", ".mp4", ".mov", ".sql", ".lock",
}

IGNORE_DIRS = {
    "vendor",
    "node_modules",
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "web/sites/default/files",
}

ALLOWED_COMMANDS = {
    "phpunit",
    "composer",
    "drush",
    "vendor/bin/phpunit",
    "python",
    "python3",
    "npm",
    "npx",
}
