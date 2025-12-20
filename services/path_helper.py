from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def get_file(*relative_parts: str) -> Path:
    """Return a Path relative to the project root."""
    return PROJECT_ROOT.joinpath(*relative_parts)