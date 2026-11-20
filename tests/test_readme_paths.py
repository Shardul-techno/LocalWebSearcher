from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PATH_SUFFIXES = {".md", ".toml", ".txt", ".ps1", ".py", ".yml", ".yaml", ".iss", ".spec", ".json", ".lock"}


def _inline_code_spans(markdown: str) -> list[str]:
    # Fenced code blocks contain commands and examples, not inline repository links.
    without_fences = re.sub(r"(?ms)^\s*```.*?^\s*```\s*", "", markdown)
    return re.findall(r"`([^`]+)`", without_fences)


def _looks_like_repo_path(value: str) -> bool:
    value = value.strip()
    if not value or any(char.isspace() for char in value):
        return False
    if value.startswith(("http://", "https://")):
        return False
    normalized = value.replace("\\", "/")
    return "/" in normalized or Path(normalized).suffix.lower() in PATH_SUFFIXES


def test_backticked_repository_paths_exist() -> None:
    markdown = README.read_text(encoding="utf-8")
    missing = []
    for value in _inline_code_spans(markdown):
        if not _looks_like_repo_path(value):
            continue
        relative = value.replace("\\", "/").rstrip("/")
        if not (ROOT / relative).exists():
            missing.append(value)
    assert not missing, f"README references missing repository paths: {missing}"
